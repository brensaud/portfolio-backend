# portfolio-backend

[![CI](https://github.com/brensaud/portfolio-backend/actions/workflows/ci.yml/badge.svg)](https://github.com/brensaud/portfolio-backend/actions/workflows/ci.yml)

FastAPI backend for [brensaud.com](https://brensaud.com).

**API:** [api.brensaud.com](https://api.brensaud.com) &nbsp;|&nbsp; **Frontend:** [portfolio-frontend](https://github.com/brensaud/portfolio-frontend)

---

## Stack

| Layer | Technology |
|---|---|
| Framework | FastAPI 0.138 |
| Language | Python 3.12 |
| ORM | SQLAlchemy 2.0 (async) |
| Database | PostgreSQL (Neon in production) |
| Migrations | Alembic |
| Validation | Pydantic v2 |
| Rate limiting | Redis (Upstash in production) |
| Package manager | uv |
| Linting | Ruff |
| Type checking | mypy |
| Testing | pytest + httpx + aiosqlite |
| Containers | Docker + Docker Compose |
| Hosting | Railway |

---

## Quick start

### Option A — Docker Compose (recommended)

```bash
cd backend
docker compose up --build
```

Starts backend + PostgreSQL + Redis. API available at [http://localhost:8000](http://localhost:8000).
Alembic migrations run automatically on container start.

### Option B — Local (uv)

```bash
# 1. Install dependencies
uv sync --group dev

# 2. Set environment variables
cp .env.example .env   # then fill in values

# 3. Run migrations (requires a running PostgreSQL)
uv run alembic upgrade head

# 4. Start the server
uv run uvicorn app.main:app --reload
```

---

## API

| Method | Path | Description |
|---|---|---|
| `GET` | `/health` | App status + DB connectivity |
| `POST` | `/api/v1/contact/messages` | Submit a contact message |

Interactive docs: [http://localhost:8000/docs](http://localhost:8000/docs) (development only)

### POST /api/v1/contact/messages

**Request:**
```json
{
  "name": "Jane Smith",
  "email": "jane@example.com",
  "subject": "Hiring inquiry",
  "message": "Hello, I would like to discuss..."
}
```

**Response 201:**
```json
{
  "id": "uuid",
  "message": "Your message has been received.",
  "reference_id": "MSG-XXXXXXXX"
}
```

**Rate limit:** 5 requests per IP per hour (Redis-backed, degrades gracefully).

---

## Commands

| Command | Description |
|---|---|
| `uv run uvicorn app.main:app --reload` | Dev server with hot reload |
| `uv run alembic upgrade head` | Apply all pending migrations |
| `uv run alembic revision --autogenerate -m "..."` | Generate a new migration |
| `uv run pytest` | Run test suite |
| `uv run pytest --cov=app` | Run tests with coverage |
| `uv run ruff check app/ tests/` | Lint |
| `uv run ruff format --check app/ tests/` | Format check |
| `uv run ruff format app/ tests/` | Format write |
| `uv run mypy app/` | Type check |

---

## Environment variables

| Variable | Required | Description |
|---|---|---|
| `DATABASE_URL` | Yes | asyncpg connection string |
| `REDIS_URL` | No | Redis URL (rate limiting disabled if absent) |
| `ALLOWED_ORIGINS` | Yes | JSON array of allowed CORS origins |
| `ENVIRONMENT` | Yes | `development` / `staging` / `production` |
| `DEBUG` | No | `true` enables SQL echo and debug logging |
| `RATE_LIMIT_REQUESTS` | No | Max submissions per IP per window (default: 5) |
| `RATE_LIMIT_WINDOW_SECONDS` | No | Rate limit window in seconds (default: 3600) |

See [`.env.example`](.env.example) for the full template.

**Production values:**

| Variable | Value |
|---|---|
| `DATABASE_URL` | Neon PostgreSQL connection string |
| `REDIS_URL` | Upstash Redis connection string (`rediss://...`) |
| `ALLOWED_ORIGINS` | `["https://brensaud.com","https://www.brensaud.com"]` |
| `ENVIRONMENT` | `production` |
| `DEBUG` | `false` |

---

## Project structure

```
app/
├── api/v1/
│   ├── endpoints/
│   │   ├── contact.py    # POST /api/v1/contact/messages
│   │   └── health.py     # GET /health
│   └── router.py
├── core/
│   ├── config.py         # Pydantic-settings (all env vars)
│   ├── logging.py        # Structured logging setup
│   └── rate_limit.py     # Redis rate limiter with graceful degradation
├── db/
│   ├── base.py           # Async engine + DeclarativeBase
│   └── session.py        # get_db dependency
├── models/
│   └── contact.py        # ContactMessage ORM model
├── repositories/
│   └── contact_repo.py   # Data access layer
├── schemas/
│   ├── contact.py        # Request / response schemas
│   └── errors.py         # ErrorResponse schema
├── services/
│   ├── contact_service.py  # Business logic, transaction boundary
│   └── email_service.py    # AbstractEmailService protocol + console stub
└── main.py               # FastAPI app factory, lifespan, CORS
```

---

## CI — GitHub Actions

Runs on every push and pull request to `main`.

| Job | What it checks |
|---|---|
| **Lint** | `ruff check` + `ruff format --check` |
| **Type check** | `mypy app/` |
| **Test** | `pytest --cov=app` + coverage artifact |
| **Docker** | `docker build` (no push) |
| **Env check** | `.env.example` present; `.env` not committed |

### Quality gates (must pass before merge)

- `uv run ruff check app/ tests/`
- `uv run ruff format --check app/ tests/`
- `uv run mypy app/`
- `uv run pytest`
- Docker build succeeds

---

## CD — Railway

Railway deploys automatically via the GitHub integration.

| Event | Result |
|---|---|
| Push to `main` | Production deployment → `api.brensaud.com` |

**Railway settings:**

| Setting | Value |
|---|---|
| Source | Dockerfile |
| Health check path | `/health` |
| Port | `8000` |

**Start command (Railway runs this after build):**
```bash
alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000
```

**Custom domain:** Add `api.brensaud.com` in Railway → Settings → Domains. Add a CNAME record in Cloudflare pointing to the Railway-provided URL.

### Production deployment checklist

- [ ] `DATABASE_URL` set to Neon connection string (use the pooled URL)
- [ ] `REDIS_URL` set to Upstash Redis URL (`rediss://` for TLS)
- [ ] `ALLOWED_ORIGINS` set to `["https://brensaud.com","https://www.brensaud.com"]`
- [ ] `ENVIRONMENT=production`
- [ ] `DEBUG=false`
- [ ] `GET /health` returns `{"status":"ok","database":"ok"}`
- [ ] Alembic migrations applied (`alembic upgrade head`)
- [ ] CORS tested from `brensaud.com`
- [ ] Rate limiting verified (submit 6 times from same IP)

---

## Branch strategy

| Branch | Purpose |
|---|---|
| `main` | Production — always deployable |
| `feat/*` | New endpoints or services |
| `fix/*` | Bug fixes |
| `chore/*` | Tooling, dependencies, migrations |

Use [Conventional Commits](https://www.conventionalcommits.org/): `feat`, `fix`, `chore`, `docs`, `refactor`, `test`.
