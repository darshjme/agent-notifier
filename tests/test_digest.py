"""Tests for DigestNotifier."""
import pytest
from agent_notifier import DigestNotifier


# ---------------------------------------------------------------------------
# Construction
# ---------------------------------------------------------------------------

def test_default_flush_size():
    d = DigestNotifier()
    assert d.flush_size == 10


def test_custom_flush_size():
    d = DigestNotifier(flush_size=3)
    assert d.flush_size == 3


def test_invalid_flush_size_raises():
    with pytest.raises(ValueError):
        DigestNotifier(flush_size=-1)


# ---------------------------------------------------------------------------
# pending_count / buffering
# ---------------------------------------------------------------------------

def test_initial_pending_count():
    d = DigestNotifier()
    assert d.pending_count == 0


def test_notify_increments_pending():
    d = DigestNotifier(flush_size=0)  # auto-flush disabled
    d.notify("ev1")
    d.notify("ev2")
    assert d.pending_count == 2


def test_notify_stores_event_and_data():
    d = DigestNotifier(flush_size=0)
    d.notify("task.done", {"id": 42})
    items = d.flush()
    assert items[0]["event"] == "task.done"
    assert items[0]["data"]["id"] == 42


def test_notify_adds_timestamp():
    import time
    d = DigestNotifier(flush_size=0)
    before = time.time()
    d.notify("ts-check")
    after = time.time()
    items = d.flush()
    assert before <= items[0]["ts"] <= after


# ---------------------------------------------------------------------------
# flush()
# ---------------------------------------------------------------------------

def test_flush_returns_all_items():
    d = DigestNotifier(flush_size=0)
    for i in range(5):
        d.notify(f"ev{i}")
    items = d.flush()
    assert len(items) == 5


def test_flush_clears_buffer():
    d = DigestNotifier(flush_size=0)
    d.notify("x")
    d.flush()
    assert d.pending_count == 0


def test_flush_empty_returns_empty_list():
    d = DigestNotifier()
    assert d.flush() == []


def test_flush_twice_second_is_empty():
    d = DigestNotifier(flush_size=0)
    d.notify("a")
    d.flush()
    assert d.flush() == []


# ---------------------------------------------------------------------------
# Auto-flush
# ---------------------------------------------------------------------------

def test_auto_flush_at_flush_size():
    d = DigestNotifier(flush_size=3)
    d.notify("a")
    d.notify("b")
    assert d.pending_count == 2
    d.notify("c")  # triggers auto-flush
    assert d.pending_count == 0


def test_auto_flush_disabled_when_zero():
    d = DigestNotifier(flush_size=0)
    for _ in range(20):
        d.notify("spam")
    assert d.pending_count == 20
