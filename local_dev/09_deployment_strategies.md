# Deployment Strategies

A comparison of every viable deployment approach for this stack
(React/Vite frontend + FastAPI backend + PostgreSQL + Redis).

Rated on: cost, complexity, cold starts, scalability, and fit for a portfolio project.

---

## Current stack (what is live today)

```
Frontend  → Vercel          (static hosting + CDN)
Backend   → Render          (Docker container)
Database  → Neon            (serverless PostgreSQL)
Cache     → Upstash Redis   (serverless Redis)
CI        → GitHub Actions
```

**Monthly cost at free tier: $0**
Render free tier sleeps after 15 min. Neon suspends compute after 5 min.
First request after sleep: ~30 s cold start. Acceptable for a portfolio.

---

## Strategy 1 — Current: Vercel + Render + Neon + Upstash (FREE)

### Architecture

```
Vercel (CDN)  ──→  Render (Docker)  ──→  Neon (PG)
                                    ──→  Upstash (Redis)
```

### Pros

- Entire stack runs on free tiers
- Zero infrastructure management
- Auto-deploy on `main` merge via GitHub
- Neon provides database branching (useful for UAT)
- Vercel gives global CDN, preview deployments per PR, custom domains
- Render runs real Docker containers — identical to local

### Cons

- Render free tier sleeps after 15 min inactivity → cold start (~30 s)
- Neon compute suspends on free tier → first-query latency spike
- Render free tier: 750 CPU-hours/month, 512 MB RAM
- No zero-downtime deploys on free tier (brief restart)

### When to upgrade

Pay for Render ($7/mo starter) to eliminate cold starts once the portfolio is actively shared.

---

## Strategy 2 — Vercel + Railway + Neon + Upstash

### Architecture

```
Vercel (CDN)  ──→  Railway (Docker)  ──→  Neon (PG)
                                     ──→  Upstash (Redis)
```

Replace Render with **Railway**. Railway is better for always-on services
because it does not sleep on inactivity (even on the $5 hobby plan).

### Pros

- No cold starts ($5/month hobby plan)
- Railway supports Docker — no code changes required
- Railway has a built-in PostgreSQL and Redis service
  (can replace both Neon and Upstash in one dashboard)
- Better developer experience than Render for Python

### Cons

- Not free ($5/mo minimum)
- Railway PostgreSQL backups require paid plan

### Migration from current stack

1. Create a Railway project
2. Add a service → "Deploy from GitHub repo" → select `portfolio-backend`
3. Railway detects the `Dockerfile` automatically
4. Copy all env vars from Render to Railway
5. Update `ALLOWED_ORIGINS` on the backend
6. Update `VITE_API_BASE_URL` in Vercel env vars to Railway URL
7. Remove the Render service

---

## Strategy 3 — Vercel + Fly.io + Neon + Upstash

### Architecture

```
Vercel (CDN)  ──→  Fly.io (Docker VM)  ──→  Neon (PG)
                                        ──→  Upstash (Redis)
```

**Fly.io** runs Docker containers as micro-VMs with persistent memory.
No cold starts, global edge deployment.

### Pros

- Free tier: 3 shared VMs, 256 MB RAM each
- No cold starts — containers stay warm
- Global regions — deploy close to users
- Built-in Fly Postgres and Redis (Upstash alternative)
- Zero-downtime deploys via rolling deployment

### Cons

- `flyctl` CLI required (extra tooling)
- More config than Render (`fly.toml` needed)
- Free tier RAM is tight for FastAPI + SQLAlchemy (256 MB)

### Deploy command

```bash
# Install flyctl
brew install flyctl  # or winget install Fly.io.flyctl

# Login and launch
flyctl auth login
flyctl launch --dockerfile Dockerfile --no-deploy

# Set env vars
flyctl secrets set ADMIN_EMAIL=... ADMIN_PASSWORD_HASH=... ...

# Deploy
flyctl deploy
```

---

## Strategy 4 — Vercel + Vercel Functions (Serverless API)

### Architecture

```
Vercel (CDN + Serverless Functions)  ──→  Neon (PG)
```

Rewrite the FastAPI backend as Vercel Serverless Functions (Node.js or Python).
Both frontend and backend live in one Vercel project.

### Pros

- Single platform, single dashboard
- Truly serverless — pay per request
- Global edge functions
- No separate backend service to manage

### Cons

- **Major rewrite required** — FastAPI does not run natively as Vercel Functions
- Vercel Python runtime is limited (no async support, 15 s max execution)
- HTTPOnly cookie auth is harder to implement correctly across Vercel domains
- SQLAlchemy connection pooling is problematic in serverless environments
- Redis sessions and refresh tokens need rethinking

**Not recommended** for this project — the FastAPI architecture (async SQLAlchemy, Pydantic, cookie auth) does not translate cleanly to Vercel Functions.

---

## Strategy 5 — Full Docker Compose on a VPS (DigitalOcean / Hetzner)

### Architecture

```
VPS (single server)
├── Nginx (reverse proxy + SSL)
├── Frontend (Nginx static files)
├── Backend (Docker container)
├── PostgreSQL (Docker container)
└── Redis (Docker container)
```

### Pros

- Full control — no vendor lock-in
- Persistent database on the same machine (no network latency)
- No cold starts
- Single `docker compose up` to run everything
- Cheap at scale (Hetzner CX21: €3.29/mo, 2 vCPU, 4 GB RAM)

### Cons

- You manage SSL certificates (Let's Encrypt / Certbot)
- You manage server updates and security patches
- Manual deploy pipeline (no auto-deploy without extra setup)
- Single point of failure (no HA)
- Database backups are your responsibility

### Deploy flow

```bash
# On the VPS
git clone https://github.com/brensaud/portfolio-backend
cd portfolio-backend

# Edit docker-compose.yml or use a .env file for prod secrets
docker compose up -d --build

# Auto-deploy via GitHub Actions webhook or cron pull
```

**Good for:** cost-conscious production workloads, full control, no sleep issues.

---

## Strategy 6 — AWS / GCP / Azure (Cloud Native)

### Architecture options

```
Option A (serverless):
  CloudFront → S3 (frontend)
  API Gateway → Lambda (backend)
  RDS PostgreSQL
  ElastiCache Redis

Option B (container):
  CloudFront → S3 (frontend)
  ECS Fargate → Docker (backend)
  RDS PostgreSQL
  ElastiCache Redis
```

### Pros

- Maximum scalability
- Managed services for everything
- Enterprise-grade SLAs

### Cons

- **Significant cost** — even minimal AWS setups cost $50–100/mo
- High complexity — IAM, VPCs, security groups, load balancers
- Over-engineered for a portfolio project

**Not recommended** unless the portfolio becomes a real production application
with traffic, compliance, or enterprise requirements.

---

## Strategy 7 — Cloudflare Pages + Workers + D1 (Edge-native)

### Architecture

```
Cloudflare Pages (frontend CDN)
Cloudflare Workers (backend — edge runtime)
Cloudflare D1 (SQLite at the edge)
```

### Pros

- Entirely free tier (100k Worker requests/day, 5 GB D1 storage)
- Global edge — near-zero latency everywhere
- No cold starts (Workers stay warm)

### Cons

- **Complete rewrite required** — FastAPI cannot run in Cloudflare Workers
  (no Python, must use JavaScript/TypeScript)
- D1 is SQLite — different from PostgreSQL (no asyncpg, no Alembic)
- HTTPOnly cookies and CORS work differently at the edge
- Admin auth with Redis refresh tokens not available in D1/KV

**Not compatible** with the current codebase.

---

## Decision matrix

| Strategy | Cost/mo | Cold starts | Complexity | Code changes | Recommended |
|---|---|---|---|---|---|
| **1. Current (Vercel + Render + Neon)** | $0 | Yes (Render free) | Low | None | ✅ Now |
| **2. Vercel + Railway + Neon** | $5 | No | Low | None | ✅ Next step |
| **3. Vercel + Fly.io + Neon** | $0–5 | No | Medium | Minor | ✅ Alternative |
| **4. Vercel Functions** | $0 | Yes | Very high | Full rewrite | ❌ |
| **5. VPS (Docker Compose)** | $3–5 | No | Medium | None | ✅ Cost-efficient |
| **6. AWS / GCP / Azure** | $50+ | No | Very high | Moderate | ❌ Overkill |
| **7. Cloudflare Workers** | $0 | No | Very high | Full rewrite | ❌ |

---

## Recommended upgrade path

### Now (portfolio in progress)
**Strategy 1 — stay on current stack.**
$0/month, zero maintenance, acceptable cold starts.

### When actively job searching / sharing the portfolio
**Strategy 2 — add Railway ($5/mo).**
No cold starts, same Docker container, zero code changes.
Just copy env vars and update the API URL in Vercel.

### When the portfolio has real traffic or a CMS
**Strategy 5 — VPS on Hetzner (€3–5/mo).**
Full control, persistent DB on-machine, no vendor dependencies.

---

## Migration checklist: Render → Railway

Whenever you decide to switch (no urgency):

```
□ Create Railway account at railway.app
□ New project → Deploy from GitHub → brensaud/portfolio-backend
□ Railway auto-detects Dockerfile
□ Add environment variables (copy from Render dashboard):
    ENVIRONMENT, DEBUG, DATABASE_URL, REDIS_URL, ALLOWED_ORIGINS,
    ADMIN_EMAIL, ADMIN_PASSWORD_HASH, ADMIN_JWT_SECRET,
    ADMIN_JWT_ISSUER, ADMIN_JWT_AUDIENCE,
    ADMIN_JWT_ACCESS_TTL_MINUTES, ADMIN_REFRESH_TTL_SECONDS
□ Set custom domain: api.brensaud.com → Railway domain
□ Update VITE_API_BASE_URL in Vercel env vars to new Railway URL
□ Test: curl https://api.brensaud.com/health
□ Test: admin login at brensaud.com/admin/login
□ Delete Render service
```
