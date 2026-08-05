# Deploying on AWS

Three practical AWS strategies for this stack, from simplest to most scalable.
All require an AWS account (https://aws.amazon.com/free — 12-month free tier available).

---

## Stack recap

```
Frontend  — React/Vite   (static files, SPA)
Backend   — FastAPI       (Docker container, port 8000)
Database  — PostgreSQL    (async via asyncpg)
Cache     — Redis         (rate limiting + auth sessions)
```

---

## Strategy A — EC2 + Docker Compose (simplest, ~$5–15/mo)

Deploy the exact same `docker-compose.yml` you use locally onto a single EC2 instance.
No new tools, no AWS-specific config, no code changes.

### Cost estimate

| Resource | Type | Monthly cost |
|---|---|---|
| EC2 instance | t3.micro (2 vCPU, 1 GB RAM) | ~$8 |
| Storage | 20 GB gp3 EBS | ~$1.60 |
| Data transfer | First 100 GB free | $0 |
| **Total** | | **~$10/mo** |

t3.micro is free for 12 months on the AWS free tier.

---

### Step 1 — Launch an EC2 instance

1. AWS Console → EC2 → Launch Instance
2. Name: `portfolio-server`
3. AMI: **Ubuntu 24.04 LTS** (free tier eligible)
4. Instance type: `t3.micro` (free tier) or `t3.small` for more headroom
5. Key pair: create a new one → download `portfolio-key.pem`
6. Security Group — add these inbound rules:

| Type | Port | Source | Purpose |
|---|---|---|---|
| SSH | 22 | Your IP only | Server access |
| HTTP | 80 | 0.0.0.0/0 | Nginx redirect to HTTPS |
| HTTPS | 443 | 0.0.0.0/0 | Frontend + API traffic |

7. Storage: 20 GB gp3
8. Launch

---

### Step 2 — SSH into the server

```powershell
# On Windows, fix key permissions
icacls "portfolio-key.pem" /inheritance:r
icacls "portfolio-key.pem" /grant:r "%username%:R"

# Connect
ssh -i portfolio-key.pem ubuntu@<EC2-PUBLIC-IP>
```

---

### Step 3 — Install Docker on the server

```bash
# Update packages
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com | sudo sh
sudo usermod -aG docker ubuntu

# Log out and back in for the group change to take effect
exit
ssh -i portfolio-key.pem ubuntu@<EC2-PUBLIC-IP>

# Verify
docker --version
docker compose version
```

---

### Step 4 — Deploy the backend

```bash
# Clone the repo
git clone https://github.com/brensaud/portfolio-backend
cd portfolio-backend

# Edit docker-compose.yml to set production values:
#   ENVIRONMENT: production
#   DEBUG: "false"
#   ALLOWED_ORIGINS: '["https://yourdomain.com"]'
#   ADMIN_EMAIL, ADMIN_PASSWORD_HASH, ADMIN_JWT_SECRET
nano docker-compose.yml

# Start all services
docker compose up -d --build

# Verify
curl http://localhost:8000/health
```

---

### Step 5 — Install Nginx + SSL

Nginx sits in front of Docker, handles HTTPS, and serves the frontend static files.

```bash
sudo apt install nginx certbot python3-certbot-nginx -y
```

Create Nginx config:

```bash
sudo nano /etc/nginx/sites-available/portfolio
```

Paste this (replace `yourdomain.com` and `api.yourdomain.com`):

```nginx
# Frontend — serve the built React app
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    root /var/www/frontend;
    index index.html;

    # SPA routing — all paths go to index.html
    location / {
        try_files $uri $uri/ /index.html;
    }
}

# Backend API
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
    }
}
```

Enable the config and get SSL certificates:

```bash
sudo ln -s /etc/nginx/sites-available/portfolio /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx

# Get Let's Encrypt certificates (replace with your domains)
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com -d api.yourdomain.com
# Certbot adds HTTPS blocks automatically and sets up auto-renewal
```

---

### Step 6 — Deploy the frontend

Build locally, then upload to the server:

```powershell
# On your local machine (in frontend/)
pnpm build   # produces dist/

# Upload to server
scp -i portfolio-key.pem -r dist/* ubuntu@<EC2-IP>:/var/www/frontend/
```

Or set up an automatic deploy script triggered by GitHub Actions.

---

### Step 7 — Point DNS to EC2

In your DNS registrar (Namecheap, Cloudflare, Route 53, etc.):

| Record | Name | Value |
|---|---|---|
| A | `yourdomain.com` | EC2 Public IP |
| A | `www.yourdomain.com` | EC2 Public IP |
| A | `api.yourdomain.com` | EC2 Public IP |

**Use an Elastic IP** so the EC2 IP does not change on restart:
AWS Console → EC2 → Elastic IPs → Allocate → Associate with your instance.

---

### Auto-deploy on git push (optional)

Add a GitHub Actions job to SSH into EC2 and run `git pull + docker compose up`:

```yaml
# .github/workflows/deploy.yml
- name: Deploy to EC2
  uses: appleboy/ssh-action@v1
  with:
    host: ${{ secrets.EC2_HOST }}
    username: ubuntu
    key: ${{ secrets.EC2_SSH_KEY }}
    script: |
      cd /home/ubuntu/portfolio-backend
      git pull origin main
      docker compose up -d --build
```

Store `EC2_HOST` and `EC2_SSH_KEY` in GitHub → repo → Settings → Secrets.

---

## Strategy B — ECS Fargate + RDS + ElastiCache (~$30–60/mo)

Managed containers with managed database and cache. No server to maintain.
Production-grade setup with auto-scaling.

### Cost estimate

| Resource | Spec | Monthly cost |
|---|---|---|
| ECS Fargate (backend) | 0.25 vCPU, 512 MB | ~$9 |
| RDS PostgreSQL | db.t3.micro, 20 GB | ~$15 |
| ElastiCache Redis | cache.t3.micro | ~$12 |
| ALB (load balancer) | 1 ALB | ~$16 |
| S3 + CloudFront | Frontend static | ~$1 |
| **Total** | | **~$53/mo** |

---

### Architecture

```
Route 53 (DNS)
   │
   ├── yourdomain.com   → CloudFront → S3 (React static files)
   │
   └── api.yourdomain.com → ALB → ECS Fargate → FastAPI container
                                                     │        │
                                                   RDS      ElastiCache
                                                 PostgreSQL   Redis
```

---

### Service overview

**S3 + CloudFront (frontend):**
- Build React app → upload `dist/` to S3 bucket
- CloudFront distribution points to S3 → global CDN + HTTPS
- `vercel.json` rewrite logic → handled by CloudFront error page: 404 → `index.html`

**ECR (container registry):**
- Push Docker image here: `aws ecr push portfolio-backend`
- ECS pulls from ECR on every deploy

**ECS Fargate (backend):**
- Runs the Docker container without managing EC2 servers
- Task definition references the ECR image and env vars
- Service maintains desired count (1 replica for portfolio)

**RDS PostgreSQL:**
- Managed PostgreSQL 16, automated backups, Multi-AZ optional
- In a private subnet — not accessible from the internet

**ElastiCache Redis:**
- Managed Redis 7, also in private subnet
- Replace `REDIS_URL` with the ElastiCache endpoint

**ALB (Application Load Balancer):**
- Terminates SSL (ACM certificate)
- Routes `api.yourdomain.com` traffic to ECS tasks
- Health checks hit `/health`

**ACM (Certificate Manager):**
- Free SSL/TLS certificates for `yourdomain.com` and `api.yourdomain.com`

---

### High-level setup steps

```
1. VPC setup
   └── Create VPC, public + private subnets, NAT gateway

2. Database
   └── RDS → Create database → PostgreSQL 16 → db.t3.micro
   └── Place in private subnet
   └── Copy connection string → use in ECS task definition

3. Cache
   └── ElastiCache → Redis → cache.t3.micro
   └── Place in private subnet
   └── Copy endpoint → use in ECS task definition

4. Container registry
   └── ECR → Create repository "portfolio-backend"
   └── docker build + docker push to ECR

5. ECS cluster + task definition
   └── ECS → Create cluster (Fargate)
   └── Task definition → image = ECR URL
   └── Add all env vars (ADMIN_EMAIL, ADMIN_PASSWORD_HASH, etc.)
   └── Port mapping: 8000

6. ECS service
   └── Create service → desired count 1
   └── Attach to ALB target group

7. ALB + ACM
   └── Request ACM certificate for api.yourdomain.com
   └── ALB listener → HTTPS 443 → forward to ECS service
   └── HTTP 80 → redirect to HTTPS

8. Frontend
   └── S3 bucket → static website hosting
   └── pnpm build → aws s3 sync dist/ s3://your-bucket
   └── CloudFront → origin = S3 bucket
   └── Custom error: 404 → index.html (SPA routing)

9. DNS (Route 53 or external)
   └── yourdomain.com → CloudFront domain
   └── api.yourdomain.com → ALB DNS name
```

---

### Deploy new backend version

```bash
# 1. Build and push new Docker image to ECR
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin \
  <ACCOUNT_ID>.dkr.ecr.us-east-1.amazonaws.com

docker build -t portfolio-backend .
docker tag portfolio-backend:latest \
  <ACCOUNT_ID>.dkr.ecr.us-east-1.amazonaws.com/portfolio-backend:latest
docker push \
  <ACCOUNT_ID>.dkr.ecr.us-east-1.amazonaws.com/portfolio-backend:latest

# 2. Force new deployment (ECS pulls latest image)
aws ecs update-service \
  --cluster portfolio \
  --service portfolio-backend \
  --force-new-deployment
```

### Deploy new frontend version

```bash
# Build and sync to S3
pnpm build
aws s3 sync dist/ s3://your-frontend-bucket --delete

# Invalidate CloudFront cache
aws cloudfront create-invalidation \
  --distribution-id <DIST_ID> \
  --paths "/*"
```

---

### Running Alembic migrations on ECS

ECS runs migrations inside the container on startup (via the `CMD` in `Dockerfile`).
To run manually without a full deploy:

```bash
# Run a one-off ECS task with the migration command
aws ecs run-task \
  --cluster portfolio \
  --task-definition portfolio-backend \
  --overrides '{"containerOverrides":[{"name":"portfolio-backend",
    "command":["/app/.venv/bin/alembic","upgrade","head"]}]}' \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-xxx],
    securityGroups=[sg-xxx]}"
```

---

## Strategy C — Lightsail (AWS simplified, ~$10–18/mo)

AWS Lightsail is a simplified VPS product — like DigitalOcean but inside AWS.
Easier than ECS Fargate, more managed than raw EC2.

### Cost estimate

| Resource | Spec | Monthly cost |
|---|---|---|
| Lightsail instance | 1 GB RAM, 1 vCPU, 40 GB SSD | $10 |
| Lightsail Database | PostgreSQL, 1 GB RAM | free 1st month, then $15 |
| **Total** | | **~$10 first month, ~$25 after** |

### Setup steps

```
1. Create Lightsail instance
   └── Platform: Linux → Blueprint: Ubuntu 24.04
   └── Plan: $10/mo (1 GB RAM)

2. Same as Strategy A from Step 2 onwards
   └── SSH → install Docker → git clone → docker compose up
   └── But use Lightsail Managed PostgreSQL instead of Docker PostgreSQL
   └── Set DATABASE_URL to the Lightsail DB endpoint

3. Lightsail static IP
   └── Assign a static IP to the instance (free)

4. DNS + SSL
   └── Same Nginx + Certbot approach as Strategy A
```

---

## Comparison

| | Strategy A (EC2) | Strategy B (ECS Fargate) | Strategy C (Lightsail) |
|---|---|---|---|
| Monthly cost | ~$10 | ~$53 | ~$25 |
| Complexity | Low | High | Low |
| Code changes | None | None | None |
| Server maintenance | Yes (you patch OS) | None | Minimal |
| Auto-scaling | Manual | Yes | No |
| Managed DB | No (Docker) | Yes (RDS) | Yes |
| Cold starts | None | None | None |
| HA / Multi-AZ | No | Optional | No |
| Good for | Portfolio | Production app | Portfolio |

---

## Recommended for this portfolio

**Strategy A (EC2 + Docker Compose)** is the best fit:

- Cheapest after the free tier ($8–10/mo)
- Zero code changes — same `docker-compose.yml`
- No cold starts
- Easy to debug (SSH in and inspect logs)
- Identical to local development environment

**Strategy B (ECS Fargate)** only makes sense if the portfolio grows
into a real product with multiple services, auto-scaling, or zero-downtime
deploy requirements.

---

## Environment variables for AWS production

Same variables as current deployment — just change the `ALLOWED_ORIGINS`
and make sure `ENVIRONMENT=production`:

```bash
ENVIRONMENT=production
DEBUG=false
DATABASE_URL=postgresql+asyncpg://<user>:<pass>@<host>:5432/portfolio
REDIS_URL=redis://<elasticache-or-docker-redis>:6379/0
ALLOWED_ORIGINS=["https://yourdomain.com"]
ADMIN_EMAIL=admin@brensaud.com
ADMIN_PASSWORD_HASH=$2b$12$...
ADMIN_JWT_SECRET=<strong-random-64-char-hex>
ADMIN_JWT_ISSUER=api.yourdomain.com
ADMIN_JWT_AUDIENCE=admin.yourdomain.com
ADMIN_JWT_ACCESS_TTL_MINUTES=15
ADMIN_REFRESH_TTL_SECONDS=86400
```

---

## Useful AWS CLI commands

```bash
# Install AWS CLI
# https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html

# Configure credentials
aws configure

# List EC2 instances
aws ec2 describe-instances --query "Reservations[].Instances[].{ID:InstanceId,IP:PublicIpAddress,State:State.Name}" --output table

# List ECS services
aws ecs list-services --cluster portfolio

# Get ECS service status
aws ecs describe-services --cluster portfolio --services portfolio-backend

# List RDS instances
aws rds describe-db-instances --query "DBInstances[].{ID:DBInstanceIdentifier,Endpoint:Endpoint.Address}" --output table

# SSH tunnel to RDS (via EC2 bastion)
ssh -i portfolio-key.pem -L 5432:<RDS-ENDPOINT>:5432 ubuntu@<EC2-IP> -N
# Then connect locally: psql -h localhost -U postgres portfolio
```
