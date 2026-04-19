# Gymweb

A small, local-first **body composition + workout tracker** built with **Django + MySQL**.

It tracks:

- **BMI** (derived from height + weight, with caveats clearly shown)
- **Body fat %** (manual / smart-scale / calipers / DEXA)
- **Muscle** (kg or %)
- **Gym routines** — programs → days → exercises with sets × reps, rest, and instructions
- **Workout history** with per-set logging and **CSV export**

The dev server runs on **port 5174**.

---

## Review of the proposed stack vs Django + MySQL

The original proposal suggested a TypeScript stack (Next.js / Vite + React, Tailwind, Recharts,
local-first storage with Dexie/Supabase later). That stack is excellent if you want a SPA with
strong editor intelligence on the client and the option of zero-backend storage.

This repository instead implements the same idea on **Django + MySQL**, which is also a very good
fit and arguably easier to operate when you want a real database from day one:

| Concern              | Django + MySQL choice in this repo                                              |
| -------------------- | ------------------------------------------------------------------------------- |
| Editor intelligence  | Django models give clear types; pyright/mypy + Pylance work well on the codebase. |
| Persistence          | MySQL via `mysqlclient` (with `PyMySQL` fallback). SQLite mode for zero-config. |
| Charts               | Chart.js via CDN — same UX as Recharts, no JS build step required.              |
| Auth                 | Django auth + admin are built-in; ready when you want multi-user sync.          |
| API later            | Add Django REST Framework if you decide to ship a SPA on top.                   |
| Cost of ops          | Single Python process + one MySQL DB; trivial to host.                          |

So yes — **Django + MySQL is a perfectly reasonable substitution** for the proposed Next.js + Supabase
plan, and is what this repo ships.

---

## Project layout

```
gymweb/                Django project (settings, urls, wsgi)
tracker/               App: models, views, forms, admin, templates, seed command
templates/base.html    Shared layout
static/tracker/        CSS
manage.py              Django entry point
start.bat              One-click Windows launcher (port 5174)
requirements.txt
.env.example
```

Domain model:

- `Profile` — height, sex, units
- `BodyLog` — dated weight / body-fat % / muscle, with source + notes
- `Program` → `Day` → `Exercise` — routine structure with rich coaching cues
- `WorkoutSession` → `SetEntry` — per-session set logging

---

## Quick start (Windows)

Double-click **`start.bat`** or **`start_server.bat`** in the repo root. **`start_server.bat`** loads **`.env.local`** first (if present), then `.env`; **`start.bat`** only loads `.env`. Both scripts will:

1. Create `.venv/` and install dependencies
2. Load the env file(s) above when present
3. Run migrations and seed the default *Full Body 3x/week* program
4. Start the dev server at <http://127.0.0.1:5174/>

By default it expects MySQL on `127.0.0.1:3306` with database `gymweb` and user `root`. Override
those by copying `.env.example` to `.env` or `.env.local`. For a zero-config run set `DB_ENGINE=sqlite`.
If you use Docker Compose, set `DB_HOST` to the MySQL service name (often `db`) **only** inside the container network; on the Windows host use `127.0.0.1` (or the published port).

## Quick start (macOS / Linux)

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env       # then edit DB_* values, or set DB_ENGINE=sqlite
python manage.py migrate
python manage.py seed_program
python manage.py runserver 127.0.0.1:5174
```

Then open <http://127.0.0.1:5174/>.

## MySQL setup

```sql
CREATE DATABASE gymweb CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'gymweb'@'localhost' IDENTIFIED BY 'change-me';
GRANT ALL PRIVILEGES ON gymweb.* TO 'gymweb'@'localhost';
FLUSH PRIVILEGES;
```

Then in `.env`:

```
DB_ENGINE=mysql
DB_NAME=gymweb
DB_USER=gymweb
DB_PASSWORD=change-me
DB_HOST=127.0.0.1
DB_PORT=3306
```

`mysqlclient` is preferred but needs MySQL client headers. On non-Windows installs,
pip pulls in `mysqlclient`; on Windows the requirements file skips it and the app uses
**PyMySQL** as a drop-in instead. Django 6’s MySQL backend insists on mysqlclient 2.2.1+,
so this repo pins **Django 5.x** until you install a matching mysqlclient on Windows
(or use SQLite via `DB_ENGINE=sqlite`).

## Admin

Create a superuser and use `/admin/` to manage everything in a structured form:

```bash
python manage.py createsuperuser
```

## Branch discipline (matches the proposal)

- `main` is the protected, always-green branch.
- Feature work happens on `cursor/...` branches and lands via PR.
- Add CI (typecheck/lint/test/build) on every PR before turning on branch protection.

## Roadmap

- [ ] Per-user accounts (replace the singleton profile)
- [ ] DRF JSON API for a future SPA / mobile client
- [ ] Imperial unit conversions in the UI
- [ ] More starter programs (PPL, Upper/Lower)
