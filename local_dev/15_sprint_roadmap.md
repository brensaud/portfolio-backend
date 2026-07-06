# Sprint Roadmap — World-Class Portfolio

All sprints from current state to completion.
Each sprint is a focused, shippable increment with clear scope and outcome.

---

## Completed

| Sprint | Name | Status | Outcome |
|---|---|---|---|
| Sprint 1 | Admin Authentication | ✅ Done | Secure login, JWT cookies, refresh rotation, rate limiting |
| Sprint 2 | Admin Contact Messages | ✅ Done | View, search, filter, manage contact form submissions |

---

## Upcoming sprints

---

## Sprint 3 — Articles CMS

**Goal:** Write and publish real engineering articles without touching code.

### Backend
- `articles` database table + migration 0004
- `GET /api/v1/articles` — public list (published only, paginated)
- `GET /api/v1/articles/{slug}` — full article with Markdown body
- `GET /admin/api/articles` — admin list (all statuses)
- `POST /admin/api/articles` — create draft
- `PUT /admin/api/articles/{id}` — update content
- `PATCH /admin/api/articles/{id}/publish` — publish
- `PATCH /admin/api/articles/{id}/unpublish` — unpublish
- `DELETE /admin/api/articles/{id}` — delete
- Audit log: created, published, unpublished, deleted

### Frontend
- Admin: Articles list page with status filters
- Admin: Article editor (Markdown, preview pane, syntax highlight)
- Public: Replace `src/data/articles.ts` with React Query fetch
- Public: Individual article reader page (`/writing/{slug}`)
- Public: Reading progress bar on article page

### Definition of done
- Admin can write an article, save draft, preview, publish
- Published articles visible on `/writing` without redeploy
- Unpublished articles invisible to public

---

## Sprint 4 — Projects CMS + Availability Toggle

**Goal:** Manage portfolio projects from the admin and show real-time availability status.

### Backend
- `projects` database table + migration 0005
- `availability` table + migration 0005
- Full CRUD: `GET/POST/PUT/DELETE /admin/api/projects`
- `PATCH /admin/api/projects/{id}/feature` — toggle featured
- `PATCH /admin/api/projects/{id}/sort` — reorder
- `GET /api/v1/projects` — public list
- `GET /api/v1/projects/{slug}` — public detail
- `GET /api/v1/availability` — current status (public)
- `PUT /admin/api/availability` — update status (admin)
- Image upload for project thumbnails (S3 / Cloudflare R2)

### Frontend
- Admin: Projects list with drag-to-reorder
- Admin: Project form (all fields including tech stack tags)
- Admin: Availability settings form (status, date, message)
- Public: Replace `src/data/projects.ts` with React Query fetch
- Public: Availability banner on homepage and contact page

### Definition of done
- Admin adds a project — it appears live on `/work` without redeploy
- Availability toggle changes the homepage banner within seconds

---

## Sprint 5 — Site Settings + Profile

**Goal:** Manage site-wide settings and personal profile from the admin, no code edits needed.

### Backend
- `site_settings` table (key-value store) + migration 0006
- `PUT /admin/api/settings/profile` — name, headline, bio, social links
- `GET /api/v1/settings/profile` — public profile data
- `PATCH /admin/api/auth/password` — already exists (Sprint 1), expose in UI

### Frontend
- Admin: Settings section with Profile form
- Admin: Password change form (backend already handles this)
- Admin: Social links form (GitHub, LinkedIn, X, email)
- Public: Replace hardcoded `site.ts` values with API-driven profile data
- Fix: Replace placeholder values in `site.ts` (LinkedIn, email, Twitter)

### Definition of done
- Admin updates bio or LinkedIn URL — visible on site without redeploy
- All placeholder values in `site.ts` replaced with real data

---

## Sprint 6 — Resume CMS

**Goal:** Update work experience, skills, and certifications from the admin dashboard.

### Backend
- `resume_sections` table + migration 0007
- `GET /api/v1/resume` — full structured resume
- `PUT /admin/api/resume/experience` — work history
- `PUT /admin/api/resume/skills` — skill groups
- `PUT /admin/api/resume/education` — education
- `PUT /admin/api/resume/certifications` — certs and status
- `GET /api/v1/resume/pdf` — download PDF (generated with WeasyPrint or ReportLab)

### Frontend
- Admin: Resume editor (tabbed: Experience / Skills / Education / Certifications)
- Admin: Drag-to-reorder within each section
- Public: Replace `src/data/resume.ts` with React Query fetch
- Public: "Download PDF" button linking to `/api/v1/resume/pdf`

### Definition of done
- Admin adds a new job entry — appears on `/resume` immediately
- PDF download works

---

## Sprint 7 — Case Studies CMS

**Goal:** Write deep-dive case studies for projects from the admin, linked to a project entry.

### Backend
- `case_studies` table (linked to `projects`) + migration 0008
- Full CRUD: `GET/POST/PUT/DELETE /admin/api/case-studies`
- `PATCH /admin/api/case-studies/{id}/publish`
- `GET /api/v1/projects/{slug}/case-study` — public case study

### Frontend
- Admin: Case study editor (sections: problem, architecture, decisions, challenges, lessons)
- Admin: Architecture component builder (visual diagram nodes)
- Public: Replace `src/data/case-studies.ts` with API fetch
- Public: Individual case study page (`/work/:slug/case-study`)

### Definition of done
- Admin writes a case study for a project and publishes it
- Case study accessible via the project detail page

---

## Sprint 8 — Privacy-First Analytics

**Goal:** Know who is visiting and what they are reading, without Google Analytics or a cookie banner.

### Backend
- `page_views` table + migration 0009
- `POST /api/v1/analytics/view` — record a page view (public, rate-limited per session)
- `GET /admin/api/analytics/summary` — total views, uniques, top pages (7d/30d/all)
- `GET /admin/api/analytics/pages` — page view breakdown
- `GET /admin/api/analytics/referrers` — traffic sources
- `GET /admin/api/analytics/countries` — visitor countries
- Country derived from IP (MaxMind GeoLite2) — IP never stored

### Frontend
- Public: `useEffect` on route change to call `POST /api/v1/analytics/view`
- Admin: Analytics section with line chart (views over time)
- Admin: Top pages table, referrers list, country breakdown

### Definition of done
- Visiting any page records an anonymous view
- Admin sees a chart of daily views and a top-5 projects list

---

## Sprint 9 — Newsletter Subscriber Management

**Goal:** Collect and manage email addresses from interested visitors.

### Backend
- `newsletter_subscribers` table + migration 0010
- `POST /api/v1/newsletter/subscribe` — public subscribe (with duplicate check)
- `POST /api/v1/newsletter/unsubscribe` — unsubscribe via token
- `GET /admin/api/newsletter/subscribers` — admin list (paginated, searchable)
- `DELETE /admin/api/newsletter/subscribers/{id}` — GDPR removal

### Frontend
- Public: Newsletter capture widget (footer + article end)
- Admin: Subscribers list with count, source, date
- Admin: Export CSV button
- Email: Confirmation email on subscribe (using existing email service)

### Definition of done
- Visitor subscribes → gets a confirmation email
- Admin sees subscriber count and list

---

## Sprint 10 — Admin Dashboard Widgets

**Goal:** Replace the placeholder dashboard with a live overview of everything that matters.

### Backend
- `GET /admin/api/dashboard/summary` — single endpoint returning all counts
  (unread messages, total articles, analytics 7d, subscriber count)

### Frontend
- Dashboard: Unread messages count + latest message preview
- Dashboard: Most viewed project this week
- Dashboard: Most read article this week
- Dashboard: Newsletter subscriber count
- Dashboard: Availability toggle (inline)
- Dashboard: Recent activity log (last 5 audit entries)
- Dashboard: System health (API uptime, DB connected)
- All widgets use React Query with 60-second refresh

### Definition of done
- Opening the admin dashboard answers "What needs my attention?" in under 5 seconds

---

## Sprint 11 — SEO, Sitemap, and RSS Feed

**Goal:** Make the portfolio discoverable on Google and RSS readers.

### Backend
- `GET /api/v1/sitemap.xml` — dynamic sitemap (all published articles + projects + static pages)
- `GET /api/v1/feed.xml` — RSS 2.0 feed of published articles
- `GET /api/v1/feed.json` — JSON Feed format

### Frontend
- Add `<head>` meta tags to every page: `og:title`, `og:description`, `og:image`, `og:url`
- Add Twitter Card meta tags
- Add `<link rel="canonical">` on every page
- Add JSON-LD structured data: `Person` on homepage, `Article` on article pages, `BreadcrumbList` on project/article pages
- Submit sitemap to Google Search Console
- Add `<link rel="alternate" type="application/rss+xml">` in `<head>`

### Definition of done
- Google Search Console shows the sitemap indexed
- Article pages show rich previews when shared on LinkedIn/Twitter

---

## Sprint 12 — Core Web Vitals and Performance

**Goal:** Lighthouse score 95+ on all pages. Fast for every visitor.

### Frontend
- Lazy-load all admin routes (removes ~300 KB from initial bundle)
- Code-split by route: each page loads only what it needs
- Optimise images: WebP format, explicit `width`/`height`, lazy loading
- Preload critical fonts
- Defer non-critical scripts
- Add `loading="lazy"` to below-fold images
- Review and remove unused Tailwind classes (purge config)
- Add `<link rel="preconnect">` to API domain

### Backend
- Add `Cache-Control` headers on public read-only endpoints (articles, projects)
- ETags on article and project responses

### Definition of done
- Lighthouse Performance score ≥ 95 on homepage and article page
- LCP < 2.5 s on a throttled mobile connection
- JavaScript bundle < 400 KB gzipped

---

## Sprint 13 — Accessibility and Mobile Polish

**Goal:** Lighthouse accessibility score 100. Perfect experience on all screen sizes.

### Frontend
- Run `axe` accessibility audit on every page and fix all violations
- Ensure every interactive element has a visible focus ring
- Verify colour contrast ≥ 4.5:1 for all text
- Add `aria-live` regions for dynamic content (toast notifications, form feedback)
- Mobile audit at 375 px (iPhone SE) and 360 px (Android)
- Fix admin table horizontal scroll on mobile
- Fix any text overflow / truncation issues on small viewports

### Definition of done
- Lighthouse Accessibility score = 100 on homepage, article page, and admin pages
- Every page usable on a 375 px viewport without horizontal scroll

---

## Sprint 14 — OG Image Generation

**Goal:** Every shared link shows a professional branded preview image.

### Backend
- `GET /api/v1/og/article/{slug}.png` — OG image for article
- `GET /api/v1/og/project/{slug}.png` — OG image for project
- Images generated with Pillow: title text + category + brand logo on template
- Results cached (in-memory or S3) — only generated once per item

### Frontend
- Update `og:image` meta tags on article and project pages to point to the OG image endpoint

### Definition of done
- Sharing an article URL on LinkedIn shows a branded card with the article title

---

## Sprint 15 — Contact Messages Enhancements

**Goal:** Polish the existing contact message admin with power features.

### Backend
- `POST /admin/api/contact-messages/bulk` — bulk status update (archive/delete multiple)
- `PATCH /admin/api/contact-messages/{id}/tag` — add/remove label (`hiring`, `collaboration`, `spam`)
- `POST /admin/api/contact-messages/{id}/notes` — add private note to a message
- `GET /admin/api/contact-messages/export` — download all messages as CSV
- Auto-classify incoming messages (rule-based): `hiring_inquiry`, `collaboration`, `spam`, `other`

### Frontend
- Checkbox column for bulk select
- Bulk action bar (archive N selected, delete N selected)
- Tags visible in list row and detail panel
- Notes section in detail dialog
- Export CSV button in list header

### Definition of done
- Admin can select 10 spam messages and delete them in two clicks
- Incoming hiring inquiries are automatically flagged with a badge

---

## Sprint 16 — Background Task Queue

**Goal:** Replace fire-and-forget tasks with a reliable, monitored queue.

### Backend
- Add ARQ (async task queue using Redis) or Celery
- Move email notification to a queued task with retry on failure
- Task: `send_contact_notification(contact_id)` — 3 retries, 5 min between retries
- Task: `generate_og_image(type, slug)` — background pre-generation on publish
- `GET /admin/api/tasks/status` — show pending/failed tasks

### Definition of done
- Contact notification email is queued, not fire-and-forget
- A failed email delivery is visible in the admin dashboard and retried

---

## Sprint 17 — Observability

**Goal:** Production-grade logging, metrics, and alerting. Demonstrates senior backend thinking.

### Backend
- Structured JSON logging on every request: `{method, path, status, duration_ms, request_id}`
- Correlation IDs — `X-Request-ID` header propagated through logs
- Prometheus metrics endpoint: `GET /metrics`
  - Request rate per endpoint
  - Error rate per endpoint
  - P50/P95/P99 response latency
  - Database pool utilisation
  - Active admin sessions
- Uptime monitoring (UptimeRobot or Better Uptime — free tier)
- Alert on error rate > 5% for 5 minutes

### Frontend
- "API status" indicator on the admin dashboard (green/yellow/red dot)
- Show uptime percentage on the public portfolio (optional: "99.9% uptime last 30 days")

### Definition of done
- Every production request leaves a structured log line
- Prometheus metrics visible at `/metrics`
- Alert fires if the API goes down

---

## Sprint 18 — AI Contact Classification (LLM)

**Goal:** Automatically understand what every contact message is about.

### Backend
- Replace rule-based classifier (Sprint 15) with LLM-backed classification
- Use Groq API (fast, cheap): classify message type, extract hiring intent, estimate priority
- Async: classification runs as a background task after message is saved
- Store: `contact_messages.classification` JSONB field
- `GET /admin/api/contact-messages` includes classification in response

### Frontend
- Classification badge visible in message list: `Hiring inquiry`, `Collaboration`, `Spam`
- Priority indicator: red for high-priority hiring inquiries
- Admin: One-click "draft reply" button — opens email client with AI-suggested opener

### Definition of done
- Every new contact message classified within 10 seconds of submission
- Classification visible in the admin list without opening the detail

---

## Sprint 19 — Ask Me Anything (RAG Chat Widget)

**Goal:** Visitors can ask questions about your experience and projects, answered by AI.

### Backend
- Vector embeddings for all projects, articles, resume entries (pgvector extension)
- `POST /api/v1/chat` — accepts a question, retrieves relevant context, calls LLM, returns answer
- Rate-limited: 5 questions per IP per hour
- Context sources: projects, articles, resume, availability

### Frontend
- Public: Chat button (bottom right of homepage)
- Chat dialog: typed question → streaming AI response
- Source citations: "Based on your Projects section" shown below answer

### Definition of done
- Visitor asks "What databases have you worked with?" and gets an accurate answer
- Response cites specific projects from the portfolio

---

## Sprint 20 — GitHub Activity and Live Indicators

**Goal:** Show that the portfolio is a live, maintained production system.

### Backend
- `GET /api/v1/github/activity` — fetch recent GitHub commits (public repos) via GitHub API
- Cache in Redis for 1 hour
- `GET /health` already exists — extend with uptime field
- `GET /api/v1/meta` — last deployed timestamp, version, total commits

### Frontend
- Homepage: "Last deployed X days ago" + version badge
- Homepage: Recent GitHub commit strip (last 5 commits across all repos)
- About page: Contribution graph embed or custom activity chart
- Admin dashboard: Repository stats widget

### Definition of done
- Homepage shows the last deployment date and a GitHub activity feed

---

## Sprint 21 — PDF Resume Generation

**Goal:** One-click download of a beautifully formatted PDF resume generated from the database.

### Backend
- `GET /api/v1/resume/pdf` — generate PDF from current resume data
- Use WeasyPrint (HTML → PDF) with a custom CSS template
- Cache the generated PDF until resume data changes

### Frontend
- Public: "Download Resume" button on `/resume` page
- Admin: "Regenerate PDF" button after editing resume entries

### Definition of done
- "Download Resume" generates a professional PDF matching the site design

---

## Sprint 22 — Full-Text Search

**Goal:** Visitors can search across all projects and articles with a single query.

### Backend
- PostgreSQL full-text search with `tsvector` + `tsquery`
- `GET /api/v1/search?q=fastapi` — returns matched projects and articles
- GIN index on `tsvector` columns for performance

### Frontend
- Search bar in the main navigation (⌘K / Ctrl+K keyboard shortcut)
- Results grouped by type: Articles / Projects
- Highlight matched terms in results

### Definition of done
- Typing "SQLAlchemy" in the search bar returns relevant projects and articles

---

## Sprint 23 — Internationalisation (i18n) Foundation

**Goal:** Prepare the codebase for multi-language support without a full rewrite.

### Frontend
- Move all display strings to `src/i18n/en.ts` locale file
- Replace hardcoded strings in JSX with `t('key')` calls
- Use `Intl.DateTimeFormat` for all date formatting
- Add `lang="en"` to `<html>` and page-specific `lang` where needed

### Definition of done
- Adding a second language requires only a new locale file, no JSX changes

---

## Sprint 24 — E2E Tests for Critical Paths

**Goal:** Playwright tests covering the most important user and admin journeys.

### Tests to add
- Public: Homepage loads, shows projects and availability
- Public: Contact form submits successfully
- Public: Article page renders with correct content
- Admin: Login → navigate to contact messages → mark as read
- Admin: Login → publish an article → verify visible on public site
- Admin: Login → change availability → verify banner appears on homepage

### Definition of done
- E2E suite runs in CI on every PR to `main`
- All 6 critical paths covered

---

## Sprint Summary table

| Sprint | Name | Category | Effort |
|---|---|---|---|
| ✅ 1 | Admin Authentication | Security | Done |
| ✅ 2 | Admin Contact Messages | Content ops | Done |
| 3 | Articles CMS | Content | Large |
| 4 | Projects CMS + Availability | Content | Large |
| 5 | Site Settings + Profile | Content | Small |
| 6 | Resume CMS | Content | Medium |
| 7 | Case Studies CMS | Content | Medium |
| 8 | Privacy-First Analytics | Growth | Medium |
| 9 | Newsletter Subscriber Management | Growth | Medium |
| 10 | Admin Dashboard Widgets | Admin UX | Medium |
| 11 | SEO + Sitemap + RSS Feed | Discoverability | Medium |
| 12 | Core Web Vitals + Performance | Quality | Medium |
| 13 | Accessibility + Mobile Polish | Quality | Medium |
| 14 | OG Image Generation | Discoverability | Small |
| 15 | Contact Messages Enhancements | Admin UX | Medium |
| 16 | Background Task Queue | Backend | Medium |
| 17 | Observability (Logging + Metrics) | Backend | Large |
| 18 | AI Contact Classification | AI | Small |
| 19 | Ask Me Anything (RAG Chat) | AI | Large |
| 20 | GitHub Activity + Live Indicators | Credibility | Small |
| 21 | PDF Resume Generation | Content | Small |
| 22 | Full-Text Search | UX | Medium |
| 23 | i18n Foundation | Quality | Small |
| 24 | E2E Tests for Critical Paths | Quality | Medium |

---

## Priority order (recommended)

```
Immediate (highest ROI)      Sprints 3, 4, 5
Content foundation            Sprints 6, 7
Growth                        Sprints 8, 9, 10
Discoverability               Sprints 11, 14
Quality + Performance         Sprints 12, 13
Admin polish                  Sprints 15, 10
Backend excellence            Sprints 16, 17
AI features                   Sprints 18, 19
Credibility signals           Sprint 20
Content tooling               Sprint 21, 22
Foundation                    Sprints 23, 24
```
