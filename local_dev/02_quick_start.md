# Local Development — Quick Start

Personal runbook for running the portfolio stack locally.
This folder is **gitignored** — notes here stay on your machine.

---

## What's in this folder

| File | Contents |
|---|---|
| `01_quick_start.md` | This file — overview and one-time setup |
| `02_docker.md` | Running with Docker Compose (recommended) |
| `03_no_docker.md` | Running without Docker (uv + local Postgres/Redis) |
| `04_environments.md` | All environment variables for every environment |

---

## One-time setup

### 1. Install Docker Desktop
Download from https://www.docker.com/products/docker-desktop/
Make sure Docker Engine is running before using Docker Compose.

### 2. Install Node / pnpm (frontend)
```bash
# Install pnpm globally if not already installed
npm install -g pnpm

# Install frontend dependencies
cd frontend
pnpm install
```

### 3. Generate the admin password hash (backend)
The admin panel requires a bcrypt hash stored in the environment.
Run this once and save the output — you will need it in step 4.

```powershell
cd backend
# If using Docker Compose (Python in container):
docker compose run --rm --no-deps backend /app/.venv/bin/python -m app.cli.hash_password

# If you have the venv locally:
.venv\Scripts\python.exe -m app.cli.hash_password
```

Copy the `$2b$12$…` string that is printed.

### 4. Set the admin credentials in docker-compose.yml
Open `backend/docker-compose.yml` and set these three values:

```yaml
ADMIN_EMAIL: you@example.com          # your login email
ADMIN_PASSWORD_HASH: "$2b$12$..."     # from step 3
ADMIN_JWT_SECRET: "<random-32-chars>" # generate below
```

Generate a JWT secret:
```powershell
python -c "import secrets; print(secrets.token_hex(32))"
```

---

## Daily workflow

```powershell
# Terminal 1 — backend + database (from /backend)
docker compose up

# Terminal 2 — frontend (from /frontend)
pnpm dev
```

| Service | URL |
|---|---|
| Frontend | http://localhost:5173 |
| Backend API | http://localhost:8000 |
| API docs (dev only) | http://localhost:8000/docs |
| Admin panel | http://localhost:5173/admin/login |

---

## Stop everything

```powershell
# Stop containers (keep data)
docker compose down

# Stop containers AND delete all database data
docker compose down -v
```
