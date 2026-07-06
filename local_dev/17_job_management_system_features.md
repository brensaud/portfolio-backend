# Job Management System — Feature List

A private admin tool for managing the entire job search lifecycle,
from discovering opportunities to signing an offer.

---

## Core modules

```
Job Management System
├── 1.  Job Board              ← discover, save, and organise job postings
├── 2.  Application Tracker   ← track every application end-to-end
├── 3.  Company Intelligence  ← research companies before applying
├── 4.  Interview Manager     ← schedule, prep, and review interviews
├── 5.  Offer Manager         ← compare, evaluate, and negotiate offers
├── 6.  Contact / Network     ← manage people in your job search network
├── 7.  Document Vault        ← store resume versions, cover letters, notes
├── 8.  AI Assistant          ← AI-powered tools across every workflow
├── 9.  Analytics Dashboard   ← metrics on your entire job search
└── 10. Communication Log     ← all emails, messages, and follow-ups
```

---

## 1. Job Board

- Save job postings by pasting a URL — auto-extract title, company, location, salary
- Add jobs manually (from LinkedIn, email, referrals)
- Kanban board: Saved → Applied → In Progress → Closed
- List view with filters and search
- Tag jobs: `remote`, `startup`, `FAANG`, `AI company`, `backend`, `staff+`
- Set priority: high / medium / low
- Star / bookmark favourite roles
- Add a "why I'm interested" note to each job
- Expiry tracking — flag jobs where the posting closed
- Detect duplicate postings (same role at same company)
- Browser bookmarklet / extension to save jobs in one click
- Import from LinkedIn Saved Jobs (via LinkedIn export)
- Batch import from a CSV (copy-paste from spreadsheet)
- Filter by: status, tag, company, location, salary range, date saved
- Sort by: date saved, priority, company name, application deadline
- Archive old/irrelevant jobs without deleting
- Job posting snapshot — save the full JD text (it often gets deleted after hiring)

---

## 2. Application Tracker

- Log an application with: date, role, company, job URL
- Link to a resume version (from the Resume CMS)
- Link to a cover letter
- Status pipeline: Applied → Recruiter screen → Technical screen → On-site → Offer → Decision
- Custom pipeline stages per company
- Add timestamps to each stage transition
- Track time in each stage (e.g. "14 days in technical screen")
- Automatic "follow up?" reminder if no response in X days
- Add notes per application (any format, free text)
- Log salary expectations submitted per application
- Track referral source: job board, LinkedIn, referral, cold outreach, recruiter
- Flag applications that came from cold outreach vs inbound
- Rejection tracking: stage reached before rejection
- Withdrawal tracking: jobs you chose to drop
- Ghosted tracker: applications with no response after 3+ weeks
- Set a deadline for each application (some companies have apply-by dates)
- Link related contacts (recruiter name, hiring manager, referrer)
- Clone an application (reapply to same company in future)

---

## 3. Company Intelligence

- Company profile per employer: size, stage, tech stack, culture notes
- Funding stage: bootstrapped / seed / Series A–C / late stage / public
- Company size range: 1–10 / 10–50 / 50–200 / 200–1000 / 1000+
- Engineering blog URL — link to their technical writing
- Glassdoor link and rating
- Levels.fyi link for compensation data
- GitHub org link — see what they open source
- LinkedIn company page link
- Known interview process notes (from your own experience or Glassdoor)
- Technology radar: what stack do they use (from job postings, GitHub, blog)
- Remote policy: fully remote / hybrid / in-office
- Salary range observed in their job postings
- Pros and cons notes (your honest assessment)
- "Red flags" field — things that concerned you during the process
- Link multiple job applications to the same company
- "I know someone there" flag — link to a contact in your network
- News feed: track recent company news (funding, layoffs, product launches)
- Rate the interview process after completion (1–5 stars + notes)

---

## 4. Interview Manager

- Schedule interviews: date, time, format (phone / video / on-site / async)
- Interview type: recruiter screen / technical / system design / behavioural / culture / final
- Interviewer names and roles (when known)
- Pre-interview prep checklist:
  - Review company profile
  - Review job description
  - Review relevant resume version
  - Practice system design questions
  - Prepare STAR examples
  - Research interviewers on LinkedIn
- Post-interview notes (what was asked, how it went, your gut feeling)
- Rate each interview: went well / neutral / rough
- Track exact questions asked (builds a searchable question bank over time)
- Interview question bank — all questions you've ever been asked, tagged by type
- Reminder X hours before an interview
- Calculate total interview time invested per company
- "Thank you email" reminder — prompt within 2 hours of interview
- Track whether thank you was sent
- Expected feedback timeline (e.g. "said they'd reply in 1 week")
- "Waiting for feedback" countdown
- Video interview link storage (Zoom / Meet / Teams URL)
- Timezone converter for international interviews
- Pre-interview research template — structured notes per company

---

## 5. Offer Manager

- Log a received offer: base salary, bonus, equity, benefits, start date
- Compare multiple offers side-by-side in a table
- Total compensation calculator:
  - Base salary
  - Annual bonus (% or fixed)
  - Equity (RSUs / options — vesting schedule, strike price)
  - Signing bonus
  - Benefits value estimate (healthcare, pension, etc.)
  - Remote stipend / equipment budget
  - Annual leave days (convert to monetary value)
- Negotiation tracker:
  - Initial offer
  - Counter-offer (yours)
  - Company response
  - Final accepted offer
- Negotiation notes — what you asked for, what reasoning you gave
- Deadline tracker — "offer expires in X days"
- Offer comparison score (weighted by what matters to you)
- "Role fit" rating per offer (not just compensation)
- Accept / decline log with reason
- Reneged offers tracker (in case you need to back out after accepting)
- Offer letter document storage

---

## 6. Contact / Network Manager

- Store contacts in your job search network: recruiters, hiring managers, referrers, peers
- Contact fields: name, role, company, email, LinkedIn, how you know them
- Type: recruiter / hiring manager / peer / friend / ex-colleague / mentor
- Last contacted date
- "Follow up" reminder per contact
- Notes per contact (what you discussed, their advice)
- Link contacts to companies
- Link contacts to applications (who referred you, who is the recruiter)
- "Warm contact" vs "cold contact" flag
- Track outreach messages sent (cold outreach log)
- Response rate per recruiter (were they responsive or ghosted?)
- Referral request status: asked / waiting / received / used
- LinkedIn connection status: not connected / request sent / connected
- "Thank you" tracker — did you thank this person for their help?

---

## 7. Document Vault

- Store all resume versions (linked to Resume CMS)
- Store all cover letters (linked to Cover Letter module)
- Upload and attach custom documents: portfolio PDFs, writing samples, references
- Associate documents with specific applications
- Document version history — never lose an older version
- "Sent with this application" log — which documents went to which company
- Document expiry — flag documents older than 6 months as potentially stale
- Quick download per application: "download all documents sent to Stripe"
- Generate application package: resume + cover letter + portfolio as single ZIP

---

## 8. AI Assistant Features

- **Job description summariser** — paste JD → get a 5-bullet summary of what they actually want
- **Seniority detector** — analyse JD language to identify real seniority level vs stated title
- **Company culture detector** — analyse JD + Glassdoor + blog for culture signals
- **Application decision helper** — score the job against your personal criteria (remote, salary, stack, growth)
- **Email draft assistant** — draft follow-up emails, thank you notes, offer negotiation emails
- **Interview prep generator** — questions likely to be asked based on JD + company + your resume
- **Offer evaluation assistant** — evaluate a total comp package, flag unusual or below-market terms
- **Red flag detector** — analyse JD text for red flags (excessive unpaid overtime language, vague equity, "startup hustle culture")
- **Rejection analyser** — based on the stage you reached, suggest what might have gone wrong
- **Job fit scorer** — score a job 0–100 based on how well it matches your preferences and skills
- **Negotiation advisor** — given an offer, suggest what to counter and how to phrase it
- **Cover letter personaliser** — given a JD and saved company intelligence, tailor the cover letter further
- **Follow-up email timer** — recommend the ideal time to follow up based on company response patterns

---

## 9. Analytics Dashboard

- Total applications sent (all time / 30 days / 7 days)
- Application funnel: Applied → Screen → Interview → Offer → Acceptance rate
- Average time from apply to first response
- Average time from first response to offer
- Rejection rate by stage (where are you losing?)
- Response rate by application source (LinkedIn vs cold outreach vs referral)
- Top rejection stage — where in the pipeline do you fall out most?
- Interview success rate (screen-to-on-site, on-site-to-offer)
- Companies ghosting rate — % with no response after 3 weeks
- Applications per week (activity tracker)
- Most used resume version — which tailored version gets the best results
- Offer rate by company size / stage (FAANG vs startup vs mid-size)
- Salary distribution across offers received
- Compensation improvement vs current role
- Job search timeline — how many weeks active, projection to offer based on current rate

---

## 10. Communication Log

- Log every email, message, or call related to the job search
- Link communications to a specific application or contact
- Types: email sent / email received / phone call / LinkedIn message / referral request
- Mark as: follow-up needed / waiting / resolved
- "Last communication" date shown on every application card
- Automatic reminder: "no communication with Stripe in 5 days — follow up?"
- Email template library:
  - Initial application follow-up
  - Post-interview thank you
  - Offer negotiation counter
  - Acceptance email
  - Decline email (gracious)
  - Staying in touch with recruiter after rejection
- Draft emails with AI assistant (links to Phase 8 AI features)
- Communication timeline per company (chronological thread of all interactions)

---

## General system features

- **Search across everything** — one search bar to find any job, company, contact, or note
- **Global keyboard shortcuts** — ⌘K to open search, ⌘N for new application, ⌘J for new job
- **Dark / light mode** — matches portfolio design system
- **Mobile-responsive** — manage your job search from your phone
- **Export everything** — full data export as JSON or CSV at any time
- **Import from spreadsheet** — for people migrating from a Google Sheet tracker
- **Weekly email digest** — summary of: applications in flight, upcoming interviews, follow-up reminders
- **Data retention** — keep all data permanently, never auto-delete
- **Timeline view** — visualise your entire job search as a horizontal timeline
- **Goal setting** — "I want to send 5 applications per week" with progress bar
- **Streak tracker** — days actively working on your job search
- **Mood/energy log per day** — optional wellbeing tracker (job searching is stressful)

---

## Integration with the Resume System

How the Job Management System and Resume System connect at every touchpoint.

---

### Connection map

```
RESUME SYSTEM                          JOB MANAGEMENT SYSTEM
──────────────────────────────────     ──────────────────────────────────────
Master Resume      ──────────────────► Job Board (saved jobs)
                                              │
Tailored Version ◄───── AI Tailor ◄──── Job Posting (JD text)
                   │
                   ├──────────────────► Application Tracker (linked version)
                   │
PDF (per version)  ├──────────────────► Document Vault (attached to application)
                   │
ATS Score     ◄────┤◄─────────────────  Job Posting (JD used for scoring)
                   │
Cover Letter  ◄────┤◄─────────────────  Application (company + role context)
                   │
Interview Prep ◄───┤◄─────────────────  Interview Manager (JD + resume → questions)
                   │
Analytics      ────┴──────────────────► Application Analytics (which version wins?)
```

---

### 1. Job posting → automatic resume tailoring

**Trigger:** Admin saves a job posting in the Job Board.

**Flow:**
```
Save job posting (URL or manual)
        ↓
System extracts the job description text
        ↓
One-click "Tailor resume for this job" button
        ↓
AI Resume Tailor opens pre-filled with the JD
        ↓
AI generates a tailored version
        ↓
Tailored version is automatically linked back to this job
```

**Result:** Every job in the Job Board can have exactly one linked resume version.
When you apply, one click downloads the right resume — no hunting through versions.

---

### 2. Application → locked to a specific resume version

When you move a job from "Saved" to "Applied":

```
Job Board card: "Senior BE @ Stripe"
  [Apply] button
        ↓
  Select resume version:
    ○ Master resume
    ● Stripe — Senior BE (AI-tailored, Jul 2026)   ← recommended
    ○ Generic backend v2
        ↓
  Application created with version locked
  Version marked as "Sent" — can no longer be edited
  (editing would create a new version automatically)
```

**Why locking matters:** You need to know exactly what you sent.
If they ask "you mentioned X on your resume" you must be able to look up the exact version.

---

### 3. ATS score feeds the job fit score

**Resume ATS Score** + **Job Management Job Fit Score** = one combined signal.

```
Job Posting (saved)
  ↓
ATS Score:  87/100     ← from Resume System
Job Fit:    72/100     ← from Job Management (remote? salary? stack match?)
Combined:   80/100     ← weighted average shown on Job Board card

  "Good match — tailor the resume to push ATS score above 90 before applying"
```

---

### 4. Interview prep uses both JD + resume version

**Interview Manager** feeds directly into **Resume System's Interview Question Generator:**

```
Interview scheduled: Technical screen @ Stripe
        ↓
System knows:
  - The job description (from Job Board)
  - The resume version sent (from Application Tracker)
        ↓
One-click: "Generate prep questions for this interview"
        ↓
AI generates questions based on:
  - What the JD asks for
  - What YOUR resume says you know
  (not generic questions — personalised to you + this role)
```

---

### 5. Cover letter linked through the whole pipeline

```
Job Posting
  → AI Cover Letter uses:
      - Tailored resume version (experience context)
      - Job description (role requirements)
      - Company intelligence (why this company)
  → Cover letter saved and linked to the application
  → Application Tracker shows: resume version + cover letter used
  → Document Vault holds both as a named package
```

---

### 6. Application analytics ↔ resume version analytics

Cross-analysis between the two systems:

| Question | Data source |
|---|---|
| Which resume version gets the most responses? | Application Tracker + Resume Download Analytics |
| What ATS score correlates with getting a screen? | ATS scores + Application stage data |
| Which bullet points appear in winning versions? | Resume version content + Application outcomes |
| Do tailored versions outperform the master? | AI-tailored flag + application response rates |

**Admin view:**

```
Resume performance report:

"Stripe — Senior BE" version
  Sent with: 1 application
  Stage reached: On-site (3rd round)
  ATS score at send: 87/100

"Generic Backend v2" version
  Sent with: 4 applications
  Best stage: Recruiter screen (2 ghosted, 1 rejected)
  ATS score at send: 61/100

Insight: AI-tailored versions reach 2.3 stages deeper on average.
```

---

### 7. Skills gap → job search strategy

**Skills Gap Analysis** (Resume System) feeds into **Job Board targeting:**

```
Skills Gap says:
  "Kubernetes appears in 3 of your 5 target JDs.
   You don't have it. Quick win: 2–4 weeks."
        ↓
Job Board filter:
  Show me jobs that DON'T require Kubernetes (apply now)
  Show me jobs that DO require Kubernetes (apply in 6 weeks)
        ↓
"Learning pipeline" tag on job board:
  Jobs you're saving for after you upskill
```

---

### 8. Company intelligence shared across both systems

Company profiles are a shared resource:

```
Resume System                       Job Management System
──────────────────                  ──────────────────────────────
AI tailors resume    ←── reads ───  Company: Stripe
using company                         Tech stack: Go, PostgreSQL, Redis
culture signals                       Engineering blog: stripe.com/blog
                                      Known interview process: 4 rounds
                                      Glassdoor: 4.2/5
                                      Stage: Public
                                      Remote: Hybrid (NY/SF)

Cold outreach       ←── reads ───   Company: Stripe
writer generates                      (uses engineering blog for specifics)
personalised email
```

A company profile is created once and used everywhere.

---

### 9. Offer negotiation ↔ resume salary intelligence

**Offer Manager** and **Salary Intelligence** work together:

```
Offer received: £95k base + £10k bonus

Salary intelligence says:
  P50 for this role: £110k
  P75: £125k
  Your current ask: £95k  ← below market

Resume System flags:
  "You have Kubernetes now — that moved your market rate up 8%"

Negotiation advisor suggests:
  Counter: £112k base + equity clarification
  Reasoning template: "Based on my experience with [X] and market data..."
```

---

### 10. Rejection feedback loop

When an application is rejected, both systems update:

```
Application rejected at: Technical screen (Stripe)
        ↓
Job Management records: rejection, stage, notes
        ↓
AI Rejection Analyser asks:
  - What was the ATS score of the version sent? (87/100 — not the issue)
  - What interview questions were asked? (system design)
  - What prep was done? (minimal)
  → Likely reason: system design preparation
        ↓
Resume System update:
  - No change to resume (ATS score was fine)
  - Add "system design at scale" to Skills Gap targets
        ↓
Job Management update:
  - Tag Stripe as "interview process: heavy system design"
  - Add to company intelligence: "Focus on distributed systems"
```

---

### Shared database tables

Both systems read/write these shared resources:

| Table | Resume System | Job Management |
|---|---|---|
| `resume_versions` | Creates, manages | Reads — links to applications |
| `cover_letters` | Creates, manages | Reads — links to applications |
| `companies` | Reads for AI context | Creates, manages |
| `job_applications` | Reads for analytics | Creates, manages |
| `ats_scores` | Creates | Reads — shown on job cards |
| `salary_benchmarks` | Reads (skills gap) | Creates, reads (offer eval) |

---

### One-page workflow: from job discovery to interview

```
1. Save job posting                (Job Management — Job Board)
        ↓
2. AI extracts JD signals          (Resume System — JD Analyser)
        ↓
3. Generate tailored resume        (Resume System — AI Tailor)
        ↓
4. Score against JD                (Resume System — ATS Analyser)
        ↓
5. Generate cover letter           (Resume System — Cover Letter Builder)
        ↓
6. Mark as Applied                 (Job Management — Application Tracker)
        ↓
7. Wait... interview invited!      (Job Management — Interview Manager)
        ↓
8. Generate prep questions         (Resume System — Interview Prep Generator)
   (using JD + resume version sent)
        ↓
9. Interview → post-interview notes (Job Management)
        ↓
10. Offer received                 (Job Management — Offer Manager)
        ↓
11. Evaluate vs market rate        (Resume System — Salary Intelligence)
        ↓
12. Draft negotiation email        (Job Management + Resume AI)
        ↓
13. Accept / decline               (Job Management)
        ↓
14. Analytics updated in both systems
```

Every step uses data from the previous step.
No copy-pasting between tools. No context lost between stages.

---

## The Job Description Intake Flow

What happens from the moment you encounter a job posting —
regardless of how you bring it in.

---

### Three input methods

```
Input method A    Input method B         Input method C
URL paste         Screenshot / image     Copied text paste
    │                    │                      │
    ▼                    ▼                      ▼
Auto-scrape JD    OCR extracts text      Direct text input
    │                    │                      │
    └────────────────────┴──────────────────────┘
                         │
                         ▼
                  JD Parser (AI)
                  Extracts structured data
                         │
                         ▼
                  Preview + confirm
                         │
              ┌──────────┴──────────┐
              ▼                     ▼
       Resume workflow        Job Management
       (resume first)         (job card created)
```

---

### Method A — URL paste (most common)

```
Admin pastes: https://stripe.com/jobs/listing/senior-backend-engineer/1234

System does:
  1. Fetches the page HTML
  2. Extracts: title, company, location, salary, JD text, deadline
  3. Takes a snapshot (JD text saved permanently — posting may be deleted)
  4. Shows preview before saving

Preview:
  ┌────────────────────────────────────────────────┐
  │  Senior Backend Engineer                       │
  │  Stripe · London · Hybrid · £90k–£130k         │
  │  Posted: 2 days ago · Apply by: Aug 1          │
  │  JD extracted: 847 words                       │
  │                                                │
  │  [Confirm and analyse →]   [Edit manually]     │
  └────────────────────────────────────────────────┘
```

---

### Method B — Screenshot or image upload

Admin screenshots a job posting from LinkedIn, email, Slack, or anywhere.

```
Admin uploads image (PNG / JPG / PDF)

System does:
  1. OCR reads all text from the image (Tesseract or Claude Vision)
  2. AI cleans up OCR noise and structures the text
  3. Extracts: title, company, requirements, responsibilities, salary (if visible)
  4. Shows extracted text for review + correction

Preview with OCR result:
  ┌────────────────────────────────────────────────┐
  │  📷 Extracted from screenshot                  │
  │                                                │
  │  Title:   Senior Backend Engineer  [edit]      │
  │  Company: Stripe                   [edit]      │
  │  Salary:  Not found                [add]       │
  │  JD text: 612 words (extracted)               │
  │                                                │
  │  ⚠️  Some text may be incomplete — review below│
  │  [View full extracted text]                    │
  │                                                │
  │  [Confirm and analyse →]   [Edit before saving]│
  └────────────────────────────────────────────────┘
```

---

### Method C — Copied text paste

Admin copies text directly from a job posting (most reliable — no scraping, no OCR).

```
Admin pastes raw text:

  "We are looking for a Senior Backend Engineer to join our
   Payments Infrastructure team. You will design and build..."

System does:
  1. AI parser identifies structure (no fixed format needed)
  2. Extracts: title, company, requirements, responsibilities, skills
  3. Flags what was found vs what's missing
  4. Shows structured preview

Preview:
  ┌────────────────────────────────────────────────┐
  │  📋 Parsed from pasted text                    │
  │                                                │
  │  Title:   Senior Backend Engineer  ✅           │
  │  Company: Not found                ⚠️  [add]   │
  │  Salary:  Not found                ⚠️  [add]   │
  │  Required skills: Python, Go, PostgreSQL ✅     │
  │  Preferred: Kubernetes, Prometheus   ✅         │
  │                                                │
  │  [Confirm and analyse →]                       │
  └────────────────────────────────────────────────┘
```

---

### After intake — the AI analysis phase

Once the JD is confirmed (from any input method), the system runs analysis automatically:

```
JD saved to database
        │
        ▼
AI extracts structured signals (runs in background, ~3 seconds):

  JobSignals {
    role_title:      "Senior Backend Engineer"
    company_name:    "Stripe"
    seniority:       "Senior (5–8 years)"
    required_skills: ["Python", "Go", "PostgreSQL", "Redis", "distributed systems"]
    preferred_skills:["Kubernetes", "Prometheus", "Grafana"]
    responsibilities:["Design high-throughput APIs", "own reliability", "mentor juniors"]
    culture_signals: ["production-first", "reliability-focused", "high ownership"]
    red_flags:       []   ← none detected
    ats_keywords:    ["asyncio", "microservices", "SLA", "observability"]
  }

  Job fit pre-score:  76/100
  (based on your master resume vs required signals)
```

---

### Resume workflow — what happens first

```
STEP 1: Show instant gap analysis
─────────────────────────────────
"Before you tailor your resume, here's what's missing:"

  ✅ You have (18/22 required skills):
     Python, FastAPI, PostgreSQL, Redis, asyncio, Docker...

  ⚠️  Missing from your resume (4):
     - Kubernetes  (appears in required)
     - Prometheus  (preferred — but you've used it)
     - Go          (preferred)
     - "SLA" keyword (not mentioned anywhere)

  💡 Quick fixes before tailoring:
     - Add Prometheus to skills — you built metrics in Sprint 17
     - Add "SLA" to an InterviewPilot bullet
     - Note Kubernetes as "learning" in certifications

  [Apply quick fixes now]  [Skip and tailor anyway]


STEP 2: Create tailored resume version
──────────────────────────────────────
AI rewrites your resume for this specific job:

  - Headline rewritten for Stripe's language
  - InterviewPilot bullet #3 reworded to match "high-throughput APIs"
  - Skills reordered: Python, PostgreSQL, Redis first (matches JD order)
  - "SLA" and "observability" keywords inserted naturally
  - Summary paragraph 2 rewritten to emphasise reliability engineering

  Side-by-side diff shown for each change.
  You accept / edit / reject each one individually.


STEP 3: ATS score check
────────────────────────
Before:   61/100 (master resume vs this JD)
After:    91/100 (tailored version vs this JD)

  ✅ All required keywords present
  ✅ Skill order matches JD priorities
  ⚠️  Kubernetes still missing — add "planned" note or remove from must-have


STEP 4: PDF generation
───────────────────────
  "Stripe — Senior BE — July 2026"
  Template: Jake's (ATS-safe)  or  Custom branded
  [Generate PDF]  →  Ready in 8 seconds
  [Preview]  [Download]


STEP 5: Cover letter (optional)
────────────────────────────────
  AI generates cover letter using:
  - Your tailored resume highlights
  - Stripe's engineering culture signals (from the JD)
  - Standard 3-paragraph structure

  [Generate cover letter]  [Skip]
```

---

### Job management workflow — happens in parallel

While the resume is being created, the job card is already live:

```
STEP 1: Job card created immediately
──────────────────────────────────────
  ┌─────────────────────────────────────────────┐
  │  ⬡ Senior Backend Engineer                 │
  │  Stripe · London · Hybrid · £90k–£130k     │
  │  Status: Saved                              │
  │  Job fit: 76/100  →  91/100 (after tailor) │
  │  Resume: Stripe — Senior BE (being created) │
  └─────────────────────────────────────────────┘


STEP 2: Company profile auto-populated
───────────────────────────────────────
  Company: Stripe
  ├── Stack detected: Python, Go, PostgreSQL, Redis (from JD)
  ├── Stage: Public
  ├── Engineering blog: stripe.com/blog (saved)
  └── Culture: production-first, reliability, high ownership


STEP 3: Application checklist generated
─────────────────────────────────────────
  Before applying, complete:
  □ Tailored resume version   ← currently being created
  □ ATS score > 85            ← currently 91 ✅
  □ Cover letter              ← optional
  □ Research company (30 min) ← not done
  □ Check deadline            ← Aug 1 (26 days away)


STEP 4: When you click "Apply"
───────────────────────────────
  Resume version locked:  "Stripe — Senior BE — July 2026"
  Cover letter linked:    "Stripe cover — July 2026" (if created)
  Status moves to:        Applied
  Date logged:            2026-07-06
  Follow-up reminder:     Set for 2026-07-13 (7 days)
```

---

### The complete picture — one JD in, everything out

```
You paste/upload/type a job description
                │
                ▼ (~5 seconds)
┌───────────────────────────────────────────────────────┐
│                    INTAKE + ANALYSIS                  │
│  • JD text saved permanently (snapshot)               │
│  • Structured signals extracted                       │
│  • Skill gap identified instantly                     │
│  • Job fit pre-scored (76/100)                        │
│  • Company profile created                            │
│  • Red flags checked                                  │
│  • Deadline extracted                                 │
└───────────────────────────────────────────────────────┘
                │
       ┌────────┴────────┐
       ▼                 ▼
┌────────────┐    ┌───────────────┐
│   RESUME   │    │ JOB MGMT      │
├────────────┤    ├───────────────┤
│ Gap shown  │    │ Job card live │
│ Quick fixes│    │ Company made  │
│ AI tailors │    │ Checklist set │
│ ATS: 91/100│    │ Deadline shown│
│ PDF ready  │    │               │
│ Cover ltr  │    │               │
└─────┬──────┘    └───────┬───────┘
      │                   │
      └─────────┬─────────┘
                ▼
      You click "Apply" — one action:
        • Resume version locked to this job
        • Cover letter linked
        • Application status: Applied
        • Follow-up reminder: 7 days
        • ATS score saved to application record
        • Analytics updated in both systems
```

---

### What you never do again

| Task | Before this system | With this system |
|---|---|---|
| Find the right resume version | Search your files | Linked automatically to the job |
| Remember what you sent | Hope you kept a copy | Locked and stored permanently |
| Manually copy JD for AI | Copy-paste into ChatGPT | Already extracted on save |
| Track follow-up dates | Calendar or spreadsheet | Auto-set on apply |
| Research company before interview | Manual Google search | Company profile already built |
| Customise resume from scratch | 45+ minutes | 5 minutes with AI diff review |
| Know your ATS score before sending | Never | Always — shown before you apply |
