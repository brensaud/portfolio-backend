# AWS Cost-Saving Deployment Plan

Maximum cost reduction while keeping the portfolio always available.
No cold starts. No sleep. No code changes required.

---

## Cost targets

| Phase | Monthly cost | When |
|---|---|---|
| Free tier (year 1) | **$0** | Months 1–12 after AWS account creation |
| After free tier | **~$2–4/mo** | Month 13 onwards |
| With 1-year reserved instance | **~$3/mo flat** | If you commit upfront |

---

## Why AWS can be this cheap

Three decisions drive most of the savings:

1. **Graviton (ARM) instances** — AWS t4g instances are 20% cheaper than
   equivalent Intel/AMD t3 instances and included in the free tier

2. **No managed database** — RDS PostgreSQL costs $15+/mo after free tier.
   Neon (serverless PostgreSQL) has a permanent free tier with no expiry.
   Upstash Redis also has a permanent free tier. Keep both outside AWS.

3. **S3 + CloudFront for frontend** — static file hosting costs ~$0.50/mo
   at portfolio traffic levels. No EC2 needed for the frontend at all.

---

## Architecture (cost-optimised)

```
Users
  │
  ├── yourdomain.com
  │     └── CloudFront → S3 (React static files)  ~$0.50/mo
  │
  └── api.yourdomain.com
        └── EC2 t4g.micro (ARM) → FastAPI (Docker)  ~$3/mo
              │
              ├── Neon PostgreSQL (free, external)    $0
              └── Upstash Redis   (free, external)    $0

Total after free tier: ~$3.50/mo
```

---

## Phase 1 — Year 1: Fully Free

Use the AWS free tier for 12 months. Everything below qualifies.

### Free tier allocations used

| Service | Free tier allowance | Used for |
|---|---|---|
| EC2 t3.micro | 750 hours/month (12 mo) | Backend container |
| EBS storage | 30 GB (12 mo) | EC2 root volume |
| S3 | 5 GB storage + 20k GET + 2k PUT | Frontend static files |
| CloudFront | 1 TB data transfer + 10M requests (12 mo) | Frontend CDN |
| Route 53 | N/A — use external DNS registrar | DNS (save $0.50/mo) |
| Data transfer out | 100 GB/month free (always free) | API responses |

### Services kept outside AWS (free tier, no expiry)

| Service | Provider | Cost | Purpose |
|---|---|---|---|
| PostgreSQL | [Neon](https://neon.tech) | Free forever | Database |
| Redis | [Upstash](https://upstash.com) | Free forever | Sessions + rate limiting |

---

### Phase 1 setup — step by step

#### 1. Launch EC2 t3.micro (free tier)

```
AWS Console → EC2 → Launch Instance
  Name: portfolio-server
  AMI: Ubuntu 24.04 LTS
  Instance type: t3.micro  ← free tier eligible
  Key pair: create new → download portfolio-key.pem
  Storage: 20 GB gp3
```

Security Group rules:

| Port | Source | Purpose |
|---|---|---|
| 22 | Your IP only | SSH |
| 80 | 0.0.0.0/0 | HTTP (redirect to HTTPS) |
| 443 | 0.0.0.0/0 | HTTPS |

Allocate a free Elastic IP and associate it with the instance so the IP
stays the same on reboots.

#### 2. Connect and install Docker

```bash
ssh -i portfolio-key.pem ubuntu@<ELASTIC-IP>

# Install Docker
curl -fsSL https://get.docker.com | sudo sh
sudo usermod -aG docker ubuntu
newgrp docker

# Verify
docker --version
docker compose version
```

#### 3. Create production docker-compose override

Instead of modifying the original `docker-compose.yml`, create an override file
that replaces Docker PostgreSQL and Redis with Neon and Upstash:

```bash
git clone https://github.com/brensaud/portfolio-backend
cd portfolio-backend
nano docker-compose.prod.yml
```

Paste:

```yaml
# docker-compose.prod.yml
# Production override — replaces local DB and Redis with managed external services.
# Usage: docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d

services:
  backend:
    environment:
      DATABASE_URL: postgresql+asyncpg://<neon-user>:<pass>@<neon-host>/portfolio?sslmode=require
      REDIS_URL: redis://:<upstash-password>@<upstash-host>:6379
      ALLOWED_ORIGINS: '["https://yourdomain.com"]'
      ENVIRONMENT: production
      DEBUG: "false"
      ADMIN_EMAIL: you@example.com
      ADMIN_PASSWORD_HASH: "$2b$12$..."
      ADMIN_JWT_SECRET: "<64-char-random-hex>"
      ADMIN_JWT_ISSUER: api.yourdomain.com
      ADMIN_JWT_AUDIENCE: admin.yourdomain.com
    # Remove the volume mount (no hot-reload in production)
    volumes: []
    # Use production CMD from Dockerfile (not the dev --reload override)
    command: []
    restart: always

  # Disable local DB and Redis — using Neon and Upstash instead
  db:
    profiles: [dev-only]

  redis:
    profiles: [dev-only]
```

Start production:

```bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build
```

Verify:

```bash
curl http://localhost:8000/health
```

#### 4. Install Nginx + SSL

```bash
sudo apt update
sudo apt install nginx certbot python3-certbot-nginx -y

sudo nano /etc/nginx/sites-available/portfolio
```

Paste (replace `yourdomain.com` and `api.yourdomain.com`):

```nginx
server {
    listen 80;
    server_name api.yourdomain.com;

    location / {
        proxy_pass         http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header   Host $host;
        proxy_set_header   X-Real-IP $remote_addr;
        proxy_set_header   X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header   X-Forwarded-Proto $scheme;
        proxy_read_timeout 60s;
    }
}
```

```bash
sudo ln -s /etc/nginx/sites-available/portfolio /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx

# Free SSL certificate
sudo certbot --nginx -d api.yourdomain.com
```

Certbot auto-renews every 90 days. Cron job is set up automatically.

#### 5. Deploy frontend to S3 + CloudFront

```bash
# On your local machine
cd frontend
pnpm build
```

In AWS Console:

```
S3 → Create bucket
  Name: portfolio-frontend-yourdomain
  Region: us-east-1
  Block public access: ON (CloudFront will serve it, not S3 directly)

Upload dist/ contents to the bucket

CloudFront → Create distribution
  Origin: S3 bucket (use OAC — Origin Access Control)
  Default root object: index.html
  Custom error response: 404 → /index.html, HTTP 200 (SPA routing)
  Price class: Use only North America and Europe (cheapest)
  Alternate domain: yourdomain.com
  SSL: Request ACM certificate in us-east-1 → yourdomain.com
```

Update `envs/.env.prod`:

```dotenv
VITE_SITE_URL=https://yourdomain.com
VITE_API_BASE_URL=https://api.yourdomain.com
```

Rebuild and re-upload after the change.

#### 6. DNS

Point your domain to CloudFront and EC2. Use your registrar's DNS
(free — no need to pay for Route 53 at $0.50/hosted zone/month):

| Record | Type | Value |
|---|---|---|
| `yourdomain.com` | CNAME | CloudFront distribution domain |
| `www.yourdomain.com` | CNAME | CloudFront distribution domain |
| `api.yourdomain.com` | A | EC2 Elastic IP |

---

## Phase 2 — After Free Tier: Switch to t4g.micro + Reserved (~$3/mo)

When the 12-month free tier expires, switch to Graviton (ARM) to cut costs.

### Why t4g is cheaper than t3

| Instance | vCPU | RAM | On-demand/mo | 1-yr reserved/mo |
|---|---|---|---|---|
| t3.micro (x86) | 2 | 1 GB | $8.47 | $5.11 |
| t4g.nano (ARM) | 2 | 512 MB | $3.07 | $1.84 |
| t4g.micro (ARM) | 2 | 1 GB | $6.13 | $3.07 |

**t4g.micro with 1-year reserved = $3.07/month** — the right balance of
RAM and cost for FastAPI + Docker.

### Migration from t3.micro to t4g.micro

The Docker image must be rebuilt for ARM64. No code changes required.

```bash
# On your local machine (Windows with Docker Desktop)
# Build for ARM64 (Graviton)
docker buildx build --platform linux/arm64 \
  -t <ACCOUNT>.dkr.ecr.us-east-1.amazonaws.com/portfolio-backend:latest \
  --push .

# Or build on the t4g instance itself (native ARM, faster)
```

Steps:

```
1. Create a new EC2 t4g.micro instance (same security group, same key pair)
2. Allocate and associate the same Elastic IP to the new instance
   (or re-associate the existing one — takes ~30 seconds, zero DNS change)
3. SSH into the new instance
4. Install Docker (same commands as Phase 1)
5. Clone repo, copy docker-compose.prod.yml, run docker compose up
6. Install Nginx + Certbot (same commands)
7. Test: curl https://api.yourdomain.com/health
8. Purchase 1-year Reserved Instance for t4g.micro in the AWS console
9. Terminate the old t3.micro instance
```

### Cost after switching

| Resource | Monthly cost |
|---|---|
| EC2 t4g.micro (1-yr reserved) | $3.07 |
| EBS 20 GB gp3 | $1.60 |
| S3 frontend (~500 MB) | ~$0.01 |
| CloudFront (~10 GB transfer) | ~$0.85 |
| Neon PostgreSQL | $0 |
| Upstash Redis | $0 |
| **Total** | **~$5.53/mo** |

With Savings Plans instead of Reserved Instances, you can get a similar
discount with more flexibility.

---

## Auto-deploy on git push

Set up GitHub Actions to deploy automatically when you merge to `main`.
Add these secrets to your GitHub repo (Settings → Secrets):

| Secret | Value |
|---|---|
| `EC2_HOST` | EC2 Elastic IP |
| `EC2_SSH_KEY` | Contents of `portfolio-key.pem` |

Create `.github/workflows/deploy.yml` in the backend repo:

```yaml
name: Deploy

on:
  push:
    branches: [main]

jobs:
  deploy:
    name: Deploy to EC2
    runs-on: ubuntu-latest
    needs: [lint, typecheck, test]   # only deploy if CI passes

    steps:
      - name: Deploy via SSH
        uses: appleboy/ssh-action@v1
        with:
          host: ${{ secrets.EC2_HOST }}
          username: ubuntu
          key: ${{ secrets.EC2_SSH_KEY }}
          script: |
            cd /home/ubuntu/portfolio-backend
            git pull origin main
            docker compose -f docker-compose.yml \
                           -f docker-compose.prod.yml \
                           up -d --build
            docker image prune -f
```

---

## Cost monitoring

Set a billing alert so AWS emails you if the monthly cost exceeds $5:

```
AWS Console → Billing → Budgets → Create budget
  Type: Cost budget
  Amount: $5
  Alert threshold: 80% ($4) and 100% ($5)
  Email: your@email.com
```

Also enable the free Cost Explorer to see a breakdown by service.

---

## Full cost summary

### Year 1 (free tier active)

| Service | Cost |
|---|---|
| EC2 t3.micro | $0 (free tier) |
| EBS 20 GB | $0 (free tier) |
| S3 + CloudFront | $0 (free tier) |
| Neon PostgreSQL | $0 (permanent free) |
| Upstash Redis | $0 (permanent free) |
| **Year 1 total** | **$0** |

### Year 2 onwards (t4g.micro reserved)

| Service | Monthly |
|---|---|
| EC2 t4g.micro (1-yr reserved) | $3.07 |
| EBS 20 GB gp3 | $1.60 |
| S3 (< 1 GB) | $0.02 |
| CloudFront (< 10 GB) | $0.85 |
| Neon PostgreSQL | $0 |
| Upstash Redis | $0 |
| **Monthly total** | **~$5.54** |
| **Annual total** | **~$66** |

Compare to current stack after potential Render upgrade ($7/mo) = **$84/yr**.
AWS saves ~$18/year and eliminates cold starts.

---

## Checklist: cost-saving decisions

```
□ Use t3.micro for year 1 (free tier) — do NOT launch t3.small or t3.medium
□ Use Neon free tier instead of RDS PostgreSQL (saves $15/mo after free tier)
□ Use Upstash free tier instead of ElastiCache (saves $12/mo)
□ Use S3 + CloudFront for frontend instead of serving from EC2 (saves RAM)
□ Use external DNS (Cloudflare free / registrar DNS) instead of Route 53 (saves $0.50/mo)
□ Set a $5 billing alert in AWS Budgets
□ After year 1: switch to t4g.micro ARM + 1-year reserved instance
□ Enable Docker image pruning after deploys (saves EBS space)
□ Set CloudFront price class to "North America + Europe only" (cheapest)
```
