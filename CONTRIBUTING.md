# Contributing

Thank you for your interest in contributing to `agent-notifier`!

## Ground rules

1. **Zero runtime dependencies** — keep it that way. The entire library must work with the Python standard library alone.
2. **Python ≥ 3.10** — no backports, no `typing_extensions`.
3. **Tests for every change** — PRs without tests will not be merged.

## Local setup

```bash
git clone https://github.com/yourorg/agent-notifier
cd agent-notifier
pip install -e ".[dev]"
python -m pytest tests/ -v
```

## Submitting a PR

1. Fork the repo and create a feature branch (`feat/my-feature`).
2. Write tests first (TDD preferred).
3. Ensure `python -m pytest tests/ -v` reports **all passed**.
4. Update `CHANGELOG.md` under `[Unreleased]`.
5. Open a pull request with a clear description of the change.

## Code style

- Follow PEP 8.
- Prefer explicit over implicit.
- Keep modules small and focused.
- Type-annotate all public APIs.

## Reporting bugs

Open a GitHub issue with:
- Python version + OS
- Minimal reproducible example
- Expected vs actual behaviour
