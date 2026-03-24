"""agent-notifier: Notification dispatch for agent events."""

from .notifier import Notifier
from .webhook import WebhookNotifier
from .digest import DigestNotifier
from .router import NotificationRouter

__all__ = ["Notifier", "WebhookNotifier", "DigestNotifier", "NotificationRouter"]
__version__ = "1.0.0"
