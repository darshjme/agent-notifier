"""Tests for the base Notifier class."""
import pytest
from agent_notifier import Notifier


def make_recorder():
    calls = []
    def handler(event, data):
        calls.append((event, data))
    handler.calls = calls
    return handler


# ---------------------------------------------------------------------------
# __init__
# ---------------------------------------------------------------------------

def test_notifier_name():
    n = Notifier("my-agent")
    assert n.name == "my-agent"


# ---------------------------------------------------------------------------
# subscribe / unsubscribe
# ---------------------------------------------------------------------------

def test_subscribe_and_notify():
    n = Notifier("a")
    h = make_recorder()
    n.subscribe("done", h)
    n.notify("done", {"status": "ok"})
    assert h.calls == [("done", {"status": "ok"})]


def test_subscribe_duplicate_ignored():
    n = Notifier("a")
    h = make_recorder()
    n.subscribe("done", h)
    n.subscribe("done", h)  # second subscribe ignored
    n.notify("done")
    assert len(h.calls) == 1


def test_unsubscribe_removes_handler():
    n = Notifier("a")
    h = make_recorder()
    n.subscribe("done", h)
    n.unsubscribe("done", h)
    n.notify("done")
    assert h.calls == []


def test_unsubscribe_noop_if_not_registered():
    n = Notifier("a")
    h = make_recorder()
    n.unsubscribe("done", h)  # should not raise


def test_notify_no_subscribers():
    n = Notifier("a")
    n.notify("nothing")  # should not raise


def test_notify_default_empty_data():
    n = Notifier("a")
    h = make_recorder()
    n.subscribe("ping", h)
    n.notify("ping")
    assert h.calls[0][1] == {}


def test_notify_handler_exception_does_not_propagate():
    n = Notifier("a")
    def bad_handler(event, data):
        raise RuntimeError("oops")
    n.subscribe("boom", bad_handler)
    n.notify("boom")  # should not raise


def test_notify_multiple_handlers():
    n = Notifier("a")
    h1, h2 = make_recorder(), make_recorder()
    n.subscribe("ev", h1)
    n.subscribe("ev", h2)
    n.notify("ev", {"x": 1})
    assert len(h1.calls) == 1
    assert len(h2.calls) == 1


# ---------------------------------------------------------------------------
# notify_all
# ---------------------------------------------------------------------------

def test_notify_all_fires_each_event():
    n = Notifier("a")
    h = make_recorder()
    n.subscribe("a", h)
    n.subscribe("b", h)
    n.subscribe("c", h)
    n.notify_all(["a", "b", "c"], {"val": 99})
    events = [c[0] for c in h.calls]
    assert events == ["a", "b", "c"]


def test_notify_all_empty_list():
    n = Notifier("a")
    n.notify_all([])  # should not raise


def test_notify_all_shared_data():
    n = Notifier("a")
    h = make_recorder()
    n.subscribe("x", h)
    n.subscribe("y", h)
    n.notify_all(["x", "y"], {"k": "v"})
    assert all(c[1] == {"k": "v"} for c in h.calls)
