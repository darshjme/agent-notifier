"""Tests for WebhookNotifier — urllib mocked throughout."""
import json
import threading
import time
from unittest.mock import MagicMock, patch
import urllib.error

import pytest
from agent_notifier import WebhookNotifier


URL = "https://example.com/hook"


def _fake_response(status: int = 200):
    resp = MagicMock()
    resp.status = status
    resp.__enter__ = lambda s: s
    resp.__exit__ = MagicMock(return_value=False)
    return resp


def _wait_for_status(notifier, timeout=2.0):
    """Poll until last_status is set (background thread)."""
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if notifier.last_status is not None:
            return
        time.sleep(0.02)


# ---------------------------------------------------------------------------
# Construction
# ---------------------------------------------------------------------------

def test_webhook_default_headers():
    wh = WebhookNotifier(URL)
    assert wh.headers["Content-Type"] == "application/json"


def test_webhook_custom_headers_merged():
    wh = WebhookNotifier(URL, headers={"X-Token": "abc"})
    assert wh.headers["X-Token"] == "abc"
    assert wh.headers["Content-Type"] == "application/json"


def test_webhook_default_timeout():
    wh = WebhookNotifier(URL)
    assert wh.timeout == 5.0


def test_webhook_last_status_initially_none():
    wh = WebhookNotifier(URL)
    assert wh.last_status is None


# ---------------------------------------------------------------------------
# Successful delivery
# ---------------------------------------------------------------------------

def test_notify_posts_json():
    wh = WebhookNotifier(URL)
    captured = {}

    def fake_urlopen(req, timeout=None):
        captured["body"] = json.loads(req.data)
        captured["method"] = req.method
        return _fake_response(200)

    with patch("agent_notifier.webhook.urllib.request.urlopen", side_effect=fake_urlopen):
        wh.notify("task.done", {"result": "ok"})
        _wait_for_status(wh)

    assert captured["method"] == "POST"
    assert captured["body"]["event"] == "task.done"
    assert captured["body"]["data"]["result"] == "ok"


def test_notify_updates_last_status_200():
    wh = WebhookNotifier(URL)
    with patch("agent_notifier.webhook.urllib.request.urlopen", return_value=_fake_response(200)):
        wh.notify("ping")
        _wait_for_status(wh)
    assert wh.last_status == 200


# ---------------------------------------------------------------------------
# Error handling
# ---------------------------------------------------------------------------

def test_notify_http_error_records_status():
    wh = WebhookNotifier(URL)
    err = urllib.error.HTTPError(URL, 500, "Server Error", {}, None)
    with patch("agent_notifier.webhook.urllib.request.urlopen", side_effect=err):
        wh.notify("error")
        _wait_for_status(wh)
    assert wh.last_status == 500


def test_notify_network_error_does_not_raise():
    wh = WebhookNotifier(URL)
    with patch("agent_notifier.webhook.urllib.request.urlopen", side_effect=OSError("unreachable")):
        wh.notify("error")  # non-blocking — should not raise
        time.sleep(0.1)   # let thread run


def test_notify_is_non_blocking():
    """notify() should return immediately, not wait for HTTP."""
    barrier = threading.Event()
    def slow_urlopen(req, timeout=None):
        barrier.wait(timeout=5)
        return _fake_response(200)

    wh = WebhookNotifier(URL)
    with patch("agent_notifier.webhook.urllib.request.urlopen", side_effect=slow_urlopen):
        t0 = time.monotonic()
        wh.notify("slow")
        elapsed = time.monotonic() - t0
    assert elapsed < 0.5, f"notify() blocked for {elapsed:.2f}s"
    barrier.set()
