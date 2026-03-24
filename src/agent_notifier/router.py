"""NotificationRouter — glob-pattern routing to multiple notifiers."""

from __future__ import annotations

import fnmatch
from typing import TYPE_CHECKING, Any, Protocol, runtime_checkable


@runtime_checkable
class NotifierProtocol(Protocol):
    """Anything with a ``notify(event, data)`` method qualifies."""

    def notify(self, event: str, data: dict | None = None) -> None: ...  # noqa: E704


class NotificationRouter:
    """Routes events to notifiers based on glob patterns.

    Example
    -------
    >>> router = NotificationRouter()
    >>> router.register("agent.*", webhook)
    >>> router.register("agent.error", pager)
    >>> router.dispatch("agent.error", {"msg": "boom"})
    # webhook AND pager both receive the event
    """

    def __init__(self) -> None:
        self._routes: list[tuple[str, NotifierProtocol]] = []

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def register(self, event_pattern: str, notifier: NotifierProtocol) -> None:
        """Map *event_pattern* (glob) to *notifier*.

        Multiple notifiers may share the same pattern; they are called
        in registration order.
        """
        self._routes.append((event_pattern, notifier))

    def dispatch(self, event: str, data: dict[str, Any] | None = None) -> None:
        """Send *event* to every notifier whose pattern matches."""
        for pattern, notifier in self._routes:
            if fnmatch.fnmatch(event, pattern):
                notifier.notify(event, data)
