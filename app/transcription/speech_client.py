from __future__ import annotations

import asyncio
import logging
from collections.abc import AsyncGenerator
from typing import Callable

import azure.cognitiveservices.speech as speechsdk

from app.config import get_settings
from app.models.session import TranscriptEntry

logger = logging.getLogger(__name__)


def _build_recognizer(
    push_stream: speechsdk.audio.PushAudioInputStream,
) -> speechsdk.SpeechRecognizer:
    """Build a SpeechRecognizer with multilingual auto-detection (EN + MS)."""
    settings = get_settings()

    speech_config = speechsdk.SpeechConfig(
        subscription=settings.azure_speech_key,
        region=settings.azure_speech_region,
    )
    # Enable language detection for English and Malay (handles Manglish via GPT-4o)
    auto_detect_config = speechsdk.languageconfig.AutoDetectSourceLanguageConfig(
        languages=["en-US", "ms-MY"]
    )

    audio_config = speechsdk.audio.AudioConfig(stream=push_stream)

    recognizer = speechsdk.SpeechRecognizer(
        speech_config=speech_config,
        audio_config=audio_config,
        auto_detect_source_language_config=auto_detect_config,
    )
    return recognizer


class SpeechClient:
    """
    Real-time speech-to-text client using Azure Speech Services.

    Yields TranscriptEntry objects as speech is recognized.
    Supports multilingual input: English (en-US), Malay (ms-MY), and Manglish.

    Usage:
        client = SpeechClient(speaker_name="Ali")
        async for entry in client.stream():
            print(entry)
        # Push raw PCM audio: client.push_audio(pcm_bytes)
        # Stop: await client.stop()
    """

    def __init__(self, speaker_name: str = "Unknown") -> None:
        self.speaker_name = speaker_name
        self._push_stream = speechsdk.audio.PushAudioInputStream()
        self._recognizer = _build_recognizer(self._push_stream)
        self._queue: asyncio.Queue[TranscriptEntry | None] = asyncio.Queue()
        self._loop: asyncio.AbstractEventLoop | None = None

    def _enqueue(self, entry: TranscriptEntry | None) -> None:
        """Thread-safe enqueue from Speech SDK callback thread."""
        if self._loop:
            self._loop.call_soon_threadsafe(self._queue.put_nowait, entry)

    def _on_recognized(self, evt: speechsdk.SpeechRecognitionEventArgs) -> None:
        if evt.result.reason == speechsdk.ResultReason.RecognizedSpeech:
            text = evt.result.text.strip()
            if not text:
                return

            # Extract detected language
            lang_result = speechsdk.AutoDetectSourceLanguageResult(evt.result)
            language = lang_result.language or "en-US"

            entry = TranscriptEntry(
                speaker=self.speaker_name,
                text=text,
                language=language,
            )
            self._enqueue(entry)

    def _on_canceled(self, evt: speechsdk.SpeechRecognitionCanceledEventArgs) -> None:
        details = speechsdk.CancellationDetails(evt.result)
        if details.reason == speechsdk.CancellationReason.Error:
            logger.error("Speech recognition canceled: %s", details.error_details)
        self._enqueue(None)  # signal end of stream

    def push_audio(self, audio_bytes: bytes) -> None:
        """Push raw PCM audio bytes (16kHz, 16-bit, mono) into the recognizer."""
        self._push_stream.write(audio_bytes)

    def close_audio(self) -> None:
        """Signal end of audio stream."""
        self._push_stream.close()

    async def stream(self) -> AsyncGenerator[TranscriptEntry, None]:
        """Async generator yielding TranscriptEntry objects as speech is recognized."""
        self._loop = asyncio.get_running_loop()

        self._recognizer.recognized.connect(self._on_recognized)
        self._recognizer.canceled.connect(self._on_canceled)
        self._recognizer.start_continuous_recognition()

        logger.info("Speech recognition started (en-US, ms-MY)")

        try:
            while True:
                entry = await self._queue.get()
                if entry is None:
                    break
                yield entry
        finally:
            self._recognizer.stop_continuous_recognition()
            logger.info("Speech recognition stopped")

    async def stop(self) -> None:
        """Gracefully stop recognition and flush the queue."""
        self.close_audio()
        self._enqueue(None)
