#!/usr/bin/env python
"""
MeetingBot — Local Meeting Runner
==================================
Captures laptop microphone audio in real-time, transcribes via Azure Speech,
and runs a live terminal meeting session against the MeetingBot FastAPI backend.

Prerequisites:
    1. FastAPI backend running:  uvicorn app.main:app --reload
    2. .env file populated with Azure credentials (loaded automatically)
    3. System audio: libportaudio2 installed (Linux) / PortAudio (macOS/Windows)

Usage:
    python scripts/local_meeting.py \\
        --title "Sprint Planning" \\
        --participants "Alice,Bob,Charlie" \\
        --speaker "Alice"

In-session commands:
    ? <question>   Ask the bot a question (uses live transcript + docs + KB + web)
    end            End the meeting, generate minutes, upload to SharePoint, create Planner tasks
    Ctrl+C         Same as 'end'
"""
from __future__ import annotations

import argparse
import asyncio
import getpass
import os
import sys
import threading
from pathlib import Path

import httpx
import numpy as np

# Load .env from project root before anything else
_project_root = Path(__file__).parent.parent
_env_file = _project_root / ".env"
if _env_file.exists():
    from dotenv import load_dotenv  # type: ignore[import]
    load_dotenv(_env_file)

import sounddevice as sd

# Import after .env is loaded so Settings picks up env vars
sys.path.insert(0, str(_project_root))
from app.transcription.speech_client import SpeechClient
from app.transcription.transcript_buffer import TranscriptBuffer

# ── Config ─────────────────────────────────────────────────────────────────────
SAMPLE_RATE = 16_000   # Hz — required by Azure Speech push stream
CHANNELS = 1           # mono
BLOCK_SIZE = 1600      # 100 ms blocks at 16kHz
DTYPE = "int16"        # Azure Speech expects 16-bit PCM


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="MeetingBot local meeting runner")
    parser.add_argument("--title", default="Local Meeting", help="Meeting title")
    parser.add_argument(
        "--participants",
        default="",
        help="Comma-separated participant names (e.g. Alice,Bob)",
    )
    parser.add_argument(
        "--speaker",
        default=getpass.getuser(),
        help="Your display name shown in the transcript (default: system username)",
    )
    parser.add_argument(
        "--api-url",
        default="http://localhost:8000",
        help="MeetingBot API base URL (default: http://localhost:8000)",
    )
    return parser.parse_args()


# ── API helpers ────────────────────────────────────────────────────────────────

def api_post(base: str, path: str, **kwargs) -> dict:
    resp = httpx.post(f"{base}{path}", timeout=60.0, **kwargs)
    resp.raise_for_status()
    return resp.json()


def api_get(base: str, path: str) -> dict:
    resp = httpx.get(f"{base}{path}", timeout=30.0)
    resp.raise_for_status()
    return resp.json()


# ── Mic → Speech pipeline ──────────────────────────────────────────────────────

class MicCapture:
    """
    Captures laptop microphone audio using sounddevice and feeds raw PCM bytes
    to an Azure SpeechClient push stream.
    """

    def __init__(self, speech_client: SpeechClient) -> None:
        self._client = speech_client
        self._stream: sd.InputStream | None = None

    def _callback(
        self,
        indata: np.ndarray,
        frames: int,
        time,
        status: sd.CallbackFlags,
    ) -> None:
        if status:
            print(f"\n[mic] {status}", file=sys.stderr)
        # sounddevice delivers float32 when dtype='float32'; we configured int16 directly
        self._client.push_audio(indata.tobytes())

    def start(self) -> None:
        self._stream = sd.InputStream(
            samplerate=SAMPLE_RATE,
            channels=CHANNELS,
            dtype=DTYPE,
            blocksize=BLOCK_SIZE,
            callback=self._callback,
        )
        self._stream.start()

    def stop(self) -> None:
        if self._stream:
            self._stream.stop()
            self._stream.close()
        self._client.close_audio()


# ── Terminal input loop ────────────────────────────────────────────────────────

async def input_loop(
    meeting_id: str,
    api_base: str,
    stop_event: asyncio.Event,
) -> None:
    """
    Reads user input from stdin:
      - '? <question>'  → Q&A against live meeting context
      - 'end'           → signals stop_event to finish the meeting
    """
    loop = asyncio.get_running_loop()
    while not stop_event.is_set():
        try:
            line = await loop.run_in_executor(None, sys.stdin.readline)
        except (EOFError, KeyboardInterrupt):
            stop_event.set()
            break

        line = line.strip()
        if not line:
            continue

        if line.lower() == "end":
            stop_event.set()
            break

        if line.startswith("?"):
            question = line[1:].strip()
            if not question:
                print("[bot] Please provide a question after '?'")
                continue
            print(f"\n[you] {question}")
            try:
                result = api_post(
                    api_base,
                    f"/meetings/{meeting_id}/qa",
                    json={"question": question, "conversation_id": meeting_id},
                )
                print(f"[bot] {result['answer']}\n")
            except Exception as exc:
                print(f"[error] Q&A failed: {exc}\n")
        else:
            print("  Commands:  ? <question>  |  end")


# ── Transcript streaming task ──────────────────────────────────────────────────

async def stream_transcript(
    speech_client: SpeechClient,
    buffer: TranscriptBuffer,
    meeting_id: str,
    api_base: str,
    stop_event: asyncio.Event,
) -> None:
    """
    Consumes TranscriptEntry objects from the SpeechClient stream,
    prints them to the terminal, appends to the buffer, and batch-pushes
    to the API so the backend buffer stays in sync.
    """
    batch: list[dict] = []

    async for entry in speech_client.stream():
        if stop_event.is_set():
            break

        ts = entry.timestamp.strftime("%H:%M:%S")
        lang_tag = f"[{entry.language}]" if entry.language != "en-US" else ""
        print(f"  [{ts}] {entry.speaker}{lang_tag}: {entry.text}")

        buffer.append(entry)
        batch.append({"speaker": entry.speaker, "text": entry.text, "language": entry.language})

        # Push to API in batches of 5 to keep backend buffer in sync
        if len(batch) >= 5:
            try:
                api_post(
                    api_base,
                    f"/meetings/{meeting_id}/transcript",
                    json=batch,
                )
            except Exception as exc:
                print(f"\n[warn] Transcript sync failed: {exc}", file=sys.stderr)
            batch.clear()

    # Flush remaining
    if batch:
        try:
            api_post(api_base, f"/meetings/{meeting_id}/transcript", json=batch)
        except Exception:
            pass


# ── End meeting + print summary ───────────────────────────────────────────────

def print_minutes(minutes: dict) -> None:
    print("\n" + "=" * 60)
    print(f"  MEETING MINUTES: {minutes.get('title', 'Meeting')}")
    print(f"  Date: {minutes.get('date')}  |  ID: {minutes.get('meeting_id')}")
    print("=" * 60)

    attendees = minutes.get("attendees", [])
    if attendees:
        print(f"\nAttendees: {', '.join(attendees)}")

    print(f"\nSummary:\n{minutes.get('summary', '(none)')}")

    decisions = minutes.get("key_decisions", [])
    if decisions:
        print("\nKey Decisions:")
        for d in decisions:
            print(f"  • {d}")

    items = minutes.get("action_items", [])
    if items:
        print("\nAction Items:")
        for item in items:
            due = f"  due {item['due_date']}" if item.get("due_date") else ""
            planner = f"  [Planner: {item['planner_task_id']}]" if item.get("planner_task_id") else ""
            print(f"  • [{item['pic']}]{due} — {item['title']}{planner}")

    sp_url = minutes.get("sharepoint_url")
    if sp_url:
        print(f"\nSharePoint: {sp_url}")

    print("=" * 60 + "\n")


# ── Main ───────────────────────────────────────────────────────────────────────

async def run(args: argparse.Namespace) -> None:
    api_base = args.api_url.rstrip("/")

    # Verify backend is reachable
    try:
        resp = httpx.get(f"{api_base}/health", timeout=5.0)
        resp.raise_for_status()
    except Exception:
        print(f"[error] Cannot reach API at {api_base}. Is the backend running?")
        print("        Start it with:  uvicorn app.main:app --reload")
        sys.exit(1)

    # Start meeting session
    participants = [p.strip() for p in args.participants.split(",") if p.strip()]
    session = api_post(
        api_base,
        "/meetings",
        json={"title": args.title, "participants": participants},
    )
    meeting_id = session["meeting_id"]

    print(f"\n{'=' * 60}")
    print(f"  Meeting: {args.title}")
    print(f"  ID: {meeting_id}")
    print(f"  Speaker: {args.speaker}")
    if participants:
        print(f"  Participants: {', '.join(participants)}")
    print(f"{'=' * 60}")
    print("  Listening... speak now.")
    print("  Commands:  ? <question>  |  end  |  Ctrl+C")
    print(f"{'=' * 60}\n")

    speech_client = SpeechClient(speaker_name=args.speaker)
    buffer = TranscriptBuffer()
    mic = MicCapture(speech_client)
    stop_event = asyncio.Event()

    mic.start()

    try:
        await asyncio.gather(
            stream_transcript(speech_client, buffer, meeting_id, api_base, stop_event),
            input_loop(meeting_id, api_base, stop_event),
        )
    except (KeyboardInterrupt, asyncio.CancelledError):
        pass
    finally:
        mic.stop()

    # End meeting
    print("\n[bot] Generating meeting minutes…")
    try:
        minutes = api_post(api_base, f"/meetings/{meeting_id}/end")
        print_minutes(minutes)
    except Exception as exc:
        print(f"[error] Failed to end meeting: {exc}")


def main() -> None:
    # Check for python-dotenv (optional but helpful for local dev)
    try:
        import dotenv  # noqa: F401
    except ImportError:
        pass  # .env loaded above via direct parse if available

    args = parse_args()
    try:
        asyncio.run(run(args))
    except KeyboardInterrupt:
        print("\nInterrupted.")


if __name__ == "__main__":
    main()
