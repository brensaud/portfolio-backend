# Portfolio Management SaaS — Complete Feature List

A multi-tenant SaaS platform that gives every developer, engineer,
and technical professional their own intelligent portfolio site,
AI-powered resume system, and career management tool.

**Product name idea:** DevFolio / CraftCV / PortfolioOS / LaunchPad
**Target market:** Software engineers, backend/frontend devs, ML engineers, designers
**Core value:** Paste a job description → AI-tailored resume → tracked application → interview prep. All in one place.

---

## Positioning

```
Current tools developers use (4–6 separate products):
  Webflow / Framer     → portfolio site
  Enhancv / Kickresume → resume PDF builder
  Teal / Huntr         → job application tracker
  ChatGPT              → resume tailoring (manual)
  LinkedIn             → profile + network
  Google Sheets        → job tracking spreadsheet

This product replaces all of them.
```

---

## Module 1 — User Accounts & Authentication

### Registration and onboarding
- Sign up with email + password
- Email verification on registration
- Onboarding wizard: choose subdomain → import LinkedIn → set up profile
- OAuth sign-up: "Continue with GitHub" / "Continue with Google"
- Magic link login (passwordless option)
- Password reset via email
- Two-factor authentication (TOTP authenticator app)
- Backup codes for 2FA recovery

### Account management
- Change email address (with re-verification)
- Change password
- Delete account (with data export first)
- Export all data as ZIP (GDPR compliance)
- Account deactivation (pause without deleting)
- Session management: see all active devices, revoke any session
- Login history: last 10 logins with IP and device

### Admin / platform management (internal)
- Platform owner dashboard: user count, MRR, churn
- Impersonate any user (support tool)
- Suspend / ban accounts
- Manual plan upgrades

---

## Module 2 — Billing & Subscriptions

### Pricing tiers
```
Free tier (always free):
  - 1 portfolio site (subdomain only)
  - Resume CMS (no AI tailoring)
  - 5 contact messages/month
  - 3 projects
  - 5 articles
  - Basic analytics
  - Watermark: "Powered by [Product]"

Pro tier ($19/month or $190/year):
  - Everything in Free
  - Unlimited AI resume tailoring
  - Unlimited projects + articles
  - Custom domain support
  - Remove watermark
  - Job management system (full)
  - LinkedIn import
  - Advanced analytics
  - PDF generation (styled + ATS-clean)
  - Cover letter AI
  - Priority support

Lifetime deal ($299 one-time):
  - Everything in Pro forever
  - Early adopter pricing (first 500 users)
  - Name in credits / changelog

Agency tier ($99/month):
  - Up to 10 sub-accounts
  - Manage portfolios for clients
  - White-label (custom branding)
  - Dedicated support
```

### Billing features
- Stripe integration for payments
- Monthly and annual billing (annual = 2 months free)
- Upgrade / downgrade plan
- Cancel subscription (immediate or end of period)
- Billing history and invoice download
- Receipt emails on each charge
- Free trial: 14 days Pro (no credit card required)
- Promo codes and discount support
- Refund within 7 days (no questions asked)
- Usage-based add-ons: extra AI credits, extra custom domains

---

## Module 3 — Portfolio Site

### Site structure
- Automatic subdomain: `username.yoursaas.com`
- Custom domain support (Pro): `brensaud.com`
- SSL certificate: auto-issued and renewed (Let's Encrypt wildcard)
- Pages: Home / About / Work / Writing / Resume / Contact / Architecture
- Mobile-responsive on all pages
- Dark mode / light mode toggle (user preference saved)
- SEO: meta tags, OG images, JSON-LD structured data, sitemap, canonical URLs
- Performance: Core Web Vitals optimised, Lighthouse 95+

### Homepage
- Hero section: name, headline, availability status, avatar
- Featured projects (admin selects which appear)
- Featured articles (most recent published)
- Open to work banner (admin toggles)
- Call to action: "View my work" / "Get in touch"

### Work / Projects page
- Grid of project cards
- Filter by category (Backend / AI / SaaS / DevOps / etc.)
- Individual project page: `/work/{slug}`
- Project detail: description, tech stack, links, case study link

### Writing / Blog page
- Article list with category filters
- Individual article page: `/writing/{slug}`
- Reading progress bar
- Table of contents (auto-generated for articles > 1000 words)
- Related articles at the bottom
- Estimated reading time shown on cards
- Social share buttons: LinkedIn / Twitter / copy link
- Newsletter subscribe prompt (after reading 75%)

### Resume page
- Full structured resume from CMS
- Download PDF button (styled version)
- Download ATS-clean PDF button
- Print-clean CSS

### Contact page
- Contact form (name, email, subject, message)
- Rate-limited (5 per IP per hour)
- Social links: GitHub, LinkedIn, Twitter/X, email
- "Open to work" status with availability message

### About page
- Bio paragraphs
- Skills and tools
- Current availability
- Location and timezone

### Architecture page (optional)
- System architecture diagrams
- For engineers who want to showcase system design thinking

### Site customisation
- Accent colour picker (within brand constraints)
- Avatar upload
- Cover image / banner per page
- Font choice: system / Inter / JetBrains Mono
- Section order (drag to reorder homepage sections)
- Show / hide individual sections

---

## Module 4 — Content CMS

### Projects CMS
- Create / edit / delete projects
- Fields: title, slug, subtitle, description, category, status, tech stack, links
- Upload project thumbnail image
- Drag-to-reorder projects
- Featured flag (shows on homepage)
- Draft / published / archived status
- Linked case study (optional)

### Articles CMS
- Rich Markdown editor with preview pane
- Syntax highlighting for code blocks
- Image upload with drag-and-drop
- Draft / published / archived / scheduled status
- Schedule future publish with date/time picker
- Tags and categories
- Article series: group related articles
- Diagram support: Mermaid.js rendered inline
- Math support: KaTeX for LaTeX notation
- Table of contents auto-generated from headings
- Reading time auto-calculated from word count
- SEO: custom meta title + description per article
- OG image: auto-generated or upload custom
- Import article from URL (Medium / Dev.to)

### Case Studies CMS
- Linked to a project
- Structured sections: Problem / Architecture / Decisions / Challenges / Lessons
- Architecture diagram builder (node-based)
- Code snippet support with syntax highlighting
- Publish independently of the project

### Availability toggle
- Status: Open / Not looking / Open to conversations
- Available from date
- Availability message (shown on homepage and contact page)
- Preferred work type: remote / hybrid / on-site / any
- Notice period

### Site settings
- Profile: display name, headline, bio, location, timezone
- Social links: GitHub, LinkedIn, Twitter/X, email
- Password change
- Notification preferences

---

## Module 5 — Resume System (AI-powered)

### Resume CMS
- Sections: Profile / Experience / Skills / Education / Certifications
- Drag-to-reorder within each section
- All fields editable inline
- Changelog: last updated date per section
- Freshness alerts: "skills section 90 days old"

### PDF generation
- Styled PDF (branded, matches portfolio design)
- ATS-clean PDF (plain, maximum compatibility)
- LaTeX engine: XeLaTeX for typographic quality
- Template selector: Jake's / AltaCV / Custom
- Generated on demand, cached until data changes
- Preview in browser before download

### Tailored resume versions
- Create versions targeting specific roles / companies
- Each version: headline override, summary override, bullet overrides, skills reorder
- Version status: draft / ready / sent / archived
- Download PDF for any version
- Version diff viewer: side-by-side changes vs master

### AI tailoring
- Paste a job description → AI generates a tailored version
- Side-by-side diff: master vs AI suggestion
- Accept / edit / reject each change individually
- Saves as a new version linked to the job
- LLM provider: Groq (fast + cheap) / OpenAI fallback

### ATS score analyser
- Score 0–100: how well resume matches a JD
- Keyword coverage, missing required terms, skills gap
- Bullet point feedback: weak verbs flagged
- Suggestions: specific actionable improvements

### Cover letter builder (AI)
- AI generates from: resume version + JD + company context
- 3-paragraph structure
- Tone selector: formal / conversational
- Editable in rich text editor
- Download as PDF
- Copy as plain text

### Bullet point strength scorer
- Per-bullet score: action verb, quantification, specificity, length
- Flags weak verbs ("helped", "worked on", "responsible for")
- Suggests rewrites

### Skills gap analysis
- Paste 3–5 target JDs
- AI identifies: skills you have, skills to learn, priority order
- "Quick wins" vs "big bets"

### Salary intelligence
- Market rate estimates (P25/P50/P75/P90) per role
- Compare your ask vs market
- Update recommendation

### Interview question generator
- Based on resume version + JD
- Technical / behavioural / system design / project deep-dive questions
- Each question has: why likely, suggested answer direction

---

## Module 6 — Job Management System

### Job Board
- Save jobs: URL paste (auto-scrape) / screenshot (OCR) / text paste (AI parse)
- JD snapshot saved permanently (even after posting is deleted)
- AI extracts structured signals: role, skills, seniority, culture
- Kanban: Saved / Applied / In Progress / Closed
- Tags, priority, deadline tracking
- Job fit score (resume vs JD)
- One-click "Tailor resume for this job"

### Application Tracker
- Full pipeline: Applied → Screen → Interview → Offer → Decision
- Resume version locked at apply time
- Cover letter linked
- Follow-up reminders
- Ghosted tracker (no response in 21 days)
- Rejection stage logging
- Source tracking: job board / LinkedIn / referral / cold outreach

### Company Intelligence
- Company profile: size, stage, stack, culture, blog, Glassdoor, Levels.fyi
- Known interview process notes
- Salary ranges observed
- Red flags field
- Rate interview process after completion

### Interview Manager
- Schedule: date, time, format, type, interviewer names
- Pre-interview prep checklist
- Post-interview notes and rating
- Question bank: all questions ever asked (searchable)
- Thank-you email reminder
- "Waiting for feedback" countdown

### Offer Manager
- Total comp calculator: base + bonus + equity + benefits
- Side-by-side offer comparison
- Negotiation tracker: initial → counter → final
- Offer deadline countdown
- Accept / decline logging

### Contact / Network Manager
- Store: recruiters, hiring managers, referrers, peers
- Follow-up reminders per contact
- Response rate per recruiter
- LinkedIn connection status
- Referral request tracker

### Document Vault
- All resume versions and cover letters
- Custom document uploads
- Per-application document package (one-click ZIP)
- Document version history

### Communication Log
- Log emails, calls, LinkedIn messages
- Email template library (follow-up, thank-you, decline)
- AI email drafts
- "No communication in 5 days" reminder

### Job Search Analytics
- Application funnel: apply → screen → interview → offer
- Response rate by source
- Rejection stage analysis
- Offer rate by company size
- Average time to offer

---

## Module 7 — Analytics

### Site analytics
- Page views per day / week / month (privacy-first, no Google Analytics)
- Top pages, top projects, top articles
- Traffic sources (referrer domain only)
- Visitor countries
- Download tracking (resume PDF)

### Content analytics
- Article view counts (public)
- Article read rate (% who read to end)
- Most clicked projects
- Newsletter conversion rate

### LinkedIn analytics
- Profile views (via export or session scrape)
- Search appearances
- Top keywords recruiters use to find you

---

## Module 8 — LinkedIn Integration

- Import via GDPR data export ZIP
- Scrape your own public profile (Playwright)
- Fields imported: experience, education, skills, certifications, projects, recommendations
- AI reformats prose bullets → action-verb bullets
- AI categorises flat skills into groups
- Conflict resolution (what to overwrite vs skip)
- Sync reminder every 90 days

---

## Module 9 — Newsletter & Subscribers

- Subscribe widget on public portfolio (footer + article end)
- Double opt-in (confirmation email)
- Subscriber list: email, source, date
- Export as CSV
- Unsubscribe via token (GDPR)
- Subscriber count on admin dashboard
- Integration: export list to Mailchimp / Resend for sending

---

## Module 10 — Notifications & Integrations

- Email: new contact message, new subscriber, error alerts
- Slack/Discord webhook
- Zapier webhook (outbound)
- Weekly digest email summary
- Google Search Console: submit sitemap, view indexing status

---

## Module 11 — Platform Infrastructure (multi-tenant)

### Tenant isolation
- All data scoped to `user_id` on every table
- Row-level security in PostgreSQL
- No data leakage between tenants

### Subdomain routing
- `username.yoursaas.com` per user
- Nginx wildcard SSL: `*.yoursaas.com`
- Custom domain: CNAME validation, SSL auto-issue

### Feature flags
- Enable/disable features per plan tier
- A/B test new features with % rollout
- Kill switch for problematic features

### Rate limiting
- Per-user API rate limits (not just per IP)
- AI usage limits per plan tier
- Contact form rate limiting per site visitor

### Storage
- Image uploads: S3 or Cloudflare R2 per tenant
- PDF storage: per-user prefix
- Max storage per plan: 100 MB free / 5 GB pro

---

## Module 12 — Developer-facing features

### Public portfolio API
- `GET /api/v1/{username}/projects` — public projects
- `GET /api/v1/{username}/articles` — published articles
- `GET /api/v1/{username}/resume` — structured resume
- Allows third-party integrations with a user's portfolio data

### Webhooks (outbound)
- `contact.message.received` — new contact form submission
- `article.published` — new article published
- `resume.version.created` — new resume version

### OpenAPI spec
- Each user's API documented at `api.yoursaas.com/{username}/docs`

---

## Module 13 — AI Credit System

- AI features consume credits
- Free plan: 10 credits/month
- Pro plan: 200 credits/month
- Lifetime: 500 credits/month
- Credit costs:
  - Resume tailor: 5 credits
  - ATS score: 2 credits
  - Cover letter: 3 credits
  - Interview prep: 4 credits
  - JD analysis: 1 credit
  - Skills gap: 3 credits
- Buy additional credits: $5 for 50 credits
- Credit usage history in billing settings

---

## Technical changes from single-user to multi-tenant

### Database (current → SaaS)

| Current | Multi-tenant |
|---|---|
| No users table | `users` table with plan, subscription, subdomain |
| Single admin auth | Per-user auth (email/password + OAuth) |
| All tables global | All tables get `user_id` FK |
| Single Redis namespace | Per-user Redis key prefix: `user:{id}:...` |
| Single JWT secret | Per-user JWT signing or shared with `sub` = user ID |
| One `.env` for admin creds | Admin credentials derived from user record |

### New tables required

```sql
users                    -- accounts and plan info
subscriptions            -- Stripe subscription records
payment_history          -- invoice log
api_keys                 -- programmatic access keys
user_domains             -- custom domain records
feature_flags            -- per-user feature overrides
ai_credit_usage          -- track AI credit consumption
webhook_endpoints        -- user-configured webhooks
email_verifications      -- pending email verifications
password_reset_tokens    -- password reset flow
totp_secrets             -- 2FA configuration
```

### New backend services

```python
UserService          -- registration, login, profile
BillingService       -- Stripe webhooks, plan changes
TenantService        -- subdomain routing, isolation
DomainService        -- custom domain validation + SSL
AICreditsService     -- credit tracking + enforcement
WebhookService       -- outbound webhook delivery
EmailService         -- transactional emails (verify, reset, notify)
StorageService       -- per-tenant S3/R2 file handling
FeatureFlagService   -- plan-based feature gating
```

---

## Go-to-market plan

### Phase 1 — Validate (before building multi-tenancy)
- Finish your own portfolio as the proof of concept
- Write 2–3 articles about what you built
- Add a "Want this for your portfolio?" email capture on the site
- Target: 200 waitlist signups before building

### Phase 2 — Early access
- Build multi-tenancy (estimated 8–12 weeks)
- Invite waitlist in batches of 50
- Lifetime deal: $149 for first 100 users, $199 for next 400
- Gather feedback aggressively

### Phase 3 — Public launch
- Product Hunt launch
- Post on: Hacker News ("Show HN"), Reddit r/webdev r/devops
- Twitter/X thread: "I built a portfolio OS for engineers"
- Dev.to / Hashnode article
- Target: 500 paying users in 3 months

### Phase 4 — Growth
- SEO: "best developer portfolio builder", "AI resume tailoring"
- Referral program: 1 month free per referral
- Affiliate program: 20% recurring for 12 months
- Partner with bootcamps and CS programs

---

## Revenue model

```
Scenario: conservative growth

Month 1:   50 Pro users × $19   = $950 MRR
Month 3:  200 Pro users × $19   = $3,800 MRR
Month 6:  500 Pro users × $19   = $9,500 MRR
Month 12: 1000 Pro users × $19  = $19,000 MRR

Lifetime deals (first 500 users × $199) = $99,500 one-time

AI cost (Groq at $0.05/tailor, 10 tailors/user/month):
  1000 users × 10 tailors × $0.05 = $500/month
  Margin on AI: very high

Infrastructure (Render/Railway, Neon, Upstash, S3):
  1000 users: ~$200–400/month
```

---

## Unique selling points vs competition

| Feature | This product | Enhancv | Teal | Huntr | read.cv |
|---|---|---|---|---|---|
| Portfolio website | ✅ | ❌ | ❌ | ❌ | ✅ |
| Resume CMS | ✅ | ✅ | ✅ | ❌ | ❌ |
| AI resume tailoring | ✅ | Basic | ❌ | ❌ | ❌ |
| ATS score analyser | ✅ | ❌ | ✅ | ❌ | ❌ |
| Job tracker | ✅ | ❌ | ✅ | ✅ | ❌ |
| Interview prep (AI) | ✅ | ❌ | ❌ | ❌ | ❌ |
| Cover letter AI | ✅ | Basic | ❌ | ❌ | ❌ |
| LinkedIn import | ✅ | ❌ | ✅ | ❌ | ❌ |
| Blog / articles | ✅ | ❌ | ❌ | ❌ | ❌ |
| Custom domain | ✅ | ❌ | ❌ | ❌ | Pro only |
| Price | $19/mo | $25/mo | $29/mo | $20/mo | Free |
