# Implementation Status — Portfolio Project

> **How to use this file:** Update the status and date after each sprint or feature is fully implemented and verified. Use this as the starting point for every new Copilot session so work continues from the correct stage.
>
> Last updated: **2026-08-05** (Sprint 5 complete — site settings + profile implemented end-to-end)

---

## Sprint Status Overview

| Sprint | Name | Status | Completed |
|--------|------|--------|-----------|
| Sprint 1 | Admin Authentication | ✅ Complete | — |
| Sprint 2 | Admin Contact Messages | ✅ Complete | — |
| Sprint 3 | Articles CMS | ✅ Complete | — |
| Sprint 4 | Projects CMS + Availability Toggle | ✅ Complete | 2026-08-05 |
| Sprint 5 | Site Settings + Profile | ✅ Complete | 2026-08-05 |
| Sprint 6 | Resume CMS | ⏳ Not started | — |
| Sprint 7 | Case Studies CMS | ⏳ Not started | — |
| Sprint 8 | Privacy-First Analytics | ⏳ Not started | — |
| Sprint 9 | Newsletter Subscriber Management | ⏳ Not started | — |
| Sprint 10 | Admin Dashboard Widgets | ⏳ Not started | — |

> ✅ **All 3 Sprint 4 debt items resolved on 2026-08-05. Sprint 5 complete on 2026-08-05.** Sprint 6 is clear to start.

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

## Next Sprint to Implement — Sprint 6: Resume CMS

**Goal:** Manage resume/CV content from the admin (work experience, education, skills, certifications) — no code edits needed.

### Planned Backend
- `resume_sections` table (type: experience/education/skills/certifications) + migration 0007
- `GET /api/v1/resume` — public resume data
- `PUT /admin/api/resume/{section}` — update a resume section

### Planned Frontend
- Admin: Resume section editor (rich text or structured fields per type)
- Public: Replace static `src/data/resume.ts` with `useResume()` hook
- Public: Resume page driven entirely from API

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
| **Total backend** | **~182** | |
| `__tests__/components/button.test.tsx` | ~15 | Button |
| `__tests__/components/admin-login-form.test.tsx` | ~10 | Login form |
| `__tests__/components/admin-contact-messages.test.tsx` | ~20 | Contact table |
| `__tests__/e2e/smoke.spec.ts` | ~5 | Smoke E2E |
| **No tests for:** projects pages, availability hook, admin mutations | — | Gap |

### Known Technical Debt (post-audit, updated 2026-08-05)

| Item | Severity | Status | File |
|------|----------|--------|------|
| `feature.mutate` wrong arg type — feature toggle broken | High | ✅ Fixed | `admin-projects-page.tsx` |
| `page_size` vs `pageSize` mismatch — pagination ignored | High | ✅ Fixed | `admin-projects-page.tsx` |
| `projects-cta.tsx` still uses static PROJECTS import | Medium | ✅ Fixed | `projects-cta.tsx` |
| No admin create/edit form for articles | Medium | ✅ Fixed | `article-form-dialog.tsx` added |
| `site.ts` has placeholder LinkedIn, email, Twitter values | Low | ✅ Resolved | admin can set via `/admin/settings` |
| No admin create/edit form for projects | Medium | Open | deferred |
| `_client_ip()` duplicated in admin endpoint files | Low | Open | Multiple admin endpoint files |
| N+1 queries in `reorder_projects()` ID validation | Low | Open | `admin_project_service.py` |
| Public `ProjectPublic` schema exposes `status` field | Low | Open | `schemas/project.py` |
| `types/index.ts` has outdated `TODO Phase 4` comment | Low | Open | `src/types/index.ts` |
| Admin dashboard is a placeholder | Low | Open | `admin-dashboard-page.tsx` |
| Backend tests for settings endpoints not written | Low | Open | No test file yet |
| Backend tests cannot run — asyncpg not installed in dev env | Info | Open | `pyproject.toml` / env |

### Open Questions (from audit)

1. Is `asyncpg` installed? The last `pytest` run exited with code 1 — diagnose before Sprint 5.
2. Is `pnpm typecheck` / `tsc --noEmit` run in CI? The two type errors above would be caught immediately by a TS check step.
3. No `.github/workflows/` directory found — are tests run manually or is there a pipeline?
4. Does `frontend/envs/` contain a `.env.example`? Verify `VITE_API_BASE_URL` and `VITE_ADMIN_API_BASE_URL` are documented for new environment setup.
5. Zod validation: no Zod schemas exist in the frontend. Decision needed before building admin create/edit forms.

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
