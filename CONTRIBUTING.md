# Contributing to Clipboard Push Server

Thanks for your interest in contributing!

## Getting Started

```bash
git clone https://github.com/clipboardpush/clipboard-push-server.git
cd clipboard-push-server
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your local settings
python wsgi.py  # Dev server on port 5055
```

## Project Structure

```
app/
  __init__.py       Flask app factory
  settings.py       All config via environment variables
  auth.py           Login + password hash logic
  route.py          HTTP routes
  signal_core.py    Room/peer state dictionaries
  socket_events.py  Socket.IO event handlers
templates/          Jinja2 HTML templates
static/             CSS, JS, favicon
```

## Code Style

- PEP 8, 4-space indent, `snake_case` for functions/vars, `UPPER_SNAKE_CASE` for constants
- Keep Socket.IO event handlers in `app/socket_events.py`
- Keep room/peer state dictionaries in `app/signal_core.py`
- All config must come from environment variables via `app/settings.py` — no hardcoded values

## Commit Messages

Follow Conventional Commits:

```
feat: add support for X
fix: handle Y edge case
docs: update deployment guide
chore: bump dependency version
```

## Pull Requests

1. Fork the repo and create a branch from `master`
2. Keep changes focused — one feature or fix per PR
3. For significant changes, open an issue first to discuss the approach
4. PR description should include:
   - What user-facing change this makes
   - Any new `.env` keys required
   - What you tested (or why tests aren't applicable)

## Running Tests

No automated tests are configured yet. If you add tests, place them under `tests/` using `test_*.py` naming and document the command here.

## Reporting Bugs

Open a GitHub issue with:
- Steps to reproduce
- Expected vs. actual behaviour
- Server version / Python version

## Security Issues

Please do **not** open a public issue for security vulnerabilities. Use GitHub's private security advisory feature instead.

## License

By contributing, you agree that your contributions will be licensed under the Apache 2.0 License.
