# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Run development server
python run.py

# Run production server (gunicorn)
python -m gunicorn wsgi:app

# Run tests
pytest

# Run single test
pytest tests/test_routes.py::test_index
```

## Architecture

**Flask application** using the application factory pattern. The app is created via `create_app()` in `app/__init__.py`, which loads configuration and registers blueprints.

**Directory structure:**
```
app/
├── __init__.py          # Application factory
├── config.py            # Config classes (DevelopmentConfig, ProductionConfig, TestingConfig)
├── models/
│   └── logs.py          # Log parsing utilities
├── routes/
│   ├── main.py          # Index and chatroom list (Blueprint: main)
│   ├── chat.py          # Daily log display (Blueprint: chat)
│   └── search.py        # Search functionality (Blueprint: search)
├── templates/           # Jinja2 templates
└── static/              # CSS
```

**Entry points:**
- `run.py` - Development server
- `wsgi.py` - Production server (gunicorn)

**Configuration:** Environment variables via `app/config.py`:
- `MATTERLOGSERVER_LOGS_PATH` - Path to log files (default: `./logs`)
- `MATTERLOGSERVER_LOGS_BASE_URL` - Base URL for logs
- `MATTERLOGSERVER_PROXY_LEVEL` - Proxy fix level
- `SECRET_KEY` - Flask secret key

**Log file format:** Tab-separated: `<ISO8601_datetime>\t<user>\t<message>`

**Testing:** pytest with test configuration that uses `./tests/data/logs` as the logs path. Fixtures provide `app` and `client`.

**Docker:** `Dockerfile` builds Alpine-based image with gunicorn entrypoint.
