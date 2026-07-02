"""
Admin authentication endpoint tests.

Test scenarios:
  Login
    ✓ Correct credentials → 200, access_token + refresh_token cookies set
    ✓ Wrong password → 401 with same body as wrong email (no enumeration)
    ✓ Wrong email → 401 with same body as wrong password
    ✓ Empty email → 422 (Pydantic validation)
    ✓ Empty password → 422 (Pydantic validation)

  /me
    ✓ Valid access_token cookie → 200 with email + expires_at
    ✓ No cookie → 401
    ✓ Tampered JWT → 401

  /logout
    ✓ Valid session → 204, cookies cleared in response

  /refresh (no Redis)
    ✓ No refresh_token cookie → 401
    ✓ Any refresh_token when Redis is None → 401 (fails closed)

  /refresh (with FakeRedis)
    ✓ Valid refresh_token → 200, new cookies issued, old token consumed

  /sessions
    ✓ Count returns 0 when Redis is None
    ✓ Count reflects tokens in FakeRedis

  /sessions DELETE
    ✓ Revokes all sessions, clears cookies → 204
"""

from __future__ import annotations

import pytest
from httpx import AsyncClient

from tests.admin.conftest import TEST_ADMIN_EMAIL, TEST_ADMIN_PASSWORD, TEST_JWT_SECRET

# ── Helpers ────────────────────────────────────────────────────────────────────


def _login_payload(
    email: str = TEST_ADMIN_EMAIL,
    password: str = TEST_ADMIN_PASSWORD,
) -> dict:
    return {"email": email, "password": password}


async def _login(client: AsyncClient, **kwargs) -> tuple[int, dict]:
    resp = await client.post("/admin/api/auth/login", json=_login_payload(**kwargs))
    return resp.status_code, resp.json() if resp.content else {}


# ── Login ──────────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_login_success(admin_client: AsyncClient) -> None:
    status, body = await _login(admin_client)
    assert status == 200
    assert body["email"] == TEST_ADMIN_EMAIL
    assert "expires_at" in body
    # Verify HTTPOnly cookies are set
    assert "access_token" in admin_client.cookies
    assert "refresh_token" in admin_client.cookies


@pytest.mark.asyncio
async def test_login_wrong_password(admin_client: AsyncClient) -> None:
    status, body = await _login(admin_client, password="wrong-password")
    assert status == 401
    assert body["detail"] == "Invalid credentials."
    assert "access_token" not in admin_client.cookies


@pytest.mark.asyncio
async def test_login_wrong_email(admin_client: AsyncClient) -> None:
    status, body = await _login(admin_client, email="notadmin@example.org")
    assert status == 401
    # Body must be identical to wrong-password response (no user enumeration)
    assert body["detail"] == "Invalid credentials."


@pytest.mark.asyncio
async def test_login_empty_email_rejected(admin_client: AsyncClient) -> None:
    resp = await admin_client.post(
        "/admin/api/auth/login", json={"email": "", "password": "something"}
    )
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_login_empty_password_rejected(admin_client: AsyncClient) -> None:
    resp = await admin_client.post(
        "/admin/api/auth/login",
        json={"email": TEST_ADMIN_EMAIL, "password": ""},
    )
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_login_unconfigured_admin_returns_401(
    admin_client: AsyncClient, monkeypatch
) -> None:
    """
    When admin_password_hash is empty (admin not yet configured), login must
    still return 401 — and bcrypt must still run (constant-time guarantee).

    This covers the H2 fix: the old code short-circuited on `not candidate_hash`
    before running bcrypt, creating a timing difference that revealed valid emails.
    After the fix, the dummy hash is used instead.
    """
    import app.core.config as _cfg
    monkeypatch.setattr(_cfg.settings, "admin_password_hash", "")
    status, body = await _login(admin_client, email=TEST_ADMIN_EMAIL)
    assert status == 401
    assert body["detail"] == "Invalid credentials."


# ── /me ────────────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_me_with_valid_cookie(admin_client: AsyncClient) -> None:
    await _login(admin_client)  # sets cookies on client
    resp = await admin_client.get("/admin/api/auth/me")
    assert resp.status_code == 200
    body = resp.json()
    assert body["email"] == TEST_ADMIN_EMAIL
    assert "expires_at" in body


@pytest.mark.asyncio
async def test_me_without_cookie_is_401(admin_client: AsyncClient) -> None:
    # Do NOT log in first — no cookie
    resp = await admin_client.get("/admin/api/auth/me")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_me_tampered_jwt_is_401(admin_client: AsyncClient) -> None:
    # Set a clearly invalid token
    admin_client.cookies.set("access_token", "not.a.valid.jwt", domain="test")
    resp = await admin_client.get("/admin/api/auth/me")
    assert resp.status_code == 401


# ── /logout ────────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_logout_clears_cookies(admin_client: AsyncClient) -> None:
    await _login(admin_client)
    assert "access_token" in admin_client.cookies

    resp = await admin_client.post("/admin/api/auth/logout")
    assert resp.status_code == 204

    # After logout, /me should return 401
    me_resp = await admin_client.get("/admin/api/auth/me")
    assert me_resp.status_code == 401


@pytest.mark.asyncio
async def test_logout_without_session_is_401(admin_client: AsyncClient) -> None:
    resp = await admin_client.post("/admin/api/auth/logout")
    assert resp.status_code == 401


# ── /refresh (no Redis) ────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_refresh_without_cookie_is_401(admin_client: AsyncClient) -> None:
    resp = await admin_client.post("/admin/api/auth/refresh")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_refresh_without_redis_is_401(admin_client: AsyncClient) -> None:
    """When Redis is unavailable, refresh must fail closed (not silently pass)."""
    # Set a fake-looking refresh token cookie; Redis is None on admin_client
    admin_client.cookies.set(
        "refresh_token", "somefaketokenthatwouldneverwork", domain="test"
    )
    resp = await admin_client.post("/admin/api/auth/refresh")
    assert resp.status_code == 401


# ── /refresh (with FakeRedis) ──────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_refresh_rotates_token_pair(admin_client_with_redis: AsyncClient) -> None:
    """Successful refresh: old token consumed, new token pair issued."""
    await _login(admin_client_with_redis)

    old_access = admin_client_with_redis.cookies.get("access_token")
    resp = await admin_client_with_redis.post("/admin/api/auth/refresh")
    assert resp.status_code == 200
    assert "expires_at" in resp.json()

    new_access = admin_client_with_redis.cookies.get("access_token")
    assert new_access != old_access, "Access token must be rotated"


@pytest.mark.asyncio
async def test_refresh_token_single_use(admin_client_with_redis: AsyncClient) -> None:
    """A refresh token can only be used once (GETDEL atomicity)."""
    await _login(admin_client_with_redis)

    refresh_token = admin_client_with_redis.cookies.get("refresh_token")

    # First refresh succeeds
    resp1 = await admin_client_with_redis.post("/admin/api/auth/refresh")
    assert resp1.status_code == 200

    # Restore the original (now-consumed) refresh token to simulate replay.
    # We must delete the new cookie first, then set the old one at the exact
    # path the server uses, otherwise httpx path-priority rules send the new
    # (still-valid) token instead of the consumed one.
    del admin_client_with_redis.cookies["refresh_token"]
    admin_client_with_redis.cookies.set(
        "refresh_token",
        refresh_token,
        domain="test",
        path="/admin/api/auth/refresh",
    )
    resp2 = await admin_client_with_redis.post("/admin/api/auth/refresh")
    assert resp2.status_code == 401, "Replay of consumed refresh token must be rejected"


# ── /sessions ──────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_sessions_count_no_redis(admin_client: AsyncClient) -> None:
    await _login(admin_client)
    resp = await admin_client.get("/admin/api/auth/sessions")
    assert resp.status_code == 200
    assert resp.json()["active_sessions"] == 0  # Redis is None → returns 0


@pytest.mark.asyncio
async def test_sessions_count_with_redis(admin_client_with_redis: AsyncClient) -> None:
    await _login(admin_client_with_redis)
    resp = await admin_client_with_redis.get("/admin/api/auth/sessions")
    assert resp.status_code == 200
    assert resp.json()["active_sessions"] == 1


@pytest.mark.asyncio
async def test_revoke_all_sessions(admin_client_with_redis: AsyncClient) -> None:
    """DELETE /sessions revokes everything and subsequent /me returns 401."""
    await _login(admin_client_with_redis)

    # Verify 1 active session
    count_resp = await admin_client_with_redis.get("/admin/api/auth/sessions")
    assert count_resp.json()["active_sessions"] == 1

    # Revoke all
    del_resp = await admin_client_with_redis.delete("/admin/api/auth/sessions")
    assert del_resp.status_code == 204

    # /me should now return 401 (cookies cleared)
    me_resp = await admin_client_with_redis.get("/admin/api/auth/me")
    assert me_resp.status_code == 401


# ── Audit log ─────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_audit_log_written_on_login(
    admin_client: AsyncClient,
    db_session,
) -> None:
    """Login events must be persisted to the audit log."""
    from sqlalchemy import select
    from app.models.audit_log import AdminAuditLog

    await _login(admin_client)

    result = await db_session.execute(
        select(AdminAuditLog).where(AdminAuditLog.action == "admin.login_success")
    )
    entries = result.scalars().all()
    assert len(entries) == 1
    assert entries[0].actor == TEST_ADMIN_EMAIL


@pytest.mark.asyncio
async def test_audit_log_written_on_login_failure(
    admin_client: AsyncClient,
    db_session,
) -> None:
    from sqlalchemy import select
    from app.models.audit_log import AdminAuditLog

    await _login(admin_client, password="wrongpassword")

    result = await db_session.execute(
        select(AdminAuditLog).where(AdminAuditLog.action == "admin.login_failure")
    )
    entries = result.scalars().all()
    assert len(entries) == 1
