# Miscellaneous Features — Everything Not Yet Covered

Features that don't fit neatly into the main sprint roadmap or
specific system plans, but belong in a world-class portfolio project.

---

## Security & Auth extras

### Two-factor authentication (2FA) for admin login
- TOTP authenticator app support (Google Authenticator, Authy)
- Backup codes (one-time use, generated at setup)
- Recovery flow if authenticator is lost
- `admin_totp_secret` stored encrypted in `site_settings`
- Admin sees: "Scan QR code with your authenticator app"
- Every login requires: email + password + 6-digit code

### Admin session visibility
- See all active sessions: device, IP, location, last active
- Revoke individual sessions
- "Sign out all other devices" button
- Session count shown in admin nav (already partially built in Sprint 1)

### API key management
- Generate API keys for programmatic access to the portfolio API
- Set key permissions (read-only vs read-write)
- Key expiry dates
- Last used timestamp per key
- Revoke keys instantly

---

## Content features

### Article series
- Group related articles into a named series (e.g. "Building a FastAPI Backend — 5 parts")
- Series landing page with part-by-part navigation
- "Part 2 of 5" indicator on each article
- Series shown on writing page as a grouped unit

### Content scheduler
- Set a future publish date on any article or project
- Backend runs a scheduled job to publish at the set time
- Admin sees a calendar view of scheduled content
- "Going live in 3 days" indicator on draft articles

### Content tags and cross-linking
- Tags across all content types: articles, projects, case studies
- Tag page: `/tag/fastapi` shows all articles + projects tagged FastAPI
- Related content block at the bottom of each article/project
- Most popular tags shown on the writing page

### Table of contents (auto-generated)
- For articles over 1000 words, auto-extract headings (H2, H3)
- Sticky sidebar TOC on desktop
- Smooth scroll to section on click
- Active section highlighted as you scroll

### Reading progress bar
- Thin bar at the top of the page filling as you scroll through an article
- Already mentioned in Sprint 3 — make it a reusable component

### Article views counter (public)
- Show view count on article cards: "1.2k views"
- Incremented by the analytics system (Sprint 8)
- Shown on the article detail page too

### Draft preview links
- Share a secret preview URL of a draft article before publishing
- URL: `/preview/article/{secret-token}`
- Token expires in 7 days
- Useful for asking someone to proofread before publishing

### Diagram support in articles (Mermaid)
- Mermaid.js rendered in article body
- Supported diagram types: flowchart, sequence, ER diagram, Gantt
- Admin can write diagram code in the editor with a live preview

### Math support in articles (KaTeX)
- LaTeX math notation rendered in articles
- Inline math: `$O(n \log n)$`
- Block math: `$$\sum_{i=1}^n$$`
- Useful for algorithm analysis articles

### Code playground embed
- Embed a live interactive code snippet in an article
- Powered by CodeSandbox embed API or StackBlitz
- One-line syntax in Markdown: `[playground src="url"]`

### Article import from Medium / Dev.to
- Paste a Medium or Dev.to article URL
- System fetches the content and imports it as a draft
- Admin reviews and edits before publishing
- Original source credited at the bottom

### Speaking and talks section
- `/speaking` page listing conference talks, meetup presentations, podcast appearances
- Fields: event name, date, topic, location, recording URL, slides URL
- Backend-driven (admin-managed)
- Featured talk on the homepage

### Reading list / book recommendations
- `/reading` page with books that shaped your engineering thinking
- Categories: System Design, Backend Engineering, AI, Career, General
- Fields: title, author, year read, one-line take, Amazon/Goodreads link
- "Currently reading" indicator

---

## Site infrastructure

### 301 Redirect manager
- Admin creates redirect rules: `/old-path` → `/new-path`
- Useful when you rename an article slug or restructure the site
- Applied in Vercel `vercel.json` or a custom Next.js redirect
- Prevents broken links after URL changes

### 404 analytics
- Track which 404 pages are hit most
- Shows: path that returned 404, referrer, count, last hit
- Admin can create a redirect from the 404 analytics page (one click)
- Helps find broken external links pointing to your site

### Portfolio health check
- Scheduled job (weekly): check all external links in articles and projects
- Report: broken links, slow-loading links, redirecting links
- Admin sees: "3 broken links found this week"

### Content changelog (public)
- `/changelog` page — public log of major portfolio updates
- "July 2026 — Added contact messages admin panel"
- "June 2026 — Published first article on JWT auth"
- Shows the portfolio is actively maintained and evolving

### Status page
- `/status` — simple uptime page
- Shows: API status (up/down), database status, last incident
- Uptime % last 30/90 days
- Powered by UptimeRobot (free tier) or custom health check polling

### Print CSS for resume and articles
- `/resume` page prints cleanly with no nav, no sidebar, no dark background
- Articles print as clean readable text
- Print-specific CSS: `@media print { .no-print { display: none } }`
- "Print / Save as PDF" button on resume page

### QR code for portfolio
- Generate a QR code linking to `brensaud.com`
- Useful for business cards, conference name badges, printed materials
- Admin can download as PNG or SVG
- `GET /admin/api/site/qr-code` endpoint using `qrcode` Python library

---

## UX features

### Keyboard shortcuts (public site)
- `⌘K` / `Ctrl+K` — open global search
- `G H` — go to home
- `G W` — go to work/projects
- `G A` — go to about
- `G C` — go to contact
- `?` — show keyboard shortcut reference

### Social sharing on articles and projects
- Share buttons: LinkedIn, Twitter/X, copy link
- Clean share preview: title + summary
- `/share/article/{slug}` redirect endpoint for tracking shares

### Estimated reading time on article cards
- Shown on article list cards and at the top of each article
- Calculated from word count: `ceil(words / 200)` minutes
- Already a field in the articles schema — show it everywhere

### Dark / light mode toggle (public site)
- Toggle button in the public navbar (already has dark mode in design system)
- User preference saved to `localStorage`
- System preference respected by default
- CSS transitions between modes

### Related articles / "You might also like"
- At the bottom of each article: 2–3 related articles
- Similarity based on: shared tags, same category, recency
- Prevents visitors from leaving after one article

### Article newsletter subscribe prompt
- After reading 75% of an article: slide-in "Enjoyed this? Subscribe for more"
- Not intrusive — appears once per session
- Links to newsletter subscribe form

### Scroll to top button
- Appears after scrolling 300px down on long pages
- Smooth scroll to top of page
- Accessible (keyboard focusable, aria-label)

---

## Notifications and integrations

### Admin email notifications
- Email when a new contact message arrives
- Email when newsletter subscriber count hits a milestone (100, 500, 1000)
- Email when any API endpoint returns 5xx errors repeatedly
- Email digest: weekly summary of contact messages + analytics

### Slack / Discord webhook notifications
- Send a Slack/Discord message when:
  - New contact message received
  - New newsletter subscriber
  - Article published
- Simple webhook: `POST https://hooks.slack.com/...`
- Admin configures the webhook URL in settings

### Zapier / Make (Integromat) webhook
- `POST /api/v1/webhooks/contact-message` — triggered on new message
- Enables: save to Google Sheets, notify via SMS, add to CRM
- Documented in the portfolio API docs

---

## Portfolio discoverability extras

### Open Graph card previewer
- Admin tool: paste any URL to see how the OG card looks
- Validates that og:title, og:description, og:image are all set
- Shows Twitter Card preview + LinkedIn preview side-by-side

### Google Search Console integration
- Verify domain ownership via DNS TXT record
- Submit sitemap via `GET /api/v1/sitemap.xml`
- View search performance inside the admin analytics section

### Schema.org JSON-LD types to add
- `Person` — on homepage
- `Article` — on each article page
- `BreadcrumbList` — on project and article pages
- `WebSite` with `SearchAction` — enables Google Sitelinks search box
- `CreativeWork` — on project pages

---

## Developer experience

### `Makefile` / task runner
- `make dev` — start backend + frontend
- `make test` — run all tests
- `make lint` — lint + format check
- `make migrate` — run pending Alembic migrations
- `make seed` — seed local DB with sample data
- `make reset-db` — drop + recreate DB

### Sample data seeder
- Seed command for local dev: `python -m app.cli.seed`
- Creates: 5 contact messages, 3 articles (1 published, 2 draft), 3 projects, availability=open
- Allows testing the admin panel without manually creating data
- Uses realistic but clearly fake data (no real PII)

### `CHANGELOG.md` in the repo
- Track all notable changes per version
- Format: Keep a Changelog (keepachangelog.com)
- Linked from the README
- Updated on every meaningful PR

### OpenAPI spec download
- `GET /openapi.json` — already exists in FastAPI
- Host a Redoc or Stoplight-style API reference page
- Public URL: `api.brensaud.com/docs`

### Architecture decision records (ADRs)
- `docs/adr/` folder in the repo
- One markdown file per major decision: ADR-001, ADR-002...
- Format: Title / Status / Context / Decision / Consequences
- Examples:
  - ADR-001: Why HTTPOnly cookies over Bearer tokens
  - ADR-002: Why repository pattern over direct SQLAlchemy in routes
  - ADR-003: Why Neon over self-hosted PostgreSQL
  - ADR-004: Why async FastAPI over Django REST Framework

---

## Analytics extras

### UTM parameter tracking
- Track traffic from campaigns: `?utm_source=linkedin&utm_medium=post&utm_campaign=article1`
- Store UTM parameters in the analytics table
- Admin sees: "32 visitors from your LinkedIn post last week"

### Funnel visualisation
- Homepage → Article → Contact form → Submission
- Show conversion rate at each step
- "3.2% of homepage visitors submit the contact form"

### Heatmap (lightweight)
- Track click positions on the homepage
- Show which projects get the most clicks
- No external service — simple click coordinate logging

---

## Mobile and PWA

### Progressive Web App (PWA)
- Service worker for offline support
- `manifest.json` with app name, icons, theme colour
- "Add to Home Screen" on mobile
- Offline: show cached article list and last-viewed article

### Mobile admin app (future, React Native)
- View and respond to contact messages from phone
- Toggle availability status
- Approve newsletter subscribers
- Basic analytics glance

---

## Monetisation / Growth (optional, future)

### Sponsor / support button
- "Buy me a coffee" or GitHub Sponsors link in the footer
- Or a custom "support my work" page with Stripe payment
- Useful once the blog gains readership

### Premium content (gated articles)
- Some deep-dive articles behind an email gate
- User enters email → gets access link → subscribes to newsletter
- No paywall — email-only

### Affiliate links in articles
- Disclose affiliate links clearly
- Track clicks on affiliate links separately
- Common for: book recommendations, tool recommendations

---

## Summary — features by priority

### Do these immediately (no backend needed)
- Print CSS for resume and articles
- Scroll to top button
- Dark/light mode toggle persistence (`localStorage`)
- Social share buttons on articles
- Keyboard shortcuts
- `make dev` / `Makefile`

### Add with next sprint
- Estimated reading time shown on cards (schema already has it)
- Related articles block
- Sample data seeder (`python -m app.cli.seed`)
- CHANGELOG.md
- Architecture Decision Records (ADRs folder)
- Article newsletter subscribe prompt

### Medium-term
- 2FA for admin login
- Content scheduler
- Article series support
- Diagram support (Mermaid)
- Table of contents
- 404 analytics
- Redirect manager
- Admin email notifications
- Slack/Discord webhooks
- Status page

### Long-term
- PWA support
- QR code generator
- Portfolio health check
- Code playground embeds
- Mobile admin app
