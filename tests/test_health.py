"""Tests for GET /health."""

from __future__ import annotations

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_returns_200(client: AsyncClient) -> None:
    response = await client.get("/api/v1/health")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_health_response_schema(client: AsyncClient) -> None:
    response = await client.get("/api/v1/health")
    body = response.json()
    assert body["status"] == "ok"
    assert "version" in body
    assert "environment" in body
    assert "database" in body


@pytest.mark.asyncio
async def test_health_database_field(client: AsyncClient) -> None:
    """Database status should be 'ok' when the test DB is available."""
    response = await client.get("/api/v1/health")
    body = response.json()
    assert body["database"] == "ok"
