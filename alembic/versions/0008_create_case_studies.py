"""Create case_studies table

Revision ID: 0008
Revises: 0007
Create Date: 2026-08-05 00:00:00.000000 UTC

One table:
  case_studies — one row per project case study (linked by slug)

The `content` column stores the full nested case study body as JSON.
Seeded with the existing interviewpilot-ai data from
frontend/src/data/case-studies.ts (converted to Python dict).
"""

from __future__ import annotations

import json
import uuid
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0008"
down_revision: str | None = "0007"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


# ── helpers ───────────────────────────────────────────────────────────────────

def _uuid() -> str:
    return str(uuid.uuid4())


# ── seed data ─────────────────────────────────────────────────────────────────

_INTERVIEWPILOT_CONTENT: dict = {
    "tocSections": [
        {"id": "overview",     "label": "Overview"},
        {"id": "problem",      "label": "Problem"},
        {"id": "goals",        "label": "Goals"},
        {"id": "architecture", "label": "Architecture"},
        {"id": "backend",      "label": "Backend"},
        {"id": "ai",           "label": "AI System"},
        {"id": "database",     "label": "Database"},
        {"id": "api",          "label": "API Design"},
        {"id": "security",     "label": "Security"},
        {"id": "performance",  "label": "Performance"},
        {"id": "testing",      "label": "Testing"},
        {"id": "decisions",    "label": "Decisions"},
        {"id": "status",       "label": "Status"},
        {"id": "roadmap",      "label": "Roadmap"},
    ],
    "overview": {
        "what":
            "InterviewPilot AI is a SaaS backend system designed to help software engineers prepare for technical interviews through AI-powered, role-specific question generation and structured answer evaluation.",
        "who":
            "Software engineers at any experience level who want to practise technical interviews with questions tailored to their target role, technology stack, and seniority level.",
        "whyItMatters":
            "Generic prep content does not reflect the specificity of real technical interviews. Candidates waste time on irrelevant material and receive no honest feedback on how their answers would perform with a real interviewer. InterviewPilot replaces guesswork with structured, personalised practice.",
        "engineeringFocus": [
            "Async FastAPI backend with layered architecture and dependency injection",
            "Celery + Redis for non-blocking AI evaluation jobs (3–10 s LLM calls)",
            "Structured LLM output via Pydantic models — no free-form JSON parsing",
            "JWT authentication with access/refresh token rotation",
            "Provider-agnostic AI abstraction layer to avoid LLM vendor lock-in",
            "Full async test suite with mocked LLM provider for deterministic tests",
        ],
    },
    "problemStatement": {
        "intro":
            "Technical interview preparation has a structural problem: content is generic, feedback is absent, progress is invisible, and practice is disconnected from the candidate's actual target role.",
        "points": [
            {
                "title": "Generic content does not reflect real interviews",
                "description":
                    "Most prep resources cover general algorithms and data structures. Real interviews at target companies use role-specific, domain-specific, and stack-specific questions. A senior Python backend engineer needs different questions than a junior frontend engineer.",
            },
            {
                "title": "Candidates practise without real feedback",
                "description":
                    "Memorising answers without evaluating them creates false confidence. Candidates need structured feedback on accuracy, technical depth, clarity, and how close their answer is to what an interviewer actually expects.",
            },
            {
                "title": "Progress is invisible without tracking",
                "description":
                    "Without persistence and analytics, candidates cannot identify weak areas, measure improvement over time, or decide which topics to focus on next. Time is spent re-covering strong areas instead of improving weak ones.",
            },
            {
                "title": "Preparation is disconnected from the target role",
                "description":
                    "A candidate targeting a distributed systems role at a fintech company needs different preparation to one targeting a full-stack position at a startup. Generic tools cannot adapt to this specificity.",
            },
        ],
    },
    "goals": [
        {
            "title": "Role-specific question generation",
            "description":
                "Generate technical interview questions based on the candidate's target role, seniority level, and selected technology topics via structured LLM prompting.",
        },
        {
            "title": "Structured answer evaluation",
            "description":
                "Evaluate candidate answers against expected content — scoring accuracy, technical depth, and clarity using Pydantic-validated structured output from the LLM.",
        },
        {
            "title": "Actionable multi-dimensional feedback",
            "description":
                "Return specific strengths, concrete improvement areas, and a worked example strong answer for each question — not just a numeric score.",
        },
        {
            "title": "Persistent session and progress tracking",
            "description":
                "Store interview sessions, questions, answers, and feedback in PostgreSQL for progress analysis, historical review, and topic-level analytics.",
        },
        {
            "title": "Scalable multi-user SaaS architecture",
            "description":
                "Support multiple concurrent users with isolated data, JWT-based authentication, and a backend designed to scale horizontally behind a load balancer.",
        },
        {
            "title": "Non-blocking AI evaluation pipeline",
            "description":
                "Route LLM evaluation jobs through Celery + Redis to decouple slow AI calls (3–10 s) from fast HTTP request cycles, keeping API response times predictable.",
        },
    ],
    "systemArchitecture": {
        "description":
            "The system is composed of five layers: a TypeScript frontend, a FastAPI REST backend, a Celery worker pool for async AI jobs, a PostgreSQL primary database, and a Redis instance serving as both cache and message broker. External LLM calls are routed exclusively through the AI abstraction layer in the worker pool, never directly from the API layer.",
        "components": [
            {"layer": "Frontend",         "tech": "React + TypeScript",    "role": "Candidate-facing SPA — session management, question display, answer submission, and feedback rendering."},
            {"layer": "API Layer",        "tech": "FastAPI (Python 3.12)", "role": "REST API — handles authentication, request validation, session orchestration, and job dispatch."},
            {"layer": "Worker Pool",      "tech": "Celery + Python",       "role": "Async task execution — processes AI evaluation jobs, retries on LLM failures, persists results."},
            {"layer": "Message Broker",   "tech": "Redis",                 "role": "Celery broker and result backend. Also used for short-lived session caching and rate-limit counters."},
            {"layer": "Primary Database", "tech": "PostgreSQL 16",         "role": "Stores all persistent data — users, profiles, sessions, questions, answers, feedback, and progress metrics."},
            {"layer": "AI Provider",      "tech": "OpenAI API (gpt-4o)",   "role": "External LLM for question generation and answer evaluation. Accessed only through the AI abstraction layer."},
        ],
    },
    "backendArchitecture": {
        "description":
            "The FastAPI application follows a strict three-layer architecture: API routers handle HTTP concerns, service functions own business logic, and repositories own all database access. This layering enables each tier to be tested in isolation.",
        "layers": [
            {
                "name": "API Layer (Routers)",
                "description":
                    "FastAPI routers grouped by domain resource. Each router handles request parsing, auth dependency injection, response serialisation, and HTTP error mapping. No business logic lives here.",
                "tech": ["FastAPI", "Pydantic v2", "python-jose"],
                "responsibilities": [
                    "Parse and validate incoming request bodies with Pydantic models",
                    "Inject dependencies (db session, current user, rate limiter)",
                    "Delegate to service layer and serialise the response model",
                    "Map domain exceptions to appropriate HTTP status codes",
                ],
            },
            {
                "name": "Service Layer",
                "description":
                    "Pure Python functions (no FastAPI dependencies) that implement business logic: session orchestration, question sequencing, Celery job dispatch, and progress aggregation.",
                "tech": ["Python", "Celery", "asyncio"],
                "responsibilities": [
                    "Orchestrate multi-step workflows (start session → generate questions → dispatch evaluation jobs)",
                    "Enforce business rules (session completion, question limits, answer uniqueness)",
                    "Dispatch Celery tasks for async AI evaluation",
                    "Aggregate progress metrics from raw feedback data",
                ],
            },
            {
                "name": "Repository Layer",
                "description":
                    "SQLAlchemy async ORM functions that provide a clean data access API. All raw SQL and ORM query logic lives here, isolated from business logic.",
                "tech": ["SQLAlchemy 2.0 async", "asyncpg", "Alembic"],
                "responsibilities": [
                    "CRUD operations for all domain entities",
                    "Parameterised queries — no raw string interpolation",
                    "Alembic-managed schema migrations",
                    "Connection pooling via asyncpg",
                ],
            },
            {
                "name": "AI Worker Layer",
                "description":
                    "Celery tasks that call the AI abstraction layer, handle structured output parsing, implement retry logic, and persist results to the database when complete.",
                "tech": ["Celery", "OpenAI Python SDK", "Pydantic v2"],
                "responsibilities": [
                    "Accept evaluation jobs from the Redis broker queue",
                    "Call LLM provider through the AI abstraction layer",
                    "Validate and parse structured LLM output with Pydantic",
                    "Retry with exponential back-off on API errors or malformed output",
                    "Write feedback results to PostgreSQL via the repository layer",
                ],
            },
        ],
    },
    "aiArchitecture": {
        "description":
            "The AI system is built around a provider-agnostic abstraction layer that isolates all LLM calls behind a typed interface. This enables swapping providers (OpenAI → self-hosted) without touching business logic, and allows the test suite to substitute a deterministic mock provider without any external network calls.",
        "components": [
            {
                "name": "Prompt Management",
                "description":
                    "Versioned, parameterised prompt templates stored as Python classes. Each template receives structured context (role, seniority, topic, candidate answer) and builds the final prompt. User input is passed as a data parameter — never concatenated directly into the instruction portion of the prompt.",
            },
            {
                "name": "AI Provider Abstraction",
                "description":
                    "A typed Python Protocol defines the LLM interface (`generate_question`, `evaluate_answer`). The OpenAI implementation and a mock implementation both satisfy this Protocol. The Celery tasks depend on the Protocol, not on OpenAI directly.",
            },
            {
                "name": "Structured Output Parsing",
                "description":
                    "All LLM responses are requested in JSON mode and validated against Pydantic models before use. If the response fails validation, the task retries with a prompt that includes the validation error as context. This prevents silently propagating malformed AI output.",
            },
            {
                "name": "Feedback Generation",
                "description":
                    "Answer evaluation returns a `FeedbackResult` Pydantic model with five fields: overall score (0–10), technical accuracy score, depth score, clarity score, a list of specific strengths, a list of improvement areas, and an example strong answer. All fields are required — no partial feedback.",
            },
            {
                "name": "Question Generation",
                "description":
                    "Questions are generated with structured output: question text, topic, expected difficulty (1–5), key concepts the answer should cover, and a model answer. Difficulty is calibrated by seniority level injected into the prompt template.",
            },
        ],
        "safetyNotes": [
            "User-submitted answers are passed as data parameters to the LLM, not injected into the instruction portion of the prompt — mitigating prompt injection.",
            "Rate limiting on AI endpoints prevents abuse and controls OpenAI API costs.",
            "All LLM responses are validated against Pydantic schemas before being stored or returned — malformed output triggers a retry, never a crash.",
            "API keys are loaded exclusively from environment variables — no hardcoded secrets.",
        ],
    },
    "databaseDesign": {
        "description":
            "PostgreSQL schema is designed around seven core entities. All foreign keys enforce referential integrity. Created/updated timestamps are present on all mutable tables. UUIDs are used as primary keys throughout to support future horizontal sharding.",
        "entities": [
            {
                "name": "User",
                "description": "Registered account. Email is the unique identity. Password is stored as a bcrypt hash.",
                "keyFields": ["id (UUID PK)", "email (unique)", "hashed_password", "role (enum)", "created_at"],
            },
            {
                "name": "UserProfile",
                "description": "Candidate preparation profile. One user may have multiple profiles.",
                "keyFields": ["id (UUID PK)", "user_id (FK → User)", "target_role", "experience_level (enum)", "focus_topics (array)", "created_at"],
                "relationships": "Many profiles → one User",
            },
            {
                "name": "InterviewSession",
                "description": "A single timed practice session. Links a user profile to a set of questions.",
                "keyFields": ["id (UUID PK)", "user_id (FK → User)", "profile_id (FK → UserProfile)", "status (enum)", "started_at", "completed_at"],
                "relationships": "Many sessions → one User; many sessions → one UserProfile",
            },
            {
                "name": "Question",
                "description": "An AI-generated interview question.",
                "keyFields": ["id (UUID PK)", "session_id (FK → InterviewSession)", "content", "topic", "difficulty (1–5)", "key_concepts (array)", "model_answer"],
                "relationships": "Many questions → one InterviewSession",
            },
            {
                "name": "Answer",
                "description": "A candidate's submitted answer to a question.",
                "keyFields": ["id (UUID PK)", "question_id (FK → Question)", "user_id (FK → User)", "content", "submitted_at"],
                "relationships": "One answer → one Question",
            },
            {
                "name": "Feedback",
                "description": "AI-generated evaluation result for one Answer.",
                "keyFields": ["id (UUID PK)", "answer_id (FK → Answer)", "overall_score (0–10)", "accuracy_score", "depth_score", "clarity_score", "strengths (array)", "improvements (array)", "example_answer", "created_at"],
                "relationships": "One feedback → one Answer",
            },
            {
                "name": "ProgressMetric",
                "description": "Aggregated progress snapshot per user per topic.",
                "keyFields": ["id (UUID PK)", "user_id (FK → User)", "topic", "avg_score", "sessions_completed", "last_session_at"],
                "relationships": "Many metrics → one User",
            },
        ],
    },
    "apiDesign": {
        "description":
            "The REST API is versioned under `/api/v1`. All endpoints return JSON. Authentication uses Bearer JWT tokens in the Authorization header. Errors return a consistent `{ detail: string }` envelope matching FastAPI defaults.",
        "endpointGroups": [
            {
                "prefix": "/auth",
                "description": "Authentication — token issuance, refresh, and revocation.",
                "endpoints": [
                    {"method": "POST", "path": "/auth/register",  "description": "Create a new user account (email + password)."},
                    {"method": "POST", "path": "/auth/login",     "description": "Exchange credentials for access + refresh tokens."},
                    {"method": "POST", "path": "/auth/refresh",   "description": "Exchange a valid refresh token for a new access token."},
                    {"method": "POST", "path": "/auth/logout",    "description": "Revoke the current refresh token."},
                ],
            },
            {
                "prefix": "/users",
                "description": "Authenticated user — profile retrieval and update.",
                "endpoints": [
                    {"method": "GET",   "path": "/users/me", "description": "Return the authenticated user's account data."},
                    {"method": "PATCH", "path": "/users/me", "description": "Update display name or email (requires password confirmation)."},
                ],
            },
            {
                "prefix": "/profiles",
                "description": "Preparation profiles — role, seniority, and topic preferences per candidate.",
                "endpoints": [
                    {"method": "GET",    "path": "/profiles",     "description": "List all preparation profiles for the authenticated user."},
                    {"method": "POST",   "path": "/profiles",     "description": "Create a new preparation profile."},
                    {"method": "GET",    "path": "/profiles/:id", "description": "Return a single profile by ID."},
                    {"method": "PATCH",  "path": "/profiles/:id", "description": "Update target role, seniority, or focus topics."},
                    {"method": "DELETE", "path": "/profiles/:id", "description": "Delete a profile and its associated sessions."},
                ],
            },
            {
                "prefix": "/sessions",
                "description": "Interview sessions — creation, lifecycle management, and question retrieval.",
                "endpoints": [
                    {"method": "GET",   "path": "/sessions",                        "description": "List sessions for the authenticated user (paginated)."},
                    {"method": "POST",  "path": "/sessions",                        "description": "Start a new interview session using a preparation profile."},
                    {"method": "GET",   "path": "/sessions/:id",                    "description": "Return session details including status and question list."},
                    {"method": "POST",  "path": "/sessions/:id/questions/generate", "description": "Trigger AI question generation for this session."},
                    {"method": "PATCH", "path": "/sessions/:id/complete",           "description": "Mark a session as complete and trigger progress metric update."},
                ],
            },
            {
                "prefix": "/answers",
                "description": "Answer submission — candidates submit answers for individual questions.",
                "endpoints": [
                    {"method": "POST", "path": "/answers",     "description": "Submit an answer for a question. Dispatches an evaluation Celery job."},
                    {"method": "GET",  "path": "/answers/:id", "description": "Return a submitted answer and its evaluation status."},
                ],
            },
            {
                "prefix": "/feedback",
                "description": "AI-generated feedback — retrieve evaluation results for answers and sessions.",
                "endpoints": [
                    {"method": "GET", "path": "/feedback/answer/:id",  "description": "Return the AI feedback for a single answer (polling endpoint)."},
                    {"method": "GET", "path": "/feedback/session/:id", "description": "Return all feedback for an entire session in one response."},
                ],
            },
            {
                "prefix": "/progress",
                "description": "Progress analytics — topic-level performance summaries.",
                "endpoints": [
                    {"method": "GET", "path": "/progress/summary",  "description": "Return overall progress: total sessions, avg score, top/weak topics."},
                    {"method": "GET", "path": "/progress/by-topic", "description": "Return per-topic breakdown: avg score, sessions completed, trend."},
                ],
            },
        ],
    },
    "securityConsiderations": [
        {
            "title": "JWT with short-lived access tokens",
            "description":
                "Access tokens expire in 15 minutes. Refresh tokens expire in 7 days and are rotated on use — if a refresh token is reused after rotation, the entire token family is revoked (detect replay attacks).",
        },
        {
            "title": "Input validation at the API boundary",
            "description":
                "All incoming data is validated against strict Pydantic models before reaching the service layer. Fields have max length constraints. Unknown fields are rejected by default.",
        },
        {
            "title": "Rate limiting on AI endpoints",
            "description":
                "The question generation and answer submission endpoints are rate-limited per user using Redis-backed counters. This prevents abuse and controls OpenAI API costs.",
        },
        {
            "title": "Prompt injection mitigation",
            "description":
                "User-submitted answers are passed to the LLM as data parameters within a structured JSON payload — never concatenated directly into the instruction portion of the prompt. The system prompt instructs the model to evaluate the `user_answer` field, not to follow instructions within it.",
        },
        {
            "title": "Password hashing with bcrypt",
            "description":
                "Passwords are hashed with bcrypt (work factor 12) before storage. Plain-text passwords are never logged or persisted at any layer.",
        },
        {
            "title": "Secrets via environment variables",
            "description":
                "All secrets (database URL, JWT secret, OpenAI API key) are loaded from environment variables via pydantic-settings. No secrets appear in source code or version control.",
        },
    ],
    "performanceConsiderations": [
        {
            "title": "Async-first throughout",
            "description":
                "FastAPI with asyncio and asyncpg for non-blocking I/O. Database queries, HTTP calls, and Redis operations never block the event loop. The server handles many concurrent requests on a single process.",
        },
        {
            "title": "Background jobs for slow AI calls",
            "description":
                "LLM evaluation takes 3–10 seconds. Answer submission dispatches a Celery task and returns immediately with a 202 Accepted. Clients poll the feedback endpoint or receive a webhook when ready.",
        },
        {
            "title": "Redis caching for hot data",
            "description":
                "Authenticated user objects and session state are cached in Redis after the first database read. Cache is invalidated on write. Reduces database load for repeated reads within a session.",
        },
        {
            "title": "Database connection pooling",
            "description":
                "asyncpg maintains a pool of persistent connections to PostgreSQL. The pool size is configurable via environment variable. Avoids connection setup overhead on every request.",
        },
        {
            "title": "Indexed queries on access patterns",
            "description":
                "B-tree indexes on `user_id`, `session_id`, and `created_at` columns cover all primary access patterns. Composite indexes on `(user_id, topic)` for progress metrics avoid full table scans.",
        },
        {
            "title": "Paginated list endpoints",
            "description":
                "All list endpoints (`/sessions`, `/answers`, `/progress/by-topic`) return paginated responses with cursor-based pagination. Prevents unbounded queries as data grows.",
        },
    ],
    "testingStrategy": [
        {
            "type": "Unit tests — service layer",
            "description":
                "Each service function is tested in isolation with mocked repository and AI provider dependencies. The mock AI provider returns deterministic Pydantic-valid responses, so tests never make real network calls.",
            "tools": ["pytest", "pytest-asyncio", "unittest.mock"],
        },
        {
            "type": "Integration tests — API layer",
            "description":
                "Full HTTP request/response cycle tests using httpx async test client against a real FastAPI application. A dedicated test PostgreSQL database is created and torn down per test session via pytest fixtures.",
            "tools": ["pytest", "pytest-asyncio", "httpx", "pytest-postgresql"],
        },
        {
            "type": "Repository tests — database layer",
            "description":
                "Each repository function is tested against a real database (in Docker) to verify ORM queries, constraint enforcement, and migration correctness.",
            "tools": ["pytest", "SQLAlchemy async", "Docker (pytest fixtures)"],
        },
        {
            "type": "AI evaluation tests — prompt integrity",
            "description":
                "Snapshot tests for prompt templates verify that changes to prompt structure are intentional. The mock LLM provider is used in all service/API tests — real LLM is never called in CI.",
            "tools": ["pytest", "syrupy (snapshot testing)", "unittest.mock"],
        },
        {
            "type": "Frontend component tests",
            "description":
                "React component tests for the candidate-facing UI: session flow, feedback display, and progress charts. Mocked API responses via MSW.",
            "tools": ["Vitest", "React Testing Library", "MSW"],
        },
    ],
    "engineeringDecisions": [
        {
            "question": "Why FastAPI over Django or Flask?",
            "answer":
                "FastAPI is async-first and integrates natively with Pydantic for request/response validation and OpenAPI schema generation. Django's ORM is synchronous; Flask lacks first-class async support. For a system where database and LLM calls are both I/O-bound, async throughout the stack is essential.",
            "tradeoffs":
                "FastAPI has a smaller ecosystem than Django. Features like admin panels and auth middleware require third-party libraries or custom implementation, increasing initial build time.",
        },
        {
            "question": "Why PostgreSQL and not a document database?",
            "answer":
                "The data model has strong relational structure: Users → Profiles → Sessions → Questions → Answers → Feedback forms a clear hierarchy with referential integrity requirements. PostgreSQL enforces this with foreign keys and constraints. It also supports array columns and will support pgvector for semantic question similarity matching in a future iteration.",
            "tradeoffs":
                "A document database like MongoDB would be more flexible for schema evolution, but at the cost of consistency guarantees that are important for billing and progress tracking.",
        },
        {
            "question": "Why Celery + Redis for AI evaluation instead of FastAPI background tasks?",
            "answer":
                "FastAPI's `BackgroundTasks` runs in the same process. If the server restarts mid-evaluation, the job is lost. Celery tasks are persisted in Redis and can be retried by any available worker. For an operation that costs money (OpenAI API call) and affects user progress data, durability is non-negotiable.",
            "tradeoffs":
                "Celery adds operational complexity: a separate worker process, Redis dependency, and monitoring overhead (Flower). For a prototype, FastAPI BackgroundTasks would have been simpler — but not acceptable for a production SaaS.",
        },
        {
            "question": "Why a provider-agnostic AI abstraction layer?",
            "answer":
                "OpenAI's API costs and availability constraints make long-term dependence on a single provider a business risk. The abstraction layer (a Python Protocol) means swapping from OpenAI to Anthropic, Mistral, or a self-hosted model requires only a new implementation of the Protocol — zero changes to the service or worker layers.",
            "tradeoffs":
                "The abstraction adds a layer of indirection that can obscure provider-specific features (e.g., structured outputs, tool use) that might not map cleanly across providers. Managed carefully by keeping the Protocol interface minimal.",
        },
        {
            "question": "Why UUID primary keys instead of auto-incrementing integers?",
            "answer":
                "UUIDs prevent enumeration attacks (sequential IDs in URLs let attackers probe other users' resources). They also support future distributed writes without a centralised sequence generator, which would become a bottleneck in a horizontally-scaled deployment.",
            "tradeoffs":
                "UUIDs are larger (16 bytes vs. 4 bytes) and slower for B-tree index operations. Acceptable trade-off at this scale; revisitable with ULID if performance becomes an issue.",
        },
    ],
    "currentStatus": {
        "description":
            "The project is in active development. Core infrastructure and authentication are complete. The AI evaluation pipeline is the primary current focus.",
        "completed": [
            "Project scaffolding — FastAPI app structure, Docker Compose for local development",
            "Database schema and Alembic migrations for all seven entities",
            "JWT authentication — registration, login, refresh token rotation",
            "User and UserProfile CRUD endpoints with full test coverage",
            "InterviewSession creation and lifecycle state machine",
            "Celery + Redis infrastructure — tasks route through the broker correctly",
            "AI provider abstraction — Protocol defined, OpenAI implementation in progress",
            "Pydantic output schemas for question generation and feedback results",
        ],
        "inProgress": [
            "OpenAI implementation of the AI provider Protocol",
            "Question generation Celery task with retry logic",
            "Answer evaluation Celery task and feedback persistence",
            "API endpoint for polling evaluation status",
        ],
        "planned": [
            "Progress analytics endpoints and aggregation logic",
            "Rate limiting middleware on AI endpoints",
            "Prompt injection testing and hardening",
            "Frontend React application (session UI, feedback display)",
            "CI/CD pipeline with GitHub Actions",
            "Production deployment configuration",
        ],
    },
    "roadmap": [
        {
            "title": "Complete AI evaluation pipeline",
            "description":
                "Finish the OpenAI implementation, question generation task, and answer evaluation task with full test coverage including the mock provider.",
            "priority": "high",
        },
        {
            "title": "Progress analytics engine",
            "description":
                "Implement the ProgressMetric aggregation logic, the `/progress/summary` and `/progress/by-topic` endpoints, and the scheduled job that keeps metrics current.",
            "priority": "high",
        },
        {
            "title": "Rate limiting and security hardening",
            "description":
                "Add Redis-backed rate limiting on AI endpoints, audit all prompts for injection vectors, and add integration tests for auth edge cases (token replay, expired tokens).",
            "priority": "high",
        },
        {
            "title": "Frontend React application",
            "description":
                "Build the candidate-facing SPA: onboarding flow, session UI with real-time question display, feedback rendering with score visualisation, and the progress dashboard.",
            "priority": "medium",
        },
        {
            "title": "Structured question bank",
            "description":
                "Pre-generate and cache a bank of high-quality questions per topic. Serve from the bank when available, fall back to live generation for niche topics. Reduces LLM costs and latency.",
            "priority": "medium",
        },
        {
            "title": "Semantic question similarity (pgvector)",
            "description":
                "Embed questions and use pgvector nearest-neighbour search to detect duplicate or near-duplicate questions within a session, ensuring topic diversity across a set.",
            "priority": "medium",
        },
        {
            "title": "Webhook and real-time feedback delivery",
            "description":
                "Replace client-side polling with server-sent events or webhooks so feedback is pushed to the frontend immediately when evaluation completes, rather than requiring the client to poll.",
            "priority": "low",
        },
        {
            "title": "Multi-provider LLM support",
            "description":
                "Implement the Anthropic and Mistral provider adapters behind the existing AI Protocol abstraction. Add per-user or per-tier provider selection.",
            "priority": "low",
        },
    ],
}


# ── upgrade ───────────────────────────────────────────────────────────────────

def upgrade() -> None:
    op.create_table(
        "case_studies",
        sa.Column("id",           sa.Uuid(as_uuid=True), primary_key=True),
        sa.Column("slug",         sa.String(250), nullable=False),
        sa.Column("status",       sa.String(20),  nullable=False, server_default="draft"),
        sa.Column("disclaimer",   sa.Text,        nullable=True),
        sa.Column("content",      sa.JSON,        nullable=False, server_default="{}"),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at",   sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at",   sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_case_studies_slug", "case_studies", ["slug"], unique=True)

    # Seed existing case study
    op.execute(
        sa.text(
            "INSERT INTO case_studies (id, slug, status, disclaimer, content, published_at)"
            " VALUES (:id, :slug, :status, :disclaimer, :content, :published_at)"
        ),
        {
            "id":           _uuid(),
            "slug":         "interviewpilot-ai",
            "status":       "published",
            "disclaimer":   (
                "InterviewPilot AI is actively in development. The architecture described below "
                "is planned and partially implemented. This case study documents the engineering "
                "design, key decisions, and current build progress — not a retrospective on a "
                "shipped product."
            ),
            "content":      json.dumps(_INTERVIEWPILOT_CONTENT),
            "published_at": "2024-01-01 00:00:00+00",
        },
    )


# ── downgrade ─────────────────────────────────────────────────────────────────

def downgrade() -> None:
    op.drop_index("ix_case_studies_slug", table_name="case_studies")
    op.drop_table("case_studies")
