# World-Class Resume System — Complete Plan

A comprehensive plan for building an intelligent, AI-powered resume
management system inside the portfolio admin panel.

---

## Vision

> A resume that adapts to every opportunity — one master document that
> spawns tailored versions for specific roles, with AI handling the heavy
> lifting of matching your experience to what each employer is looking for.

---

## Current state

Resume lives in `src/data/resume.ts` — a static TypeScript file.
To update a job title or add a skill: edit the file, commit, wait for CI, redeploy.
No PDF. No tailoring. No tracking. No AI.

---

## What the system becomes

```
Admin Panel → Resume
├── Master Resume          ← the full truth — all experience, all skills
├── Tailored Versions      ← AI-adapted variants per role/company
├── Job Applications       ← track where each version was sent
├── AI Tailor              ← paste job description → get adapted resume
├── ATS Analyser           ← score resume against a job description
├── Cover Letter Builder   ← AI generates + you edit
└── Analytics              ← who downloaded, from which source
```

---

## Phase 1 — Resume CMS (Sprint 6)

Move the resume from a static TypeScript file to a live database.
Update any field instantly from the admin, no redeploy needed.

### Database schema

#### `resume_experience`
```sql
id              UUID PRIMARY KEY
company         VARCHAR(200) NOT NULL
role            VARCHAR(200) NOT NULL
start_date      DATE NOT NULL
end_date        DATE           -- NULL = current
is_current      BOOLEAN DEFAULT false
description     TEXT           -- what you did overall
highlights      TEXT[]         -- bullet points (each one is a string)
tech_stack      TEXT[]
sort_order      INTEGER
created_at      TIMESTAMPTZ
updated_at      TIMESTAMPTZ
```

#### `resume_skills`
```sql
id              UUID PRIMARY KEY
group_name      VARCHAR(100)   -- "Backend", "AI Engineering", etc.
skills          TEXT[]         -- ordered list of skill names
sort_order      INTEGER
updated_at      TIMESTAMPTZ
```

#### `resume_education`
```sql
id              UUID PRIMARY KEY
institution     VARCHAR(200)
degree          VARCHAR(200)
status          VARCHAR(50)    -- Completed / In progress / Planned
start_year      INTEGER
end_year        INTEGER
notes           TEXT
sort_order      INTEGER
```

#### `resume_certifications`
```sql
id              UUID PRIMARY KEY
title           VARCHAR(200)
provider        VARCHAR(200)
status          VARCHAR(50)    -- Completed / In progress / Planned
completed_date  DATE
credential_url  VARCHAR(500)
sort_order      INTEGER
```

#### `resume_profile`
```sql
id              UUID PRIMARY KEY  -- single row
headline        VARCHAR(300)
summary_paragraphs TEXT[]         -- ordered list of paragraphs
pdf_cache_key   VARCHAR(200)      -- S3 key of cached PDF
pdf_generated_at TIMESTAMPTZ
updated_at      TIMESTAMPTZ
```

### API endpoints

```
Public
  GET  /api/v1/resume                  Full structured resume
  GET  /api/v1/resume/pdf              Download latest PDF

Admin
  GET  /admin/api/resume               Full resume for editing
  PUT  /admin/api/resume/profile       Update headline + summary
  POST /admin/api/resume/experience    Add experience entry
  PUT  /admin/api/resume/experience/{id}
  DELETE /admin/api/resume/experience/{id}
  PATCH /admin/api/resume/experience/reorder   Drag-to-reorder
  POST /admin/api/resume/skills        Add skill group
  PUT  /admin/api/resume/skills/{id}
  DELETE /admin/api/resume/skills/{id}
  POST /admin/api/resume/education     Add education
  PUT  /admin/api/resume/education/{id}
  POST /admin/api/resume/certifications
  PUT  /admin/api/resume/certifications/{id}
  POST /admin/api/resume/pdf/generate  Trigger PDF regeneration
```

### Admin UI

```
Resume Editor
├── Tabs: Profile | Experience | Skills | Education | Certifications
│
├── Profile tab
│   ├── Headline (text input)
│   └── Summary paragraphs (rich text, add/remove/reorder)
│
├── Experience tab
│   ├── Sortable list of experience cards
│   ├── Click to expand → edit all fields
│   ├── Add new entry button
│   └── Each entry: company, role, dates, description, highlights[], tech[]
│
├── Skills tab
│   ├── Skill groups (drag to reorder)
│   ├── Each group: name + comma-separated skills
│   └── Add group button
│
├── Education tab
│   └── Simple form per entry
│
└── Certifications tab
    └── Simple form per entry with status picker
```

---

## Phase 2 — PDF Generation (Sprint 21)

Generate a beautiful, ATS-compatible PDF from the database on demand.

### PDF requirements

| Requirement | Detail |
|---|---|
| Format | A4, single or multi-page |
| ATS compatibility | Clean structure — no tables, no headers/footers, no columns |
| Fonts | System fonts or embedded Google Fonts |
| Sections | Profile, Experience, Skills, Education, Certifications |
| Design | Matches the portfolio design system (dark/light mode PDF variants) |

### Implementation

**Backend: WeasyPrint**
- HTML template rendered with Jinja2
- WeasyPrint converts HTML + CSS → PDF
- Result stored in S3/Cloudflare R2
- Cached until resume data changes (invalidated on any PUT/POST to resume endpoints)

**Two templates:**
1. `resume_clean.html` — plain, ATS-optimised (no styling, maximum compatibility)
2. `resume_styled.html` — branded, for human readers (matches portfolio design)

**Endpoints:**
```
GET /api/v1/resume/pdf                  Download styled PDF (public)
GET /api/v1/resume/pdf?style=ats        Download ATS-clean PDF (public)
POST /admin/api/resume/pdf/generate     Force regeneration
GET /admin/api/resume/pdf/preview       View the PDF in browser
```

### Admin UI
- "Generate PDF" button → shows loading spinner → "Download PDF"
- Preview pane: embedded iframe showing the PDF
- Toggle: Styled PDF / ATS-clean PDF

---

## Phase 3 — Tailored Resume Versions (Sprint A)

The master resume contains everything. Tailored versions are subsets +
modifications created for a specific role or company.

### Concept

```
Master Resume (the full truth)
    │
    ├── Tailored: "Senior Backend Engineer @ Stripe"
    │       - Emphasises payment system experience
    │       - Reorders skills: Python, PostgreSQL, Redis first
    │       - Tweaks 3 bullet points to match Stripe's language
    │
    ├── Tailored: "AI Engineer @ Anthropic"
    │       - Emphasises LLM/RAG projects
    │       - Leads with AI Engineering skill group
    │       - Adds pgvector and structured output to highlights
    │
    └── Tailored: "Tech Lead @ Series B startup"
            - Emphasises architecture and team decisions
            - Leads with system design experience
```

### Database schema

#### `resume_versions`
```sql
id              UUID PRIMARY KEY
name            VARCHAR(200)   -- "Senior Backend Engineer @ Stripe"
target_role     VARCHAR(200)
target_company  VARCHAR(200)
job_description TEXT           -- the original JD used for tailoring
headline        VARCHAR(300)   -- version-specific headline
summary         TEXT           -- version-specific summary
experience_overrides JSONB     -- per-entry highlight overrides
skills_order    TEXT[]         -- reordered skill group names
extra_keywords  TEXT[]         -- added specifically for this role
status          VARCHAR(20)    -- draft / ready / sent / archived
ai_generated    BOOLEAN        -- was this AI-tailored?
ai_model        VARCHAR(50)    -- which model was used
created_at      TIMESTAMPTZ
updated_at      TIMESTAMPTZ
```

### Admin UI — Versions

```
Resume → Versions tab
├── List of all versions with: name, target, status, created date
├── "Create tailored version" button
├── "Duplicate" button on each version
└── Version detail:
    ├── Metadata (role, company, status)
    ├── Headline override (or inherit from master)
    ├── Summary override (or inherit from master)
    ├── Experience section:
    │     Each entry shows master bullets with ability to:
    │       - Show/hide the entry for this version
    │       - Edit individual bullet points
    │       - Add role-specific bullets
    ├── Skills override (drag to reorder, show/hide individual skills)
    ├── Download PDF button for this version
    └── Delete version
```

---

## Phase 4 — AI Resume Tailoring (Sprint B)

The centrepiece feature. Paste a job description, get a tailored resume version.

### How it works

```
Admin pastes job description
        ↓
Backend extracts:
  - Required skills
  - Preferred skills
  - Key responsibilities
  - Seniority signals
  - Company culture signals
        ↓
LLM analyses master resume + extracted JD signals
        ↓
AI produces:
  - Tailored headline
  - Tailored summary (2-3 paragraphs)
  - Reordered/reworded bullet points per job
  - Recommended skill ordering
  - Keywords to add / remove
        ↓
Admin reviews in side-by-side editor
  Left: original master resume section
  Right: AI suggestion (editable)
        ↓
Admin accepts / edits / rejects each change
        ↓
Save as new tailored version
```

### Backend

```python
# New service: AIResumeService
class AIResumeService:

    async def extract_jd_signals(self, job_description: str) -> JobSignals:
        """
        Extract structured requirements from a job description.
        Returns: required_skills, preferred_skills, seniority, responsibilities,
                 culture_signals, company_name, role_title.
        Uses structured LLM output (Pydantic model) for reliable parsing.
        """

    async def tailor_resume(
        self,
        master_resume: MasterResume,
        jd_signals: JobSignals,
    ) -> TailoredResumeSuggestion:
        """
        Generate a tailored resume version.
        Returns suggested changes: headline, summary, bullet_rewrites,
        skills_ordering, keywords_to_add, keywords_to_remove.
        """

    async def score_match(
        self,
        resume_version: ResumeVersion,
        job_description: str,
    ) -> ATSScore:
        """
        Score how well a resume version matches a job description.
        Returns: overall_score, keyword_coverage, missing_keywords,
                 strengths, weaknesses, suggestions.
        """
```

### API endpoints

```
POST /admin/api/resume/ai/extract-signals
  Body: { job_description: string }
  Returns: JobSignals

POST /admin/api/resume/ai/tailor
  Body: { job_description: string, version_name: string }
  Returns: TailoredResumeSuggestion (not yet saved)

POST /admin/api/resume/ai/tailor/save
  Body: { suggestion_id, accepted_changes: [...] }
  Creates a new ResumeVersion with accepted changes

POST /admin/api/resume/ai/score
  Body: { version_id: string, job_description: string }
  Returns: ATSScore
```

### LLM provider

- **Primary:** Groq (Llama 3.3 70B) — fast, cheap, good at structured output
- **Fallback:** OpenAI GPT-4o — more reliable for complex rewrites
- **Provider abstraction:** Same pattern as InterviewPilot AI — swap models in config

### Admin UI — AI Tailor

```
Resume → AI Tailor tab

Step 1: Paste job description
  ┌─────────────────────────────────────────┐
  │ Paste job description here...           │
  │                                         │
  └─────────────────────────────────────────┘
  [Analyse JD]

Step 2: Review extracted signals (auto-populated)
  Required skills: Python, FastAPI, PostgreSQL, Redis
  Preferred skills: Kubernetes, Prometheus, Grafana
  Role: Senior Backend Engineer
  Seniority: Senior (5+ years)
  Company: Stripe
  Culture signals: production systems, reliability, scale

Step 3: Generate tailored version
  [Generate with AI] ← calls /ai/tailor

Step 4: Review side-by-side
  ┌──────────────────┬──────────────────────┐
  │ MASTER           │ AI SUGGESTION        │
  ├──────────────────┼──────────────────────┤
  │ Headline:        │ Headline:            │
  │ Python backend   │ Senior Backend Eng.  │ [Accept] [Edit] [Reject]
  │ engineer...      │ specialising in...   │
  ├──────────────────┼──────────────────────┤
  │ InterviewPilot:  │ InterviewPilot:      │
  │ - Built Celery   │ - Designed durable   │ [Accept] [Edit] [Reject]
  │   task queue     │   background job     │
  │                  │   system at scale    │
  └──────────────────┴──────────────────────┘

Step 5: Save version
  Version name: "Senior BE @ Stripe — July 2026"
  [Save as new version]
```

---

## Phase 5 — ATS Score Analyser (Sprint C)

Check how well any resume version matches a job description before sending.

### What the analyser checks

| Check | Detail |
|---|---|
| Keyword coverage | % of required JD keywords found in resume |
| Missing keywords | Critical terms absent from the resume |
| Seniority match | Does the experience level match the role? |
| Skills gap | Required skills not in your skills section |
| Bullet point strength | Action verb usage, quantification, specificity |
| Summary relevance | How well the summary addresses the role |
| Overall ATS score | 0–100 composite score |

### Response shape

```python
class ATSScore(BaseModel):
    overall_score: int           # 0–100
    keyword_coverage: float      # 0.0–1.0
    missing_required: list[str]  # critical missing keywords
    missing_preferred: list[str] # nice-to-have keywords present in JD
    present_keywords: list[str]  # keywords found in resume
    skills_gap: list[str]        # skills in JD not in resume at all
    strengths: list[str]         # what the resume does well for this role
    weaknesses: list[str]        # what the resume does poorly for this role
    suggestions: list[str]       # actionable improvements
    bullet_analysis: list[BulletAnalysis]  # per-bullet feedback
```

### Admin UI — ATS Score

```
Version detail → "Check ATS Score" button

Paste the JD (or auto-filled if version was AI-tailored from this JD)

Results:
  Overall match: 87/100  ████████░░

  ✅ Present keywords (18):
    FastAPI, PostgreSQL, Redis, async, Python, SQLAlchemy...

  ⚠️ Missing required (3):
    Kubernetes, Prometheus, load testing

  💡 Suggestions:
    1. Add "Prometheus" to skills — you have observability experience
    2. Mention "load testing" in InterviewPilot bullet — you did this
    3. Reorder skills: put PostgreSQL before Redis for this role
```

---

## Phase 6 — Cover Letter Builder (Sprint D)

AI-generated cover letter tailored to the role and company.

### How it works

1. Admin selects a tailored resume version (already targeted at a role)
2. Optionally pastes additional context: company research, why this role
3. AI generates a 3-paragraph cover letter:
   - Paragraph 1: Why this role, why this company
   - Paragraph 2: The most relevant experience and project
   - Paragraph 3: Enthusiasm, call to action
4. Admin edits in a rich text editor
5. Download as PDF or copy as plain text

### Backend

```
POST /admin/api/cover-letters/generate
  Body: { version_id, additional_context?: string, tone?: "formal"|"conversational" }
  Returns: { content: string, word_count: int }

POST /admin/api/cover-letters
  Create a saved cover letter linked to a resume version

GET /admin/api/cover-letters/{id}/pdf
  Download as PDF

GET /admin/api/cover-letters
  List all saved cover letters
```

### Database

```sql
cover_letters
  id              UUID PRIMARY KEY
  resume_version_id UUID REFERENCES resume_versions(id)
  content         TEXT           -- Markdown
  tone            VARCHAR(20)    -- formal / conversational
  ai_generated    BOOLEAN
  created_at      TIMESTAMPTZ
  updated_at      TIMESTAMPTZ
```

---

## Phase 7 — Job Application Tracker (Sprint E)

Track every job you apply to: which resume version, which cover letter,
current status, and notes.

### Database

```sql
job_applications
  id               UUID PRIMARY KEY
  company          VARCHAR(200)
  role             VARCHAR(200)
  job_url          VARCHAR(500)
  applied_date     DATE
  resume_version_id UUID REFERENCES resume_versions(id)
  cover_letter_id  UUID REFERENCES cover_letters(id)
  status           VARCHAR(50)   -- applied/screening/interview/offer/rejected/withdrawn
  salary_range     VARCHAR(100)  -- e.g. "£80k–£100k"
  notes            TEXT
  next_action      VARCHAR(200)  -- "Send thank you email", "Follow up Friday"
  next_action_date DATE
  created_at       TIMESTAMPTZ
  updated_at       TIMESTAMPTZ
```

### Admin UI — Job Tracker

```
Resume → Applications tab

Kanban board (or table view):
  Applied  →  Screening  →  Interview  →  Offer  →  Result

Each card shows:
  Company logo (auto-fetched via Clearbit or logo.dev)
  Role title
  Applied date
  Resume version used
  Status
  Next action reminder

Click card → drawer with full detail:
  All fields above
  Timeline: Applied → Screening call (date) → Tech interview (date)
  Notes (free text)
  Download resume version used
  Download cover letter used
```

---

## Phase 8 — Resume Analytics (Sprint F)

Know who downloaded your resume and from where.

### Tracking

```sql
resume_downloads
  id            UUID PRIMARY KEY
  version_id    UUID   -- null = master
  source        VARCHAR(100)  -- 'public_page', 'shared_link', 'direct'
  referrer      VARCHAR(200)  -- referring domain
  country       VARCHAR(2)
  session_id    VARCHAR(64)   -- hashed, not reversible
  created_at    TIMESTAMPTZ
```

### What you can see

| Metric | Detail |
|---|---|
| Total downloads this month | Count from `resume_downloads` |
| Downloads by version | Which tailored version is shared most |
| Top referrers | LinkedIn, Google, direct |
| Download countries | Where your resume is being reviewed |
| Download timeline | Downloads per day over last 30 days |

### Shareable links

Each resume version gets a unique shareable URL:
- `brensaud.com/resume/v/stripe-senior-be-2026`
- Viewing this URL records a download event
- Admin can revoke a link (set version to archived)

---

## Phase 9 — Skills Gap Analysis (Sprint G)

Understand what skills to learn next for your target roles.

### How it works

1. Admin adds 3–5 target job descriptions (roles they want in 6 months)
2. System analyses all JDs against current skills
3. Returns: skills you have, skills you need, priority order for learning

### Backend

```
POST /admin/api/resume/ai/skills-gap
  Body: { target_jds: string[] }
  Returns: SkillsGapReport

class SkillsGapReport(BaseModel):
    skills_you_have: list[str]       # already in resume
    skills_to_learn: list[PrioritisedSkill]
    # PrioritisedSkill: { name, frequency_in_jds, demand_level, learning_resources }
    quick_wins: list[str]            # skills close to what you know
    big_bets: list[str]              # skills requiring significant learning
    summary: str                     # narrative paragraph
```

### Admin UI

```
Resume → Skills Gap tab

Add target roles:
  + "Senior Backend Engineer (FAANG)"
  + "Staff Engineer (Series B startup)"
  + "AI Engineer (AI-first company)"

Analysis:
  ✅ Skills you have (18/25 required):
    FastAPI, PostgreSQL, Redis, Docker, Python...

  📚 Skills to learn — sorted by frequency in target JDs:
    1. Kubernetes (appears in 3/3 JDs) — 2–4 weeks
    2. Prometheus + Grafana (2/3) — 1 week, you have Prometheus knowledge
    3. System design at scale (3/3) — ongoing
    4. Go (1/3) — optional, lower priority

  ⚡ Quick wins:
    - Add "load testing" to resume — you've done this
    - Mention "observability" — you built Prometheus metrics
```

---

## Phase 10 — Interview Question Generator (Sprint H)

Given your resume version and a target job, generate likely interview questions.

### How it works

Takes: resume version + job description
Generates:
- Technical questions based on your stated skills
- Behavioural questions based on your projects
- System design questions for the seniority level
- Questions about specific projects on your resume

### API

```
POST /admin/api/resume/ai/interview-prep
  Body: { version_id, job_description }
  Returns: InterviewPrepSet

class InterviewPrepSet(BaseModel):
    technical_questions: list[InterviewQuestion]
    behavioural_questions: list[InterviewQuestion]
    system_design_questions: list[InterviewQuestion]
    project_deep_dives: list[ProjectQuestions]
    # Each InterviewQuestion: { question, why_likely, suggested_answer_direction }
```

### Admin UI

```
Resume → Interview Prep tab

Select version + paste JD → [Generate prep questions]

Technical (8 questions):
  ▶ "Explain how you designed the refresh token rotation in your portfolio backend."
    Why likely: Your resume mentions HTTPOnly cookies and JWT rotation.
    Answer direction: Describe the Redis-backed rotation, single-use tokens, timing attack prevention.

Behavioural (5 questions):
  ▶ "Tell me about a time you had to make a security-critical design decision."
    Why likely: Seniority level + security-first auth design on resume.
```

---

## Full feature summary

| Phase | Feature | Sprint | Complexity |
|---|---|---|---|
| 1 | Resume CMS (database-driven) | 6 | Medium |
| 2 | PDF generation (styled + ATS-clean) | 21 | Medium |
| 3 | Tailored resume versions | A | Medium |
| 4 | **AI tailoring from job description** | B | Large |
| 5 | ATS score analyser | C | Medium |
| 6 | Cover letter builder (AI) | D | Medium |
| 7 | Job application tracker (Kanban) | E | Medium |
| 8 | Resume download analytics | F | Small |
| 9 | Skills gap analysis (AI) | G | Medium |
| 10 | Interview question generator (AI) | H | Medium |
| 11 | Salary intelligence | I | Small |
| 12 | LinkedIn import / sync | J | Medium |
| 13 | Bullet point strength scorer | K | Small |
| 14 | Resume version diff viewer | L | Small |
| 15 | Recruiter-facing public link | M | Small |
| 16 | Resume expiry / freshness alerts | N | Small |
| 17 | Multi-language resume | O | Medium |
| 18 | Video resume / intro clip | P | Medium |
| 19 | Reference management | Q | Small |
| 20 | AI cold outreach writer | R | Medium |

---

## Additional features (Phase 11–20)

---

## Phase 11 — Salary Intelligence (Sprint I)

Know your market rate before every application. Never undersell yourself.

### How it works

When you add a job to the application tracker, the system estimates the
salary range for that role based on:
- Role title + seniority level
- Location (remote / city / country)
- Company size / funding stage
- Tech stack required

### Data sources (no paid API needed)
- **levels.fyi** — public salary data scraped or via unofficial API
- **Glassdoor** — public band estimates
- **LinkedIn Salary Insights** — aggregated data
- **Your own application history** — what ranges you've seen in real JDs

### What you see

```
Application: Senior Backend Engineer @ Stripe

Salary intelligence:
  Market range (UK, remote):   £90k – £130k
  P25 (entry-level senior):    £90k
  P50 (typical):               £110k
  P75 (strong candidate):      £125k
  P90 (Staff-equivalent):      £145k

  Your current ask:            £105k
  Recommendation:              ✅ Within market — you could push to £115k

  Based on: 847 data points from levels.fyi (last updated 30 days ago)
```

### Database

```sql
salary_benchmarks
  id          UUID PRIMARY KEY
  role_title  VARCHAR(200)
  location    VARCHAR(100)
  p25         INTEGER
  p50         INTEGER
  p75         INTEGER
  p90         INTEGER
  currency    VARCHAR(3)
  source      VARCHAR(50)
  data_date   DATE
  created_at  TIMESTAMPTZ
```

---

## Phase 12 — LinkedIn Import / Sync (Sprint J)

Import your LinkedIn profile data directly into the resume CMS.
Stop maintaining two sources of truth.

### Two approaches

**Approach A — Manual JSON export (safest, no API needed)**
LinkedIn lets you export your data as a ZIP. Parse the included CSV files
and populate the resume database.

```python
class LinkedInImportService:
    async def import_from_zip(self, zip_bytes: bytes) -> ImportResult:
        """
        Parse LinkedIn data export ZIP.
        Extracts: Positions.csv, Education.csv, Skills.csv, Profile.csv
        Maps to resume database tables.
        Returns a preview for admin review before saving.
        """
```

**Approach B — LinkedIn URL scraper (with rate limiting)**
Given a LinkedIn profile URL, extract public data via scraping.
Only scrape your own profile — no ethical issues.

### Admin UI — Import flow

```
Resume → Import tab

Step 1: Choose source
  ○ Upload LinkedIn export ZIP
  ○ Enter your LinkedIn profile URL (public scrape)

Step 2: Preview extracted data
  ✅ Experience (3 entries found)
  ✅ Education (2 entries found)
  ✅ Skills (24 found)
  ⚠️  2 entries need manual review (date format)

Step 3: Choose what to import
  [Import all]  [Select individually]  [Cancel]

Step 4: Conflict resolution
  "Senior Engineer at Acme" already exists — overwrite or keep both?
```

### What gets imported

| LinkedIn field | Resume field |
|---|---|
| Position: title | `resume_experience.role` |
| Position: company | `resume_experience.company` |
| Position: dates | `resume_experience.start_date / end_date` |
| Position: description | `resume_experience.highlights` (split by line) |
| Skills | `resume_skills.skills` |
| Education: school | `resume_education.institution` |
| Education: degree | `resume_education.degree` |
| Headline | `resume_profile.headline` |
| Summary | `resume_profile.summary_paragraphs` |

---

## Phase 13 — Bullet Point Strength Scorer (Sprint K)

Every resume bullet should start with a strong action verb, be specific,
and ideally be quantified. This tool scores each one and suggests improvements.

### Scoring criteria

| Criterion | Weight | Example |
|---|---|---|
| Starts with action verb | 20% | "Built", "Designed", "Led" |
| Quantified (numbers) | 30% | "reduced latency by 40%" |
| Specific (not vague) | 25% | "asyncpg connection pool" vs "database" |
| Concise (≤ 20 words) | 15% | — |
| Avoids weak verbs | 10% | Not "helped", "worked on", "assisted" |

### Weak verbs to flag (auto-detected)

```python
WEAK_VERBS = {
    "helped", "worked", "assisted", "supported", "involved",
    "participated", "contributed to", "responsible for", "tasked with",
    "handled", "did", "made", "used", "managed" (in most contexts)
}

STRONG_VERBS = {
    "Architected", "Designed", "Built", "Implemented", "Optimised",
    "Reduced", "Increased", "Led", "Delivered", "Automated",
    "Migrated", "Refactored", "Deployed", "Secured", "Scaled"
}
```

### Admin UI

```
Experience: InterviewPilot AI

Bullet analysis:
  "Built Celery + Redis background job queue for AI evaluation"
  Score: 78/100  ████████░░
  ✅ Strong verb ("Built")
  ✅ Specific (Celery, Redis, AI evaluation)
  ⚠️  Not quantified — add: "processing N evaluations/day"
  💡 Suggestion: "Built Celery + Redis queue processing 500+ AI evaluations/day"

  "Implemented JWT authentication with refresh token rotation"
  Score: 85/100  █████████░
  ✅ Strong verb
  ✅ Specific
  ✅ Good length
  💡 Optional: quantify sessions or token TTL for credibility
```

---

## Phase 14 — Resume Version Diff Viewer (Sprint L)

See exactly what changed between the master resume and any tailored version,
or between two tailored versions.

### What it shows

Side-by-side diff, like a GitHub PR review:

```
Master                              Stripe version
─────────────────────────────────── ───────────────────────────────────────
Headline:                           Headline:
"Python backend engineer focused    "Senior Backend Engineer specialising
 on FastAPI, AI SaaS, and           in high-throughput payment APIs,
 production-grade systems."         async FastAPI, and PostgreSQL."

InterviewPilot — highlights:        InterviewPilot — highlights:
- Built Celery + Redis queue   →    - Designed durable background job
  for AI evaluation                   processing system for AI eval at scale
- Implemented JWT auth         →    [UNCHANGED]
- [REMOVED from this version]  ←    N/A (clause search not relevant to Stripe)
```

### Implementation
Diff algorithm: Myers diff on JSON-serialised resume sections.
Frontend: similar to GitHub's split diff view.

---

## Phase 15 — Recruiter-Facing Public Link (Sprint M)

Each tailored resume version gets a unique, shareable public URL that
renders the resume as a web page — not just a PDF download.

### What it provides

- `brensaud.com/r/stripe-senior-2026` — a web-rendered resume
- Clean, readable, no admin navigation
- Includes: headline, summary, experience, skills, education
- "Download PDF" button at the top
- Download event tracked in analytics
- Admin can revoke the link (sets version to archived)

### Why web + PDF together

PDF gets emailed. Web link gets shared on LinkedIn, in messages, via text.
The web version renders instantly, works on any device, and is indexed by Google.

### Link management

```
Resume → Versions → [version] → Sharing

Public link: brensaud.com/r/stripe-senior-2026
Status: ✅ Active
Views: 14   Downloads: 6   Last viewed: 2 days ago

[Copy link]  [Revoke link]  [Regenerate slug]
```

### Database

```sql
ALTER TABLE resume_versions ADD COLUMN public_slug VARCHAR(100) UNIQUE;
ALTER TABLE resume_versions ADD COLUMN public_link_active BOOLEAN DEFAULT false;
ALTER TABLE resume_versions ADD COLUMN public_link_expires_at TIMESTAMPTZ;
```

---

## Phase 16 — Resume Freshness Alerts (Sprint N)

Your resume becomes stale. This feature makes sure you never apply
with an outdated document.

### What it tracks

| Check | Trigger | Alert |
|---|---|---|
| Skills not updated | No skills edit in 90 days | "Your skills section is 90 days old" |
| Experience gap | Last role's end date + 2 months | "Add recent experience or current role" |
| Certifications expiring | Cert expiry date - 60 days | "AWS SAA expires in 60 days — renew?" |
| Old tailored versions | Version created > 6 months ago | "Stripe version is 6 months old — refresh?" |
| Availability out of sync | `AVAILABILITY_STATUS` not updated in 30 days | "Confirm your availability status is accurate" |

### Admin dashboard notification

```
⚠️  Resume freshness alerts (2)
    · Skills section last updated 94 days ago
    · "Stripe — Senior BE" version is 7 months old

    [Review now] [Dismiss]
```

---

## Phase 17 — Multi-Language Resume (Sprint O)

Generate your resume in multiple languages for international applications.

### How it works

1. Master resume is always in English
2. Admin selects a version → "Translate to [language]"
3. AI translates: summary, headlines, bullet points
4. Admin reviews translation section by section
5. Save as a new version tagged with the target language
6. PDF generated using the correct font for that language

### Supported initially

- **Spanish** — large engineering market in Spain + LATAM
- **French** — France, Belgium, Canada
- **German** — Germany, Austria, Switzerland

### Language-specific PDF considerations

LaTeX handles CJK (Chinese, Japanese, Korean) via the `CJKutf8` package.
For European languages (French, Spanish, German), standard XeLaTeX works
with proper font encoding.

```latex
% German example — proper umlauts
\usepackage[german]{babel}
% Resume: "Berufserfahrung" instead of "Experience"
```

---

## Phase 18 — Video Resume / Intro Clip (Sprint P)

A 90-second video introduction linked from the resume page.
Increasingly common in tech — especially for remote roles.

### What it adds

- A "Watch intro" button on the public resume page
- 90-second structured video: who you are, what you build, why you engineer
- Hosted on Cloudflare Stream or Mux (cheap video hosting)
- Admin can upload a new clip from the admin panel
- Video metadata: title, description, upload date

### Structure of a good video resume

```
0:00 – 0:15  Who you are — name, role, speciality
0:15 – 0:45  What you build — 2 specific projects, what problem they solve
0:45 – 1:10  How you work — your engineering philosophy in 1–2 sentences
1:10 – 1:30  What you're looking for — role type, company stage, availability
```

### Backend

```
POST /admin/api/resume/video/upload  — upload video file
GET  /api/v1/resume/video            — public video metadata + stream URL
DELETE /admin/api/resume/video       — remove current video
```

### Database

```sql
resume_video
  id          UUID PRIMARY KEY  -- single row
  title       VARCHAR(200)
  description TEXT
  stream_url  VARCHAR(500)      -- Cloudflare Stream / Mux playback URL
  duration_s  INTEGER
  uploaded_at TIMESTAMPTZ
  is_active   BOOLEAN DEFAULT true
```

---

## Phase 19 — Reference Management (Sprint Q)

Store professional references and generate reference request emails.

### What it manages

- List of professional references (name, role, company, relationship, contact)
- Which versions/applications they've been used for
- "Request reference letter" email draft (AI-generated)
- Track whether a reference letter has been received

### Database

```sql
references
  id            UUID PRIMARY KEY
  name          VARCHAR(200)
  role          VARCHAR(200)
  company       VARCHAR(200)
  relationship  VARCHAR(100)   -- "Former manager", "Peer", "Client"
  email         VARCHAR(255)
  linkedin_url  VARCHAR(500)
  notes         TEXT
  available     BOOLEAN DEFAULT true
  created_at    TIMESTAMPTZ
```

### Admin UI

```
Resume → References tab

Reference: Sarah Chen — Engineering Manager @ Acme Corp
  Relationship: Former direct manager (2022–2024)
  Contact: sarah@acmecorp.com
  Status: ✅ Available

  [Draft reference request email]
  [View request history]
```

---

## Phase 20 — AI Cold Outreach Writer (Sprint R)

Write personalised cold emails to hiring managers and engineers at target
companies. Not spam — thoughtful, researched outreach.

### How it works

1. Admin enters: target person name + role + company + why this company
2. AI researches the company's recent engineering blog posts, job postings, GitHub activity
3. AI drafts a 3-sentence email:
   - Line 1: Specific observation about their engineering work
   - Line 2: Why your background is directly relevant
   - Line 3: Soft ask — "happy to share my work if useful"

### What makes this different from a spam generator

The AI prompt enforces:
- Reference a specific engineering choice or blog post (not generic)
- No "I noticed you're hiring" — too salesy
- Under 100 words — respects the recipient's time
- Matches your actual experience — pulls from your resume CMS

### Backend

```
POST /admin/api/resume/ai/cold-outreach
  Body: {
    target_name: string,
    target_role: string,
    company: string,
    company_context: string,  # Why this company, what you know about them
    resume_version_id: string
  }
  Returns: { subject: string, body: string, word_count: int }
```

### Admin UI

```
Outreach writer:
  Target: Marcus Lee, Engineering Director @ Linear

  Company context:
  "Linear uses Go and Rust. They wrote about moving from PostgreSQL to
   CockroachDB in their 2024 engineering blog..."

  [Generate email]

  Subject: RE: Backend systems at Linear

  Body:
  "Your post on distributed transaction handling in CockroachDB was
   genuinely interesting — the trade-offs you described mirror what I
   worked through building a multi-tenant async API at scale.
   I specialise in Python/FastAPI backend systems and have been following
   Linear's engineering blog closely. Happy to share some of my
   production work if it's ever useful."

  [Copy]  [Edit]  [Save as template]
```

---

## Updated full feature summary

| Phase | Feature | Category | Complexity |
|---|---|---|---|
| 1 | Resume CMS | Foundation | Medium |
| 2 | PDF generation | Output | Medium |
| 3 | Tailored versions | Customisation | Medium |
| 4 | AI tailoring from JD | AI | Large |
| 5 | ATS score analyser | AI | Medium |
| 6 | Cover letter builder | AI | Medium |
| 7 | Job application tracker | Workflow | Medium |
| 8 | Resume analytics | Insights | Small |
| 9 | Skills gap analysis | AI | Medium |
| 10 | Interview question generator | AI | Medium |
| 11 | Salary intelligence | Insights | Small |
| 12 | LinkedIn import / sync | Data | Medium |
| 13 | Bullet point strength scorer | Quality | Small |
| 14 | Version diff viewer | UX | Small |
| 15 | Recruiter-facing public link | Distribution | Small |
| 16 | Freshness alerts | Maintenance | Small |
| 17 | Multi-language resume | Distribution | Medium |
| 18 | Video resume / intro clip | Distribution | Medium |
| 19 | Reference management | Workflow | Small |
| 20 | AI cold outreach writer | AI | Medium |

---

## Technology decisions

| Decision | Choice | Reason |
|---|---|---|
| LLM provider | Groq (primary) / OpenAI (fallback) | Groq: fast + cheap. OpenAI: fallback for complex tasks |
| LLM output | Structured (Pydantic models) | No hallucinated field names, no parsing failures |
| PDF generation | WeasyPrint (HTML → PDF) | Easy to style, no external service, open source |
| PDF storage | S3 / Cloudflare R2 | Cache until resume data changes |
| ATS scoring | LLM + keyword matching | LLM for semantic, regex for exact keyword coverage |
| Job tracker | Simple CRUD + Kanban UI | No external integration needed |
| Analytics | Server-side, no third party | No cookie consent, privacy-first |

---

## Recommended build order

```
Week 1–2  Phase 1: Resume CMS
          → foundation everything else builds on

Week 3    Phase 2: PDF generation
          → immediately useful, no AI complexity

Week 4–5  Phase 3: Tailored versions
          → manual first, before adding AI

Week 6–7  Phase 4: AI tailoring (the main event)
          → LLM integration, side-by-side editor

Week 8    Phase 5: ATS analyser
          → natural companion to Phase 4

Week 9    Phase 6: Cover letter builder
          → small, reuses LLM setup from Phase 4

Week 10   Phase 7: Job application tracker
          → ties versions + cover letters together

Week 11   Phase 8: Analytics
          → observe what happens after shipping

Week 12   Phase 9: Skills gap analysis
          → longer-term career planning feature

Week 13   Phase 10: Interview prep
          → final AI feature, highest polish
```

---

## The one thing that changes everything

**The AI tailoring feature (Phase 4)** is what separates this from every other developer portfolio.

Most portfolios have a static PDF resume. Some have a nice `/resume` page.

You will have: paste a job description → AI rewrites your resume to match → review changes in a diff view → download tailored PDF → paste into application.

The entire workflow takes 5 minutes instead of 45.
And because you built it yourself, it becomes one of your portfolio projects.

---

## Appendix — LaTeX PDF Generation

### Why LaTeX produces the best resumes

LaTeX is the industry standard for typesetting resumes in technical fields.
Engineering managers at companies like Google, DeepMind, and Stripe frequently
see LaTeX-generated resumes and associate them with rigorous, detail-oriented engineers.

| Quality | WeasyPrint (HTML) | LaTeX |
|---|---|---|
| Typography | Good | Exceptional — optical kerning, ligatures |
| Spacing | CSS-based, sometimes inconsistent | Mathematical precision |
| ATS compatibility | Good | Excellent — clean linear text flow |
| Professional signal | Neutral | Strong in technical fields |
| Customisability | CSS | Full typographic control |
| Setup complexity | Low | Medium |
| Server-side generation | Easy | Medium (requires LaTeX install) |

**Recommendation:** Use LaTeX as the primary PDF engine for the styled resume,
and WeasyPrint as a fallback for the fast ATS-clean variant.

---

### Best LaTeX resume templates

#### 1. Jake's Resume (most popular, highly ATS-safe)

Repository: https://github.com/jakegut/resume

```latex
% Clean, single-column, no tables
% Uses standard LaTeX commands only
% Renders perfectly on every ATS
% Used by tens of thousands of engineers

\documentclass[letterpaper,11pt]{article}
\usepackage{latexsym}
\usepackage[empty]{fullpage}
\usepackage{titlesec}
\usepackage{marvosym}
\usepackage[usenames,dvipsnames]{color}
\usepackage{verbatim}
\usepackage{enumitem}
\usepackage[hidelinks]{hyperref}
\usepackage{fancyhdr}
```

**Best for:** Maximum ATS compatibility. Every major job board parses it correctly.

---

#### 2. AltaCV (modern, two-column, visual)

Repository: https://github.com/liantze/AltaCV

```latex
% Modern two-column layout
% Coloured section headers
% Timeline-style experience entries
% Skill rating bars (optional)
% Requires XeLaTeX or LuaLaTeX
```

**Best for:** Human readers — recruiters, hiring managers.
**Caution:** Two-column layouts can confuse some ATS parsers.

---

#### 3. Awesome-CV (polished, widely used)

Repository: https://github.com/posquit0/Awesome-CV

```latex
% Font Awesome icons for contact info
% Elegant colour accents
% Section-level colour control
% Honours, awards, publications support
% Requires XeLaTeX
```

**Best for:** Companies where a human reviews first. Strong visual impression.

---

#### 4. Friggeri CV (creative, bold)

Repository: https://github.com/afriggeri/cv

```latex
% Timeline-based layout
% Bold typography
% Best for senior engineers applying to design-conscious companies
```

**Best for:** Companies that value design taste (Figma, Notion, Linear).

---

#### 5. Custom minimal (recommended for this project)

Build a custom template based on Jake's structure with your portfolio's
design language applied:

```latex
\documentclass[a4paper,10.5pt]{article}

% ── Fonts ─────────────────────────────────────────────────────────────────────
\usepackage{fontspec}                      % requires XeLaTeX
\setmainfont{Inter}[                       % matches portfolio font
  BoldFont = Inter Bold,
  ItalicFont = Inter Italic
]

% ── Colour (matches portfolio accent) ─────────────────────────────────────────
\usepackage{xcolor}
\definecolor{accent}{HTML}{AA3BFF}        % purple from design system
\definecolor{textprimary}{HTML}{08060D}
\definecolor{textsecondary}{HTML}{6B6375}

% ── Layout ────────────────────────────────────────────────────────────────────
\usepackage[a4paper, margin=0.75in]{geometry}
\pagestyle{empty}                         % no page numbers

% ── Section headings ──────────────────────────────────────────────────────────
\usepackage{titlesec}
\titleformat{\section}
  {\large\bfseries\color{textprimary}}    % font style
  {}                                      % no numbering
  {0em}                                   % no indent
  {}                                      % no prefix
  [\color{accent}\titlerule]              % accent underline

% ── Hyperlinks ────────────────────────────────────────────────────────────────
\usepackage[colorlinks=true, urlcolor=accent, hidelinks]{hyperref}
```

---

### Architecture: how LaTeX fits into the backend

#### Option 1 — Server-side LaTeX (recommended)

Install LaTeX (TeX Live) inside the Docker container and compile on the server.

```dockerfile
# In Dockerfile — add LaTeX
RUN apt-get update && apt-get install -y \
    texlive-xetex \
    texlive-fonts-extra \
    texlive-latex-extra \
    && rm -rf /var/lib/apt/lists/*

# Image size increase: ~800 MB — use a multi-stage build
```

**Multi-stage build to keep production image small:**

```dockerfile
# Stage 1 — LaTeX builder
FROM python:3.12-slim AS latex-builder
RUN apt-get update && apt-get install -y texlive-xetex texlive-fonts-extra

# Stage 2 — runtime (only what's needed at runtime)
FROM python:3.12-slim
COPY --from=latex-builder /usr/share/texmf /usr/share/texmf
COPY --from=latex-builder /usr/bin/xelatex /usr/bin/xelatex
```

**Python compilation:**

```python
import subprocess
import tempfile
from pathlib import Path

class LatexPDFService:

    async def generate(
        self,
        template_name: str,
        context: dict,
    ) -> bytes:
        """
        Render a Jinja2 .tex template, compile with XeLaTeX, return PDF bytes.

        Two compilation passes are required for correct cross-references.
        """
        # 1. Render the .tex template with resume data
        tex_content = self._render_template(template_name, context)

        with tempfile.TemporaryDirectory() as tmpdir:
            tex_file = Path(tmpdir) / "resume.tex"
            tex_file.write_text(tex_content, encoding="utf-8")

            # 2. Compile twice (needed for correct page references)
            for _ in range(2):
                result = subprocess.run(
                    [
                        "xelatex",
                        "-interaction=nonstopmode",
                        "-output-directory", tmpdir,
                        str(tex_file),
                    ],
                    capture_output=True,
                    timeout=30,
                )
                if result.returncode != 0:
                    raise PDFGenerationError(result.stderr.decode())

            pdf_path = Path(tmpdir) / "resume.pdf"
            return pdf_path.read_bytes()

    def _render_template(self, name: str, ctx: dict) -> str:
        """Render a Jinja2 .tex template with LaTeX-safe escaping."""
        env = jinja2.Environment(
            loader=jinja2.FileSystemLoader("app/templates/latex"),
            # LaTeX uses { } extensively — use different delimiters
            block_start_string="((*",
            block_end_string="*))",
            variable_start_string="(((",
            variable_end_string=")))",
            comment_start_string="((#",
            comment_end_string="#))",
            autoescape=False,
        )
        # Escape special LaTeX characters in all values
        env.filters["latex_escape"] = self._latex_escape
        template = env.get_template(f"{name}.tex")
        return template.render(**ctx)

    @staticmethod
    def _latex_escape(value: str) -> str:
        """Escape special LaTeX characters to prevent compilation errors."""
        replacements = {
            "&": r"\&",
            "%": r"\%",
            "$": r"\$",
            "#": r"\#",
            "_": r"\_",
            "{": r"\{",
            "}": r"\}",
            "~": r"\textasciitilde{}",
            "^": r"\textasciicircum{}",
            "\\": r"\textbackslash{}",
        }
        for char, replacement in replacements.items():
            value = value.replace(char, replacement)
        return value
```

---

#### Option 2 — External LaTeX service (simpler, no Docker bloat)

Use a dedicated LaTeX compilation service:
- **Papeeria API** — REST API for LaTeX compilation
- **Overleaf API** (enterprise only)
- **Self-hosted LaTeXOnHTTP** — Docker container running LaTeX HTTP server

```python
# Using LaTeXOnHTTP
async def compile_via_http(tex_content: str) -> bytes:
    async with aiohttp.ClientSession() as session:
        async with session.post(
            "http://latex-service:8080/compile",
            json={"tex": tex_content, "engine": "xelatex"},
        ) as resp:
            if resp.status != 200:
                raise PDFGenerationError(await resp.text())
            return await resp.read()
```

---

### Jinja2 .tex template structure

```
app/templates/latex/
├── resume_jake.tex          ← ATS-safe, based on Jake's template
├── resume_altacv.tex        ← visual, two-column
├── resume_custom.tex        ← your branded template
├── _macros.tex              ← shared LaTeX macros
└── cover_letter.tex         ← cover letter template
```

**Sample template structure (`resume_custom.tex`):**

```latex
\documentclass[a4paper,10.5pt]{article}
((* include "_macros.tex" *))

\begin{document}

%% ── Header ──────────────────────────────────────────────────────────────────
\begin{center}
  {\Huge\bfseries ((( profile.name | latex_escape )))}\\[4pt]
  ((( profile.headline | latex_escape )))\\[2pt]
  \href{mailto:((( profile.email )))}{\small ((( profile.email )))}
  $\cdot$
  \href{((( profile.github )))}{GitHub}
  $\cdot$
  \href{((( profile.linkedin )))}{LinkedIn}
\end{center}

%% ── Summary ─────────────────────────────────────────────────────────────────
\section{Summary}
((* for para in profile.summary_paragraphs *))
((( para | latex_escape )))

((* endfor *))

%% ── Experience ──────────────────────────────────────────────────────────────
\section{Experience}
((* for job in experience *))
\textbf{((( job.role | latex_escape )))} \hfill ((( job.start_date ))) -- ((( job.end_date | default("Present") )))\\
\textit{((( job.company | latex_escape )))}

\begin{itemize}[leftmargin=*, topsep=2pt, itemsep=1pt]
  ((* for bullet in job.highlights *))
  \item ((( bullet | latex_escape )))
  ((* endfor *))
\end{itemize}
((* endfor *))

%% ── Skills ───────────────────────────────────────────────────────────────────
\section{Skills}
((* for group in skills *))
\textbf{((( group.name | latex_escape )):}
((( group.skills | join(", ") | latex_escape )))\\
((* endfor *))

%% ── Education ────────────────────────────────────────────────────────────────
\section{Education}
((* for edu in education *))
\textbf{((( edu.degree | latex_escape )))} — ((( edu.institution | latex_escape ))) \hfill ((( edu.status )))\\
((* endfor *))

\end{document}
```

---

### Admin UI — template selector

```
Resume → PDF tab

Template:
  ○ Custom (branded, matches portfolio)   ← default for sharing
  ○ Jake's (ATS-safe, plain)              ← default for job applications
  ○ AltaCV (two-column, visual)           ← for creative companies

[Generate PDF]  [Preview in browser]  [Download]
```

---

### Caching strategy

```python
# Cache key: hash of (template_name + resume_data + version_id)
# Stored in: S3 or Cloudflare R2
# Invalidated: on any resume data change (PUT/POST to any resume endpoint)

cache_key = hashlib.sha256(
    f"{template}:{version_id}:{resume_updated_at.isoformat()}".encode()
).hexdigest()

# Check cache first
if await s3.exists(f"resumes/{cache_key}.pdf"):
    return await s3.get(f"resumes/{cache_key}.pdf")

# Generate and cache
pdf_bytes = await latex_service.generate(template, context)
await s3.put(f"resumes/{cache_key}.pdf", pdf_bytes)
return pdf_bytes
```

---

### Summary: recommended LaTeX approach

| Decision | Recommendation | Reason |
|---|---|---|
| Default template | **Custom minimal** (based on Jake's structure) | ATS-safe + branded |
| Visual template | **AltaCV** | Best for human readers |
| Engine | **XeLaTeX** | Required for custom fonts (Inter) |
| Integration | **Server-side** (TeX Live in Docker multi-stage) | No external service dependency |
| Jinja2 delimiters | `((( )))` instead of `{{ }}` | LaTeX heavily uses `{` and `}` |
| Special char escaping | `_latex_escape` filter on all user data | Prevents compilation crashes |
| Caching | S3/R2 with hash-based cache keys | Never recompile unchanged resumes |
| Fallback | WeasyPrint if LaTeX fails | Compilation edge cases |

**Build order:** Start with WeasyPrint (Phase 2, Sprint 21) — fast to ship.
Add LaTeX support as an enhancement in Sprint 21b or when PDF quality becomes a priority.
LaTeX gives better output but WeasyPrint gives you 90% of the value with 20% of the effort.

