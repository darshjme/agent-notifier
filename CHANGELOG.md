# Changelog

All notable changes to `agent-notifier` are documented here.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
This project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.0.0] — 2026-03-24

### Added
- `Notifier` — in-process pub/sub dispatcher with `subscribe`, `unsubscribe`, `notify`, `notify_all`.
- `WebhookNotifier` — non-blocking HTTP POST via `urllib`; exposes `last_status`.
- `DigestNotifier` — buffered notifications with auto-flush at configurable `flush_size`.
- `NotificationRouter` — glob-pattern routing (`fnmatch`) to multiple notifiers.
- Zero runtime dependencies; requires Python ≥ 3.10.
- 45 pytest tests with full `unittest.mock` coverage for urllib.
