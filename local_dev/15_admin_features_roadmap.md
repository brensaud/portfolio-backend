# Admin Panel — Full Feature Roadmap

Everything the admin (you, the portfolio owner) should be able to manage
from the private dashboard. Single-user design — no roles, no teams.

---

## Design principle: single admin

This portfolio has exactly one admin user — you. There is no:
- Role-based access control (no viewer / editor / admin roles)
- Team management
- Invitations or shared access

Every feature in this document is built for one person who needs full
control over their portfolio without touching code.

---

## What is built today (Sprint 1 + Sprint 2)

| Section | Status | What you can do |
|---|---|---|
| Login / Logout | ✅ Done | Secure session with HTTPOnly cookies, refresh token rotation |
| Contact Messages | ✅ Done | View, search, filter, mark read/unread, archive, delete |

---

## Full admin panel vision

```
Admin Panel
├── Dashboard          ← overview of everything at a glance
├── Contact Messages   ← ✅ built
├── Content
│   ├── Projects       ← manage portfolio projects
│   ├── Articles       ← write and publish blog posts
│   ├── Case Studies   ← detailed engineering write-ups
│   └── Resume         ← update experience, skills, education
├── Site Settings
│   ├── Availability   ← "open to work" toggle + message
│   ├── Profile        ← name, bio, social links
│   └── Password       ← change admin password
├── Analytics          ← page views, top projects, referrers
├── Newsletter         ← subscribers list and management
└── Activity Log       ← audit trail of all admin actions
```

---

## Section 1 — Dashboard (overview)

**Sprint:** 10
**Current state:** Placeholder page with "Dashboard widgets coming soon."

The dashboard is the first page after login. Should answer:
"What needs my attention right now?"

### Widgets to build

| Widget | Data | Action |
|---|---|---|
| Unread messages | Count from `contact_messages WHERE status='unread'` | Click → go to Messages |
| Latest message preview | Most recent unread message | Click → open detail |
| Most viewed project this week | From analytics | Click → go to Projects |
| Most read article this week | From analytics | Click → go to Articles |
| Newsletter subscribers | Total count | Click → go to Newsletter |
| Open to work status | Current availability | Click to toggle |
| Recent activity | Last 5 audit log entries | — |
| System health | DB connection, uptime | — |

### What the backend needs
All widget data comes from existing tables (contact_messages, analytics, newsletter_subscribers)
plus a new `GET /admin/api/dashboard/summary` endpoint that returns all counts
in a single request to avoid waterfall loading.

---

## Section 2 — Contact Messages

**Sprint:** ✅ Complete (Sprint 2)

### Already built
- Paginated list (20 per page)
- Search by name, email, subject
- Filter by status: unread / read / archived
- Sort: newest / oldest first
- Detail view with full message content and metadata
- Mark as read / unread
- Archive
- Delete with confirmation dialog
- Audit log for every action
- Toast notifications

### Future improvements (nice to have)
- **Quick reply button** — open the user's email client pre-filled with their address and a reply template
- **Bulk actions** — select multiple messages and archive/delete all at once
- **Label/tag system** — tag messages as `hiring`, `collaboration`, `feedback`, `spam`
- **Notes** — add a private note to a message (e.g. "Replied on 2026-07-06")
- **Export** — download all messages as CSV for backup

---

## Section 3 — Projects CMS

**Sprint:** 4 (planned)

Replace `src/data/projects.ts` with a backend-driven CMS.
Add a new project in 30 seconds without touching code.

### What you can do
- Create a new project with title, slug, description, tech stack, status
- Upload a project thumbnail image
- Add/remove links (GitHub, demo, case study, article)
- Mark a project as "featured" (shows on homepage)
- Drag to reorder projects (sort_order)
- Toggle project visibility (published / draft)
- Archive old projects (still stored, hidden from public)
- Delete permanently

### Fields per project

| Field | Type | Notes |
|---|---|---|
| Title | Text | Short display name |
| Slug | Text | URL-safe identifier (auto-generated from title) |
| Subtitle | Text | One-line technical description |
| Description | Rich text | Multi-paragraph detail |
| Category | Select | Backend / AI / SaaS / DevOps |
| Status | Select | In development / Prototype / Production-focused |
| Tech stack | Tags | Multi-value list |
| Links | Repeater | [{label, url, type}] |
| Featured | Toggle | Shows on homepage |
| Thumbnail | Image upload | Displayed on project card |
| Sort order | Drag handle | Controls display order |
| Visibility | Toggle | Published / Draft |

### Admin page layout
- Left: sortable project list with drag handles
- Right: edit form for the selected project
- Save / Publish / Delete buttons

---

## Section 4 — Articles CMS

**Sprint:** 3 (planned — highest priority content feature)

Replace `src/data/articles.ts`. Write and publish real engineering articles
without committing code or redeploying.

### What you can do
- Write articles in a rich text editor (Markdown or WYSIWYG)
- Save as draft (not visible to public)
- Preview how the article looks before publishing
- Publish with one click — live immediately
- Unpublish without deleting
- Set category, reading time estimate, summary
- Add tags for filtering
- Set a publish date (schedule for future release)
- Edit after publishing (changes show immediately)
- Delete permanently

### Fields per article

| Field | Type | Notes |
|---|---|---|
| Title | Text | |
| Slug | Text | Auto-generated, editable |
| Summary | Text (2–3 sentences) | Shown on article cards |
| Body | Markdown editor | Full article content |
| Category | Select | Backend / FastAPI / AI / System Design / etc. |
| Tags | Multi-select | For filtering and related articles |
| Reading time | Number | Minutes (auto-estimated from word count) |
| Status | Select | Draft / Published / Archived |
| Published at | Date/time | Supports scheduled publishing |
| Cover image | Image upload | Optional OG image |

### Editor requirement
A good Markdown editor with:
- Preview pane
- Syntax highlighting for code blocks
- Image paste-to-upload
- Keyboard shortcuts (Cmd+B for bold, etc.)

Options: **Monaco Editor** (VS Code engine), **CodeMirror**, or a WYSIWYG like **Tiptap**.

---

## Section 5 — Case Studies CMS

**Sprint:** 7 (planned)

Replace `src/data/case-studies.ts`. Each project can have a linked deep-dive
case study with architecture diagrams, code snippets, and engineering decisions.

### What you can do
- Attach a case study to any project
- Write structured sections: Problem, Architecture, Decisions, Challenges, Outcomes
- Add architecture component diagrams (JSON-driven)
- Embed code snippets with syntax highlighting
- Publish / unpublish independently of the linked project

### Sections per case study
1. Problem statement
2. Architecture overview (visual diagram)
3. Technical decisions (table of alternatives considered)
4. Implementation highlights
5. Challenges and solutions
6. Lessons learned
7. What I would do differently

---

## Section 6 — Resume CMS

**Sprint:** 6 (planned)

Replace `src/data/resume.ts`. Update your experience without opening a code editor.

### What you can do
- Add / edit / remove work experience entries
- Update the tech skills list (grouped by category)
- Update education
- Add certifications and their status (Completed / In progress / Planned)
- Toggle "Open to download PDF" (links to the PDF export)
- Reorder entries with drag handles

### Sections managed

| Section | Examples |
|---|---|
| Work experience | Company, title, date range, description, tech used |
| Skills | Backend / Frontend / AI / DevOps groups |
| Education | Degree, institution, year |
| Certifications | AWS SAA, name, status, date |
| Technical strengths | 4–6 narrative strengths shown on resume page |

---

## Section 7 — Site Settings

**Sprint:** 5 (planned)

### 7.1 Availability (open to work toggle)

The single most impactful "settings" feature for a portfolio.
Recruiters land on your site and immediately know if you're available.

What you can set:
- Status: `open` / `not looking` / `open to conversations`
- Available from date
- Short message: "Available for backend roles from August 2026"
- Notice period
- Preferred work type: remote / hybrid / on-site / any

Displayed on: homepage hero, about page, contact page, resume page.

### 7.2 Profile settings

| Field | Notes |
|---|---|
| Display name | Shown in the admin nav and public bio |
| Headline | Shown on homepage ("Python Backend Engineer") |
| Bio | 2–3 sentence about paragraph |
| Location | City, country |
| GitHub URL | |
| LinkedIn URL | |
| X (Twitter) URL | |

### 7.3 Password change

Form with: current password → new password → confirm.
All existing sessions revoked on change (already built in Sprint 1).

---

## Section 8 — Analytics

**Sprint:** 5 (planned)

Server-side analytics — no Google Analytics, no cookie consent banner needed.

### What you can see

| View | Shows |
|---|---|
| Overview | Total views last 7 days / 30 days / all time |
| Top pages | Which pages are visited most |
| Top projects | Which project cards are clicked most |
| Top articles | Which articles are read and for how long |
| Referrers | LinkedIn, Google, GitHub, direct |
| Countries | Where visitors come from (no city, no full IP) |

### What is NOT tracked (privacy)
- No full IP addresses stored
- No fingerprinting
- No cross-site tracking
- No cookie required
- Only the domain of the referrer (not the full URL)

### Admin chart types
- Line chart: views over time (7d / 30d / 90d)
- Bar chart: top 10 projects by views
- Pie chart: traffic sources
- Table: full page list sorted by views

---

## Section 9 — Newsletter

**Sprint:** 5 (planned)

### What you can do
- See the list of all subscribers (email, source page, signup date)
- Mark subscriber as confirmed / unconfirmed
- Delete / unsubscribe a subscriber (GDPR)
- Export subscriber list as CSV
- See total count on the dashboard widget

### What you cannot do (intentionally out of scope)
- Send newsletters from this admin panel (use Resend, Mailchimp, or Buttondown for that)
- Design email templates inside the portfolio admin

The admin panel manages the list. Sending emails is delegated to a dedicated
email platform that is better suited for that job.

---

## Section 10 — Activity Log

**Sprint:** already partially built (admin_audit_logs table exists)

A read-only log of every admin action with timestamp, action type, and affected resource.

### What it shows

| Column | Example |
|---|---|
| When | 2026-07-06 09:45:12 |
| Action | `admin.contact_message.archived` |
| Resource | Contact message #A1B2C3 |
| IP address | 1.2.3.4 |

### Existing audit events (Sprint 1 + 2)
- Login success / failure
- Logout
- Token refresh
- Password changed
- Sessions revoked
- Contact message: viewed / marked_read / marked_unread / archived / deleted

### Future audit events
- Project created / updated / deleted / published
- Article created / updated / published / unpublished
- Availability status changed
- Newsletter subscriber deleted
- Resume updated

---

## Recommended sprint order

| Sprint | Feature | Why now |
|---|---|---|
| Sprint 3 | Articles CMS | Highest content ROI — publish real writing |
| Sprint 4 | Projects CMS + Availability toggle | Core portfolio content |
| Sprint 5 | Analytics + Newsletter + Site Settings | Growth and presence |
| Sprint 6 | Resume CMS | Keeps resume accurate without code |
| Sprint 7 | Case Studies CMS | Deep engineering credibility |
| Sprint 8 | Dashboard widgets | Tie everything together in one view |
| Sprint 9 | RSS feed + Sitemap + Search | Discoverability |
| Sprint 10 | Contact Messages enhancements (bulk, notes) | Polish |

---

## Admin navigation (final state)

```
┌─────────────────────────────────────────────────────────┐
│  🛡 Admin        Dashboard  Messages  Content  Settings │
│                                        ↓                 │
│                               Projects / Articles /      │
│                               Case Studies / Resume      │
└─────────────────────────────────────────────────────────┘
```

| Nav item | Sub-items | Sprint |
|---|---|---|
| Dashboard | — | 10 |
| Messages | — | ✅ 2 |
| Content | Projects, Articles, Case Studies, Resume | 3–7 |
| Analytics | — | 5 |
| Newsletter | — | 5 |
| Settings | Availability, Profile, Password | 5 |
| Activity Log | — | already exists (audit table) |
