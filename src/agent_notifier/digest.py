"""DigestNotifier — buffers notifications and delivers in bulk."""

from __future__ import annotations

import threading
import time
from typing import Any


class DigestNotifier:
    """Batches notifications; delivers them when :meth:`flush` is called.

    Parameters
    ----------
    flush_size:
        Maximum number of items to hold before auto-flushing on the next
        :meth:`notify` call (default 10).  A value of 0 disables auto-flush.
    """

    def __init__(self, flush_size: int = 10) -> None:
        if flush_size < 0:
            raise ValueError("flush_size must be >= 0")
        self.flush_size = flush_size
        self._buffer: list[dict[str, Any]] = []
        self._lock = threading.Lock()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    @property
    def pending_count(self) -> int:
        """Number of buffered but un-flushed notifications."""
        with self._lock:
            return len(self._buffer)

    def notify(self, event: str, data: dict[str, Any] | None = None) -> None:
        """Buffer *event* + *data*.

        If *flush_size* > 0 and the buffer reaches that size, it is
        automatically flushed (items are discarded — override this method
        to deliver them somewhere).
        """
        entry = {"event": event, "data": data or {}, "ts": time.time()}
        with self._lock:
            self._buffer.append(entry)
            should_flush = self.flush_size > 0 and len(self._buffer) >= self.flush_size

        if should_flush:
            self.flush()

    def flush(self) -> list[dict[str, Any]]:
        """Return all buffered notifications and clear the buffer."""
        with self._lock:
            items = list(self._buffer)
            self._buffer.clear()
        return items
