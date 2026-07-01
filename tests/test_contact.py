"""Tests for POST /api/v1/contact/messages."""

from __future__ import annotations

import pytest
from httpx import AsyncClient

ENDPOINT = "/api/v1/contact/messages"

VALID_PAYLOAD = {
    "name": "Jane Smith",
    "email": "jane@example.com",
    "subject": "Hiring inquiry",
    "message": "Hello, I'd like to discuss a backend engineering opportunity with you.",
}


# ── Success ───────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_submit_contact_returns_201(client: AsyncClient) -> None:
    response = await client.post(ENDPOINT, json=VALID_PAYLOAD)
    assert response.status_code == 201


@pytest.mark.asyncio
async def test_submit_contact_response_schema(client: AsyncClient) -> None:
    response = await client.post(ENDPOINT, json=VALID_PAYLOAD)
    body = response.json()
    assert "id" in body
    assert "message" in body
    assert "reference_id" in body


@pytest.mark.asyncio
async def test_submit_contact_reference_id_format(client: AsyncClient) -> None:
    response = await client.post(ENDPOINT, json=VALID_PAYLOAD)
    body = response.json()
    assert body["reference_id"].startswith("MSG-")


@pytest.mark.asyncio
async def test_submit_contact_success_message(client: AsyncClient) -> None:
    response = await client.post(ENDPOINT, json=VALID_PAYLOAD)
    body = response.json()
    assert "received" in body["message"].lower()


# ── Validation errors ─────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_missing_name_returns_422(client: AsyncClient) -> None:
    payload = {**VALID_PAYLOAD, "name": ""}
    response = await client.post(ENDPOINT, json=payload)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_invalid_email_returns_422(client: AsyncClient) -> None:
    payload = {**VALID_PAYLOAD, "email": "not-an-email"}
    response = await client.post(ENDPOINT, json=payload)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_missing_subject_returns_422(client: AsyncClient) -> None:
    payload = {**VALID_PAYLOAD, "subject": ""}
    response = await client.post(ENDPOINT, json=payload)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_message_too_short_returns_422(client: AsyncClient) -> None:
    payload = {**VALID_PAYLOAD, "message": "Too short."}
    response = await client.post(ENDPOINT, json=payload)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_message_at_min_length_accepted(client: AsyncClient) -> None:
    payload = {**VALID_PAYLOAD, "message": "x" * 20}
    response = await client.post(ENDPOINT, json=payload)
    assert response.status_code == 201


@pytest.mark.asyncio
async def test_message_exceeds_max_length_returns_422(client: AsyncClient) -> None:
    payload = {**VALID_PAYLOAD, "message": "x" * 5001}
    response = await client.post(ENDPOINT, json=payload)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_name_exceeds_max_length_returns_422(client: AsyncClient) -> None:
    payload = {**VALID_PAYLOAD, "name": "A" * 101}
    response = await client.post(ENDPOINT, json=payload)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_empty_body_returns_422(client: AsyncClient) -> None:
    response = await client.post(ENDPOINT, json={})
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_whitespace_only_name_returns_422(client: AsyncClient) -> None:
    payload = {**VALID_PAYLOAD, "name": "   "}
    response = await client.post(ENDPOINT, json=payload)
    assert response.status_code == 422


# ── Idempotency / multiple submissions ───────────────────────────────────────


@pytest.mark.asyncio
async def test_two_submissions_get_different_ids(client: AsyncClient) -> None:
    r1 = await client.post(ENDPOINT, json=VALID_PAYLOAD)
    r2 = await client.post(ENDPOINT, json=VALID_PAYLOAD)
    assert r1.status_code == 201
    assert r2.status_code == 201
    assert r1.json()["id"] != r2.json()["id"]
