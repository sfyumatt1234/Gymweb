# Gymweb — Development notes

This document captures integration planning for **MuscleWiki API** (`https://api.musclewiki.com/documentation`), UI goals inspired by **MuscleWiki** (workout planning / results), and how we avoid burning API quota.

---

## 1. MuscleWiki API — authentication & quota

### Authentication

- Every request needs header: **`X-API-Key: mw_...`**
- Create/manage keys in the developer dashboard: `https://api.musclewiki.com/dashboard/api-keys`

### Plans & direct API access

Per official docs / marketing pages:

- **BASIC (free)**: playground exploration; **direct API access from your own code may require upgrade** (docs mention upgrading to **TESTING (~$5/mo)** or higher for full direct API access).
- Paid tiers bill **monthly API call quotas**; when exceeded, responses return **HTTP 429** with a message like “Monthly API quota exceeded”.

### Where to see quota usage

- Use the **MuscleWiki API dashboard** (same area as API keys / billing) for usage counters and alerts (docs mention email alerts around high usage).

### High-cost endpoints (watch billing)

Some “aggregate” endpoints **count as multiple API calls**:

- `/routines/{id}/full` — response includes `api_calls_cost`; header **`X-API-Calls-Cost`**
- `/workouts/{id}/full` — same pattern

**Rule of thumb**: prefer `/exercises` list + `/exercises/{id}` detail instead of `/full` unless you truly need one-shot expansion.

### Media streaming also counts

Streaming endpoints under `/stream/...` **still require `X-API-Key`** and **meter as API usage** per docs.

---

## 2. Core endpoints for building our exercise UX

### Discover metadata (cache aggressively)

| Endpoint | Purpose |
|----------|---------|
| `GET /` | Root metadata + endpoint map |
| `GET /health` | Health check |
| `GET /statistics` | DB stats |
| `GET /muscles` | Primary muscle groups + counts (build filters) |
| `GET /categories` | Equipment categories + counts |
| `GET /filters` | All filter values for dynamic UI |

Docs suggest caching **`/muscles`, `/categories`, `/filters`** for long periods (up to ~30 days) because they change infrequently.

### List & detail exercises

| Endpoint | Purpose |
|----------|---------|
| `GET /exercises` | Paginated list; supports filters |
| `GET /exercises/{id}` | Full exercise payload (steps, videos, etc.) |
| `GET /exercises/{id}/videos` | Video URLs only (bandwidth saver) |
| `GET /search?q=...` | Text search with relevance ranking |
| `GET /random` | Random exercise (variation features) |

### `/exercises` query parameters (high-signal)

Documented filters include:

- `limit` (1–100), `offset`
- `search` (min 2 chars)
- `gender` for videos (`male` / `female`)
- `category` equipment (`barbell`, `dumbbell`, `bodyweight`, …)
- **`muscles`** — muscle group filter (examples show values like “Chest”, “Biceps”)
- `difficulty` (`novice`, `intermediate`, `advanced`, …)
- `force` (`push`, `pull`, `static`)
- `mechanic` (`isolation`, `compound`)
- `grips` (e.g. overhand / underhand)

### Routines / workouts (optional)

| Endpoint | Purpose |
|----------|---------|
| `GET /routines` | Browse programs |
| `GET /workouts` | Browse workouts (can filter by goal/equipment/muscles) |
| `GET /workouts/{id}` | Workout details w/ prescriptions |

These are useful for “Workout results” pages similar to MuscleWiki’s generated plans, but watch **quota cost** especially for `*/full`.

---

## 3. Plan: fetch exercises per muscle bucket (chest / back / legs / abs / other)

### Step A — canonical names from API

1. Call `GET /muscles`
2. Store exact **API muscle names** (display strings) — these are what `muscles=` expects.

### Step B — map “UI buckets” → API muscles

Because “Legs” may split into **Quads / Hamstrings / Glutes / Calves**, maintain a mapping table in code or DB:

| UI bucket | Example API `muscles=` values (illustrative; verify via `/muscles`) |
|-----------|----------------------------------------------------------------------|
| Chest | `Chest` |
| Back | `Lats`, `Upper Back`, `Lower Back`, … |
| Legs | `Quads`, `Hamstrings`, `Glutes`, `Calves`, … |
| Abs / core | `Abs`, `Obliques`, … |
| Other | everything else bucketed (arms, shoulders, cardio tags, etc.) |

### Step C — pagination for each bucket

For each muscle name in a bucket:

```
GET /exercises?muscles={Name}&limit=100&offset=0
```

Repeat with `offset += limit` until `offset + count >= total`.

### Step D — detail-on-demand

For list views, prefer **minimal list** data from `/exercises`.  
When user opens a card, fetch:

```
GET /exercises/{id}
```

If only video is needed:

```
GET /exercises/{id}/videos
```

---

## 4. Quota-efficient architecture for Gymweb

### Do

- Cache `/muscles`, `/categories`, `/filters` locally (DB or Django cache).
- Paginate (`limit`/`offset`) and **filter on the server** (`muscles`, `category`, …).
- Lazy-load exercise details.
- Track `X-API-Calls-Cost` when using any `*/full` endpoint.

### Avoid

- Scraping the public website instead of API (terms + maintenance).
- Downloading all videos during development.
- Calling `/workouts/{id}/full` or `/routines/{id}/full` in tight loops without caching.

---

## 5. UI reference — MuscleWiki-style “Workout results”

Target experience (screenshots / `musclewiki.com`):

- Left: stacked **exercise cards** — thumbnail, title, equipment tag, prescription table (sets × reps or time), swap/link affordances.
- Right: **summary** — coverage %, targeted muscle groups count, equipment tags.
- **Body graph / heatmap** — front/back silhouette with highlighted muscles.

### Gymweb implementation status (snapshot)

- App shell with sidebar navigation (Exercises / Planning / Schedule / Tools / Body graph).
- Local curated library under `/exercises/` (fallback / offline-first dev).
- `/planning/` form → `/planning/results/` scaffold (generated plan cards + summary sidebar).

### Next integration steps with MuscleWiki API

1. Add server-side client + env var `MUSCLEWIKI_API_KEY`.
2. Replace or augment curated lists with API-backed queries by `muscles` + `category`.
3. Exercise detail page from `GET /exercises/{id}` with embedded streamed video URLs.
4. Upgrade body graph from clickable regions → heatmap driven by **primary muscles** returned by API.

---

## 6. Env vars (planned)

```
MUSCLEWIKI_API_KEY=mw_...
MUSCLEWIKI_API_BASE=https://api.musclewiki.com
```

Never commit real keys; use `.env.local` / deployment secrets.

---

## 7. References

- API docs: `https://api.musclewiki.com/documentation`
- OpenAPI (from root `GET /`): `GET https://api.musclewiki.com/openapi.json`
- Terms (pricing channels): `https://api.musclewiki.com/api-terms`
