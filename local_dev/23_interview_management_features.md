# Interview Management — Complete Feature List

Part of the Job Management System. Every interview from every application
lives here — tracked, prepared, and learned from.

---

## Overview

```
Interview Management
├── 1.  Interview Scheduler       ← schedule, format, location, reminders
├── 2.  Pre-Interview Prep        ← research, checklist, practice
├── 3.  Interview Question Bank   ← every question you've ever been asked
├── 4.  AI Interview Prep         ← personalised questions from JD + resume
├── 5.  Live Interview Notes      ← real-time note capture during interview
├── 6.  Post-Interview Review     ← debrief, rating, feedback log
├── 7.  Follow-Up Manager         ← thank-you emails, feedback waiting
├── 8.  Interview Analytics       ← patterns, success rates, weak areas
└── 9.  Mock Interview Mode       ← self-practice with AI feedback
```

---

## 1. Interview Scheduler

### Scheduling basics
- Create interview linked to a job application
- Interview title (e.g. "Technical screen with Sarah Chen")
- Date, time, timezone (with timezone auto-detection)
- Duration (30 min / 45 min / 1 hour / custom)
- Format: Phone call / Video call / On-site / Async (take-home) / Panel / Pair programming

### Interview type classification
- Recruiter / HR screen
- Hiring manager call
- Technical screen (code review / algorithmic)
- System design interview
- Behavioural / culture fit
- Take-home assessment
- Pair programming session
- Panel interview (multiple interviewers)
- Final round / executive interview
- Reference check

### Location and access
- Video call link storage (Zoom / Google Meet / Teams / custom)
- On-site address with Google Maps link
- Building access instructions (visitor badge, floor, contact on arrival)
- Parking / transit notes

### Interviewers
- Add interviewer names and roles (when shared in advance)
- LinkedIn profile links per interviewer (for research)
- "Add more interviewers" (for panel rounds)
- Notes per interviewer (what you've researched about them)

### Calendar integration
- Export to Google Calendar (.ics download)
- Export to Apple Calendar (.ics download)
- Outlook-compatible .ics file
- Direct Google Calendar add link

### Reminders
- Email reminder: 24 hours before
- Email reminder: 1 hour before
- Push notification (if PWA installed): 30 minutes before
- Custom reminder time (set per interview)
- "Prep reminder": 48 hours before — "start preparing for your interview"

### Status tracking
- Scheduled → Completed / Cancelled / Rescheduled / No-show
- Reschedule tracking: log every reschedule with reason
- Cancellation reason log (company cancelled / you cancelled / ghosted)

---

## 2. Pre-Interview Prep Checklist

### Auto-generated checklist per interview type

**For every interview:**
- [ ] Review the job description (link to saved JD)
- [ ] Review the resume version you sent
- [ ] Research the company (link to company intelligence profile)
- [ ] Research the interviewers on LinkedIn
- [ ] Prepare questions to ask them
- [ ] Test audio and video (for video calls)
- [ ] Find / confirm interview location or dial-in details

**Technical screen extras:**
- [ ] Brush up on relevant algorithms and data structures
- [ ] Review code you've written on this tech stack
- [ ] Practice on coding platform (LeetCode / HackerRank)
- [ ] Have IDE or coding environment ready
- [ ] Prepare to explain your past technical decisions

**System design extras:**
- [ ] Review system design fundamentals (scaling, caching, databases)
- [ ] Prepare to design a system similar to this company's product
- [ ] Know the CAP theorem and trade-offs
- [ ] Be ready to estimate scale (QPS, storage, bandwidth)

**Behavioural extras:**
- [ ] Prepare 5–7 STAR stories from your experience
- [ ] Map stories to common themes: leadership, conflict, failure, success
- [ ] Have specific numbers and outcomes ready
- [ ] Know your "tell me about yourself" pitch cold

### Research cards (auto-populated from company intelligence)

```
Company: Stripe
  ├── What they do: Payment infrastructure
  ├── Stack: Go, Ruby, PostgreSQL, Redis (from job posting)
  ├── Engineering blog: stripe.com/blog
  │     Last post: "Migrating to distributed tracing" (3 days ago)
  ├── Known interview style: "Heavy on systems thinking, reliability focus"
  │     (from your notes on previous Stripe round)
  ├── Glassdoor: 4.2/5 — "rigorous but fair"
  └── Recent news: "Stripe launches Stablecoin APIs" (Jul 2026)
```

### Interviewer research cards

```
Interviewer: Sarah Chen — Senior Engineering Manager
  ├── LinkedIn: linkedin.com/in/sarahchen
  ├── Last 3 posts: talks about distributed systems, reliability
  ├── Previous companies: Google, Cloudflare
  ├── Technical blog: sarahchen.dev (found via LinkedIn)
  └── Research notes: [your notes here]
```

### Questions to ask them
- Pre-populated suggestions based on company and role type
- Add your own custom questions
- Mark which questions you actually asked (post-interview)
- "Good questions" bank: save questions that got great responses across all interviews

### STAR story builder
- Create and store STAR stories (Situation / Task / Action / Result)
- Tag stories by theme: leadership, technical challenge, conflict, failure, initiative
- Map stories to common behavioural questions
- "This story is relevant to: [3 question themes]"
- Word count guide: keep stories under 2 minutes (≈ 300 words)
- Stories re-usable across all applications

---

## 3. Interview Question Bank

### Building the bank
- Add questions during prep (predict what you'll be asked)
- Add questions after interview (what you were actually asked)
- Import from the AI prep generator
- "Add question" during live notes (quick capture)
- Community contributed questions (SaaS: shared anonymously)

### Question fields

```
Question: "Design a distributed rate limiter"
  Company:    Stripe (optional — anonymise if preferred)
  Round:      System design
  Interview:  Technical screen — Jul 2026
  Difficulty: Hard
  Category:   System design / Distributed systems
  Tags:       [rate limiting, distributed, Redis, consistency]
  My answer:  [how you answered or how you would answer]
  Better answer: [what you'd say next time]
  Resources:  [links to relevant articles / videos]
  Appeared in: 2 interviews
```

### Question categories
- Data structures and algorithms
- System design
- Distributed systems
- Databases and SQL
- Python-specific (language features, performance, idioms)
- FastAPI / async patterns
- Security and authentication
- DevOps and infrastructure
- Behavioural (STAR-format)
- Culture fit and values
- "Tell me about yourself" variants
- "Why this company?"
- "Where do you see yourself in 5 years?"
- Project deep-dives
- Code review scenarios
- Debugging scenarios

### Question bank features
- Full-text search across all questions
- Filter by: category, difficulty, company, date, "answered" status
- Sort by: frequency (asked most), recency, difficulty
- "I got this question!" — mark questions from prep that appeared
- "Study this" flag — questions you want to review before next interview
- Spaced repetition: surface due-for-review questions
- Export question bank as Markdown or PDF study guide

### Frequency insights
- "System design questions appear in 4 of your 6 interviews"
- "Rate limiting and distributed systems: most common theme for your target roles"
- "Behavioural: 'Tell me about a conflict' — asked 3 times"

---

## 4. AI Interview Prep

### Personalised question generation
**Input:** resume version + JD + interview type + company
**Output:** predicted questions specific to YOUR experience and THIS role

```
Technical questions likely for YOUR resume at Stripe:

1. "Walk me through how you designed the HTTPOnly cookie auth system
   on your portfolio project. Why cookies instead of Bearer tokens?"
   Why likely: Your resume explicitly mentions this. Stripe is security-conscious.
   Answer direction: Explain XSS protection, SameSite=Strict, token rotation.
   Relevant project: Portfolio Backend

2. "Your InterviewPilot project uses Celery + Redis for background jobs.
   How would you handle a Redis outage gracefully?"
   Why likely: Stripe uses Redis heavily. They'll probe your Redis knowledge.
   Answer direction: Dead letter queues, retry logic, fallback strategies.
```

### STAR story mapper
Given a company + role type, AI suggests which of your stored STAR stories
are most relevant and how to adapt them:

```
For Stripe (reliability, production systems):

  Best story for "biggest technical challenge":
    → "InterviewPilot Redis queue failure at 2am" (if you have this)
    Angle: emphasise monitoring → detection → fix → prevention
    Add: how you'd prevent it at Stripe's scale

  Best story for "disagreement with a colleague":
    → Your most conflict-related story
    Angle: technical disagreement about architecture, resolved through data
```

### System design warmup
For system design rounds, AI generates a warmup problem matching the company:

"Design a webhook delivery system" (for Stripe — they have webhooks)
"Design a rate limiter for an API" (classic, relevant to your stack)
"Design the contact message queue in your portfolio" (using your own work)

With: requirements clarification questions, scaling considerations, hints if stuck.

### "Know your own resume" quiz
AI generates questions ABOUT YOUR OWN PROJECTS:

```
Quiz question:
"In your InterviewPilot project — what is the retry strategy for
 failed AI evaluation jobs in Celery? What's the max retry count?"

This tests whether you know your own work deeply enough to discuss
it confidently. Interviewers often ask for specifics.
```

### Real-time prep session (mock Q&A mode)
- Admin types a question
- Timer starts (simulate 3-minute answer window)
- Admin types / voice-records their answer
- AI evaluates: structure, specificity, conciseness, technical accuracy
- Feedback: "Good structure, but you didn't mention the outcome"

---

## 5. Live Interview Notes

### Real-time note capture
- Notes tab opens automatically when interview starts (based on scheduled time)
- Fast input: keyboard-first, no mouse required
- Auto-timestamp every note entry (shows time since interview start)
- Quick tags: [question] [important] [follow-up] [unclear] [good-point]

### Question logging during interview
- "Add question asked" button — quickly log what they asked
- Pre-loaded with AI-predicted questions (tap to mark as "they asked this")
- New question not predicted → flag as "surprised by this"

### Interview flow tracking
- Multi-round awareness (this is round 2 of 4)
- Track topics covered per round (don't repeat yourself in later rounds)
- "What we covered" summary carries forward to next round

### Offline support
- Notes work offline (PWA service worker)
- Sync when connection restored
- Critical for on-site interviews where WiFi is unreliable

### Voice-to-text (optional)
- Tap microphone → transcribes what's being said
- Useful when listening and want to capture exact phrasing
- Transcription shown + editable before saving

---

## 6. Post-Interview Review

### Debrief form (prompted immediately after interview ends)
Prompted via notification: "Your interview ended 30 minutes ago — time to debrief"

```
Overall feeling: 😊 Went well  /  😐 Mixed  /  😟 Rough

Technical performance: 1–5 stars
Communication clarity: 1–5 stars
STAR story delivery:   1–5 stars
Questions I asked:     1–5 stars

What went well:
[free text]

What I'd do differently:
[free text]

Questions they asked (that I hadn't logged live):
[add any missed]

Surprises / unexpected topics:
[free text]

My confidence: High / Medium / Low

Would you work here? Yes / Maybe / No
Reason: [free text]
```

### Feedback recording
- Log feedback when company provides it (rare but valuable)
- "Stage reached before feedback" — auto-suggests likely reason
- Flag companies that provide structured feedback (send thank you to interviewer)

### Interview rating for company
- Rate the interview experience: 1–5 stars
- Notes on the interview process quality
- "Would I interview with this company again?" Yes / No

### Outcome tracking
- Pass → advance to next round
- Fail → rejection
- Offer received
- Waiting for feedback (set countdown)
- Ghosted (no feedback after X days)

---

## 7. Follow-Up Manager

### Thank-you email system
- Prompted: "Send thank you within 2 hours of interview"
- Pre-filled draft: AI generates personalised thank-you based on interview notes
- Personalisation: mentions a specific point from the conversation
- Sends via: email client (mailto: link) or copied text
- Mark as sent (so reminder doesn't repeat)

### Feedback request email
- If no feedback in X days: AI drafts a polite follow-up
- Tracks: feedback request sent, response received, no response
- Escalation: 3 follow-ups maximum (auto-stops to avoid being annoying)

### Thank-you tracking per interviewer
- Multi-round panels: track thank-you per person
- LinkedIn connection request: "Did you connect with your interviewer on LinkedIn?"
- "Staying in touch" reminders for strong connections

### Waiting for feedback countdown
- Set expected timeline: "said they'd reply in 1 week"
- Countdown shown on application card
- Alert when deadline passes with no response
- "Likely ghosted" flag after 2× expected timeline

---

## 8. Interview Analytics

### Success metrics
- Interview-to-offer rate overall
- Interview-to-offer rate by round type (technical / system design / behavioural)
- Average rounds before offer
- Average rounds before rejection
- Rejection stage distribution (where do you lose most?)
- Time between rounds (company responsiveness)

### Performance trends
- Post-interview rating trend over time ("I've improved from 3.1 to 4.2 avg")
- Most improved areas (comparing self-ratings over time)
- Weakest round types (behavioural is consistently lower than technical)
- Best performance by company stage (startup vs FAANG vs scale-up)

### Question pattern analysis
- Most frequently asked question categories
- Questions you've been asked at multiple companies
- Topics that surprised you (not in prep)
- Questions where your answer felt strongest / weakest

### Company interview process comparison
- Average rounds per company
- Average time from first screen to offer
- Companies known for fast processes vs slow
- Companies that ghosted vs gave feedback

### Personal coaching insights
- "System design is your strongest round (4.3/5 avg)"
- "Behavioural rounds drag you down (2.9/5 avg) — prepare more STAR stories"
- "You perform better in morning interviews (4.1) vs afternoon (3.2)"
- "You're better at FAANG-style interviews than startup culture-fit rounds"

---

## 9. Mock Interview Mode

### Self-practice sessions
- Select: interview type + topic + difficulty level
- AI asks a question
- Timer: 3 minutes to answer (shown as progress bar)
- Admin types or voice-records answer
- AI evaluates the answer and gives feedback
- Next question automatically queued

### Feedback dimensions
```
Answer evaluation:
  Structure:     4/5  (had opening, examples, conclusion)
  Specificity:   3/5  (mentioned Redis but no specific numbers)
  Conciseness:   5/5  (under 2 minutes — good)
  Relevance:     4/5  (answered the question asked)
  Technical depth: 4/5 (showed understanding of trade-offs)

Improvement:
  "Add a specific metric: how many jobs/second, what was the latency impact?"
  "Mention the alternative you considered and why you chose this approach"
```

### Session types
- Quick warmup: 5 random questions, 2 minutes each (15 minutes total)
- Deep dive: 1 system design problem, 30 minutes
- Behavioural blitz: 8 STAR questions, 2 minutes each
- "Interview simulation": full mock round matching a real company's known format

### Progress tracking
- Mock session history
- Score improvement over time per topic
- "Ready for interview" score: percentage of prep completed
- "Weak areas" automatically surfaced based on mock performance

---

## 10. Take-Home Assignment Tracker

A dedicated section for tracking coding challenges, technical assessments,
and any task given to complete as part of the hiring process.

### Assignment types
- Coding challenge (LeetCode-style, timed)
- Take-home project (build something, 3–7 days)
- System design document (written response)
- Code review assignment (review provided code and comment)
- Architecture proposal (design doc for a given problem)
- Data / SQL challenge
- Technical writing task

### Assignment record fields

```
Assignment: "Build a rate limiter API"
  Company:           Stripe
  Application:       Senior Backend Engineer — Jul 2026
  Type:              Take-home project
  Given date:        2026-07-06
  Deadline:          2026-07-10 (4 days)
  Deadline countdown: 3 days 14 hours remaining

  Task description:
    [paste or upload the full task document / PDF]
    [if given as a URL, snapshot the content]

  Requirements extracted:
    - REST API in any language
    - Token bucket algorithm
    - Redis for state
    - Tests required
    - README with design decisions

  Time tracking:
    Started:    2026-07-06 19:00
    Total time: 6h 45m (logged across sessions)
    Time log:   [start, stop, duration per session]

  Your approach notes:
    [freeform notes on your design decisions as you work]

  Submission:
    Submitted at:  2026-07-09 16:30
    Submission URL: github.com/brensaud/stripe-rate-limiter
    Submission method: GitHub link via email

  Outcome:
    Passed / Failed / No feedback received
    Feedback: [exact feedback if provided]
    What I'd do differently: [post-assignment reflection]
```

### Task document storage
- Upload task PDF, image, or paste task text
- Snapshot saved permanently (original link may expire)
- OCR if uploaded as image/screenshot (Claude Vision)
- AI extracts structured requirements from the task description

### Requirements tracker
- AI parses task → generates a checklist of requirements
- Check off completed requirements before submitting
- "All requirements met" gate before marking as submitted

```
Task requirements checklist:
  ✅ REST API endpoint (POST /rate-limit/check)
  ✅ Token bucket algorithm implemented
  ✅ Redis for token state
  ✅ Unit tests (pytest)
  ✅ README with architecture explanation
  ❌ Rate limit header (X-RateLimit-Remaining) — not done yet
  ❌ Docker Compose for local run
```

### Time tracker
- Start / pause / stop timer
- Session history with notes per session
- Total time shown (useful to know if you over/under-invested)
- "Expected time" field (set from task instructions, e.g. "spend 4–6 hours")
- Alert if you've exceeded the expected time

### Submission tracker
- Mark as submitted with timestamp
- Store submission link (GitHub URL, Google Drive, etc.)
- Attach submission confirmation email screenshot
- "Follow up if no response in X days" reminder

### Post-assignment reflection
- Did you finish everything?
- What corners did you cut? (be honest — interviewers notice)
- What would you add with more time?
- What was technically challenging?
- What are you proud of?
- AI generates a "talking points" summary to use if called to discuss it

### Assignment analytics
- Completion rate (how many you submitted vs given)
- Pass rate on assignments
- Average time spent per type
- Most common task types in your target companies
- "Your take-home pass rate is 80% — your highest conversion stage"

---

## 11. Job Description Reference (cross-module)

Everywhere a JD is needed, it comes from one place — the Job Board.
Never paste the same JD twice.

### Where the saved JD is used automatically

| Feature | Uses JD from |
|---|---|
| Resume AI tailoring | Job Board snapshot |
| ATS score analyser | Job Board snapshot |
| AI interview prep questions | Job Board snapshot |
| Take-home requirements extraction | Job Board snapshot or assignment upload |
| Cover letter generator | Job Board snapshot |
| Job fit scoring | Job Board snapshot |
| Company culture signals | Job Board snapshot |
| Skills gap analysis | Multiple JDs from Job Board |

### JD snapshot — what's saved
- Full original JD text (always)
- Extracted structured signals (role, skills, seniority, culture)
- Screenshot of the original posting (if available)
- Source URL
- Date saved + date last verified (link still active)
- "JD archived" flag (if posting was taken down)

---

## Summary — updated total

| Module | Feature count |
|---|---|
| 1. Interview Scheduler | 18 |
| 2. Pre-Interview Prep Checklist | 22 |
| 3. Interview Question Bank | 18 |
| 4. AI Interview Prep | 16 |
| 5. Live Interview Notes | 10 |
| 6. Post-Interview Review | 12 |
| 7. Follow-Up Manager | 12 |
| 8. Interview Analytics | 16 |
| 9. Mock Interview Mode | 12 |
| 10. Take-Home Assignment Tracker | 18 |
| 11. JD Reference (cross-module) | 8 |
| **Total** | **162** |

```
JOB SAVED                         INTERVIEW SCHEDULED
      ↓                                 ↓
JD signals extracted          Auto-generates prep checklist
Job fit scored                Pulls company intelligence
      ↓                       Pulls resume version sent
APPLICATION CREATED           Loads AI question predictions
      ↓                                 ↓
Resume version locked      INTERVIEW COMPLETED
      ↓                                 ↓
Cover letter linked        Post-interview debrief prompted
                           Questions added to bank
                           Thank-you email drafted
                                        ↓
                           FEEDBACK / REJECTION
                                        ↓
                           Rejection analyser runs
                           Question bank updated
                           Analytics updated
                           Skills gap re-evaluated
```

---

## Summary — total features

| Module | Feature count |
|---|---|
| 1. Interview Scheduler | 18 |
| 2. Pre-Interview Prep Checklist | 22 |
| 3. Interview Question Bank | 18 |
| 4. AI Interview Prep | 16 |
| 5. Live Interview Notes | 10 |
| 6. Post-Interview Review | 12 |
| 7. Follow-Up Manager | 12 |
| 8. Interview Analytics | 16 |
| 9. Mock Interview Mode | 12 |
| **Total** | **136** |
