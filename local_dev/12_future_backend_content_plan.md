# Future Plan — Backend-Driven Content for a World-Class Portfolio

A prioritised roadmap of features that should be moved from hardcoded
TypeScript files to a dynamic backend to make this portfolio stand out.

---

## Why move content to the backend?

Currently, updating a project card or blog article requires:
1. Edit a `.ts` file
2. Commit to GitHub
3. Wait for CI + Vercel to redeploy (~2 minutes)

A backend-driven portfolio allows:
- Update content instantly from an admin dashboard (no code, no deploy)
- Track who reads what and for how long (analytics)
- Serve personalised content based on visitor context
- Accept guest feedback, newsletter sign-ups, and project inquiries
- Expose an RSS feed, sitemap, and OpenGraph previews for every article
- Let recruiters bookmark and share specific projects

---

## Priority tiers

```
Tier 1 — High impact, low effort    (do these first)
Tier 2 — High impact, medium effort (next quarter)
Tier 3 — Differentiators            (makes it best in class)
Tier 4 — Advanced / AI features     (long-term vision)
```

---

## Tier 1 — High impact, low effort

### 1.1 Blog / Articles CMS

**Current state:**
`src/data/articles.ts` — hardcoded TypeScript array. Status: all "Planned" / "In progress".

**Future state:**
Admin can write, edit, publish, and unpublish articles from the dashboard.
Articles are stored in the database with full Markdown or rich text body.

**What the backend needs:**

| Endpoint | Purpose |
|---|---|
| `GET /api/v1/articles` | Public list — published only, paginated |
| `GET /api/v1/articles/{slug}` | Full article content |
| `GET /admin/api/articles` | Admin list — all statuses |
| `POST /admin/api/articles` | Create draft |
| `PUT /admin/api/articles/{id}` | Update content |
| `PATCH /admin/api/articles/{id}/publish` | Publish |
| `PATCH /admin/api/articles/{id}/unpublish` | Unpublish |
| `DELETE /admin/api/articles/{id}` | Delete |

**Database table:** `articles`

```sql
id          UUID PRIMARY KEY
slug        VARCHAR(200) UNIQUE NOT NULL
title       VARCHAR(300) NOT NULL
category    VARCHAR(50)
summary     TEXT
body        TEXT          -- Markdown
reading_time_minutes INT
status      VARCHAR(20)   -- draft / published / archived
published_at TIMESTAMPTZ
created_at  TIMESTAMPTZ
updated_at  TIMESTAMPTZ
```

**Frontend change:** Replace `src/data/articles.ts` static import with a
React Query `useQuery` call to `GET /api/v1/articles`.

**Impact:** Publish real articles without a redeploy. SEO-friendly article pages.

---

### 1.2 Projects CMS

**Current state:**
`src/data/projects.ts` — hardcoded TypeScript array.

**Future state:**
Admin can add, update, and reorder projects from the dashboard.
New projects appear live without any frontend deployment.

**What the backend needs:**

| Endpoint | Purpose |
|---|---|
| `GET /api/v1/projects` | Public list |
| `GET /api/v1/projects/{slug}` | Single project detail |
| `GET /admin/api/projects` | Admin list — all statuses |
| `POST /admin/api/projects` | Create project |
| `PUT /admin/api/projects/{id}` | Update |
| `PATCH /admin/api/projects/{id}/feature` | Mark as featured |
| `PATCH /admin/api/projects/{id}/sort` | Reorder |
| `DELETE /admin/api/projects/{id}` | Delete |

**Database table:** `projects`

```sql
id           UUID PRIMARY KEY
slug         VARCHAR(200) UNIQUE NOT NULL
title        VARCHAR(200) NOT NULL
subtitle     TEXT
description  TEXT
category     VARCHAR(50)
status       VARCHAR(50)
tech_stack   TEXT[]        -- PostgreSQL array
is_featured  BOOLEAN DEFAULT false
sort_order   INTEGER
links        JSONB         -- [{label, href, type}]
created_at   TIMESTAMPTZ
updated_at   TIMESTAMPTZ
```

**Impact:** Add a new project in 30 seconds from the admin panel.

---

### 1.3 Resume CMS

**Current state:**
`src/data/resume.ts` — hardcoded TypeScript file, requires redeploy to update.

**Future state:**
Admin updates experience, skills, and certifications from the dashboard.
PDF export triggered on demand.

**What the backend needs:**

| Endpoint | Purpose |
|---|---|
| `GET /api/v1/resume` | Full structured resume data |
| `PUT /admin/api/resume/experience` | Update work history |
| `PUT /admin/api/resume/skills` | Update skill groups |
| `PUT /admin/api/resume/education` | Update education |
| `GET /api/v1/resume/pdf` | Download generated PDF |

**Impact:** Update job titles and skills without touching code.

---

## Tier 2 — High impact, medium effort

### 2.1 Page View Analytics

Track which projects and articles get the most attention without relying
on Google Analytics (no cookie consent required for server-side analytics).

**What the backend needs:**

```python
# New table: page_views
id         UUID
path       VARCHAR(500)   # /work/portfolio-backend
referrer   VARCHAR(500)   # null or referring domain only (no full URL)
country    VARCHAR(2)     # from IP geolocation (no IP stored)
session_id VARCHAR(64)    # hash of (IP + UA + date) — not reversible to PII
duration_s INTEGER        # time on page in seconds
created_at TIMESTAMPTZ
```

| Endpoint | Purpose |
|---|---|
| `POST /api/v1/analytics/view` | Record a page view (public, rate-limited) |
| `GET /admin/api/analytics/pages` | Top pages by views |
| `GET /admin/api/analytics/projects` | Which projects get most clicks |
| `GET /admin/api/analytics/articles` | Which articles are read most |
| `GET /admin/api/analytics/referrers` | Where visitors come from |

**Admin dashboard widget:** "Top 5 most viewed projects this week"

**Privacy:** No full IP stored. Country only. No tracking pixels. No third-party JS.

---

### 2.2 Newsletter / Email Capture

Collect email addresses from interested visitors — recruiters, engineers
who want to follow the engineering blog.

**What the backend needs:**

| Endpoint | Purpose |
|---|---|
| `POST /api/v1/newsletter/subscribe` | Submit email + consent |
| `GET /admin/api/newsletter/subscribers` | Admin list |
| `DELETE /admin/api/newsletter/subscribers/{id}` | Unsubscribe (GDPR) |

**Database table:** `newsletter_subscribers`

```sql
id           UUID PRIMARY KEY
email        VARCHAR(255) UNIQUE NOT NULL
source       VARCHAR(50)   -- 'homepage', 'article', 'resume'
confirmed    BOOLEAN DEFAULT false
created_at   TIMESTAMPTZ
```

**Impact:** Build a direct line to recruiters and readers.

---

### 2.3 Case Studies as Structured Backend Content

**Current state:**
`src/data/case-studies.ts` — deeply nested TypeScript with architecture diagrams,
API designs, and database models. Requires code changes to update.

**Future state:**
Case studies stored as structured JSON in the database. Editable from admin panel.
Each case study can have: problem statement, architecture, technical decisions,
challenges, outcomes, and embedded code snippets.

**Database table:** `case_studies`

```sql
id              UUID PRIMARY KEY
project_id      UUID REFERENCES projects(id)
problem         TEXT
architecture    JSONB   -- components, layers, decisions
challenges      JSONB   -- [{title, description, resolution}]
tech_deep_dives JSONB
lessons         TEXT[]
status          VARCHAR(20)  -- draft / published
published_at    TIMESTAMPTZ
```

---

### 2.4 Project Availability / Open to Work Status

Show a real-time "Open to work" or "Available from [date]" banner that the
admin can toggle without redeploying.

**What the backend needs:**

| Endpoint | Purpose |
|---|---|
| `GET /api/v1/availability` | Current availability status |
| `PUT /admin/api/availability` | Update availability |

```json
{
  "status": "open",
  "available_from": "2026-08-01",
  "message": "Available for backend engineering roles",
  "notice_period_weeks": 2
}
```

**Impact:** Recruiters always see accurate availability. No redeploy to update.

---

### 2.5 Testimonials / Recommendations

Store professional recommendations that can be shown on the homepage
or resume page. Admin approves each one before it is displayed.

**Database table:** `testimonials`

```sql
id          UUID PRIMARY KEY
author_name VARCHAR(100)
author_role VARCHAR(200)
company     VARCHAR(100)
body        TEXT
is_featured BOOLEAN
sort_order  INTEGER
approved    BOOLEAN DEFAULT false
created_at  TIMESTAMPTZ
```

---

## Tier 3 — Differentiators

### 3.1 Admin Dashboard with Real-Time Metrics

Transform the current minimal dashboard placeholder into a command centre:

| Widget | Data source |
|---|---|
| Unread contact messages | `contact_messages` count |
| Top projects this week | `page_views` grouped by project |
| Latest article reads | `page_views` grouped by article |
| Newsletter subscribers | `newsletter_subscribers` count |
| Open to work status | `availability` table |
| Recent audit log | `admin_audit_logs` |

All widgets powered by React Query with a 60-second stale time.

---

### 3.2 Full-Text Search API

Allow visitors to search across projects and articles with a single query.

| Endpoint | Purpose |
|---|---|
| `GET /api/v1/search?q=fastapi` | Search projects + articles |

**Implementation:** PostgreSQL full-text search with `tsvector` and `tsquery`.
No Elasticsearch required at portfolio scale.

```sql
-- Index on articles
ALTER TABLE articles ADD COLUMN search_vector tsvector
  GENERATED ALWAYS AS (
    to_tsvector('english', coalesce(title,'') || ' ' || coalesce(body,''))
  ) STORED;
CREATE INDEX idx_articles_search ON articles USING GIN(search_vector);
```

---

### 3.3 RSS Feed

Auto-generated RSS feed from published articles — lets readers subscribe
in any RSS reader without giving an email address.

| Endpoint | Purpose |
|---|---|
| `GET /api/v1/feed.xml` | RSS 2.0 feed of published articles |
| `GET /api/v1/feed.json` | JSON Feed format |

FastAPI can return XML directly via `Response(content=xml, media_type="application/rss+xml")`.

---

### 3.4 Dynamic OG Images for Articles and Projects

Generate Open Graph preview images on-the-fly so every shared link
shows a rich preview with title, category, and brand styling.

| Endpoint | Purpose |
|---|---|
| `GET /api/v1/og/article/{slug}.png` | OG image for an article |
| `GET /api/v1/og/project/{slug}.png` | OG image for a project |

**Implementation:** `Pillow` library draws text + branding onto a template image.
Result cached in S3 or a CDN.

---

### 3.5 Structured Sitemap

Auto-generated XML sitemap that updates as new articles and projects are added.
Essential for search engine indexing.

| Endpoint | Purpose |
|---|---|
| `GET /sitemap.xml` | Dynamic XML sitemap |

Includes: all published articles, all projects, static pages.
`lastmod` driven by `updated_at` from the database.

---

## Tier 4 — Advanced / AI features

### 4.1 AI-Powered Project Summaries

Use an LLM (OpenAI / Claude / Groq) to generate concise, recruiter-focused
summaries of each project based on the technical content stored in the database.

| Endpoint | Purpose |
|---|---|
| `POST /admin/api/projects/{id}/generate-summary` | Trigger AI summary generation |

Stored result: `projects.ai_summary` — used on the homepage as a one-liner.

---

### 4.2 Intelligent Contact Form Categorisation

When a contact message arrives, automatically classify it:
- Type: `hiring_inquiry` / `collaboration` / `question` / `spam`
- Priority: `high` / `medium` / `low`
- Suggested reply: generate a draft response using the message content

**Implementation:** Small classifier using the message text + subject.
Can be rule-based first, LLM-backed later.

---

### 4.3 Visitor Intelligence

Show the admin contextual information about contact message senders:
- LinkedIn profile (if link provided)
- Company domain from email (look up via Clearbit or Hunter API)
- Estimated seniority / role from message content

This gives context before replying: "Jane is a Senior Engineering Manager at Stripe."

---

### 4.4 Smart Availability Engine

Automatically adjust the "Open to work" status based on calendar integration
(Calendly / Google Calendar) and workload signals.

---

## Implementation order

```
Phase A — Content CMS (most impactful)
  □ Articles (Sprint 3)
  □ Projects (Sprint 4)
  □ Availability status (Sprint 4, small)

Phase B — Growth
  □ Analytics (Sprint 5)
  □ Newsletter subscribe (Sprint 5)
  □ Resume CMS (Sprint 6)

Phase C — Quality signals
  □ Case studies CMS (Sprint 7)
  □ Testimonials (Sprint 7)
  □ RSS feed (Sprint 8, small)
  □ Sitemap (Sprint 8, small)

Phase D — Discoverability
  □ Full-text search (Sprint 9)
  □ OG images (Sprint 9)

Phase E — Dashboard
  □ Admin dashboard widgets (Sprint 10)

Phase F — AI
  □ Contact message classification (Sprint 11)
  □ AI project summaries (Sprint 12)
```

---

## What stays hardcoded forever

Some content should intentionally never move to the database:

| Content | Why it stays static |
|---|---|
| Navigation menu items | Structural — changes are always code changes |
| Site name and branding | Needs a code + design decision to change |
| Color tokens / design system | CSS, not data |
| Page layouts | React components, not content |
| Error pages (404, 500) | No dynamic content needed |
