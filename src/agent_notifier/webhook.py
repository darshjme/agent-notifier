"""WebhookNotifier — non-blocking HTTP POST via urllib."""

from __future__ import annotations

import json
import logging
import threading
import urllib.request
from typing import Any

logger = logging.getLogger(__name__)

_SENTINEL = object()


class WebhookNotifier:
    """Posts JSON payloads to a URL in a background thread.

    Parameters
    ----------
    url:
        Endpoint to POST to.
    headers:
        Extra HTTP headers (``Content-Type: application/json`` is always set).
    timeout:
        Socket timeout in seconds (default 5.0).
    """

    def __init__(
        self,
        url: str,
        headers: dict[str, str] | None = None,
        timeout: float = 5.0,
    ) -> None:
        self.url = url
        self.headers: dict[str, str] = {"Content-Type": "application/json"}
        if headers:
            self.headers.update(headers)
        self.timeout = timeout
        self._last_status: int | None = None
        self._lock = threading.Lock()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    @property
    def last_status(self) -> int | None:
        """HTTP status code from the most recent delivery, or ``None``."""
        with self._lock:
            return self._last_status

    def notify(self, event: str, data: dict[str, Any] | None = None) -> None:
        """POST *event* and *data* as JSON — fires in a daemon thread."""
        payload = {"event": event, "data": data or {}}
        thread = threading.Thread(
            target=self._post,
            args=(payload,),
            daemon=True,
            name=f"webhook-{event}",
        )
        thread.start()

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _post(self, payload: dict) -> None:
        body = json.dumps(payload).encode()
        req = urllib.request.Request(
            self.url,
            data=body,
            headers=self.headers,
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                status = resp.status
        except urllib.error.HTTPError as exc:
            status = exc.code
            logger.warning("Webhook %s returned HTTP %d", self.url, status)
        except Exception as exc:  # noqa: BLE001
            logger.error("Webhook delivery failed: %s", exc)
            status = None  # type: ignore[assignment]

        with self._lock:
            self._last_status = status
