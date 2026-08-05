"""Create resume tables

Revision ID: 0007
Revises: 0006
Create Date: 2026-08-05 00:00:00.000000 UTC

Five tables:
  resume_profile       — singleton headline + summary paragraphs
  resume_experience    — ordered experience entries
  resume_skill_groups  — ordered named skill groups
  resume_education     — education entries
  resume_certifications — certifications and learning items

Seed data mirrors the current static frontend/src/data/resume.ts so the
public resume page works immediately without any admin edits.
"""

from __future__ import annotations

import uuid
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0007"
down_revision: str | None = "0006"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

# ── helpers ───────────────────────────────────────────────────────────────────

def _uuid() -> str:
    return str(uuid.uuid4())


# ── upgrade ───────────────────────────────────────────────────────────────────


def upgrade() -> None:
    # resume_profile — singleton
    op.create_table(
        "resume_profile",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("headline", sa.String(300), nullable=False),
        sa.Column("summary_paragraphs", sa.JSON(), nullable=False, server_default="[]"),
        sa.Column("pdf_url", sa.String(500), nullable=True),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )

    # resume_experience
    op.create_table(
        "resume_experience",
        sa.Column("id", sa.Uuid(as_uuid=True), primary_key=True),
        sa.Column("role", sa.String(200), nullable=False),
        sa.Column("context", sa.String(200), nullable=False),
        sa.Column("period", sa.String(100), nullable=False),
        sa.Column("highlights", sa.JSON(), nullable=False, server_default="[]"),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )

    # resume_skill_groups
    op.create_table(
        "resume_skill_groups",
        sa.Column("id", sa.Uuid(as_uuid=True), primary_key=True),
        sa.Column("group_name", sa.String(100), nullable=False),
        sa.Column("skills", sa.JSON(), nullable=False, server_default="[]"),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )

    # resume_education
    op.create_table(
        "resume_education",
        sa.Column("id", sa.Uuid(as_uuid=True), primary_key=True),
        sa.Column("institution", sa.String(200), nullable=False),
        sa.Column("degree", sa.String(200), nullable=False),
        sa.Column("status", sa.String(50), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )

    # resume_certifications
    op.create_table(
        "resume_certifications",
        sa.Column("id", sa.Uuid(as_uuid=True), primary_key=True),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("provider", sa.String(200), nullable=False),
        sa.Column("status", sa.String(50), nullable=False),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )

    # ── Seed data (mirrors frontend/src/data/resume.ts) ───────────────────────

    profile_t = sa.table(
        "resume_profile",
        sa.column("id"),
        sa.column("headline"),
        sa.column("summary_paragraphs"),
        sa.column("pdf_url"),
    )
    op.bulk_insert(profile_t, [
        {
            "id": 1,
            "headline": "Python backend engineer focused on FastAPI, AI SaaS, and production-grade systems.",
            "summary_paragraphs": (
                '["I build backend systems for AI-powered SaaS products using Python, FastAPI, and PostgreSQL. '
                'My focus is clean layered architecture, scalable API design, and integrating LLMs with the '
                'rigour that production systems require \u2014 structured output validation, provider abstraction, '
                'background job durability, and meaningful test coverage.",'
                '"Currently building InterviewPilot AI \u2014 an AI SaaS backend that generates role-specific '
                'technical interview questions and evaluates candidate responses. The project demonstrates async '
                'FastAPI architecture, Celery + Redis for background AI evaluation jobs, JWT authentication, and '
                'a test suite that uses a mock LLM provider for deterministic results.",'
                '"I approach engineering as a craft: every layer has one responsibility, every contract is '
                'explicit, and every system is designed to be testable before it is designed to be fast."]'
            ),
            "pdf_url": None,
        }
    ])

    exp_t = sa.table(
        "resume_experience",
        sa.column("id"),
        sa.column("role"),
        sa.column("context"),
        sa.column("period"),
        sa.column("highlights"),
        sa.column("sort_order"),
    )
    op.bulk_insert(exp_t, [
        {
            "id": _uuid(),
            "role": "Backend Engineering Practice",
            "context": "Independent \u2014 project-based portfolio",
            "period": "2024 \u2013 present",
            "highlights": (
                '["Building InterviewPilot AI \u2014 a multi-user SaaS backend with async FastAPI, PostgreSQL, '
                'Redis, Celery, and OpenAI integration",'
                '"Implementing clean layered architecture (API \u2192 Service \u2192 Repository \u2192 Domain) '
                'with full test coverage at each layer",'
                '"Designing LLM integration systems with provider abstraction, structured output validation, '
                'and prompt injection mitigations",'
                '"Applying production-focused engineering practices: Alembic migrations, Docker Compose, GitHub Actions CI/CD"]'
            ),
            "sort_order": 0,
        },
        {
            "id": _uuid(),
            "role": "AI Backend Development",
            "context": "Independent \u2014 project-based portfolio",
            "period": "2024 \u2013 present",
            "highlights": (
                '["Built Clause Search System \u2014 RAG-powered semantic document search using pgvector and LLM embeddings",'
                '"Built AI Resume Analyzer \u2014 FastAPI service with Pydantic-validated structured LLM output extraction",'
                '"Applied prompt engineering for consistent, parseable multi-section AI responses",'
                '"Designed AI abstraction layers following Python Protocol pattern for LLM vendor independence"]'
            ),
            "sort_order": 1,
        },
        {
            "id": _uuid(),
            "role": "Full-Stack Portfolio Development",
            "context": "Independent \u2014 this website",
            "period": "2025 \u2013 present",
            "highlights": (
                '["Designed and built this portfolio site: React 19, TypeScript, Tailwind CSS v4, React Router v7",'
                '"Phase-by-phase implementation following a Product Strategy, UX Specification, and technical roadmap",'
                '"Applied strict TypeScript, ESLint, Vitest test suite, and production build pipeline"]'
            ),
            "sort_order": 2,
        },
    ])

    skill_t = sa.table(
        "resume_skill_groups",
        sa.column("id"),
        sa.column("group_name"),
        sa.column("skills"),
        sa.column("sort_order"),
    )
    op.bulk_insert(skill_t, [
        {"id": _uuid(), "group_name": "Backend",         "skills": '["Python 3.12","FastAPI","Pydantic v2","SQLAlchemy 2.0","HTTPX","asyncio"]',              "sort_order": 0},
        {"id": _uuid(), "group_name": "Databases",       "skills": '["PostgreSQL 16","Redis","Alembic","asyncpg","pgvector"]',                                "sort_order": 1},
        {"id": _uuid(), "group_name": "AI Engineering",  "skills": '["OpenAI API","Prompt engineering","Structured LLM output","RAG design","LLM abstraction"]', "sort_order": 2},
        {"id": _uuid(), "group_name": "Frontend",        "skills": '["React 19","TypeScript","Tailwind CSS v4","Vite","React Router v7"]',                    "sort_order": 3},
        {"id": _uuid(), "group_name": "DevOps",          "skills": '["Docker","Docker Compose","GitHub Actions","nginx"]',                                    "sort_order": 4},
        {"id": _uuid(), "group_name": "Testing",         "skills": '["pytest","pytest-asyncio","httpx","Vitest","React Testing Library","MSW"]',              "sort_order": 5},
        {"id": _uuid(), "group_name": "Architecture",    "skills": '["REST API design","Layered architecture","Repository pattern","Background jobs","OpenAPI"]', "sort_order": 6},
    ])

    edu_t = sa.table(
        "resume_education",
        sa.column("id"),
        sa.column("institution"),
        sa.column("degree"),
        sa.column("status"),
        sa.column("notes"),
        sa.column("sort_order"),
    )
    op.bulk_insert(edu_t, [
        {
            "id": _uuid(),
            "institution": "Self-directed engineering education",
            "degree": "Backend engineering, distributed systems, and AI integration",
            "status": "In progress",
            "notes": (
                "Deep-dive study of FastAPI, PostgreSQL internals, async Python patterns, system design "
                "principles, and AI engineering concepts. Applied through project-based learning across "
                "multiple production-focused builds."
            ),
            "sort_order": 0,
        },
    ])

    cert_t = sa.table(
        "resume_certifications",
        sa.column("id"),
        sa.column("title"),
        sa.column("provider"),
        sa.column("status"),
        sa.column("sort_order"),
    )
    op.bulk_insert(cert_t, [
        {"id": _uuid(), "title": "Python async programming patterns",         "provider": "Self-directed study + official docs",               "status": "Self-directed", "sort_order": 0},
        {"id": _uuid(), "title": "FastAPI documentation (complete)",           "provider": "tiangolo/fastapi official docs",                     "status": "Self-directed", "sort_order": 1},
        {"id": _uuid(), "title": "PostgreSQL indexing and query optimization", "provider": "Self-directed study + PostgreSQL docs",              "status": "In progress",   "sort_order": 2},
        {"id": _uuid(), "title": "System design fundamentals",                 "provider": "Self-directed \u2014 books, articles, and documentation", "status": "In progress",   "sort_order": 3},
        {"id": _uuid(), "title": "AWS Cloud Practitioner",                     "provider": "AWS Training",                                      "status": "Planned",       "sort_order": 4},
        {"id": _uuid(), "title": "Retrieval-Augmented Generation (RAG) architecture", "provider": "Self-directed study + project application", "status": "In progress",   "sort_order": 5},
    ])


# ── downgrade ─────────────────────────────────────────────────────────────────


def downgrade() -> None:
    op.drop_table("resume_certifications")
    op.drop_table("resume_education")
    op.drop_table("resume_skill_groups")
    op.drop_table("resume_experience")
    op.drop_table("resume_profile")
