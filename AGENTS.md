# Gymweb Agent Guide

## Purpose

This repository is a Django app for tracking body composition, workout programs, and workout history.

## Project layout

- `tracker/`: main app for models, views, forms, admin, templates, and management commands
- `gymweb/`: Django project settings and URL configuration
- `templates/`: shared base templates
- `static/`: static assets

## Setup and run

### Windows

Prefer `start_server.bat`. It creates `.venv`, installs dependencies, loads `.env.local` first and then `.env`, runs migrations, seeds the default program, and starts the dev server on `http://127.0.0.1:5174/`.

If `.env.local` and `.env` are both missing, defaults from `gymweb/settings.py` are used.

### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py seed_program
python manage.py runserver 127.0.0.1:5174
```

## Environment notes

- Preferred local override file: `.env.local`
- Shared env template: `.env.example`
- Supported Django env names include both `DJANGO_*` and short names like `DEBUG` or `SECRET_KEY`
- Default database is MySQL
- For zero-config local work, set `DB_ENGINE=sqlite`
- Do not commit secrets from `.env` or `.env.local`

## Validation

- Run tests with `python manage.py test`
- There is currently very little automated coverage, so also sanity-check key pages in the browser when changing views, templates, routing, or forms
- When database schema changes are introduced, run `python manage.py migrate`

## Agent workflow

- Prefer small, targeted changes
- Avoid changing unrelated files
- Preserve the current dev server port: `5174`
- The seed command `python manage.py seed_program` is intended to be idempotent and is safe to rerun during setup
- If MySQL is unavailable in local or cloud environments, switch to SQLite instead of blocking on DB setup
