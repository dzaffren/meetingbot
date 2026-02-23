"""Unit tests for TranscriptBuffer."""
from __future__ import annotations

import threading

import pytest

from app.models.session import TranscriptEntry
from app.transcription.transcript_buffer import TranscriptBuffer


def _entry(speaker: str = "Alice", text: str = "Hello") -> TranscriptEntry:
    return TranscriptEntry(speaker=speaker, text=text)


def test_append_and_snapshot():
    buf = TranscriptBuffer()
    e1 = _entry("Alice", "Hello")
    e2 = _entry("Bob", "World")
    buf.append(e1)
    buf.append(e2)
    snap = buf.snapshot()
    assert len(snap) == 2
    assert snap[0].text == "Hello"
    assert snap[1].speaker == "Bob"


def test_snapshot_does_not_clear():
    buf = TranscriptBuffer()
    buf.append(_entry())
    buf.snapshot()
    assert len(buf) == 1


def test_snapshot_and_clear():
    buf = TranscriptBuffer()
    buf.append(_entry("A", "1"))
    buf.append(_entry("B", "2"))
    drained = buf.snapshot_and_clear()
    assert len(drained) == 2
    assert len(buf) == 0


def test_last_n():
    buf = TranscriptBuffer()
    for i in range(10):
        buf.append(_entry(text=str(i)))
    last = buf.last_n(3)
    assert [e.text for e in last] == ["7", "8", "9"]


def test_to_text():
    buf = TranscriptBuffer()
    buf.append(_entry("Alice", "Good morning"))
    text = buf.to_text()
    assert "Alice" in text
    assert "Good morning" in text


def test_thread_safety():
    buf = TranscriptBuffer()
    errors: list[Exception] = []

    def writer():
        try:
            for i in range(100):
                buf.append(_entry(text=str(i)))
        except Exception as e:
            errors.append(e)

    threads = [threading.Thread(target=writer) for _ in range(5)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert not errors
    assert len(buf) == 500


def test_clear():
    buf = TranscriptBuffer()
    buf.append(_entry())
    buf.clear()
    assert len(buf) == 0
