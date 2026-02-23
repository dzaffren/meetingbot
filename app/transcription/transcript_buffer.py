from __future__ import annotations

import threading
from copy import deepcopy
from typing import Sequence

from app.models.session import TranscriptEntry


class TranscriptBuffer:
    """
    Thread-safe in-memory buffer for accumulating TranscriptEntry objects
    during a live meeting session.

    Entries are appended as they arrive from the SpeechClient stream.
    Use snapshot() to read without clearing, or snapshot_and_clear() to
    atomically drain the buffer (e.g., at meeting end).
    """

    def __init__(self) -> None:
        self._entries: list[TranscriptEntry] = []
        self._lock = threading.Lock()

    def append(self, entry: TranscriptEntry) -> None:
        """Append a new transcript entry (thread-safe)."""
        with self._lock:
            self._entries.append(entry)

    def snapshot(self) -> list[TranscriptEntry]:
        """Return a shallow copy of all entries without clearing."""
        with self._lock:
            return list(self._entries)

    def snapshot_and_clear(self) -> list[TranscriptEntry]:
        """Atomically return all entries and clear the buffer."""
        with self._lock:
            entries = list(self._entries)
            self._entries.clear()
            return entries

    def clear(self) -> None:
        """Discard all buffered entries."""
        with self._lock:
            self._entries.clear()

    def last_n(self, n: int) -> list[TranscriptEntry]:
        """Return the last N entries (for QA context window)."""
        with self._lock:
            return list(self._entries[-n:])

    def to_text(self, entries: Sequence[TranscriptEntry] | None = None) -> str:
        """
        Format entries as a readable transcript string.
        Uses current buffer contents if entries is None.
        """
        source = entries if entries is not None else self.snapshot()
        lines = [f"[{e.timestamp.strftime('%H:%M:%S')}] {e.speaker}: {e.text}" for e in source]
        return "\n".join(lines)

    def __len__(self) -> int:
        with self._lock:
            return len(self._entries)
