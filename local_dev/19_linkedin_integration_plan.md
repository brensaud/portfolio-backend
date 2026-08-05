# LinkedIn Data Integration Plan

A complete plan to pull information from your LinkedIn profile and
use it across the portfolio, resume system, and job management system.

---

## What LinkedIn has that this project needs

```
LinkedIn Profile
├── Identity        → Portfolio site (name, headline, bio, photo)
├── Experience      → Resume CMS (work history, highlights)
├── Education       → Resume CMS (degrees, institutions)
├── Skills          → Resume CMS (skills list)
├── Certifications  → Resume CMS (certs and status)
├── Projects        → Portfolio Projects CMS
├── Publications    → Portfolio Articles / Writing section
├── Recommendations → Portfolio Testimonials
├── Activity        → Portfolio Writing (LinkedIn articles)
├── Analytics       → Admin dashboard (profile views, post reach)
└── Connections     → Job Management contact network
```

---

## Three methods to get LinkedIn data

### Method 1 — LinkedIn Data Export (recommended, free, always works)

LinkedIn legally provides a full data export under GDPR.
Request it from Settings → Data Privacy → Get a copy of your data.

**Delivery:** ZIP file emailed within 10 minutes to 24 hours.

**What's included:**

| CSV file | Contents |
|---|---|
| `Profile.csv` | Name, headline, summary, location, industry |
| `Positions.csv` | Job title, company, dates, description |
| `Education.csv` | School, degree, field, dates |
| `Skills.csv` | All skills (no endorsement counts in export) |
| `Certifications.csv` | Name, authority, licence number, dates |
| `Projects.csv` | Title, description, URL, dates, contributors |
| `Publications.csv` | Title, publisher, date, description, URL |
| `Recommendations_Received.csv` | Author, role, company, recommendation text |
| `Recommendations_Given.csv` | — |
| `Connections.csv` | Name, company, position, connected date |
| `Articles.csv` | Published LinkedIn articles — title, URL, published date |
| `Posts.csv` | LinkedIn posts — content, published date, likes, comments |
| `Profile Views.csv` | Weekly profile view counts (last 90 days) |
| `Search Appearances.csv` | How you appeared in recruiter searches |

**Limitation:** No real-time data. Snapshot at time of export.
Re-import every time you update your LinkedIn.

---

### Method 2 — LinkedIn Public Profile Scrape (your own profile only)

Scrape your own public profile page for the most current data.

**URL format:** `https://linkedin.com/in/your-username`

**What can be extracted:** Everything visible on your public profile —
name, headline, summary, experience, education, skills, certifications,
featured projects, activity (recent posts).

**Tools:**
- `playwright` (headless browser — handles JavaScript-rendered content)
- `httpx` + `BeautifulSoup` (for static content)
- Claude Vision API (screenshot → structured data)

**Limitation:** LinkedIn's HTML structure changes. Scraper needs maintenance.
Rate limiting if run too frequently. Only works if profile is public.

---

### Method 3 — LinkedIn API (most reliable, requires approval)

LinkedIn offers two API products:

| API | Access | What you get |
|---|---|---|
| LinkedIn Sign-In (OAuth) | Free, immediate | Basic profile: name, photo, headline, email |
| LinkedIn Partner API | Application required, usually denied for individuals | Full profile data, connections, analytics |

**Reality check:** LinkedIn Partner API access is almost impossible for
individual developers. Use the export (Method 1) or scraping (Method 2) instead.

---

## What to extract and where it goes

### 1. Identity → Portfolio public site

| LinkedIn field | Maps to | Where used |
|---|---|---|
| First/last name | `resume_profile.name` | Homepage, about page, all pages |
| Headline | `resume_profile.headline` | Homepage hero, about page |
| Summary / About | `resume_profile.summary_paragraphs` | About page, resume page |
| Profile photo URL | `site_settings.avatar_url` | Avatar throughout site |
| Location | `site_settings.location` | About page, contact page |
| Custom LinkedIn URL | `site_settings.linkedin` | Social links |

**Admin action:** Import → review → confirm. These are your public-facing details.

---

### 2. Experience → Resume CMS

| LinkedIn field | Maps to | Notes |
|---|---|---|
| Title | `resume_experience.role` | Direct import |
| Company name | `resume_experience.company` | Also creates Company record in Job Mgmt |
| Start/end date | `resume_experience.start_date / end_date` | Date format normalised |
| Description | `resume_experience.highlights` | Split by newline into bullet array |
| Employment type | `resume_experience.employment_type` | Full-time / contract / freelance |
| Location | `resume_experience.location` | |

**AI enhancement on import:**
LinkedIn descriptions are often paragraph-style prose.
AI reformats them into strong action-verb bullet points automatically:

```
LinkedIn (prose):
  "I was responsible for building the backend API for the
   payments platform and worked closely with the frontend team..."

AI reformats to bullets:
  • Built backend API for payments platform using FastAPI + PostgreSQL
  • Collaborated with frontend team to define API contracts
  • [flag: no quantification found — add a number if possible]
```

---

### 3. Education → Resume CMS

| LinkedIn field | Maps to |
|---|---|
| School name | `resume_education.institution` |
| Degree name | `resume_education.degree` |
| Field of study | `resume_education.field` |
| Start/end year | `resume_education.start_year / end_year` |
| Grade / GPA | `resume_education.notes` |
| Activities | `resume_education.notes` |

---

### 4. Skills → Resume CMS

LinkedIn skills are flat (no categories).
AI groups them automatically:

```
LinkedIn skills (flat list):
  Python, FastAPI, PostgreSQL, Docker, React, Kubernetes,
  Machine Learning, Redis, TypeScript, GitHub Actions...

AI categorises:
  Backend:    Python, FastAPI, PostgreSQL, Redis
  AI/ML:      Machine Learning, LangChain
  Frontend:   React, TypeScript
  DevOps:     Docker, Kubernetes, GitHub Actions
  Databases:  PostgreSQL, Redis
```

Admin reviews the groupings before saving.

---

### 5. Certifications → Resume CMS

| LinkedIn field | Maps to |
|---|---|
| Name | `resume_certifications.title` |
| Issuing organisation | `resume_certifications.provider` |
| Issue date | `resume_certifications.completed_date` |
| Expiry date | `resume_certifications.expiry_date` |
| Credential ID | `resume_certifications.credential_id` |
| Credential URL | `resume_certifications.credential_url` |

---

### 6. Projects → Portfolio Projects CMS

| LinkedIn field | Maps to |
|---|---|
| Project name | `projects.title` |
| Description | `projects.description` |
| Project URL | `projects.links` |
| Start/end date | `projects.created_at` |
| Contributors | Notes field |

**Enhancement:** AI generates a `slug` from the title and a
`subtitle` (one-line tech description) from the description.

---

### 7. Recommendations → Testimonials

| LinkedIn field | Maps to |
|---|---|
| Recommender name | `testimonials.author_name` |
| Recommender headline | `testimonials.author_role` |
| Recommender company | `testimonials.company` |
| Recommendation text | `testimonials.body` |
| Date | `testimonials.created_at` |

All imported as `approved: false` — admin reviews before making public.

---

### 8. LinkedIn Articles → Portfolio Writing

| LinkedIn field | Maps to |
|---|---|
| Article title | `articles.title` (draft) |
| Article URL | `articles.linkedin_url` |
| Published date | `articles.published_at` |
| Article content | `articles.body` (if accessible) |

**Note:** LinkedIn article body text is accessible from the article page.
Import as drafts — admin decides whether to republish on the portfolio.

---

### 9. Activity / Posts → Writing inspiration

LinkedIn posts that performed well (many likes/comments) indicate
which topics your audience cares about most. Import as:

| LinkedIn post data | Used for |
|---|---|
| Post text | Article idea bank (topics that resonated) |
| Likes count | Signals strong content |
| Comments count | Signals discussion-worthy content |
| Published date | Recency filter |

**Admin view:** "Your top 5 performing LinkedIn posts — turn these into articles?"

---

### 10. Analytics → Admin dashboard

| LinkedIn field | Maps to |
|---|---|
| Profile views (weekly) | Admin dashboard widget |
| Search appearances | Admin dashboard widget |
| Post impressions | Writing analytics |
| Follower count | Profile stats |

**Dashboard widget:**
```
LinkedIn stats (last 7 days):
  Profile views:     342  (+18% vs last week)
  Search appearances: 67  (appeared in recruiter searches)
  Post impressions:  1.2k (last post)
```

---

### 11. Connections → Job Management contacts

| LinkedIn field | Maps to |
|---|---|
| Connection name | `contacts.name` |
| Connection headline | `contacts.role` |
| Connection company | `contacts.company` |
| Connected date | `contacts.connected_date` |

**Smart import:** Only import connections tagged as relevant to job search
(engineers, hiring managers, recruiters) — not every connection.

---

## Import workflow — step by step

### Phase A — Upload LinkedIn export ZIP

```
Admin → Settings → LinkedIn Import → Upload ZIP

System reads:
  ✅ Profile.csv          → identity fields
  ✅ Positions.csv         → 4 experience entries found
  ✅ Education.csv         → 2 education entries
  ✅ Skills.csv            → 24 skills
  ✅ Certifications.csv    → 3 certs
  ✅ Projects.csv          → 5 projects
  ✅ Recommendations_Received.csv → 2 recommendations
  ✅ Connections.csv       → 312 connections
  ⚠️  Articles.csv         → 0 articles (none published)
  ✅ Posts.csv             → 14 posts
  ✅ Profile Views.csv     → 90 days of data
```

---

### Phase B — Preview per section (review before saving)

Each section shows a diff — what will be added vs what already exists:

```
Experience import preview:
  ┌────────────────────────────────────────────────────┐
  │  NEW (3)          EXISTING (1)        CONFLICT (0) │
  ├────────────────────────────────────────────────────┤
  │  + Acme Corp                                       │
  │    Backend Engineer · Jan 2023 – Dec 2024          │
  │    3 bullets extracted from description            │
  │    ⚠️  Bullets are prose — AI reformatted          │
  │    [View original]  [View AI version]              │
  │                                                    │
  │  + Freelance Python Developer · 2021 – 2023        │
  │    2 bullets                                       │
  │                                                    │
  │  + Junior Developer @ StartupXYZ · 2020 – 2021     │
  │    1 bullet                                        │
  │                                                    │
  │  ✓ Portfolio Backend (already exists — skipped)    │
  └────────────────────────────────────────────────────┘
  [Import selected]  [Import all]  [Skip section]
```

---

### Phase C — AI enhancement pass

After import, AI runs an optional enhancement pass:

```
Enhancement options:
  □ Reformat prose descriptions into action-verb bullets
  □ Add missing quantification prompts (flag bullets with no numbers)
  □ Categorise skills into groups
  □ Generate slugs for imported projects
  □ Flag weak language ("responsible for", "helped with")

[Run enhancements]  [Skip — import as-is]
```

---

### Phase D — Sync strategy for future updates

Since LinkedIn export is a manual process, set a sync reminder:

```
LinkedIn sync settings:
  Last imported:  2026-07-06
  Next reminder:  2026-10-06 (90 days)

  Auto-remind when:
    ○ Every 90 days
    ○ After a new job role is added on LinkedIn
    ○ Manually only

  [Schedule reminder]
```

---

## Real-time LinkedIn scraping (advanced)

For users who want current data without waiting for an export:

### What gets scraped (your own public profile)

```python
class LinkedInProfileScraper:

    async def scrape_public_profile(self, linkedin_url: str) -> ProfileData:
        """
        Scrape public LinkedIn profile using Playwright.

        Extracts:
          - Headline and summary
          - Experience entries (current + past)
          - Education
          - Skills (top skills shown publicly)
          - Featured section (projects, posts, links)
          - Recent activity (last 5 posts)

        Note: Only scrape your own profile.
        Playwright renders the full JavaScript page before parsing.
        """

    async def get_post_analytics(self, post_url: str) -> PostAnalytics:
        """
        Get likes + comments count for a specific post.
        Requires being logged in — uses stored session cookies.
        """
```

### Session cookie approach (for analytics)

LinkedIn analytics are only visible when logged in.
Store your LinkedIn session cookies in the admin settings (encrypted).
The scraper uses these to access your analytics dashboard.

```
Admin → Settings → LinkedIn → Session
  LinkedIn session cookie: [paste cookie value]
  Last validated: 2026-07-06
  Status: ✅ Active

  ⚠️ Cookies expire every 30–90 days. Re-paste when analytics stop loading.
```

---

## Backend services

### `LinkedInImportService`

```python
class LinkedInImportService:

    async def parse_export_zip(self, zip_bytes: bytes) -> LinkedInExport:
        """Parse LinkedIn ZIP export into structured Python objects."""

    async def preview_import(
        self,
        export: LinkedInExport,
        existing_data: MasterResume,
    ) -> ImportPreview:
        """
        Compare export data with what already exists.
        Returns: new, existing, conflicts per section.
        """

    async def apply_import(
        self,
        preview: ImportPreview,
        selections: ImportSelections,
        enhance_with_ai: bool = True,
    ) -> ImportResult:
        """
        Write selected data to the database.
        Optionally runs AI enhancement pass.
        """

    async def enhance_bullets(
        self,
        bullets: list[str],
    ) -> list[EnhancedBullet]:
        """
        Reformat prose → action-verb bullets.
        Flag bullets missing quantification.
        """

    async def categorise_skills(
        self,
        skills: list[str],
    ) -> list[SkillGroup]:
        """Group flat skills list into named categories."""
```

### `LinkedInScraperService` (optional, advanced)

```python
class LinkedInScraperService:

    async def scrape_profile(self, url: str) -> ScrapedProfile:
        """Use Playwright to scrape public profile."""

    async def get_analytics(
        self,
        session_cookie: str,
    ) -> LinkedInAnalytics:
        """Fetch profile views and search appearances."""

    async def get_post_performance(
        self,
        session_cookie: str,
        days: int = 30,
    ) -> list[PostPerformance]:
        """Get impression and engagement data for recent posts."""
```

---

## Admin UI — LinkedIn section

```
Admin → Settings → LinkedIn

Tabs: Import | Analytics | Sync

── Import tab ──────────────────────────────────────────────
  Last import: Never

  Option A: Upload LinkedIn export ZIP
    [Choose file...]
    "Request your data at: linkedin.com/settings/data-privacy"

  Option B: Scrape current profile (requires public profile URL)
    LinkedIn URL: linkedin.com/in/brensaud
    [Scrape now]

  Option C: Session-based (for analytics)
    Session cookie: [••••••••••]
    [Validate]  [Clear]

── Analytics tab ────────────────────────────────────────────
  Profile views (last 7 days):   342  ↑18%
  Profile views (last 30 days):  1.2k
  Search appearances (7 days):    67
  Recruiter searches:             12 of 67

  Top search keywords:
    "Python backend engineer"     38 appearances
    "FastAPI developer"           19 appearances
    "AI engineer"                  8 appearances

  Where viewers work:
    Stripe · Google · Monzo · Goldman Sachs · Revolut

── Sync tab ─────────────────────────────────────────────────
  Last imported:  Never
  Remind me to re-import every: [90 days ▼]
  [Save reminder]
```

---

## Data mapping summary

| LinkedIn data | Portfolio destination | Priority |
|---|---|---|
| Name, headline, summary | Site settings, about page, resume | ⭐⭐⭐ High |
| Work experience | Resume CMS | ⭐⭐⭐ High |
| Education | Resume CMS | ⭐⭐⭐ High |
| Skills | Resume CMS | ⭐⭐⭐ High |
| Certifications | Resume CMS | ⭐⭐ Medium |
| Projects | Portfolio Projects CMS | ⭐⭐ Medium |
| Recommendations | Testimonials | ⭐⭐ Medium |
| Profile views (analytics) | Admin dashboard | ⭐⭐ Medium |
| Search appearances | Admin dashboard | ⭐⭐ Medium |
| LinkedIn articles | Writing / Blog | ⭐ Low |
| Posts (top performing) | Article idea bank | ⭐ Low |
| Connections | Job Mgmt contacts | ⭐ Low |
| Post impressions | Writing analytics | ⭐ Low |

---

## Limitations and honest notes

| Limitation | Detail |
|---|---|
| Export is a snapshot | Not live. Re-export when LinkedIn data changes. |
| No endorsement counts in export | Skills are a flat list with no popularity signal |
| Recommendations text is truncated in CSV | May need to copy full text manually |
| Article body not in export | Only title + URL — body requires scraping the article page |
| Analytics history max 90 days | LinkedIn only provides 90 days of profile view history |
| Scraper maintenance | LinkedIn HTML changes periodically — scraper may break |
| API access for individuals | LinkedIn Partner API is essentially unavailable |
| Photos | Profile photo URL is not in the export — download manually |

---

## Implementation phases

| Phase | Feature | Effort |
|---|---|---|
| Phase 1 | Parse LinkedIn export ZIP → resume CMS import | Medium |
| Phase 2 | AI bullet reformatter + skill categoriser | Small |
| Phase 3 | Projects import → portfolio CMS | Small |
| Phase 4 | Recommendations → testimonials | Small |
| Phase 5 | Public profile scraper (Playwright) | Medium |
| Phase 6 | Analytics dashboard (session cookie method) | Medium |
| Phase 7 | Post performance → article idea bank | Small |
| Phase 8 | Connections → job management contacts | Small |
