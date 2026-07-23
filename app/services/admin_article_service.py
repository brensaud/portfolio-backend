"""
AdminArticleService — business logic for admin article management.

Responsibilities:
  1. List articles (all statuses) with pagination, filtering, search.
  2. Fetch a single article for the editor.
  3. Create a new draft.
  4. Update editable fields.
  5. Publish, unpublish, archive.
  6. Delete with pre-delete audit log.

Design constraints:
  • Service owns every transaction boundary (commit).
  • Repository only flushes.
  • Publish requires title + summary + body + category — missing fields raise ValueError.
  • Slug is auto-generated from title on create; locked once published.
  • published_at is set on first publish and never overwritten on re-publish.
  • No PII in audit log metadata.
"""

from __future__ import annotations

import logging
import math
import re
import uuid
from datetime import UTC, datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.article import ArticleStatus
from app.repositories.article_repo import ArticleRepository
from app.repositories.audit_repo import AuditRepository
from app.schemas.admin.article import (
    AdminArticleDetail,
    AdminArticlesPage,
    AdminArticleSummary,
    ArticleCreate,
    ArticleUpdate,
)

logger = logging.getLogger(__name__)

# ── Audit action catalog ──────────────────────────────────────────────────────
_ACTION_CREATED    = "admin.article.created"
_ACTION_UPDATED    = "admin.article.updated"
_ACTION_PUBLISHED  = "admin.article.published"
_ACTION_UNPUBLISHED = "admin.article.unpublished"
_ACTION_ARCHIVED   = "admin.article.archived"
_ACTION_DELETED    = "admin.article.deleted"

_RESOURCE_TYPE = "article"

# ── Slug helpers ──────────────────────────────────────────────────────────────

def _slugify(text: str) -> str:
    """Convert a title string to a URL-safe slug."""
    slug = text.lower().strip()
    slug = re.sub(r"[^\w\s-]", "", slug)
    slug = re.sub(r"[\s_-]+", "-", slug)
    slug = re.sub(r"^-+|-+$", "", slug)
    return slug[:200]  # cap at 200 chars (slug column is 250)


def _calculate_reading_time(body: str | None) -> int | None:
    """Estimate reading time from word count at 200 wpm. Returns None if no body."""
    if not body:
        return None
    word_count = len(body.split())
    return max(1, math.ceil(word_count / 200))


class AdminArticleService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._repo = ArticleRepository(session)
        self._audit = AuditRepository(session)

    # ── List ──────────────────────────────────────────────────────────────────

    async def list_articles(
        self,
        *,
        page: int,
        page_size: int,
        status: ArticleStatus | None,
        search: str | None,
        sort_by: str,
    ) -> AdminArticlesPage:
        items, total = await self._repo.list_admin(
            page=page,
            page_size=page_size,
            status=status,
            search=search,
            sort_by=sort_by,
        )
        pages = math.ceil(total / page_size) if total > 0 else 0
        return AdminArticlesPage(
            items=[AdminArticleSummary.model_validate(a) for a in items],
            total=total,
            page=page,
            page_size=page_size,
            pages=pages,
        )

    # ── Get detail ────────────────────────────────────────────────────────────

    async def get_article(self, article_id: uuid.UUID) -> AdminArticleDetail:
        """
        Raises:
            LookupError — article not found.
        """
        article = await self._repo.get_by_id(article_id)
        if article is None:
            raise LookupError(f"Article {article_id} not found.")
        return AdminArticleDetail.model_validate(article)

    # ── Create ────────────────────────────────────────────────────────────────

    async def create_article(
        self,
        data: ArticleCreate,
        *,
        actor: str,
        ip_address: str | None,
    ) -> AdminArticleDetail:
        """Create a new draft article with an auto-generated unique slug."""
        base_slug = _slugify(data.title)
        slug = await self._unique_slug(base_slug)

        reading_time = _calculate_reading_time(data.body)

        article = await self._repo.create(
            slug=slug,
            title=data.title,
            summary=data.summary,
            body=data.body,
            category=data.category,
            tags=data.tags,
            featured=data.featured,
            reading_time_minutes=reading_time,
        )

        await self._audit.write(
            action=_ACTION_CREATED,
            actor=actor,
            resource_type=_RESOURCE_TYPE,
            resource_id=str(article.id),
            metadata={"slug": slug, "status": ArticleStatus.DRAFT},
            ip_address=ip_address,
        )
        await self._session.commit()

        logger.info("Admin created article id=%s slug=%r actor=%s", article.id, slug, actor)
        return AdminArticleDetail.model_validate(article)

    # ── Update ────────────────────────────────────────────────────────────────

    async def update_article(
        self,
        article_id: uuid.UUID,
        data: ArticleUpdate,
        *,
        actor: str,
        ip_address: str | None,
    ) -> AdminArticleDetail:
        """
        Update editable fields.

        Raises:
            LookupError — article not found.
        """
        article = await self._repo.get_by_id(article_id)
        if article is None:
            raise LookupError(f"Article {article_id} not found.")

        reading_time = (
            _calculate_reading_time(data.body)
            if data.body is not None
            else article.reading_time_minutes
        )

        article = await self._repo.update(
            article,
            title=data.title,
            summary=data.summary,
            body=data.body,
            category=data.category,
            tags=data.tags,
            featured=data.featured,
            reading_time_minutes=reading_time,
        )

        await self._audit.write(
            action=_ACTION_UPDATED,
            actor=actor,
            resource_type=_RESOURCE_TYPE,
            resource_id=str(article_id),
            metadata={"status": article.status},
            ip_address=ip_address,
        )
        await self._session.commit()

        logger.info("Admin updated article id=%s actor=%s", article_id, actor)
        return AdminArticleDetail.model_validate(article)

    # ── Status mutations ──────────────────────────────────────────────────────

    async def publish_article(
        self,
        article_id: uuid.UUID,
        *,
        actor: str,
        ip_address: str | None,
    ) -> AdminArticleDetail:
        """
        Transition draft → published.

        Raises:
            LookupError  — article not found.
            ValueError   — required fields missing (title, summary, body, category).
        """
        article = await self._repo.get_by_id(article_id)
        if article is None:
            raise LookupError(f"Article {article_id} not found.")

        missing = [
            field for field, value in [
                ("title",    article.title),
                ("summary",  article.summary),
                ("body",     article.body),
                ("category", article.category),
            ]
            if not value
        ]
        if missing:
            raise ValueError(
                f"Cannot publish: missing required fields: {', '.join(missing)}"
            )

        # Set published_at only on first publish
        published_at = article.published_at or datetime.now(UTC)

        article = await self._repo.update_status(
            article,
            ArticleStatus.PUBLISHED,
            published_at=published_at,
        )
        await self._audit.write(
            action=_ACTION_PUBLISHED,
            actor=actor,
            resource_type=_RESOURCE_TYPE,
            resource_id=str(article_id),
            metadata={"slug": article.slug},
            ip_address=ip_address,
        )
        await self._session.commit()

        logger.info(
            "Admin published article id=%s slug=%r actor=%s",
            article_id,
            article.slug,
            actor,
        )
        return AdminArticleDetail.model_validate(article)

    async def unpublish_article(
        self,
        article_id: uuid.UUID,
        *,
        actor: str,
        ip_address: str | None,
    ) -> AdminArticleDetail:
        """Transition published → draft. Article disappears from public immediately."""
        return await self._mutate_status(
            article_id,
            new_status=ArticleStatus.DRAFT,
            action=_ACTION_UNPUBLISHED,
            actor=actor,
            ip_address=ip_address,
        )

    async def archive_article(
        self,
        article_id: uuid.UUID,
        *,
        actor: str,
        ip_address: str | None,
    ) -> AdminArticleDetail:
        """Archive — hidden from both public and default admin list."""
        return await self._mutate_status(
            article_id,
            new_status=ArticleStatus.ARCHIVED,
            action=_ACTION_ARCHIVED,
            actor=actor,
            ip_address=ip_address,
        )

    async def _mutate_status(
        self,
        article_id: uuid.UUID,
        *,
        new_status: ArticleStatus,
        action: str,
        actor: str,
        ip_address: str | None,
    ) -> AdminArticleDetail:
        article = await self._repo.get_by_id(article_id)
        if article is None:
            raise LookupError(f"Article {article_id} not found.")

        previous = article.status
        article = await self._repo.update_status(article, new_status)
        await self._audit.write(
            action=action,
            actor=actor,
            resource_type=_RESOURCE_TYPE,
            resource_id=str(article_id),
            metadata={"status_before": previous, "status_after": new_status},
            ip_address=ip_address,
        )
        await self._session.commit()

        logger.info(
            "Admin %s article id=%s actor=%s %s→%s",
            action, article_id, actor, previous, new_status,
        )
        return AdminArticleDetail.model_validate(article)

    # ── Delete ────────────────────────────────────────────────────────────────

    async def delete_article(
        self,
        article_id: uuid.UUID,
        *,
        actor: str,
        ip_address: str | None,
    ) -> None:
        """
        Hard-delete an article. Audit log written before deletion in same transaction.

        Raises:
            LookupError — article not found.
        """
        article = await self._repo.get_by_id(article_id)
        if article is None:
            raise LookupError(f"Article {article_id} not found.")

        status_at_delete = article.status

        await self._audit.write(
            action=_ACTION_DELETED,
            actor=actor,
            resource_type=_RESOURCE_TYPE,
            resource_id=str(article_id),
            metadata={"slug": article.slug, "status_at_delete": status_at_delete},
            ip_address=ip_address,
        )
        await self._repo.delete(article)
        await self._session.commit()

        logger.info("Admin deleted article id=%s actor=%s", article_id, actor)

    # ── Helpers ───────────────────────────────────────────────────────────────

    async def _unique_slug(self, base: str) -> str:
        """
        Return a slug that does not exist in the database.

        If base is taken, appends -2, -3, ... until a free slot is found.
        """
        slug = base
        counter = 2
        while await self._repo.slug_exists(slug):
            slug = f"{base}-{counter}"
            counter += 1
        return slug
