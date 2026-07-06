A

# Admin Login — Setup & Access Guide

Everything needed to get the admin panel working, from first run to signing in.

---

## How admin authentication works

There is **no admin_users database table**. Credentials live entirely in
environment variables on the server:

| Variable                | What it stores                                         |
| ----------------------- | ------------------------------------------------------ |
| `ADMIN_EMAIL`         | Your login email address                               |
| `ADMIN_PASSWORD_HASH` | bcrypt hash of your password (not the password itself) |
| `ADMIN_JWT_SECRET`    | Secret used to sign session tokens                     |

> **Important — what you actually type to log in:**
>
> - `ADMIN_PASSWORD_HASH` is **not** the password you type at the login page.
> - It is a hashed version of your password, stored securely in the environment.
> - When you log in, you type your **plain-text password** (e.g. `MyPassword123!`).
> - The backend hashes what you type and compares it to the stored hash.
> - You choose the plain-text password when you run `python -m app.cli.hash_password`.
>
> **In short:** run the hash generator once → it produces `ADMIN_PASSWORD_HASH`.
> The password you typed into the generator is what you use to log in.

When you log in, the backend compares the submitted password against the stored
hash. If it matches, it issues two HTTPOnly cookies:

- `access_token` — valid for 15 minutes
- `refresh_token` — valid for 24 hours, rotates on each use (stored in Redis)

---

## Step 1 — Make sure the backend is running

Pick one:

```powershell
# Option A — Docker Compose (recommended)
cd backend
docker compose up

# Option B — local uv (no Docker)
cd backend
.venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8000
```

Verify it's up:

```powershell
curl http://localhost:8000/health
# Expected: {"status":"ok","database":"connected",...}
```

---

## Step 2 — Generate a password hash

The backend never stores your plain-text password.
You must generate a bcrypt hash and put it in the environment.

Run the built-in CLI tool:

```powershell
# Docker Compose (backend is running)
docker compose exec backend /app/.venv/bin/python -m app.cli.hash_password

# Docker Compose (backend NOT running yet)
docker compose run --rm --no-deps backend /app/.venv/bin/python -m app.cli.hash_password

# Local uv (no Docker)
cd backend
.venv\Scripts\python.exe -m app.cli.hash_password
```

The tool prompts you twice (no echo):

```
Admin password hash generator
================================
Enter new admin password:
Confirm password:

Your bcrypt hash (copy this into ADMIN_PASSWORD_HASH):
$2b$12$Kq3mNpXv...
```

**Copy the entire `$2b$12$...` string.** You need it in Step 3.

Password requirements:

- Minimum 12 characters (warning shown if shorter)
- Any characters allowed
- The tool uses SHA-256 pre-hashing + bcrypt cost 12 (~0.4 s/verify)

---

## Step 3 — Set the environment variables

Choose the method matching your setup:

### Docker Compose (local dev)

Open `backend/docker-compose.yml` and fill in:

```yaml
ADMIN_EMAIL: you@example.com          # your login email
ADMIN_PASSWORD_HASH: "$2b$12$..."     # paste the hash from Step 2
ADMIN_JWT_SECRET: "change-me-32-chars-minimum-random!!"
```

Generate a proper JWT secret:

```powershell
python -c "import secrets; print(secrets.token_hex(32))"
# Example output: a3f8c2e1d...  (64 hex chars)
```

Restart after editing:

```powershell
docker compose down
docker compose up
```

### Local uv (no Docker)

Open `backend/.env` (copy from `envs/.env.example` if it doesn't exist):

```dotenv
ADMIN_EMAIL=you@example.com
ADMIN_PASSWORD_HASH=$2b$12$...
ADMIN_JWT_SECRET=your-random-secret-min-32-chars-here
ADMIN_JWT_ISSUER=api.brensaud.com
ADMIN_JWT_AUDIENCE=admin.brensaud.com
```

Restart the server after saving.

### Render (production)

Render dashboard → your backend service → **Environment** tab → add/edit:

| Key                     | Value              |
| ----------------------- | ------------------ |
| `ADMIN_EMAIL`         | your login email   |
| `ADMIN_PASSWORD_HASH` | `$2b$12$...`     |
| `ADMIN_JWT_SECRET`    | 64-char random hex |

Save → Render triggers an automatic redeploy.

---

## Step 4 — Log in

Open the admin login page:

| Environment         | URL                               |
| ------------------- | --------------------------------- |
| Local (Docker / uv) | http://localhost:5173/admin/login |
| Production          | https://brensaud.com/admin/login  |

Fill in the form:

| Field              | What to enter                                                                |
| ------------------ | ---------------------------------------------------------------------------- |
| **Email**    | The value of`ADMIN_EMAIL` (e.g. `you@example.com`)                       |
| **Password** | The**plain-text password** you typed into the hash generator in Step 2 |

> You do **not** paste the `$2b$12$...` hash into the login form.
> That hash lives only in the environment. Your login password is the
> human-readable password you chose (e.g. `MySecurePassword123!`).

On success you are redirected to `/admin/dashboard`.

---

## Verification — confirm credentials are loaded

Before logging in, you can hit the backend directly to check it started correctly:

```powershell
# Should return 200 with your email if already logged in
# Should return 401 if not (correct — means the endpoint is protected)
curl http://localhost:8000/admin/api/auth/me
# Expected (not logged in): {"detail":"Authentication required."}
```

If you see `{"detail":"Invalid credentials."}` on login, the most common causes are:

| Symptom                                   | Cause                | Fix                                                                         |
| ----------------------------------------- | -------------------- | --------------------------------------------------------------------------- |
| "Invalid credentials" on correct password | Hash not loaded      | Restart the backend after setting the env var                               |
| "Invalid credentials" always              | Hash empty string    | Run Step 2 again and paste the full`$2b$12$...` value                     |
| "Invalid credentials" always              | Email mismatch       | `ADMIN_EMAIL` in env must exactly match what you type in the login form   |
| Page loads but login button does nothing  | Frontend not started | Run`pnpm dev` in the `frontend/` folder                                 |
| 401 on every request after login          | JWT secret wrong     | `ADMIN_JWT_SECRET` must be the same value on every restart                |
| Locked out after 5 attempts               | Rate limit hit       | Wait 15 minutes (Redis required), or restart backend without Redis to clear |

---

## Logging out

Click **Sign out** in the top-right of the admin nav bar.
This calls `POST /admin/api/auth/logout`, revokes the session in Redis,
and clears both cookies.

---

## Changing the password

There is no "change password" UI. To change it:

1. Run `python -m app.cli.hash_password` with the new password
2. Copy the new `$2b$12$...` hash
3. Update `ADMIN_PASSWORD_HASH` in the environment
4. Restart the backend
5. All existing sessions expire within 15 minutes (access token TTL)

---

## Rate limiting behaviour

Login attempts are rate-limited per IP address when Redis is running:

| Trigger               | Limit            | Lockout                     |
| --------------------- | ---------------- | --------------------------- |
| Failed login attempts | 5 per 15 minutes | Soft block — 429 returned  |
| Cumulative failures   | 10 total         | Hard lockout for 30 minutes |

**Redis is optional.** If Redis is not running (local dev without Docker),
rate limiting is silently skipped — you can attempt login any number of times.

To reset a lockout in development: restart the backend (Redis state is lost on container restart with `docker compose down`).

---

## Session lifetime

| Token         | Lifetime   | Storage                                          |
| ------------- | ---------- | ------------------------------------------------ |
| Access token  | 15 minutes | HTTPOnly cookie (`access_token`)               |
| Refresh token | 24 hours   | HTTPOnly cookie (`refresh_token`) + Redis hash |

The frontend automatically refreshes the access token using the refresh token
before it expires. You stay logged in for up to 24 hours without re-entering credentials.

---

## Quick-start checklist

```
□ Backend running (docker compose up OR uv run uvicorn)
□ Frontend running (pnpm dev)
□ ADMIN_EMAIL set in environment
□ ADMIN_PASSWORD_HASH set — generated with python -m app.cli.hash_password
□ ADMIN_JWT_SECRET set — at least 32 characters, random
□ Backend restarted after setting env vars
□ Open http://localhost:5173/admin/login
□ Enter the email and password you used in the hash generator
```
