# Security Policy

## Supported versions

| Version | Supported |
|---------|-----------|
| 1.x     | ✅ Yes     |

## Reporting a vulnerability

**Please do not open a public GitHub issue for security vulnerabilities.**

Email the maintainers at **security@yourorg.example** with:

- A description of the vulnerability
- Steps to reproduce
- Potential impact
- Any suggested fix

We will acknowledge receipt within **48 hours** and provide a fix timeline within **7 days**.

## Scope

Relevant security concerns for this library:

- **SSRF via WebhookNotifier** — callers control the URL. Validate/allowlist URLs before passing user-supplied values.
- **Sensitive data in payloads** — `data` dicts are serialised to JSON and sent over the wire. Do not include credentials, PII, or secrets.
- **Thread safety** — `WebhookNotifier._last_status` and `DigestNotifier._buffer` are protected by `threading.Lock`. Extensions should follow the same pattern.
