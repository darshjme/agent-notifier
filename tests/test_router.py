"""Tests for NotificationRouter."""
import pytest
from agent_notifier import NotificationRouter, Notifier, DigestNotifier


def make_spy_notifier(name="spy"):
    calls = []
    n = Notifier(name)
    def handler(event, data):
        calls.append((event, data))
    n.subscribe("*", handler)  # won't match — we track via direct mock
    # Simpler: wrap notify
    original = n.notify
    def spy_notify(event, data=None):
        calls.append((event, data))
    n.notify = spy_notify
    n.calls = calls
    return n


# ---------------------------------------------------------------------------
# register / dispatch — basic
# ---------------------------------------------------------------------------

def test_dispatch_exact_match():
    router = NotificationRouter()
    spy = make_spy_notifier()
    router.register("agent.done", spy)
    router.dispatch("agent.done", {"ok": True})
    assert spy.calls == [("agent.done", {"ok": True})]


def test_dispatch_no_match_no_call():
    router = NotificationRouter()
    spy = make_spy_notifier()
    router.register("agent.done", spy)
    router.dispatch("agent.error")
    assert spy.calls == []


def test_dispatch_glob_star():
    router = NotificationRouter()
    spy = make_spy_notifier()
    router.register("agent.*", spy)
    router.dispatch("agent.error")
    router.dispatch("agent.done")
    router.dispatch("agent.budget")
    assert len(spy.calls) == 3


def test_dispatch_glob_question_mark():
    router = NotificationRouter()
    spy = make_spy_notifier()
    router.register("ev.?", spy)
    router.dispatch("ev.a")
    router.dispatch("ev.b")
    router.dispatch("ev.xyz")  # should NOT match
    assert len(spy.calls) == 2


def test_dispatch_multiple_notifiers_same_pattern():
    router = NotificationRouter()
    spy1, spy2 = make_spy_notifier(), make_spy_notifier()
    router.register("task.*", spy1)
    router.register("task.*", spy2)
    router.dispatch("task.done")
    assert len(spy1.calls) == 1
    assert len(spy2.calls) == 1


def test_dispatch_multiple_patterns_one_notifier():
    router = NotificationRouter()
    spy = make_spy_notifier()
    router.register("agent.*", spy)
    router.register("task.*", spy)
    router.dispatch("agent.error")
    router.dispatch("task.start")
    assert len(spy.calls) == 2


def test_dispatch_wildcard_matches_all():
    router = NotificationRouter()
    spy = make_spy_notifier()
    router.register("*", spy)
    router.dispatch("anything")
    router.dispatch("agent.done")
    assert len(spy.calls) == 2


def test_dispatch_passes_data():
    router = NotificationRouter()
    spy = make_spy_notifier()
    router.register("x", spy)
    router.dispatch("x", {"key": "value"})
    assert spy.calls[0][1] == {"key": "value"}


def test_dispatch_none_data_default():
    router = NotificationRouter()
    spy = make_spy_notifier()
    router.register("ping", spy)
    router.dispatch("ping")
    assert spy.calls[0][1] is None


def test_dispatch_empty_router_no_error():
    router = NotificationRouter()
    router.dispatch("orphan")  # should not raise


# ---------------------------------------------------------------------------
# Integration: router → DigestNotifier
# ---------------------------------------------------------------------------

def test_router_with_digest_notifier():
    router = NotificationRouter()
    digest = DigestNotifier(flush_size=0)
    router.register("agent.*", digest)
    router.dispatch("agent.error", {"msg": "fail"})
    router.dispatch("agent.done", {"msg": "ok"})
    items = digest.flush()
    assert len(items) == 2
    assert items[0]["event"] == "agent.error"
    assert items[1]["event"] == "agent.done"
