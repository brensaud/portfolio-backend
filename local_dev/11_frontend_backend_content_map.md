# Frontend Content — What Comes From Backend vs What Is Local

A clear breakdown of every piece of content in the frontend and where it lives.

---

## Summary

```
Frontend content
├── Hardcoded in TypeScript files (src/data/)   ← NO backend needed
│     Projects, articles, resume, engineering, case studies
│
├── Sent TO the backend (user input)
│     Contact form submission
│
├── Fetched FROM the backend (API calls)
│     Contact form acknowledgement (reference ID)
│     Admin: login session, all contact message management
│
└── Infrastructure only (no content)
      Health check  ← used by Docker / load balancers, not shown in UI
```

---

## Content that is hardcoded in the frontend (no backend needed)

These files live in `frontend/src/data/` and are compiled into the
static bundle at build time. Changing them requires a frontend redeploy.

| File | Page | What it contains |
|---|---|---|
| `src/data/projects.ts` | `/work` | Project cards — title, tech stack, description, status, links |
| `src/data/articles.ts` | `/writing` | Blog/article list — title, category, reading time, status |
| `src/data/resume.ts` | `/resume` | Work history, skills, education, certifications |
| `src/data/engineering.ts` | `/engineering` | Engineering principles and notes |
| `src/data/case-studies.ts` | `/work/:slug` | Detailed case studies for projects |
| `src/data/architecture/` | `/architecture` | System architecture diagrams and explanations |
| `src/constants/site.ts` | All pages | Site name, author name, social links, meta tags |
| `src/constants/navigation.ts` | Navbar/footer | Navigation menu items |

### What this means

- The portfolio can be fully browsed (Home, About, Work, Writing, Resume, Engineering)
  with the backend completely offline.
- No API call is made for any of these pages.
- To update a project, article, or skill — edit the `.ts` file and redeploy the frontend.

---

## Content sent TO the backend (frontend → backend)

### 1. Contact form submission

**Page:** `/contact`
**File:** `src/lib/contact-api.ts`
**Endpoint:** `POST /api/v1/contact/messages`

The public contact form sends a JSON payload to the backend:

```json
{
  "name": "Jane Smith",
  "email": "jane@example.com",
  "subject": "Hiring inquiry",
  "message": "Hello, I'd like to discuss..."
}
```

The backend:
- Validates all fields (required, max lengths, email format)
- Saves the message to the PostgreSQL database
- Optionally sends an email notification
- Returns a reference ID to the frontend

The frontend only shows a success message after the backend confirms.
If the backend is offline, the contact form fails with an error.

---

## Content received FROM the backend (backend → frontend)

### 1. Contact form acknowledgement

**Endpoint:** `POST /api/v1/contact/messages` → response
**Used by:** `/contact` page — success state

```json
{
  "id": "uuid",
  "message": "Your message has been received. I'll respond within 48 hours.",
  "reference_id": "MSG-A1B2C3D4"
}
```

The frontend shows this `reference_id` as a confirmation to the user.
The success message text also comes from the backend (not hardcoded in the frontend).

---

### 2. Admin authentication — login response

**Endpoint:** `POST /admin/api/auth/login`
**Used by:** `/admin/login` page

```json
{
  "email": "admin@example.com",
  "expires_at": "2026-07-06T10:15:00Z"
}
```

The backend also sets two HTTPOnly cookies (invisible to JavaScript):
- `access_token` — JWT valid for 15 minutes
- `refresh_token` — valid for 24 hours

The frontend stores only `email` and `expires_at` in React state.
The actual auth token never appears in JavaScript.

---

### 3. Admin — current session identity

**Endpoint:** `GET /admin/api/auth/me`
**Used by:** Every admin page (on mount, to restore session after page refresh)

```json
{
  "email": "admin@example.com",
  "expires_at": "2026-07-06T10:15:00Z"
}
```

If this returns 401, the admin is redirected to `/admin/login`.

---

### 4. Admin — contact message list

**Endpoint:** `GET /admin/api/contact-messages`
**Used by:** `/admin/contact-messages` page
**Query params:** `page`, `page_size`, `status`, `search`, `sort`

```json
{
  "items": [
    {
      "id": "uuid",
      "name": "Jane Smith",
      "email": "jane@example.com",
      "subject": "Hiring inquiry",
      "status": "unread",
      "created_at": "2026-07-05T09:00:00Z",
      "updated_at": "2026-07-05T09:00:00Z"
    }
  ],
  "total": 42,
  "page": 1,
  "page_size": 20,
  "pages": 3
}
```

Note: the `message` body is NOT included in list responses to minimise data exposure.

---

### 5. Admin — single message detail

**Endpoint:** `GET /admin/api/contact-messages/{id}`
**Used by:** Message detail dialog in `/admin/contact-messages`

```json
{
  "id": "uuid",
  "name": "Jane Smith",
  "email": "jane@example.com",
  "subject": "Hiring inquiry",
  "message": "Hello, I'd like to discuss a backend engineering opportunity.",
  "status": "read",
  "ip_address": "1.2.3.4",
  "user_agent": "Mozilla/5.0...",
  "created_at": "2026-07-05T09:00:00Z",
  "updated_at": "2026-07-06T08:00:00Z"
}
```

This is the only endpoint that returns the full message body and metadata.

---

### 6. Admin — status mutation responses

All status change endpoints return the updated message detail:

| Action | Endpoint | What changes |
|---|---|---|
| Mark as read | `PATCH /admin/api/contact-messages/{id}/read` | `status` → `"read"` |
| Mark as unread | `PATCH /admin/api/contact-messages/{id}/unread` | `status` → `"unread"` |
| Archive | `PATCH /admin/api/contact-messages/{id}/archive` | `status` → `"archived"` |
| Delete | `DELETE /admin/api/contact-messages/{id}` | 204 No Content (no body) |

---

## Complete endpoint map

| Endpoint | Direction | Public/Admin | Used on page |
|---|---|---|---|
| `GET /health` | Backend → (infra only) | Public | Not shown in UI |
| `POST /api/v1/contact/messages` | Frontend → Backend | Public | `/contact` |
| `POST /admin/api/auth/login` | Frontend → Backend | Admin | `/admin/login` |
| `POST /admin/api/auth/logout` | Frontend → Backend | Admin | Admin nav bar |
| `GET /admin/api/auth/me` | Backend → Frontend | Admin | All admin pages |
| `POST /admin/api/auth/refresh` | Frontend → Backend | Admin | Automatic (token renewal) |
| `GET /admin/api/contact-messages` | Backend → Frontend | Admin | `/admin/contact-messages` |
| `GET /admin/api/contact-messages/{id}` | Backend → Frontend | Admin | Message detail dialog |
| `PATCH /admin/api/contact-messages/{id}/read` | Frontend → Backend | Admin | Message detail / row action |
| `PATCH /admin/api/contact-messages/{id}/unread` | Frontend → Backend | Admin | Message detail / row action |
| `PATCH /admin/api/contact-messages/{id}/archive` | Frontend → Backend | Admin | Message detail / row action |
| `DELETE /admin/api/contact-messages/{id}` | Frontend → Backend | Admin | Message detail / row action |

---

## What works without the backend

| Feature | Works offline? | Why |
|---|---|---|
| Home page | ✅ Yes | Hardcoded in `src/data/` |
| About page | ✅ Yes | Static content |
| Work / Projects | ✅ Yes | `src/data/projects.ts` |
| Writing / Blog | ✅ Yes | `src/data/articles.ts` |
| Resume | ✅ Yes | `src/data/resume.ts` |
| Engineering | ✅ Yes | `src/data/engineering.ts` |
| Architecture | ✅ Yes | `src/data/architecture/` |
| Contact form | ❌ No | Needs `POST /api/v1/contact/messages` |
| Admin panel | ❌ No | Needs all `/admin/api/auth/*` and `/admin/api/contact-messages/*` |

---

## What requires a database

| Feature | Needs database? | Why |
|---|---|---|
| All public portfolio pages | ❌ No | All content is in TypeScript files |
| Contact form submission | ✅ Yes | Messages saved to `contact_messages` table |
| Admin login | ✅ Yes | Auth audit log written to `admin_audit_logs` table |
| Admin contact message list | ✅ Yes | Reads `contact_messages` table |
| Admin status changes | ✅ Yes | Writes to `contact_messages` + `admin_audit_logs` |

---

## Adding new content — where to put it

| What you want to add | Where to add it | Backend needed? |
|---|---|---|
| New project card | `src/data/projects.ts` | No |
| New blog article | `src/data/articles.ts` | No |
| New resume entry | `src/data/resume.ts` | No |
| Dynamic blog posts (CMS) | New backend endpoint + frontend fetch | Yes |
| Portfolio analytics | New backend endpoint | Yes |
| Email notifications on contact | Already in backend `email_service.py` | Already exists |
| Multiple admin users | New backend feature (not yet built) | Yes |
