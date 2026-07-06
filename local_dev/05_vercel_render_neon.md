# Deployed Infrastructure

Reference for the live deployment stack: Vercel + Render + Neon + Upstash.

---

## Architecture overview

```
Users
  │
  ▼
Vercel (Frontend)                  GitHub Actions (CI)
  brensaud.com                       ├── lint / format
  portfolio-frontend-drab-ten        ├── type-check
    .vercel.app                       ├── tests
  │                                   └── build
  │ HTTPS API calls
  ▼
Render (Backend)
  portfolio-backend-tqoh.onrender.com
  api.brensaud.com (custom domain)
  │         │
  ▼         ▼
Neon      Upstash Redis
(PostgreSQL) (Rate limiting)
```

---

## Services

### Frontend — Vercel

| Item | Value |
|---|---|
| Provider | [Vercel](https://vercel.com) |
| Production URL | https://portfolio-frontend-drab-ten.vercel.app |
| Custom domain | https://brensaud.com |
| UAT / preview URL | https://uat.brensaud.com |
| GitHub repo | https://github.com/brensaud/portfolio-frontend |
| Deploys from | `main` branch (auto-deploy on merge) |
| Framework preset | Vite |
| Build command | `pnpm build` |
| Output directory | `dist` |
| Node version | 22 |
| SPA routing | `vercel.json` rewrites all paths to `index.html` |

**Environment variables set in Vercel dashboard:**

| Variable | Production value | UAT value |
|---|---|---|
| `VITE_SITE_URL` | `https://brensaud.com` | `https://uat.brensaud.com` |
| `VITE_API_BASE_URL` | `https://portfolio-backend-tqoh.onrender.com` | `https://portfolio-backend-tqoh.onrender.com` |

**To update frontend env vars:**
Vercel → project → Settings → Environment Variables → add/edit → redeploy

---

### Backend — Render

| Item | Value |
|---|---|
| Provider | [Render](https://render.com) |
| Production URL | https://portfolio-backend-tqoh.onrender.com |
| Custom domain | https://api.brensaud.com |
| GitHub repo | https://github.com/brensaud/portfolio-backend |
| Deploys from | `main` branch (auto-deploy on merge) |
| Runtime | Docker (built from `Dockerfile`) |
| Port | 8000 |
| Startup command | `alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000` |
| Health check path | `/health` |

**Environment variables set in Render dashboard:**

| Variable | Production value |
|---|---|
| `ENVIRONMENT` | `production` |
| `DEBUG` | `false` |
| `DATABASE_URL` | *(Neon connection string — see Neon section below)* |
| `REDIS_URL` | *(Upstash Redis URL — see Upstash section below)* |
| `ALLOWED_ORIGINS` | `["https://brensaud.com"]` |
| `ADMIN_EMAIL` | your admin email |
| `ADMIN_PASSWORD_HASH` | `$2b$12$...` (bcrypt hash) |
| `ADMIN_JWT_SECRET` | strong random secret ≥ 32 chars |
| `ADMIN_JWT_ISSUER` | `api.brensaud.com` |
| `ADMIN_JWT_AUDIENCE` | `admin.brensaud.com` |
| `ADMIN_JWT_ACCESS_TTL_MINUTES` | `15` |
| `ADMIN_REFRESH_TTL_SECONDS` | `86400` |

**To update backend env vars:**
Render → service → Environment → add/edit → save (triggers redeploy)

**To rotate the admin password in production:**
```bash
# 1. Generate new hash locally
python -m app.cli.hash_password

# 2. Update ADMIN_PASSWORD_HASH in Render env vars
# 3. Wait for Render to redeploy (or trigger manual deploy)
# 4. Sign in with the new password — old sessions expire within 15 minutes
```

---

### Database — Neon (PostgreSQL)

| Item | Value |
|---|---|
| Provider | [Neon](https://neon.tech) |
| Engine | PostgreSQL 16 |
| Region | *(check Neon dashboard)* |
| Branches | `main` (production) |

**Connection string format (stored in Render as `DATABASE_URL`):**
```
postgresql+asyncpg://<user>:<password>@<host>.neon.tech/<dbname>?sslmode=require
```

**Migrations are applied automatically** on every Render deploy via the Docker CMD:
```
alembic upgrade head && uvicorn app.main:app ...
```

**To run migrations manually against production:**
```bash
# Set DATABASE_URL to the Neon production connection string
DATABASE_URL="postgresql+asyncpg://..." uv run alembic upgrade head

# Check current migration revision
DATABASE_URL="postgresql+asyncpg://..." uv run alembic current

# Show migration history
DATABASE_URL="postgresql+asyncpg://..." uv run alembic history
```

**Current migrations in order:**

| Revision | Description |
|---|---|
| `0001` | Create `contact_messages` table |
| `0002` | Create `admin_audit_logs` table |
| `0003` | Rename status enum (`new→unread`, `replied→read`), add composite index |

---

### Redis — Upstash

| Item | Value |
|---|---|
| Provider | [Upstash](https://console.upstash.com) |
| Purpose | Contact form rate limiting (5 req / IP / hour) |
| Graceful degradation | App starts without Redis — rate limiting is skipped if Upstash is unreachable |

**Connection string format (stored in Render as `REDIS_URL`):**
```
redis://:<password>@<host>.upstash.io:6379
```

---

## CI / CD pipelines

### GitHub Actions — Backend

Runs on every push and PR to `main`:

| Job | What it checks |
|---|---|
| `lint` | `ruff check` + `ruff format --check` |
| `typecheck` | `mypy app/` |
| `test` | `pytest tests/` with SQLite in-memory (no external services needed) |

Workflow file: `.github/workflows/ci.yml`

All three jobs must pass before a PR can be merged (enforce via branch protection on `main`).

### GitHub Actions — Frontend

Runs on every push and PR to `main`:

| Job | What it checks |
|---|---|
| `quality` | ESLint + Prettier + `tsc --noEmit` |
| `test` | `vitest run` |
| `build` | `pnpm build` (type-check + Vite production build) |

Workflow file: `.github/workflows/ci.yml`

---

## Deploy process

### Normal deploy (code change)

```
1. Push to dev branch
2. Open PR: dev → main
3. GitHub Actions CI runs automatically
4. Review + approve PR
5. Merge to main
6. Vercel detects main push → builds + deploys frontend automatically
7. Render detects main push → builds Docker image + deploys backend automatically
8. Backend startup runs: alembic upgrade head (applies any new migrations)
```

### Force redeploy without a code change

- **Vercel:** Vercel dashboard → Deployments → top deployment → ⋯ → Redeploy
- **Render:** Render dashboard → service → Manual Deploy → Deploy latest commit

### Rollback

- **Vercel:** Deployments → find previous deployment → Promote to Production
- **Render:** Render dashboard → Events → find previous deploy → Rollback

---

## Monitoring

| Service | Dashboard URL |
|---|---|
| Vercel | https://vercel.com/dashboard |
| Render | https://dashboard.render.com |
| Neon | https://console.neon.tech |
| Upstash | https://console.upstash.com |
| Backend health | https://portfolio-backend-tqoh.onrender.com/health |
| GitHub Actions backend | https://github.com/brensaud/portfolio-backend/actions |
| GitHub Actions frontend | https://github.com/brensaud/portfolio-frontend/actions |

---

## Custom domains (DNS)

| Domain | Points to | Managed via |
|---|---|---|
| `brensaud.com` | Vercel | DNS registrar → CNAME/A to Vercel |
| `api.brensaud.com` | Render | DNS registrar → CNAME to Render |
| `uat.brensaud.com` | Vercel preview | DNS registrar → CNAME to Vercel |

---

## Notes / gotchas

- **Render free tier sleeps** after 15 min of inactivity. First request after sleep takes ~30 s (cold start). Upgrade to paid plan to disable sleep.
- **Neon auto-suspends** the compute after 5 min of inactivity on the free tier. First query after suspend adds ~500 ms. Normal after the first request.
- **ADMIN_JWT_SECRET must differ** between dev, UAT, and production. A token signed with the dev secret will be rejected in production and vice versa.
- **Migrations run on every deploy.** Alembic is idempotent — re-running already-applied migrations is safe.
- **Database backups:** Neon free tier provides 7-day point-in-time restore. Upgrade for longer retention.
