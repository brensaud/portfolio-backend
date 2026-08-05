# Environment Variables Reference

All environment variables for every deployment environment.

---

## Backend

### How variables are applied

| Environment | Where to set |
|---|---|
| Local (Docker Compose) | `backend/docker-compose.yml` → `backend.environment` |
| Local (no Docker) | `backend/.env` (copy from `envs/.env.example`) |
| UAT / Production | Railway environment variables dashboard |

---

### Variable reference

#### Application

| Variable | Dev default | Required in prod | Description |
|---|---|---|---|
| `ENVIRONMENT` | `development` | Yes | `development` / `staging` / `production` |
| `DEBUG` | `true` | No | `true` enables SQL echo, `/docs`, `/redoc` |

#### Database

| Variable | Dev default | Required in prod | Description |
|---|---|---|---|
| `DATABASE_URL` | `postgresql+asyncpg://postgres:postgres@localhost:5432/portfolio` | Yes | asyncpg connection string. In Docker Compose use `@db:5432` (internal hostname) |

#### Redis

| Variable | Dev default | Required in prod | Description |
|---|---|---|---|
| `REDIS_URL` | `redis://localhost:6379/0` | No | Rate limiting. App starts without Redis — rate limiting is disabled |

#### CORS

| Variable | Dev default | Required in prod | Description |
|---|---|---|---|
| `ALLOWED_ORIGINS` | `["http://localhost:5173"]` | Yes | JSON array of allowed origins. Must include the deployed frontend URL |

#### Rate limiting (public contact form)

| Variable | Dev default | Required in prod | Description |
|---|---|---|---|
| `RATE_LIMIT_REQUESTS` | `5` | No | Max contact form submissions per IP per window |
| `RATE_LIMIT_WINDOW_SECONDS` | `3600` | No | Window size in seconds (default 1 hour) |

#### Admin authentication

| Variable | Dev default | Required in prod | Description |
|---|---|---|---|
| `ADMIN_EMAIL` | `admin@example.com` | Yes | Admin login email |
| `ADMIN_PASSWORD_HASH` | *(empty)* | Yes | bcrypt hash — generate with `python -m app.cli.hash_password` |
| `ADMIN_JWT_SECRET` | `dev-secret-CHANGE-IN-PRODUCTION-must-be-32-plus-chars!!` | Yes | HS256 signing secret. **Must be ≥ 32 chars. Never use the default in production.** Generate with `python -c "import secrets; print(secrets.token_hex(64))"` |
| `ADMIN_JWT_ISSUER` | `api.brensaud.com` | Yes | JWT `iss` claim. Must match across environments |
| `ADMIN_JWT_AUDIENCE` | `admin.brensaud.com` | Yes | JWT `aud` claim. Must match across environments |
| `ADMIN_JWT_ACCESS_TTL_MINUTES` | `15` | No | Access token lifetime in minutes |
| `ADMIN_REFRESH_TTL_SECONDS` | `86400` | No | Refresh token lifetime in seconds (24 h) |
| `ADMIN_LOGIN_RATE_LIMIT_ATTEMPTS` | `5` | No | Max login attempts per IP per window before 429 |
| `ADMIN_LOGIN_RATE_LIMIT_WINDOW_SECONDS` | `900` | No | Login rate limit window (15 min) |
| `ADMIN_LOGIN_LOCKOUT_THRESHOLD` | `10` | No | Cumulative failures before full lockout |
| `ADMIN_LOGIN_LOCKOUT_SECONDS` | `1800` | No | Lockout duration (30 min) |

---

### Docker Compose `.env` per environment

The `docker-compose.yml` values are hardcoded for local dev.
For staging/production, Railway injects env vars directly — no `.env` file needed on the server.

**Local dev (`docker-compose.yml`):**
```yaml
ENVIRONMENT: development
DEBUG: "true"
DATABASE_URL: postgresql+asyncpg://postgres:postgres@db:5432/portfolio
REDIS_URL: redis://redis:6379/0
ALLOWED_ORIGINS: '["http://localhost:5173"]'
ADMIN_EMAIL: you@example.com
ADMIN_PASSWORD_HASH: "$2b$12$..."
ADMIN_JWT_SECRET: "your-local-secret-min-32-chars-here!!"
ADMIN_JWT_ISSUER: api.brensaud.com
ADMIN_JWT_AUDIENCE: admin.brensaud.com
```

**Staging / UAT (Railway):**
```
ENVIRONMENT=staging
DEBUG=false
DATABASE_URL=postgresql+asyncpg://<user>:<pass>@<host>:5432/<db>
REDIS_URL=redis://<upstash-or-railway-redis>
ALLOWED_ORIGINS=["https://uat.brensaud.com"]
ADMIN_EMAIL=admin@brensaud.com
ADMIN_PASSWORD_HASH=$2b$12$...
ADMIN_JWT_SECRET=<strong-random-secret>
ADMIN_JWT_ISSUER=api.brensaud.com
ADMIN_JWT_AUDIENCE=admin.brensaud.com
```

**Production (Railway):**
```
ENVIRONMENT=production
DEBUG=false
DATABASE_URL=postgresql+asyncpg://<user>:<pass>@<host>:5432/<db>
REDIS_URL=redis://<upstash-or-railway-redis>
ALLOWED_ORIGINS=["https://brensaud.com"]
ADMIN_EMAIL=admin@brensaud.com
ADMIN_PASSWORD_HASH=$2b$12$...
ADMIN_JWT_SECRET=<different-strong-random-secret>
ADMIN_JWT_ISSUER=api.brensaud.com
ADMIN_JWT_AUDIENCE=admin.brensaud.com
```

---

## Frontend

### How variables are applied

| Environment | Where to set |
|---|---|
| Local dev | `frontend/envs/.env.dev` |
| UAT | `frontend/envs/.env.uat` |
| Production | `frontend/envs/.env.prod` OR Vercel environment variables |

Vite reads the correct file based on the `--mode` flag:

```powershell
pnpm dev                  # reads envs/.env.dev
pnpm build --mode uat     # reads envs/.env.uat
pnpm build                # reads envs/.env.prod (Vite default mode = production)
```

---

### Variable reference

| Variable | Required | Description |
|---|---|---|
| `VITE_SITE_URL` | Yes | Canonical site URL for absolute links and OG tags |
| `VITE_SITE_NAME` | No | Display name override (defaults to constant in `site.ts`) |
| `VITE_API_BASE_URL` | Yes | Backend base URL for the public contact form API |
| `VITE_ADMIN_API_BASE_URL` | No | Backend base URL for admin API. Defaults to `VITE_API_BASE_URL` if not set |

---

### Per-environment values

**Local dev (`envs/.env.dev`):**
```dotenv
VITE_SITE_URL=http://localhost:5173
VITE_API_BASE_URL=http://localhost:8000
```

**UAT (`envs/.env.uat`):**
```dotenv
VITE_SITE_URL=https://uat.brensaud.com
VITE_API_BASE_URL=https://portfolio-backend-tqoh.onrender.com
```

**Production (`envs/.env.prod`):**
```dotenv
VITE_SITE_URL=https://brensaud.com
VITE_API_BASE_URL=https://portfolio-backend-tqoh.onrender.com
```

---

## Security notes

- `ADMIN_PASSWORD_HASH` and `ADMIN_JWT_SECRET` must **never** be committed to git
- The dev default JWT secret (`dev-secret-CHANGE-IN-PRODUCTION...`) is intentionally obvious — the app validates and **refuses to start in production** if this exact string is set
- Generate a unique `ADMIN_JWT_SECRET` per environment — dev, uat, and prod should each have a different secret
- The admin password itself is never stored anywhere — only the bcrypt hash
