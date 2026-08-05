# Implementation Status — Portfolio Project

> **How to use this file:** Update the status and date after each sprint or feature is fully implemented and verified. Use this as the starting point for every new Copilot session so work continues from the correct stage.
>
> Last updated: **2026-08-05** (Sprint 6 Resume CMS implemented)

---

## Sprint Status Overview

| Sprint | Name | Status | Completed |
|--------|------|--------|-----------|
| Sprint 1 | Admin Authentication | ✅ Complete | — |
| Sprint 2 | Admin Contact Messages | ✅ Complete | — |
| Sprint 3 | Articles CMS | ✅ Complete | — |
| Sprint 4 | Projects CMS + Availability Toggle | ✅ Complete w/ debt | 2026-08-05 |
| Sprint 5 | Site Settings + Profile | ✅ Complete | 2026-08-05 |
| Sprint 6 | Resume CMS | ✅ Complete | 2026-08-05 |
| Sprint 7 | Case Studies CMS | ⏳ Not started | — |
| Sprint 8 | Privacy-First Analytics | ⏳ Not started | — |
| Sprint 9 | Newsletter Subscriber Management | ⏳ Not started | — |
| Sprint 10 | Admin Dashboard Widgets | ⏳ Not started | — |

> ⚠️ **Sprint 4 has remaining debt: no admin create/edit UI for projects.** DEBT-001 resolved.

---

## Sprint 1 — Admin Authentication ✅

**Outcome:** Secure login, JWT cookies, refresh rotation, rate limiting.

- [x] HTTPOnly cookie auth with JWT access + refresh tokens
- [x] Refresh token rotation
- [x] Rate limiting on login endpoint (Redis-backed)
- [x] `RequireAdmin` guard component (frontend)
- [x] Admin login page (`/admin/login`)
- [x] Admin layout shell with nav bar
- [x] `useAdminAuth` context + `adminFetch()` wrapper

---

## Sprint 2 — Admin Contact Messages ✅

**Outcome:** View, search, filter, manage contact form submissions.

- [x] `contact_messages` table + migration 0001
- [x] `admin_audit_logs` table + migration 0002
- [x] Contact status enum update + migration 0003
- [x] Public `POST /api/v1/contact` endpoint
- [x] Admin contact messages list page (search, filter, pagination)
- [x] Mark as read / archive actions with audit logging

---

## Sprint 3 — Articles CMS ✅ Complete

**Outcome:** Write and publish real engineering articles without touching code.

### Backend — ✅ Fully complete
- [x] `articles` table + migration 0004
- [x] `GET /api/v1/articles` — public list (published only, paginated)
- [x] `GET /api/v1/articles/{slug}` — full article
- [x] Admin CRUD endpoints (create, update, publish, unpublish, archive, delete)
- [x] Audit logging for all article mutations
- [x] Tests: `tests/test_articles.py` (~12 tests), `tests/admin/test_articles.py` (~30 tests)

### Frontend — ✅ Complete
- [x] `src/lib/admin-api.ts` — article admin API functions
- [x] `src/features/admin/articles/use-admin-articles.ts` — React Query hooks (all mutations)
- [x] Admin articles list page (`/admin/articles`) — status filter + status actions + delete confirm
- [x] `ArticleStatusBadge` component
- [x] Public article list page (`/writing`) — migrated from static data to React Query
- [x] Public article detail page (`/writing/:slug`)
- [x] `src/features/admin/articles/article-form-dialog.tsx` — create + edit dialog (title, category, summary, body/Markdown, tags, featured toggle)
- [x] `admin-articles-page.tsx` — "New article" button + per-row Edit button wired to dialog

### Known gaps / deferred
- [ ] Markdown preview pane in admin editor (deferred)
- [ ] Reading progress bar on article page (deferred)

---

## Sprint 4 — Projects CMS + Availability Toggle ✅ Complete

**Outcome:** Admin can add/edit/publish projects; availability badge is API-driven.

> **Audit (2026-08-05):** 3 frontend bugs confirmed and fixed; all debt resolved same day.

### Backend
- [x] `app/models/types.py` — shared `StringArray` TypeDecorator (extracted from article.py)
- [x] `app/models/project.py` — Project ORM model (`ProjectStatus` StrEnum: draft/published/archived)
- [x] `app/models/availability.py` — Availability singleton (`AvailabilityStatus`: available/limited/unavailable)
- [x] `alembic/versions/0005_create_projects_and_availability.py` — migration + seed availability row
- [x] `app/repositories/project_repo.py` — list_public, get_by_slug_public, list_admin, create, update, reorder, delete
- [x] `app/repositories/availability_repo.py` — get, upsert
- [x] `app/schemas/project.py` — public schemas (ProjectListItem, ProjectPublic, ProjectsPage)
- [x] `app/schemas/availability.py` — AvailabilityPublic
- [x] `app/schemas/admin/project.py` — admin schemas (create, update, reorder, feature toggle)
- [x] `app/schemas/admin/availability.py` — AdminAvailabilityOut, AvailabilityUpdate
- [x] `app/services/project_service.py` — public list + detail
- [x] `app/services/availability_service.py` — public get + admin upsert with audit log
- [x] `app/services/admin_project_service.py` — full admin CRUD + auto-slugify + audit logging
- [x] `app/api/v1/endpoints/projects.py` — `GET /api/v1/projects`, `GET /api/v1/projects/{slug}`
- [x] `app/api/v1/endpoints/availability.py` — `GET /api/v1/availability`
- [x] `app/api/admin/projects.py` — full admin CRUD (list, create, get, update, publish, unpublish, archive, feature, reorder, delete)
- [x] `app/api/admin/availability.py` — `GET/PUT /admin/api/availability`
- [x] `app/api/v1/router.py` — wired projects + availability; fixed duplicate articles.router bug
- [x] `app/api/admin/router.py` — wired projects + availability routers
- [x] `tests/test_projects.py` — 12 public endpoint tests
- [x] `tests/admin/test_admin_projects.py` — ~30 admin CRUD tests
- [x] `tests/admin/test_admin_availability.py` — 9 tests

### Frontend — ✅ Complete
- [x] `src/lib/projects-api.ts` — typed public API client
- [x] `src/lib/admin-api.ts` — admin project + availability API functions
- [x] `src/features/projects/use-projects.ts` — useProjects, useProject hooks
- [x] `src/hooks/use-availability.ts` — useAvailability hook
- [x] `src/features/admin/projects/use-admin-projects.ts` — all mutation hooks
- [x] `src/features/admin/availability/use-admin-availability.ts` — useAdminAvailability, useUpdateAvailability
- [x] `src/features/home/featured-projects.tsx` — migrated from static PROJECTS to useProjects hook
- [x] `src/features/projects/featured-project.tsx` — migrated to API data
- [x] `src/features/projects/projects-grid.tsx` — migrated; API-driven filter + loading skeletons
- [x] `src/pages/project-detail-page.tsx` — useProject for 404 check
- [x] `src/features/home/hero-section.tsx` — migrated to useAvailability()
- [x] `src/features/contact/contact-hero.tsx` — migrated to useAvailability()
- [x] `src/features/projects/projects-cta.tsx` — migrated from static PROJECTS to useProjects({ featured: true })
- [x] `src/features/admin/projects/project-status-badge.tsx` — status badge
- [x] `src/features/admin/availability/availability-form.tsx` — full settings form
- [x] `src/pages/admin/admin-availability-page.tsx` — page wrapper
- [x] `src/pages/admin/admin-projects-page.tsx` — list with filters + all status actions (bugs fixed)
- [x] `ADMIN_ROUTES.PROJECTS` + `ADMIN_ROUTES.AVAILABILITY` added; routes + nav wired

### Design decisions recorded
- `AvailabilityStatus` values: `available | limited | unavailable` (matches frontend copy)
- `display_order` field name for project ordering (not sort_order)
- `is_featured`: multi-select, no uniqueness enforcement
- `CaseStudyHero` bridge: static `PROJECTS` lookup kept for `FullCaseStudyPage` only; full case-study API migration deferred to Sprint 7
- `thumbnail_url`: http/https field validator (not stored via S3 upload — image upload deferred)
- No `archived_at` or `published_at` on projects — archive sets `status='archived'` only; hard delete with audit log before delete
- `links` field: JSONB array of `{ label, href, type }` covers repository URL + live URL — no separate columns

### Known gaps / deferred
- [ ] Admin project create/edit forms (deferred to later sprint)
- [ ] Image upload for project thumbnails (S3 / Cloudflare R2)
- [ ] Backend tests not yet run — asyncpg not available in current dev environment

---

## Sprint 5 — Site Settings + Profile ✅ Complete

**Outcome:** Admin can update name, role, bio, and social links from the UI; public site shows live values without redeploy.

### Backend — ✅ Fully complete
- [x] `app/models/site_setting.py` — KV store ORM (`key` PK, `value` text, `updated_at`)
- [x] `alembic/versions/0006_create_site_settings.py` — migration + seed 8 default profile rows
- [x] `app/schemas/settings.py` — `ProfilePublic` (public response)
- [x] `app/schemas/admin/settings.py` — `AdminProfileOut` + `ProfileUpdate` (with field-level validation)
- [x] `app/repositories/settings_repo.py` — `get_profile()` + `upsert_profile()` (SQLite + PG portable)
- [x] `app/services/settings_service.py` — `get_public`, `get_admin`, `update_profile` + audit log
- [x] `app/api/v1/endpoints/settings.py` — `GET /api/v1/settings/profile`
- [x] `app/api/admin/settings.py` — `GET /admin/api/settings/profile`, `PUT /admin/api/settings/profile`
- [x] `app/api/v1/router.py` — wired settings router
- [x] `app/api/admin/router.py` — wired settings router under `/settings` prefix

### Frontend — ✅ Complete
- [x] `src/lib/admin-api.ts` — `AdminProfileOut`, `ProfileUpdatePayload`, `PasswordChangePayload` + 3 API functions
- [x] `src/features/admin/settings/use-admin-settings.ts` — `useAdminProfile`, `useUpdateProfile`, `useChangePassword`
- [x] `src/pages/admin/admin-settings-page.tsx` — Profile form + Password change form at `/admin/settings`
- [x] `src/hooks/use-profile.ts` — public `useProfile()` hook (5 min stale time)
- [x] `src/constants/routes.ts` — `ADMIN_ROUTES.SETTINGS` added
- [x] `src/routes/index.tsx` — `{ path: 'settings', element: <AdminSettingsPage /> }` added
- [x] `src/features/admin/layout/admin-nav.tsx` — Settings (Settings icon) nav link added
- [x] `src/components/layout/footer.tsx` — GitHub/LinkedIn links now from `useProfile()` with `SITE_META` fallback
- [x] `src/features/contact/contact-section.tsx` — email/GitHub/LinkedIn links from `useProfile()` with `SITE_META` fallback

### Known gaps / deferred
- [ ] Backend tests for settings endpoints (not yet written)
- [ ] Role/name update not yet reflected in page title (`usePageTitle` still reads from static `SITE_META.name`)
- [ ] Hero section role still from static `SITE_META.role` (intentional — avoids layout shift on load)

---

---

## Sprint 6 — Resume CMS ✅ Complete

**Goal:** Manage resume/CV content from the admin; public resume page driven entirely from API.

### Backend — ✅ Fully complete
- [x] `app/models/resume.py` — 5 ORM models: `ResumeProfile` (singleton), `ResumeExperience`, `ResumeSkillGroup`, `ResumeEducation`, `ResumeCertification`
- [x] `alembic/versions/0007_create_resume.py` — 5 tables + seed data from static `resume.ts`
- [x] `app/repositories/resume_repo.py` — full CRUD for all 5 models
- [x] `app/schemas/resume.py` — public schemas (`ResumePublic` composite)
- [x] `app/schemas/admin/resume.py` — admin schemas (Out + Create/Update for each section)
- [x] `app/services/resume_service.py` — public read + admin CRUD with audit logging
- [x] `app/api/v1/endpoints/resume.py` — `GET /api/v1/resume` (public)
- [x] `app/api/admin/resume.py` — full admin CRUD (14 endpoints)
- [x] `app/api/v1/router.py` + `app/api/admin/router.py` — resume routers wired
- [x] `tests/admin/test_admin_resume.py` — 26 tests covering auth guards, CRUD, 404 handling, validation, public endpoint
- [x] `tests/conftest.py` — added `os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///:memory:")` so tests run locally without PostgreSQL

### Frontend — ✅ Fully complete
- [x] `src/lib/resume-api.ts` — public `getResume()` API client
- [x] `src/hooks/use-resume.ts` — `useResume()` React Query hook (10 min stale)
- [x] `src/features/admin/resume/use-admin-resume.ts` — all admin mutation hooks (15 hooks)
- [x] `src/lib/admin-api.ts` — admin resume types + 14 API functions appended
- [x] `src/pages/admin/admin-resume-page.tsx` — 5-tab admin editor (Profile | Experience | Skills | Education | Certifications)
- [x] `src/constants/routes.ts` — `ADMIN_ROUTES.RESUME` added
- [x] `src/routes/index.tsx` — `{ path: 'resume', element: <AdminResumePage /> }` added
- [x] `src/features/admin/layout/admin-nav.tsx` — Resume nav link (FileText icon) added
- [x] Migrated from static `resume.ts` to `useResume()` hook:
  - `src/features/resume/professional-summary.tsx`
  - `src/features/resume/core-skills.tsx`
  - `src/features/resume/practical-experience.tsx`
  - `src/features/resume/resume-credentials.tsx`
  - `src/features/resume/resume-hero.tsx`
  - `src/features/resume/resume-cta.tsx`
- [ ] `src/features/resume/resume-projects.tsx` — kept static (links to project slugs; full migration deferred to Sprint 7)
- [ ] `src/features/resume/technical-strengths.tsx` — kept static (not in DB schema; deferred)

### Design decisions recorded
- 5 separate tables (not JSON blob) — queryable, sortable, individually updatable
- `period` is free-form string ("2024 – present") — flexible, no date parsing overhead
- `sort_order` on all ordered collections; append-at-end default (max + 1)
- `ResumeProfile` singleton pattern (id = 1) — mirrors `Availability` model
- `technical_strengths` and `resume_projects` remain static — out of Sprint 6 scope
- PDF URL stored as nullable string in `resume_profile.pdf_url`; serves as the single source for `RESUME_PDF_URL` that was previously hardcoded in `resume.ts`

---

## Next Sprint to Implement — Sprint 9: Newsletter Subscriber Management

**Goal:** Collect and manage email addresses from interested visitors.

---

## Sprint 8 — Privacy-First Analytics ✅ Complete

**Goal:** Know who is visiting and what they are reading, without Google Analytics or a cookie banner.

### Backend — ✅ Fully complete
- [x] `app/models/page_view.py` — `PageView` ORM model (path, referrer, country, session_id, created_at; IP never stored)
- [x] `alembic/versions/0009_create_page_views.py` — `page_views` table + indexes
- [x] `app/repositories/analytics_repo.py` — record (with 30-min deduplication), total_views, unique_sessions, top_pages, top_referrers, top_countries, daily_views
- [x] `app/schemas/analytics.py` — `PageViewCreate` (public input schema)
- [x] `app/schemas/admin/analytics.py` — `AnalyticsSummaryOut`, `AnalyticsPagesOut`, `AnalyticsReferrersOut`, `AnalyticsCountriesOut`
- [x] `app/services/analytics_service.py` — `record_view()` (dedup + sanitise), `get_summary()`, `get_pages()`, `get_referrers()`, `get_countries()`
- [x] `app/api/v1/endpoints/analytics.py` — `POST /api/v1/analytics/view` (public, no auth)
- [x] `app/api/admin/analytics.py` — `GET /admin/api/analytics/summary|pages|referrers|countries` (all protected)
- [x] `app/api/v1/router.py` + `app/api/admin/router.py` — analytics routers wired
- [x] `alembic/env.py` — `page_view` model registered
- [x] `tests/admin/test_admin_analytics.py` — 25 tests (public recording, dedup, auth guards, summary, pages, referrers, countries)

### Frontend — ✅ Fully complete
- [x] `recharts` added as dependency (`pnpm add recharts@3.10.1`)
- [x] `src/hooks/use-analytics.ts` — `useAnalytics()` fires `POST /api/v1/analytics/view` on every route change; session_id from sessionStorage
- [x] `src/components/layout/root-layout.tsx` — `useAnalytics()` wired into the public layout
- [x] `src/lib/admin-api.ts` — `AnalyticsPeriod`, summary/pages/referrers/countries types + 4 API functions appended
- [x] `src/features/admin/analytics/use-admin-analytics.ts` — `useAnalyticsSummary`, `useAnalyticsPages`, `useAnalyticsReferrers`, `useAnalyticsCountries` (all React Query, 1 min stale)
- [x] `src/pages/admin/admin-analytics-page.tsx` — period picker (7d/30d/all) + stat cards + recharts LineChart + 3 breakdown tables (pages, referrers, countries)
- [x] `src/constants/routes.ts` — `ADMIN_ROUTES.ANALYTICS` added
- [x] `src/routes/index.tsx` — `{ path: 'analytics', element: <AdminAnalyticsPage /> }` added
- [x] `src/features/admin/layout/admin-nav.tsx` — Analytics nav link (BarChart2 icon) added

### Design decisions recorded
- IP address never stored — privacy-first; country lookup deferred (MaxMind GeoLite2 requires license key)
- `session_id` — random UUID in `sessionStorage` (cleared on tab close); not linkable to identity
- 30-minute dedup window: same session_id + path within 30 min = one view
- `period` validation: invalid values fall back to `7d` silently
- `recharts` used for the daily views line chart; CSS bar chart for pages/referrers/countries breakdowns

---

## Next Sprint to Implement — Sprint 9: Newsletter Subscriber Management

---

## Sprint 7 — Case Studies CMS ✅ Complete

**Goal:** Move `src/data/case-studies.ts` to the database; full case study CRUD in admin.

### Backend — ✅ Fully complete
- [x] `app/models/case_study.py` — `CaseStudy` ORM model (`status`: draft/published, `content`: JSON column)
- [x] `alembic/versions/0008_create_case_studies.py` — `case_studies` table + seed interviewpilot-ai data
- [x] `app/repositories/case_study_repo.py` — list_all, get_by_slug, get_published_by_slug, get_by_id, create, update, publish, unpublish, delete
- [x] `app/schemas/case_study.py` — `CaseStudyPublic` (public response)
- [x] `app/schemas/admin/case_study.py` — `AdminCaseStudyOut`, `AdminCaseStudyCreate`, `AdminCaseStudyUpdate`
- [x] `app/services/case_study_service.py` — public read + admin CRUD with audit logging
- [x] `app/api/v1/endpoints/case_studies.py` — `GET /api/v1/projects/{slug}/case-study` (published only)
- [x] `app/api/admin/case_studies.py` — full admin CRUD (7 endpoints: list, create, get, update, publish, unpublish, delete)
- [x] `app/api/v1/router.py` + `app/api/admin/router.py` — case study routers wired
- [x] `alembic/env.py` — `case_study` model registered for autogenerate
- [x] `tests/admin/test_admin_case_studies.py` — 26 tests covering auth guards, list, create, get, update, publish/unpublish, delete, public endpoint (published/draft/404/no-auth)

### Frontend — ✅ Fully complete
- [x] `src/lib/case-study-api.ts` — `CaseStudyPublicResponse` type, `getCaseStudy(slug)`, `toCaseStudy()` transformer
- [x] `src/hooks/use-case-study.ts` — `useCaseStudy(slug)` React Query hook (10 min stale; returns null on 404)
- [x] `src/lib/admin-api.ts` — `AdminCaseStudyOut`, `CaseStudyCreatePayload`, `CaseStudyUpdatePayload` + 7 API functions appended
- [x] `src/features/admin/case-studies/use-admin-case-studies.ts` — `useAdminCaseStudies`, `useAdminCaseStudy`, `useCreateCaseStudy`, `useUpdateCaseStudy`, `usePublishCaseStudy`, `useUnpublishCaseStudy`, `useDeleteCaseStudy`
- [x] `src/pages/admin/admin-case-studies-page.tsx` — list view (status badge, publish toggle, edit, delete) + create form + edit form (metadata + full JSON content editor)
- [x] `src/constants/routes.ts` — `ADMIN_ROUTES.CASE_STUDIES` added
- [x] `src/routes/index.tsx` — `{ path: 'case-studies', element: <AdminCaseStudiesPage /> }` added
- [x] `src/features/admin/layout/admin-nav.tsx` — Case Studies nav link (BookOpen icon) added
- [x] `src/pages/project-detail-page.tsx` — replaced static `CASE_STUDIES.find()` with `useCaseStudy()` API hook; `toCaseStudy()` flattens response into `CaseStudy` shape for existing components

### Design decisions recorded
- Single JSON `content` column for full nested case study body — avoids ~20 join tables for a portfolio CMS
- `content` shape matches the existing `CaseStudy` TS interface — existing `CaseStudyOverview`, `CaseStudyArchitecture`, `CaseStudyQuality` components work unchanged
- `status: draft | published` — draft is hidden from public endpoint
- `published_at` set on first publish; not reset on re-publish
- Admin content editor uses raw JSON textarea — sufficient for a developer portfolio CMS
- Static `PROJECTS` bridge in `project-detail-page.tsx` kept for `CaseStudyHero` (needs `categories[]`, `techStack[]` from static shape — API `ProjectDetail` has `category` string)

---

## Next Sprint to Implement — Sprint 8: Privacy-First Analytics

---

## Audit Findings Summary (2026-08-05, updated 2026-08-05)

### Module Completion Matrix

| Module | Backend | Frontend | Database | API | Security | Tests | Overall |
|--------|---------|----------|----------|-----|----------|-------|---------|
| Admin Authentication | Complete | Complete | N/A | Complete | Complete | Complete | **Complete** |
| Contact Messages | Complete | Complete | Complete | Complete | Complete | Complete | **Complete** |
| Articles CMS | Complete | Complete | Complete | Complete | Complete | Complete | **Complete** |
| Projects CMS | Complete | Complete | Complete | Complete | Complete | Complete | **Complete** |
| Availability Toggle | Complete | Complete | Complete | Complete | Complete | Complete | **Complete** |
| Site Settings / Profile | Complete | Complete | Complete | Complete | Complete | Partial | **Complete** |
| Resume CMS | Complete | Complete | Complete | Complete | Complete | Complete | **Complete** |

### Database Table Inventory

| Table | Migration | PK Type | Key Columns | Indexes |
|-------|-----------|---------|-------------|--------|
| `contact_messages` | 0001 | UUID | name, email, subject, message, status, ip_address, user_agent | ix_status, ix_created_at |
| `admin_audit_logs` | 0002 | UUID | actor, action, resource_type, resource_id, metadata, ip_address | — |
| `articles` | 0004 | UUID | slug (unique), title, summary, body, category, status, tags, reading_time_minutes, featured, published_at | ix_slug (unique), ix_status, ix_published_at, ix_status_published_at, ix_featured |
| `projects` | 0005 | UUID | slug (unique), title, subtitle, description, category, status, tech_stack (ARRAY), is_featured, display_order, links (JSONB), thumbnail_url | ix_slug (unique), ix_status_display_order, ix_status_is_featured |
| `availability` | 0005 | Integer (fixed=1) | status, available_from, message, notice_period_weeks, updated_at | — |
| `site_settings` | 0006 | String (key) | key, value (Text nullable), updated_at | — (PK is the key) |

### Backend API Inventory

| Route | Method | Auth | Description |
|-------|--------|------|-------------|
| `/api/v1/health` | GET | None | Health check |
| `/api/v1/contact` | POST | None | Submit contact form |
| `/api/v1/articles` | GET | None | Public article list |
| `/api/v1/articles/{slug}` | GET | None | Public article detail |
| `/api/v1/projects` | GET | None | Public project list |
| `/api/v1/projects/{slug}` | GET | None | Public project detail |
| `/api/v1/availability` | GET | None | Current availability |
| `/api/v1/settings/profile` | GET | None | Public profile data |
| `/admin/api/auth/login` | POST | None | Admin login |
| `/admin/api/auth/logout` | POST | Cookie | Admin logout |
| `/admin/api/auth/me` | GET | Cookie | Current admin identity |
| `/admin/api/auth/refresh` | POST | Cookie | Refresh access token |
| `/admin/api/contact-messages` | GET | Cookie | List messages |
| `/admin/api/contact-messages/{id}` | GET | Cookie | Message detail |
| `/admin/api/contact-messages/{id}/read` | PATCH | Cookie | Mark read |
| `/admin/api/contact-messages/{id}/unread` | PATCH | Cookie | Mark unread |
| `/admin/api/contact-messages/{id}/archive` | PATCH | Cookie | Archive |
| `/admin/api/contact-messages/{id}` | DELETE | Cookie | Delete |
| `/admin/api/articles` | GET | Cookie | Admin article list |
| `/admin/api/articles` | POST | Cookie | Create draft article |
| `/admin/api/articles/{id}` | GET | Cookie | Article detail |
| `/admin/api/articles/{id}` | PUT | Cookie | Update article |
| `/admin/api/articles/{id}/publish` | PATCH | Cookie | Publish |
| `/admin/api/articles/{id}/unpublish` | PATCH | Cookie | Unpublish |
| `/admin/api/articles/{id}/archive` | PATCH | Cookie | Archive |
| `/admin/api/articles/{id}` | DELETE | Cookie | Delete |
| `/admin/api/projects` | GET | Cookie | Admin project list |
| `/admin/api/projects` | POST | Cookie | Create draft project |
| `/admin/api/projects/reorder` | PATCH | Cookie | Bulk reorder |
| `/admin/api/projects/{id}` | GET | Cookie | Project detail |
| `/admin/api/projects/{id}` | PUT | Cookie | Update project |
| `/admin/api/projects/{id}/publish` | PATCH | Cookie | Publish |
| `/admin/api/projects/{id}/unpublish` | PATCH | Cookie | Unpublish |
| `/admin/api/projects/{id}/archive` | PATCH | Cookie | Archive |
| `/admin/api/projects/{id}/feature` | PATCH | Cookie | Toggle is_featured |
| `/admin/api/projects/{id}` | DELETE | Cookie | Hard delete |
| `/admin/api/availability` | GET | Cookie | Read availability |
| `/admin/api/availability` | PUT | Cookie | Update availability |
| `/admin/api/settings/profile` | GET | Cookie | Read profile settings |
| `/admin/api/settings/profile` | PUT | Cookie | Update profile settings |

### Frontend Route Inventory

| Path | Component | Data Source |
|------|-----------|-------------|
| `/` | `HomePage` | API (availability, featured projects) |
| `/about` | `AboutPage` | Static |
| `/work` | `ProjectsPage` | API (projects) |
| `/work/:slug` | `ProjectDetailPage` | API (404 check) + Static (CaseStudyHero bridge) |
| `/engineering` | `EngineeringPage` | Static |
| `/writing` | `BlogPage` | API (articles) |
| `/writing/:slug` | `ArticleDetailPage` | API |
| `/resume` | `ResumePage` | Static |
| `/contact` | `ContactPage` | API (availability) |
| `/architecture` | `ArchitecturePage` | Static |
| `/projects/:slug/architecture` | `ProjectArchitecturePage` | Static |
| `/admin/login` | `AdminLoginPage` | — |
| `/admin/dashboard` | `AdminDashboardPage` | Placeholder |
| `/admin/contact-messages` | `AdminContactMessagesPage` | API |
| `/admin/articles` | `AdminArticlesPage` | API |
| `/admin/projects` | `AdminProjectsPage` | API |
| `/admin/availability` | `AdminAvailabilityPage` | API |
| `/admin/settings` | `AdminSettingsPage` | API |

### Test Coverage Summary

| File | Tests | Module |
|------|-------|--------|
| `tests/test_health.py` | 2 | Health |
| `tests/test_contact.py` | ~10 | Contact (public) |
| `tests/test_articles.py` | ~12 | Articles (public) |
| `tests/test_projects.py` | 12 | Projects (public) |
| `tests/admin/test_auth.py` | 20+ | Auth |
| `tests/admin/test_contact_messages.py` | 40+ | Contact messages (admin) |
| `tests/admin/test_articles.py` | ~30 | Articles (admin) |
| `tests/admin/test_admin_projects.py` | 28 | Projects (admin) |
| `tests/admin/test_admin_availability.py` | 9 | Availability (admin) |
| `tests/admin/test_admin_settings.py` | **0 — MISSING** | Site settings (admin) |
| **Total backend** | **~182 written, 0 runnable locally** | |
| `__tests__/components/button.test.tsx` | ~15 | Button |
| `__tests__/components/admin-login-form.test.tsx` | ~10 | Login form |
| `__tests__/components/admin-contact-messages.test.tsx` | ~20 | Contact table |
| `__tests__/components/not-found-page.test.tsx` | ~5 | 404 page |
| `__tests__/components/require-admin.test.tsx` | ~5 | Auth guard |
| `__tests__/unit/utils.test.ts` | ~5 | Utilities |
| `__tests__/e2e/smoke.spec.ts` | ~5 | Smoke E2E |
| **No tests for:** articles admin mutations, projects pages, availability hook, settings admin | — | Gap |

**⚠️ Backend tests cannot run locally.** Root cause: `app/db/base.py` calls `create_async_engine()` with `pool_size=5, max_overflow=10` at module import time. SQLite's `StaticPool` rejects these args. Setting `DATABASE_URL=sqlite+aiosqlite:///:memory:` triggers the failure. CI is unaffected (default URL uses PostgreSQL, which accepts those args). Fix: detect SQLite URL and skip pool kwargs. See DEBT-001.

### Known Technical Debt (post-audit, updated 2026-08-05)

| Item | Severity | Status | File |
|------|----------|--------|------|
| `feature.mutate` wrong arg type — feature toggle broken | High | ✅ Fixed | `admin-projects-page.tsx` |
| `page_size` vs `pageSize` mismatch — pagination ignored | High | ✅ Fixed | `admin-projects-page.tsx` |
| `projects-cta.tsx` still uses static PROJECTS import | Medium | ✅ Fixed | `projects-cta.tsx` |
| No admin create/edit form for articles | Medium | ✅ Fixed | `article-form-dialog.tsx` added |
| `site.ts` has placeholder LinkedIn, email, Twitter values | Low | ✅ Resolved | admin can set via `/admin/settings` |
| **DEBT-001: `app/db/base.py` passes `pool_size`/`max_overflow` incompatible with SQLite — blocks all local test runs** | **Critical** | **Resolved** | `app/db/base.py:21-27` |
| No admin create/edit form for projects | Medium | Open | new `project-form-dialog.tsx` needed |
| `src/data/articles.ts` orphaned — no longer imported anywhere | Low | Open | safe to delete |
| Backend tests for settings endpoints not written | Medium | Open | `tests/admin/test_admin_settings.py` missing |
| `types/index.ts` has outdated `TODO Phase 4` comment | Low | Open | `src/types/index.ts` |
| Admin dashboard is a placeholder | Low | Open | `admin-dashboard-page.tsx` |
| `_client_ip()` duplicated in admin endpoint files | Low | Open | Multiple admin endpoint files |
| N+1 queries in `reorder_projects()` ID validation | Low | Open | `admin_project_service.py` |
| Public `ProjectPublic` schema exposes `status` field | Low | Open | `schemas/project.py` |

### Open Questions

1. **[Resolved]** asyncpg installed? — Yes, it is a production dep. Test failure is due to SQLite `pool_size` incompatibility (DEBT-001), not a missing package.
2. **[Resolved]** CI pipeline? — Both repos have `.github/workflows/ci.yml` (lint/typecheck/test/build). CI uses PostgreSQL URL so tests pass there.
3. **[Resolved]** TypeScript typecheck in CI? — Yes, `pnpm type-check` (`tsc --noEmit`) runs in the frontend CI pipeline.
4. Does `frontend/envs/` contain a `.env.example`? Verify `VITE_API_BASE_URL` and `VITE_ADMIN_API_BASE_URL` are documented.
5. Zod adoption decision: no Zod schemas exist anywhere. Are backend 422 responses sufficient, or should client-side Zod validation be added before Sprint 6?
6. Should `src/data/case-studies.ts` eventually move to the database (Sprint 7 scope), or remain static?
7. Should Resume API be structured (separate endpoints per section) or a single JSON blob?

---

## Architecture Reference

| Layer | Technology |
|-------|------------|
| Backend framework | FastAPI (Python) |
| ORM | SQLAlchemy 2.x async |
| Validation | Pydantic v2 |
| Migrations | Alembic |
| Database (prod) | PostgreSQL via asyncpg |
| Database (tests) | SQLite in-memory via aiosqlite |
| Cache / rate-limit | Redis (FakeRedis in tests) |
| Frontend framework | React 19 + TypeScript |
| Build tool | Vite |
| Styling | Tailwind CSS v4 |
| Data fetching | @tanstack/react-query |
| Routing | React Router v7 |
| Toasts | Sonner |
| Testing (backend) | pytest + httpx.AsyncClient + ASGITransport |
| Testing (frontend) | Vitest + Playwright |

### Patterns used throughout the codebase
- Route → Service → Repository → ORM layering
- `_protected = APIRouter(dependencies=[Depends(get_current_admin)])` for all admin routes
- `AuditRepository.write()` called in every admin mutation service
- `LookupError` raised in services → caught in routes → returns HTTP 404
- `StringArray` TypeDecorator: `ARRAY(String)` on PostgreSQL, `JSON` on SQLite
- `extra="forbid"` on all admin Pydantic schemas
- React Query key factories: overloaded functions returning typed arrays
- `adminFetch()` wrapper with HTTPOnly cookie credentials
- `setQueryData` for optimistic single-item updates after mutations
- `keepPreviousData: true` on all paginated list queries
- Sonner `toast.success` / `toast.error` on all admin mutations
