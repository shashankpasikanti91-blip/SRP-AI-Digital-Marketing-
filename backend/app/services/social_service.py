"""Social Media Service"""

import uuid
from datetime import date, datetime, timezone
from typing import Optional

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.social import PostStatus, SocialPlatform, SocialPost
from app.schemas.social import CalendarDay, CalendarResponse, SocialPostCreate, SocialPostUpdate


class SocialService:

    @staticmethod
    async def create(db: AsyncSession, tenant_id: uuid.UUID, payload: SocialPostCreate) -> SocialPost:
        post = SocialPost(tenant_id=tenant_id, **payload.model_dump())
        if post.scheduled_at and post.status == PostStatus.DRAFT:
            post.status = PostStatus.SCHEDULED
        db.add(post)
        await db.flush()
        await db.refresh(post)
        return post

    @staticmethod
    async def get(db: AsyncSession, tenant_id: uuid.UUID, post_id: uuid.UUID) -> SocialPost | None:
        result = await db.execute(
            select(SocialPost).where(SocialPost.id == post_id, SocialPost.tenant_id == tenant_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def list(
        db: AsyncSession,
        tenant_id: uuid.UUID,
        platform: Optional[SocialPlatform] = None,
        status: Optional[PostStatus] = None,
        campaign: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[SocialPost], int]:
        query = select(SocialPost).where(SocialPost.tenant_id == tenant_id)
        if platform:
            query = query.where(SocialPost.platform == platform)
        if status:
            query = query.where(SocialPost.status == status)
        if campaign:
            query = query.where(SocialPost.campaign == campaign)

        count_q = select(func.count()).select_from(query.subquery())
        total = (await db.execute(count_q)).scalar_one()
        query = query.order_by(SocialPost.scheduled_at.asc().nullslast(), SocialPost.created_at.desc())
        query = query.offset((page - 1) * page_size).limit(page_size)
        result = await db.execute(query)
        return list(result.scalars().all()), total

    @staticmethod
    async def get_calendar(
        db: AsyncSession,
        tenant_id: uuid.UUID,
        from_date: date,
        to_date: date,
        platform: Optional[SocialPlatform] = None,
    ) -> CalendarResponse:
        from_dt = datetime.combine(from_date, datetime.min.time()).replace(tzinfo=timezone.utc)
        to_dt = datetime.combine(to_date, datetime.max.time()).replace(tzinfo=timezone.utc)
        query = select(SocialPost).where(
            SocialPost.tenant_id == tenant_id,
            SocialPost.scheduled_at >= from_dt,
            SocialPost.scheduled_at <= to_dt,
        )
        if platform:
            query = query.where(SocialPost.platform == platform)
        query = query.order_by(SocialPost.scheduled_at.asc())
        result = await db.execute(query)
        posts = list(result.scalars().all())

        # Group by date
        day_map: dict[str, list] = {}
        for post in posts:
            day_key = post.scheduled_at.strftime("%Y-%m-%d") if post.scheduled_at else "unscheduled"
            day_map.setdefault(day_key, []).append(post)

        days = [CalendarDay(date=d, posts=p) for d, p in sorted(day_map.items())]
        return CalendarResponse(days=days, from_date=str(from_date), to_date=str(to_date))

    @staticmethod
    async def update(db: AsyncSession, tenant_id: uuid.UUID, post_id: uuid.UUID, payload: SocialPostUpdate) -> SocialPost | None:
        post = await SocialService.get(db, tenant_id, post_id)
        if not post:
            return None
        for field, value in payload.model_dump(exclude_unset=True).items():
            setattr(post, field, value)
        await db.flush()
        await db.refresh(post)
        return post

    @staticmethod
    async def publish_now(db: AsyncSession, tenant_id: uuid.UUID, post_id: uuid.UUID) -> SocialPost | None:
        post = await SocialService.get(db, tenant_id, post_id)
        if not post:
            return None
        # Enqueue immediate publish task
        try:
            from app.workers.social_worker import publish_post_task
            publish_post_task.delay(str(post.id))
        except Exception:
            pass
        post.status = PostStatus.SCHEDULED
        post.scheduled_at = datetime.now(timezone.utc)
        await db.flush()
        await db.refresh(post)
        return post

    @staticmethod
    async def delete(db: AsyncSession, tenant_id: uuid.UUID, post_id: uuid.UUID) -> bool:
        post = await SocialService.get(db, tenant_id, post_id)
        if not post:
            return False
        await db.delete(post)
        return True
