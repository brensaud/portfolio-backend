# Running with Docker Compose

All services (PostgreSQL, Redis, FastAPI) in one command.
No local Python, Postgres, or Redis installation required.

---

## Prerequisites

- Docker Desktop running
- Admin credentials set in `docker-compose.yml` (see `01_quick_start.md`)

---

## Start everything

```powershell
cd backend
docker compose up --build   # first run, or after code changes
docker compose up           # subsequent runs (no rebuild)
```

Docker Compose starts three containers:

| Container | Image | Port | Purpose |
|---|---|---|---|
| `backend` | Built from `Dockerfile` | 8000 | FastAPI app |
| `db` | `postgres:16-alpine` | 5432 | PostgreSQL database |
| `redis` | `redis:7-alpine` | 6379 | Rate limiting |

Alembic migrations run automatically on every backend startup.

---

## Verify the backend is running

```powershell
# Health check
curl http://localhost:8000/health

# Expected response:
# {"status":"ok","database":"connected","version":"0.1.0",...}
```

---

## Start the frontend (separate terminal)

```powershell
cd frontend
pnpm dev
```

Open **http://localhost:5173** — the contact form will talk to the backend at port 8000.

---

## Admin panel

1. Go to **http://localhost:5173/admin/login**
2. Sign in with the email and password you set in `docker-compose.yml`
3. Navigate to **Messages** in the top nav bar

---

## Useful Docker commands

```powershell
# Follow backend logs
docker compose logs -f backend

# Follow all logs
docker compose logs -f

# Rebuild only the backend image
docker compose build backend

# Open a psql shell on the database
docker compose exec db psql -U postgres portfolio

# Run a one-off backend command
docker compose exec backend /app/.venv/bin/python -m app.cli.hash_password

# Run pending Alembic migrations manually
docker compose exec backend /app/.venv/bin/alembic upgrade head

# Check current migration state
docker compose exec backend /app/.venv/bin/alembic current

# Stop containers (data is preserved)
docker compose down

# Stop containers and wipe ALL data (fresh database)
docker compose down -v

# Stop and remove images too
docker compose down --rmi local -v
```

---

## Troubleshooting

### Backend fails to start — "database connection refused"
The backend starts before PostgreSQL is ready.
The `healthcheck` in `docker-compose.yml` handles this automatically — the backend
waits until `pg_isready` succeeds before starting. If it still fails, run:

```powershell
docker compose down -v
docker compose up --build
```

### Port 8000 or 5432 already in use
Another process is using that port. Find and stop it:

```powershell
netstat -ano | findstr :8000
taskkill /PID <pid> /F
```

### Admin login fails — "Invalid credentials"
The password hash in `docker-compose.yml` is wrong or missing.
Re-run the hash generator and update the value:

```powershell
docker compose run --rm --no-deps backend /app/.venv/bin/python -m app.cli.hash_password
```

Then restart:

```powershell
docker compose down
docker compose up
```

### Changes to Python code not reflected
Source code is mounted as a volume (`./app:/app/app`) so hot-reload is active.
Save the file — uvicorn reloads automatically. No rebuild needed.

### Changes to dependencies (pyproject.toml)
Rebuild the image:

```powershell
docker compose build backend
docker compose up
```
