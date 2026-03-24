# agent-notifier

> Notification dispatch for agent events — webhooks, digests, and routers. Zero dependencies.

[![Python](https://img.shields.io/badge/python-%3E%3D3.10-blue)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## Why

When an agent completes a task, hits an error, or blows through a budget threshold you need to tell someone *fast*. Wiring this ad-hoc leads to duplicated, untested code. `agent-notifier` gives you four composable primitives:

| Class | What it does |
|---|---|
| `Notifier` | In-process pub/sub dispatcher |
| `WebhookNotifier` | Non-blocking HTTP POST (urllib, no deps) |
| `DigestNotifier` | Batches events, flushes on demand or at threshold |
| `NotificationRouter` | Glob-pattern routing to multiple notifiers |

## Install

```bash
pip install agent-notifier
```

## Quick-start — agent error notification

```python
from agent_notifier import NotificationRouter, WebhookNotifier, DigestNotifier, Notifier

# 1. Webhook fires immediately on any agent.error
slack_hook = WebhookNotifier(
    url="https://hooks.slack.com/services/T000/B000/XXXX",
    headers={"X-Source": "my-agent"},
)

# 2. Digest collects all events for a batch report
digest = DigestNotifier(flush_size=0)

# 3. Router wires it together with glob patterns
router = NotificationRouter()
router.register("agent.error", slack_hook)   # immediate Slack alert
router.register("agent.*",     digest)        # every agent event buffered

# 4. Simulate your agent lifecycle
router.dispatch("agent.start",  {"agent": "summariser", "job": "doc-42"})
router.dispatch("agent.error",  {"agent": "summariser", "msg": "context window exceeded"})
router.dispatch("agent.done",   {"agent": "summariser", "tokens_used": 8_192})

# 5. Flush digest at end of run (e.g. send as email)
batch = digest.flush()
print(f"Batch report: {len(batch)} events")
for item in batch:
    print(f"  [{item['event']}] {item['data']}")
```

Output:
```
Batch report: 3 events
  [agent.start]  {'agent': 'summariser', 'job': 'doc-42'}
  [agent.error]  {'agent': 'summariser', 'msg': 'context window exceeded'}
  [agent.done]   {'agent': 'summariser', 'tokens_used': 8192}
```

Slack receives an immediate POST for `agent.error`; `last_status` lets you verify delivery.

## API reference

### `Notifier(name)`

```python
n = Notifier("budget-guard")
n.subscribe("budget.exceeded", lambda event, data: print(data))
n.notify("budget.exceeded", {"limit": 1.00, "spent": 1.23})
n.notify_all(["budget.exceeded", "agent.error"], {"critical": True})
n.unsubscribe("budget.exceeded", handler)
```

- Handlers are called synchronously in registration order.
- A handler that raises does **not** propagate — the error is logged and execution continues.
- `notify_all(events, data)` fires each event with the same `data` dict.

### `WebhookNotifier(url, headers=None, timeout=5.0)`

```python
wh = WebhookNotifier("https://example.com/hook", headers={"Authorization": "Bearer tok"})
wh.notify("task.done", {"result": "success"})
print(wh.last_status)   # e.g. 200
```

- Fires in a **daemon thread** — `notify()` returns immediately.
- Payload: `{"event": "<event>", "data": {…}}` (JSON).
- `last_status` is `None` until the first delivery attempt completes.

### `DigestNotifier(flush_size=10)`

```python
d = DigestNotifier(flush_size=5)
d.notify("ev", {"n": 1})
print(d.pending_count)   # 1
items = d.flush()        # [{"event": "ev", "data": {"n": 1}, "ts": 1234.5}]
```

- `flush_size=0` disables auto-flush entirely.
- When `pending_count >= flush_size` the buffer is flushed automatically.
- Each item carries `ts` (Unix timestamp from `time.time()`).

### `NotificationRouter()`

```python
router = NotificationRouter()
router.register("agent.*",    webhook)   # glob — matches agent.done, agent.error …
router.register("agent.error", pager)    # exact — also matches
router.dispatch("agent.error", {"msg": "boom"})
# → webhook called, pager called
```

- Patterns follow [`fnmatch`](https://docs.python.org/3/library/fnmatch.html) rules (`*`, `?`, `[seq]`).
- Multiple patterns/notifiers are independent; all matching notifiers are called.

## Development

```bash
git clone https://github.com/yourorg/agent-notifier
cd agent-notifier
pip install -e ".[dev]"
python -m pytest tests/ -v
```

## License

MIT — see [LICENSE](LICENSE).
