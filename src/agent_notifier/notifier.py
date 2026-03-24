"""Base Notifier — event dispatcher with subscribe/unsubscribe."""

from __future__ import annotations

import logging
from collections import defaultdict
from typing import Callable

logger = logging.getLogger(__name__)


class Notifier:
    """Base notification dispatcher.

    Handlers registered via :meth:`subscribe` are called synchronously
    when :meth:`notify` fires an event.
    """

    def __init__(self, name: str) -> None:
        self.name = name
        self._handlers: dict[str, list[Callable]] = defaultdict(list)

    # ------------------------------------------------------------------
    # Subscription management
    # ------------------------------------------------------------------

    def subscribe(self, event: str, handler: Callable) -> None:
        """Register *handler* for *event*."""
        if handler not in self._handlers[event]:
            self._handlers[event].append(handler)

    def unsubscribe(self, event: str, handler: Callable) -> None:
        """Remove *handler* from *event*.  No-op if not registered."""
        try:
            self._handlers[event].remove(handler)
        except ValueError:
            pass

    # ------------------------------------------------------------------
    # Dispatch
    # ------------------------------------------------------------------

    def notify(self, event: str, data: dict | None = None) -> None:
        """Fire all handlers registered for *event*."""
        data = data or {}
        handlers = list(self._handlers.get(event, []))
        for handler in handlers:
            try:
                handler(event, data)
            except Exception as exc:  # noqa: BLE001
                logger.exception(
                    "Handler %r raised while processing event %r: %s",
                    handler,
                    event,
                    exc,
                )

    def notify_all(self, events: list[str], data: dict | None = None) -> None:
        """Fire :meth:`notify` for every event in *events*."""
        for event in events:
            self.notify(event, data)
