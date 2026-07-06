# AWS Architecture Patterns — Pros, Cons & Fit

A complete comparison of every meaningful AWS deployment architecture
for this stack (FastAPI + PostgreSQL + Redis + React/Vite).

---

## Quick reference

| Architecture | Monthly cost | Complexity | Code changes | Cold starts | Scales | Best for |
|---|---|---|---|---|---|---|
| A. EC2 + Docker Compose | ~$5–10 | Low | None | No | Manual | Portfolio |
| B. EC2 + RDS + ElastiCache | ~$30–40 | Medium | None | No | Manual | Small prod |
| C. Elastic Beanstalk | ~$15–30 | Low | Minor | No | Auto | Easy managed |
| D. App Runner | ~$5–15 | Low | None | No | Auto | Simple containers |
| E. ECS Fargate + RDS | ~$50–80 | High | None | No | Auto | Production |
| F. ECS on EC2 | ~$15–25 | High | None | No | Semi-auto | Cost + control |
| G. Lambda + API Gateway | ~$0–5 | Very high | Major rewrite | Yes | Infinite | Micro APIs |
| H. Lambda + Mangum (FastAPI) | ~$1–10 | High | Minor | Yes | Infinite | Serverless FastAPI |
| I. EC2 Auto Scaling + ALB | ~$40–60 | High | None | No | Auto | High traffic |

---

## Architecture A — EC2 + Docker Compose

Single server running all services via `docker-compose.yml`.
No managed AWS services except the EC2 instance itself.

```
Internet → EC2 (Nginx)
              ├── FastAPI container  (port 8000)
              ├── PostgreSQL container (port 5432, internal only)
              └── Redis container      (port 6379, internal only)
```

### Services used
- EC2 (t4g.micro / t3.micro)
- EBS (root volume, 20 GB)
- Elastic IP
- S3 + CloudFront (frontend)

### Pros
- Identical to local development — no surprises
- Cheapest option ($3–10/mo)
- Full control over all services
- Simple to debug — SSH in and inspect logs
- No AWS-specific knowledge required beyond EC2 basics
- All data stays on one server — no network latency between services
- No cold starts

### Cons
- Single point of failure — if EC2 goes down, everything is down
- You patch the OS manually (`apt update && apt upgrade`)
- No automatic backups for PostgreSQL (you must set up cron + pg_dump)
- Cannot scale horizontally (only vertical: bigger instance)
- No zero-downtime deploys on its own (brief restart during `docker compose up`)
- EBS volume lost if you forget to keep it when terminating

### Code changes required
None. Exact same `Dockerfile` and `docker-compose.yml`.

### When to choose
Portfolio, personal projects, low traffic, budget-conscious.

---

## Architecture B — EC2 + RDS + ElastiCache

Same EC2 backend but replaces Docker PostgreSQL and Redis with
AWS managed services. Better durability and backups.

```
Internet → EC2 (Nginx → FastAPI)
                  │
                  ├── RDS PostgreSQL (managed, automated backups)
                  └── ElastiCache Redis (managed, multi-AZ optional)
```

### Services used
- EC2 (backend)
- RDS PostgreSQL (db.t3.micro)
- ElastiCache Redis (cache.t3.micro)
- VPC with public + private subnets
- Security Groups
- S3 + CloudFront (frontend)

### Pros
- Automated daily RDS backups (7–35 day retention)
- Point-in-time restore for the database
- RDS handles PostgreSQL patches automatically
- ElastiCache is more reliable than Redis in Docker
- Can enable RDS Multi-AZ for high availability

### Cons
- Significantly more expensive than Architecture A (~$35/mo after free tier)
- RDS in a private subnet requires a VPC, subnets, and security group config
- Adds AWS networking complexity (VPC peering, security group rules)
- ElastiCache for a rate-limiting Redis is overkill at portfolio scale

### Code changes required
None. Just change `DATABASE_URL` and `REDIS_URL` env vars.

### When to choose
When you need automated database backups and can afford ~$35/mo.
Consider Neon (external, free) as a cheaper alternative to RDS.

---

## Architecture C — Elastic Beanstalk

AWS's managed PaaS. You deploy a Dockerfile and Beanstalk handles
EC2, load balancer, auto-scaling, and health checks automatically.
Similar to Heroku but on AWS.

```
Internet → ALB (Beanstalk-managed)
               └── EC2 instances (Beanstalk-managed, runs Docker)
                       │
                       ├── RDS PostgreSQL (add-on)
                       └── ElastiCache Redis (separate)
```

### Services used
- Elastic Beanstalk (wraps EC2 + ALB + Auto Scaling)
- RDS PostgreSQL (Beanstalk add-on or separate)
- ElastiCache Redis (separate)
- S3 (source bundle + frontend)
- CloudFront (frontend CDN)

### Pros
- Auto-scaling built in — scale out on CPU/request spikes
- Built-in health monitoring and auto-healing (restarts unhealthy instances)
- Rolling/blue-green deployments with zero downtime
- Simple deployment: `eb deploy` from terminal
- Managed OS patches (Beanstalk replaces EC2 AMI automatically)
- ALB is included — no manual Nginx required

### Cons
- Less transparent than raw EC2 — harder to debug Beanstalk internals
- Beanstalk has its own config format (`.ebextensions/`) if you need customisation
- Still costs ~$20–40/mo (EC2 + ALB + RDS)
- Cold deploy can take 5–10 minutes
- ALB costs ~$16/mo even when idle

### Deploy command
```bash
# Install Elastic Beanstalk CLI
pip install awsebcli

# Initialise (one-time)
eb init portfolio-backend --region us-east-1 --platform docker

# Create environment
eb create portfolio-prod \
  --instance-type t4g.micro \
  --database.engine postgres \
  --database.version 16

# Set env vars
eb setenv ADMIN_EMAIL=... ADMIN_PASSWORD_HASH=... ADMIN_JWT_SECRET=...

# Deploy
eb deploy

# Check status
eb status
eb logs
```

### Code changes required
Minor — Beanstalk needs a `Dockerrun.aws.json` or works directly
from your existing `Dockerfile`. No application code changes.

### When to choose
When you want managed scaling without learning ECS but can afford ~$25/mo.

---

## Architecture D — AWS App Runner

The simplest managed container service on AWS. Point it at a GitHub repo
or ECR image, and App Runner handles everything else: build, deploy,
scaling, HTTPS, health checks.

```
Internet → App Runner (HTTPS, auto-scaling)
               └── FastAPI container (auto-provisioned)
                       │
                       ├── Neon PostgreSQL (external, free)
                       └── Upstash Redis   (external, free)
```

### Services used
- AWS App Runner
- ECR (container image registry) or GitHub source
- S3 + CloudFront (frontend)
- Neon / Upstash (external, free managed services)

### Pros
- Genuinely the simplest AWS managed container deployment
- No VPC, no ALB, no security groups required by default
- Auto-scales from 0 to N instances (true serverless containers)
- Built-in HTTPS on the App Runner domain
- Automatic health checks and restarts
- GitHub integration — pushes trigger auto-deploy
- Pay per use — $0.064/vCPU-hour + $0.007/GB-hour

### Cons
- Scales **to zero** when idle → cold start of 10–30 seconds
  (App Runner has a "warm instances" option for $0.005/instance-hour to avoid this)
- Less control than ECS (no custom networking config by default)
- Minimum 0.25 vCPU, 0.5 GB per instance
- VPC connector is extra config if you need RDS in private subnet

### Monthly cost
```
App Runner (0.25 vCPU, 0.5 GB, always on with 1 warm instance):
  vCPU:    $0.064 × 0.25 × 730 hours = $11.68
  Memory:  $0.007 × 0.5  × 730 hours = $2.56
  Subtotal: ~$14/mo

App Runner (idle, 0 warm instances, scales to zero):
  Only pay when requests are in flight → ~$0–2/mo at portfolio traffic
  But has cold starts on first request after idle period
```

### Deploy commands
```bash
# Build and push image to ECR
aws ecr create-repository --repository-name portfolio-backend
docker build -t portfolio-backend .
docker tag portfolio-backend:latest \
  <ACCOUNT>.dkr.ecr.us-east-1.amazonaws.com/portfolio-backend:latest
docker push \
  <ACCOUNT>.dkr.ecr.us-east-1.amazonaws.com/portfolio-backend:latest

# Create App Runner service (AWS Console is easier, but CLI works too)
aws apprunner create-service \
  --service-name portfolio-backend \
  --source-configuration '{
    "ImageRepository": {
      "ImageIdentifier": "<ACCOUNT>.dkr.ecr.us-east-1.amazonaws.com/portfolio-backend:latest",
      "ImageRepositoryType": "ECR",
      "ImageConfiguration": {
        "Port": "8000",
        "RuntimeEnvironmentVariables": {
          "ENVIRONMENT": "production",
          "DATABASE_URL": "...",
          "ADMIN_EMAIL": "..."
        }
      }
    }
  }' \
  --instance-configuration '{"Cpu":"0.25 vCPU","Memory":"0.5 GB"}'
```

### Code changes required
None. Existing `Dockerfile` works directly.

### When to choose
When you want the simplest managed AWS deployment and are willing to use
Neon + Upstash (free) for data services. Best balance of simplicity and
managed infrastructure.

---

## Architecture E — ECS Fargate + RDS + ElastiCache + ALB

Fully managed container platform. Production-grade, no servers to manage,
auto-scaling, zero-downtime rolling deploys.

```
Route 53
  ├── yourdomain.com   → CloudFront → S3
  └── api.yourdomain.com → ACM → ALB → ECS Fargate tasks
                                            │       │
                                          RDS   ElastiCache
                                        (private subnet)
```

### Services used
- ECS Fargate (container runtime)
- ECR (container image registry)
- ALB (Application Load Balancer)
- ACM (SSL certificates, free)
- RDS PostgreSQL (managed database)
- ElastiCache Redis (managed cache)
- VPC with public + private subnets
- NAT Gateway (optional, $32/mo)
- S3 + CloudFront (frontend)
- Route 53 (DNS, $0.50/mo per zone)
- Secrets Manager (env vars, optional)

### Pros
- Zero server management — AWS handles patching, placement, scaling
- Rolling deployments with zero downtime (old task stays up until new is healthy)
- Auto-scales based on CPU/memory/request count
- RDS Multi-AZ for database high availability
- RDS automated backups with point-in-time restore
- Private subnet isolates DB and Redis from internet
- CloudWatch integration for logs and metrics
- IAM roles replace hardcoded credentials
- Production-grade reliability

### Cons
- Most expensive option (~$53–80/mo minimum)
- Significant setup complexity — VPC, subnets, security groups, task definitions,
  service definitions, ALB rules, target groups, IAM roles
- NAT Gateway for private subnet outbound traffic adds $32/mo
- Learning curve: ECS concepts (clusters, tasks, services, task definitions)
- Overkill for a portfolio with < 1000 daily visitors

### Estimated monthly cost (no NAT Gateway)
```
ECS Fargate (0.25 vCPU, 0.5 GB, 1 task):         ~$14
RDS db.t3.micro PostgreSQL:                       ~$15
ElastiCache cache.t3.micro Redis:                 ~$12
ALB:                                              ~$16
S3 + CloudFront:                                  ~$1
ECR storage (10 GB):                              ~$1
Total:                                            ~$59/mo
```

### Code changes required
None. Existing `Dockerfile` deploys directly to ECS.

### When to choose
When the portfolio becomes a real product with > 10k daily visitors,
SLA requirements, or you need to demonstrate AWS production architecture
on your CV.

---

## Architecture F — ECS on EC2 (self-managed cluster)

Run ECS tasks on EC2 instances you own — the cost of Architecture A
with the container orchestration benefits of Architecture E.

```
Internet → ALB → EC2 instances running ECS agent
                     └── ECS tasks (FastAPI containers)
                              │       │
                            RDS   ElastiCache (or Docker Redis)
```

### Services used
- ECS cluster (EC2 launch type)
- EC2 instances (you manage)
- ECR
- ALB
- RDS / ElastiCache (optional, or Docker services)

### Pros
- Cheaper than Fargate (~40% cost reduction on compute)
- Still get ECS rolling deployments and service management
- Can use EC2 reserved instances for bigger savings
- EC2 spot instances for even cheaper (if interruptions are acceptable)

### Cons
- You still manage the EC2 instances (OS patches, scaling groups)
- More complex than Architecture A or D
- ALB still costs ~$16/mo
- Benefits of ECS (rolling deploys) require more config than Docker Compose

### When to choose
High container workloads where Fargate compute cost is significant
but you still want ECS orchestration. Not ideal for a portfolio.

---

## Architecture G — Lambda + API Gateway (pure serverless)

Rewrite the backend as individual Lambda functions, exposed via API Gateway.
No container, no server.

```
Internet → API Gateway → Lambda functions (per route)
                              │
                              ├── RDS Proxy → RDS PostgreSQL
                              └── (Redis sessions not supported in Lambda)
```

### Services used
- Lambda (individual function per endpoint or grouped)
- API Gateway (HTTP API)
- RDS Proxy + RDS PostgreSQL
- S3 + CloudFront (frontend)
- Secrets Manager (env vars)

### Pros
- Truly pay-per-request ($0 when idle)
- Infinite scale on demand
- AWS handles all infrastructure
- First 1M Lambda invocations free every month forever

### Cons
- **Major rewrite required** — FastAPI as written does not run natively on Lambda
- Cold starts: first request after idle period takes 1–5 seconds for Python
- SQLAlchemy async connection pooling breaks in Lambda (each invocation is stateless)
  → must use RDS Proxy ($0.015/vCPU-hour) to manage connections
- Redis (for admin JWT sessions) is problematic in Lambda — each invocation
  is isolated and cannot hold a persistent connection
- The admin panel requires HTTPOnly cookies, which work with Lambda +
  API Gateway but need careful CORS + cookie domain configuration
- `asyncpg` and the lifespan/startup pattern in FastAPI need adaptation

### Estimated cost
```
Lambda (1M requests/month, 512 MB, avg 200ms):
  Compute: 1M × 0.2s × 0.5 GB × $0.0000166667/GB-s = $1.67
  Requests: 1M × $0.20/1M = $0.20
  Total Lambda: ~$2/mo (very low traffic)

RDS Proxy: $0.015 × vCPUs × hours = ~$5/mo
RDS PostgreSQL db.t3.micro: ~$15/mo
API Gateway HTTP API: ~$1/mo at low traffic
Total: ~$23/mo
```

### Code changes required
**Extensive.** Would need to:
1. Replace `uvicorn` startup with Lambda handler
2. Adapt SQLAlchemy connection management for stateless invocations
3. Replace Redis session storage with DynamoDB or SSM Parameter Store
4. Restructure the project for Lambda packaging

### When to choose
Not recommended for this codebase. The FastAPI + SQLAlchemy async +
Redis sessions architecture is designed for a long-lived server process,
not stateless Lambda invocations.

---

## Architecture H — Lambda + Mangum (FastAPI Adapter)

Mangum is an ASGI adapter that wraps a FastAPI app to run inside a
single Lambda function. No rewrite — just add one dependency.

```
Internet → API Gateway (HTTP API) → Lambda (single function)
                                         └── Full FastAPI app via Mangum
                                               │         │
                                             Neon     Upstash Redis
                                          (external)  (external)
```

### Services used
- Lambda (single function, whole FastAPI app)
- API Gateway (HTTP API)
- S3 + CloudFront (frontend)
- Neon / Upstash (external, free)

### Pros
- Minimal code change — just wrap the FastAPI app with Mangum
- True pay-per-request (very cheap at low traffic)
- No server to manage
- Lambda has 15-minute max execution — fine for API calls
- Works with existing Pydantic, middleware, routing

### Cons
- Cold starts: Python 3.12 Lambda cold start is 2–5 seconds
  (use Lambda Snapstart or SnapStart-compatible runtimes to reduce)
- Lambda container image size limit: 10 GB (fine for this project)
- SQLAlchemy connection pooling is wasted in Lambda — each invocation
  creates a new connection. Neon's connection pooling (PgBouncer) mitigates this.
- Alembic migrations cannot run at Lambda startup — must be triggered separately
- HTTPOnly cookie domain must match between API Gateway domain and frontend domain
- Max request body size: 10 MB (fine for a contact form)

### Code change (minimal)
```python
# main.py — add 3 lines
from mangum import Mangum
from app.main import create_app

app = create_app()
handler = Mangum(app)  # Lambda entry point
```

```toml
# pyproject.toml — add one dependency
"mangum>=0.17.0",
```

### Deployment with SAM
```bash
# Install SAM CLI
# https://docs.aws.amazon.com/serverless-application-model/

# template.yaml
AWSTemplateFormatVersion: '2010-09-09'
Transform: AWS::Serverless-2016-10-31
Resources:
  PortfolioBackend:
    Type: AWS::Serverless::Function
    Properties:
      PackageType: Image
      MemorySize: 512
      Timeout: 30
      Environment:
        Variables:
          DATABASE_URL: !Ref DatabaseUrl
          ADMIN_EMAIL: !Ref AdminEmail
      Events:
        Api:
          Type: HttpApi

# Deploy
sam build
sam deploy --guided
```

### Estimated monthly cost (low traffic portfolio)
```
Lambda (50k requests/month, 512 MB, avg 300ms):
  Compute: 50k × 0.3s × 0.5 GB × $0.0000166667 = $0.13
  Requests: 50k × $0.20/1M = $0.01
API Gateway: 50k × $1/1M = $0.05
Neon + Upstash: $0
Total: ~$0.19/mo ≈ essentially free
```

### When to choose
When you want near-zero cost and can accept occasional cold starts (2–5 s).
Good if you know the portfolio will get very low traffic most of the time.

---

## Architecture I — EC2 Auto Scaling Group + ALB

Multiple EC2 instances behind a load balancer, automatically scaling
out on high traffic and in during quiet periods.

```
Internet → Route 53 → ALB
                        ├── EC2 instance 1 (FastAPI Docker)
                        ├── EC2 instance 2 (FastAPI Docker, auto-added)
                        └── EC2 instance N (auto-added on high CPU)
                                │            │
                               RDS       ElastiCache Redis
                           (Multi-AZ)    (shared across instances)
```

### Services used
- ALB (Application Load Balancer)
- Auto Scaling Group (manages EC2 fleet)
- Launch Template (EC2 config template)
- RDS PostgreSQL Multi-AZ
- ElastiCache Redis Cluster (shared state across instances)
- S3 + CloudFront (frontend)
- CloudWatch (scaling metrics + alarms)

### Pros
- Truly horizontally scalable — handles traffic spikes automatically
- High availability — instances spread across Availability Zones
- RDS Multi-AZ: automatic failover if primary DB goes down
- ElastiCache cluster: shared Redis state across all API instances
- Zero-downtime rolling updates via ASG instance refresh

### Cons
- Most complex non-Fargate architecture
- Expensive: ALB ($16) + 2× EC2 ($16) + RDS Multi-AZ ($30) + ElastiCache ($12) = ~$75/mo
- ALB distributes requests — Redis must be shared (ElastiCache, not Docker)
  because JWT refresh tokens are stored in Redis and any instance must validate them
- Database migrations must be handled carefully before scaling up new instances
- Overkill for a personal portfolio

### Code changes required
None. But Redis must be external (ElastiCache) because Docker Redis on
instance 1 is not visible to instance 2.

### When to choose
When you expect > 100k API requests/day and need guaranteed uptime.
Not appropriate for a portfolio.

---

## Decision guide

```
Is the project a portfolio / personal project?
  ├── Budget is $0/year → Architecture H (Lambda + Mangum)
  │     Cold starts acceptable? If yes → H. If no → keep on Render free.
  │
  ├── Budget is $5–10/month → Architecture A (EC2 + Docker Compose)
  │     Simplest AWS option. No cold starts.
  │
  └── Budget is $10–15/month → Architecture D (App Runner)
        Managed, no server admin, no cold starts with 1 warm instance.

Is the project growing into a real product?
  ├── < 10k req/day → Architecture B (EC2 + RDS + ElastiCache)
  ├── 10k–100k req/day → Architecture E (ECS Fargate + RDS)
  └── > 100k req/day → Architecture I (ASG + ALB + RDS Multi-AZ)
```

---

## Service comparison table

| AWS Service | Purpose | Replaces | Free tier |
|---|---|---|---|
| EC2 | VM server | Render / Railway | t3.micro, 12 months |
| ECS Fargate | Managed containers | Render / Railway | No |
| App Runner | Simple managed containers | Render | No |
| Elastic Beanstalk | Managed PaaS | Heroku | No (EC2 free tier applies) |
| Lambda | Serverless functions | — | 1M req/mo forever |
| RDS | Managed PostgreSQL | Neon / Docker | db.t3.micro, 12 months |
| ElastiCache | Managed Redis | Upstash / Docker | No |
| S3 | Static file storage | Vercel | 5 GB, 12 months |
| CloudFront | CDN | Vercel | 1 TB transfer, 12 months |
| ALB | Load balancer | Nginx | No ($16/mo always) |
| API Gateway | HTTP API routing | Nginx | 1M calls/mo, 12 months |
| ECR | Container image registry | Docker Hub | 500 MB/mo free |
| Route 53 | DNS | External registrar | No ($0.50/hosted zone) |
| ACM | SSL certificates | Let's Encrypt | Free (always) |
| Secrets Manager | Env var storage | `.env` / Render env | No ($0.40/secret/mo) |
| CloudWatch | Logs + metrics | — | 5 GB logs, 10 metrics free |
