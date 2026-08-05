# Running Without Docker

Use this approach if you want faster hot-reload, easier debugging,
or if Docker is not available.

Requires: PostgreSQL 16, Redis 7, Python 3.12, uv, pnpm.

---

## Backend — uv + local services

### 1. Create and activate the virtual environment

```powershell
cd backend
uv sync --group dev
# venv is at .venv/
```

### 2. Create the database

```powershell
# Assumes PostgreSQL is installed and pg_ctl / createdb are in PATH
createdb portfolio
```

### 3. Create `.env` from the template

```powershell
copy envs\.env.example .env
```

Open `.env` and fill in:

```dotenv
ENVIRONMENT=development
DEBUG=true

DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/portfolio
REDIS_URL=redis://localhost:6379/0   # optional — rate limiting disabled without Redis

ALLOWED_ORIGINS=["http://localhost:5173"]

ADMIN_EMAIL=you@example.com
ADMIN_PASSWORD_HASH=                 # output of: python -m app.cli.hash_password
ADMIN_JWT_SECRET=                    # output of: python -c "import secrets; print(secrets.token_hex(32))"
ADMIN_JWT_ISSUER=api.brensaud.com
ADMIN_JWT_AUDIENCE=admin.brensaud.com
ADMIN_JWT_ACCESS_TTL_MINUTES=15
ADMIN_REFRESH_TTL_SECONDS=86400
```

### 4. Generate admin password hash

```powershell
.venv\Scripts\python.exe -m app.cli.hash_password
# Paste the $2b$12$... output into ADMIN_PASSWORD_HASH in .env
```

### 5. Run migrations

```powershell
.venv\Scripts\python.exe -m alembic upgrade head
```

### 6. Start the backend

```powershell
.venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8000
```

---

## Frontend — pnpm

No extra setup needed — `envs/.env.dev` already has the right values.

```powershell
cd frontend
pnpm dev
```

---

## Backend commands reference

```powershell
# Run tests
.venv\Scripts\python.exe -m pytest tests/ -v

# Run tests with coverage
.venv\Scripts\python.exe -m pytest tests/ --cov=app --cov-report=term-missing

# Lint
.venv\Scripts\python.exe -m ruff check app/ tests/

# Format
.venv\Scripts\python.exe -m ruff format app/ tests/

# Type check
.venv\Scripts\python.exe -m mypy app/

# Create a new migration
.venv\Scripts\python.exe -m alembic revision --autogenerate -m "describe the change"

# Apply migrations
.venv\Scripts\python.exe -m alembic upgrade head

# Roll back one migration
.venv\Scripts\python.exe -m alembic downgrade -1

# Show current migration
.venv\Scripts\python.exe -m alembic current

# Show migration history
.venv\Scripts\python.exe -m alembic history --verbose
```

## Frontend commands reference

```powershell
pnpm dev                # dev server with HMR
pnpm build              # type-check + production build
pnpm type-check         # TypeScript check only
pnpm lint               # ESLint
pnpm test:run           # Vitest single run
pnpm test               # Vitest watch mode
pnpm test:coverage      # Vitest with coverage
```
