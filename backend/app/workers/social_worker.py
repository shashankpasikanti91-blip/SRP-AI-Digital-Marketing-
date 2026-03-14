"""Social Post Publisher Worker"""

import asyncio
import logging
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from app.workers.celery_app import celery_app

logger = logging.getLogger(__name__)


def _make_session():
    """Create a fresh engine+session per Celery task to avoid asyncio event-loop conflicts."""
    from app.config import settings
    engine = create_async_engine(settings.DATABASE_URL, poolclass=NullPool)
    return engine, async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


@celery_app.task(name="app.workers.social_worker.check_and_publish_posts", bind=True, max_retries=3)
def check_and_publish_posts(self):
    """Periodic task: find all SCHEDULED posts due for publishing and publish them."""
    asyncio.run(_check_and_publish())


@celery_app.task(name="app.workers.social_worker.publish_post_task", bind=True, max_retries=3)
def publish_post_task(self, post_id: str):
    """Publish a single post immediately."""
    asyncio.run(_publish_single(post_id))


async def _check_and_publish():
    from sqlalchemy import select
    from app.models.social import PostStatus, SocialPost

    engine, session_maker = _make_session()

    now = datetime.now(timezone.utc)
    try:
        async with session_maker() as db:
            result = await db.execute(
                select(SocialPost).where(
                    SocialPost.status == PostStatus.SCHEDULED,
                    SocialPost.scheduled_at <= now,
                )
            )
            due_posts = list(result.scalars().all())
            for post in due_posts:
                try:
                    await _do_publish(post)
                    post.status = PostStatus.PUBLISHED
                    post.published_at = datetime.now(timezone.utc)
                    logger.info("Published post %s to %s", post.id, post.platform)
                except Exception as exc:
                    post.retry_count += 1
                    post.error_message = str(exc)
                    if post.retry_count >= 3:
                        post.status = PostStatus.FAILED
                    logger.error("Failed to publish post %s: %s", post.id, exc)
            await db.commit()
    finally:
        await engine.dispose()


async def _publish_single(post_id: str):
    from sqlalchemy import select
    from app.models.social import PostStatus, SocialPost

    engine, session_maker = _make_session()
    try:
        async with session_maker() as db:
            result = await db.execute(select(SocialPost).where(SocialPost.id == post_id))
            post = result.scalar_one_or_none()
            if not post:
                logger.warning("Post %s not found", post_id)
                return
            try:
                await _do_publish(post)
                post.status = PostStatus.PUBLISHED
                post.published_at = datetime.now(timezone.utc)
            except Exception as exc:
                post.status = PostStatus.FAILED
                post.error_message = str(exc)
            await db.commit()
    finally:
        await engine.dispose()


async def _do_publish(post) -> None:
    """
    Platform-specific publishing logic.
    In production: call Facebook Graph API / Instagram API / LinkedIn API.
    Here we simulate the API call.
    """
    import httpx
    from app.config import settings

    _plat = post.platform.value if hasattr(post.platform, 'value') else str(post.platform)
    if _plat == "facebook":
        if settings.FACEBOOK_ACCESS_TOKEN and settings.FACEBOOK_PAGE_ID:
            async with httpx.AsyncClient() as client:
                resp = await client.post(
                    f"https://graph.facebook.com/v19.0/{settings.FACEBOOK_PAGE_ID}/feed",
                    params={"access_token": settings.FACEBOOK_ACCESS_TOKEN},
                    json={"message": post.content},
                    timeout=30.0,
                )
                resp.raise_for_status()
                data = resp.json()
                post.external_post_id = data.get("id")

    elif _plat == "instagram":
        # Instagram requires a two-step process: create media container, then publish
        if settings.INSTAGRAM_ACCESS_TOKEN and settings.INSTAGRAM_ACCOUNT_ID:
            async with httpx.AsyncClient() as client:
                # Step 1: Create media container
                resp = await client.post(
                    f"https://graph.facebook.com/v19.0/{settings.INSTAGRAM_ACCOUNT_ID}/media",
                    params={"access_token": settings.INSTAGRAM_ACCESS_TOKEN},
                    json={"caption": post.content, "image_url": post.media_url},
                    timeout=30.0,
                )
                resp.raise_for_status()
                container_id = resp.json().get("id")
                # Step 2: Publish
                pub_resp = await client.post(
                    f"https://graph.facebook.com/v19.0/{settings.INSTAGRAM_ACCOUNT_ID}/media_publish",
                    params={"access_token": settings.INSTAGRAM_ACCESS_TOKEN},
                    json={"creation_id": container_id},
                    timeout=30.0,
                )
                pub_resp.raise_for_status()
                post.external_post_id = pub_resp.json().get("id")

    elif _plat == "linkedin":
        if settings.LINKEDIN_ACCESS_TOKEN:
            async with httpx.AsyncClient() as client:
                payload = {
                    "author": f"urn:li:organization:{settings.LINKEDIN_ORG_ID}",
                    "lifecycleState": "PUBLISHED",
                    "specificContent": {
                        "com.linkedin.ugc.ShareContent": {
                            "shareCommentary": {"text": post.content},
                            "shareMediaCategory": "NONE",
                        }
                    },
                    "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"},
                }
                resp = await client.post(
                    "https://api.linkedin.com/v2/ugcPosts",
                    headers={"Authorization": f"Bearer {settings.LINKEDIN_ACCESS_TOKEN}"},
                    json=payload,
                    timeout=30.0,
                )
                resp.raise_for_status()
                post.external_post_id = resp.headers.get("X-RestLi-Id", "")
    else:
        logger.warning("Unknown platform: %s — skipping API call", post.platform)
