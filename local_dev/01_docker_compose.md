# 01 — Run the project with Docker Compose

All commands are run from the `backend/` directory.

---

## First-time setup

```bash
# Build the backend image
docker compose build

# Start all services (PostgreSQL, Redis, FastAPI)
# Runs migrations automatically on startup
docker compose up
```

The API will be available at **http://localhost:8000**.

---

## Daily workflow

```bash
# Start in the foreground (shows logs)
docker compose up

# Start in the background
docker compose up -d

# Tail logs for a specific service
docker compose logs -f backend
docker compose logs -f db
docker compose logs -f redis

# Stop all services (keeps volumes)
docker compose down

# Stop and wipe all volumes (fresh DB + Redis state)
docker compose down -v
```

---

## Rebuild after dependency changes

```bash
# Rebuild the backend image then restart
docker compose build && docker compose up
```

---

## Services

| Service | Port | Notes                           |
| ------- | ---- | ------------------------------- |
| backend | 8000 | FastAPI, hot-reload enabled     |
| db      | 5432 | PostgreSQL 16, user`postgres` |
| redis   | 6379 | Redis 7, AOF persistence        |
