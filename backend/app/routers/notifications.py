"""Notifications Router — in-app notification management"""

import uuid
from typing import Optional

from fastapi import APIRouter, Query, status
from pydantic import BaseModel
from sqlalchemy import func, select, update

from app.core.dependencies import DB, CurrentTenant
from app.models.notification import Notification

router = APIRouter(prefix="/notifications", tags=["Notifications"])


class NotificationResponse(BaseModel):
    id: uuid.UUID
    type: str
    title: str
    body: Optional[str] = None
    link: Optional[str] = None
    is_read: bool
    created_at: str

    model_config = {"from_attributes": True}


class NotificationListResponse(BaseModel):
    items: list[NotificationResponse]
    total: int
    unread_count: int


@router.get("/", response_model=NotificationListResponse)
async def list_notifications(
    tenant: CurrentTenant,
    db: DB,
    unread_only: bool = Query(False),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    """List all notifications for the tenant, newest first."""
    query = select(Notification).where(Notification.tenant_id == tenant.id)
    if unread_only:
        query = query.where(Notification.is_read == False)

    # Total count
    count_q = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_q)).scalar_one()

    # Unread count
    unread_q = select(func.count(Notification.id)).where(
        Notification.tenant_id == tenant.id, Notification.is_read == False
    )
    unread_count = (await db.execute(unread_q)).scalar_one()

    query = query.order_by(Notification.created_at.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    items = result.scalars().all()

    return NotificationListResponse(
        items=[
            NotificationResponse(
                id=n.id,
                type=n.type,
                title=n.title,
                body=n.body,
                link=n.link,
                is_read=n.is_read,
                created_at=n.created_at.isoformat(),
            )
            for n in items
        ],
        total=total,
        unread_count=unread_count,
    )


@router.get("/unread-count")
async def get_unread_count(tenant: CurrentTenant, db: DB):
    """Fast unread count for badge display."""
    count = (
        await db.execute(
            select(func.count(Notification.id)).where(
                Notification.tenant_id == tenant.id, Notification.is_read == False
            )
        )
    ).scalar_one()
    return {"unread_count": count}


@router.post("/mark-read/{notification_id}", status_code=status.HTTP_204_NO_CONTENT)
async def mark_read(notification_id: uuid.UUID, tenant: CurrentTenant, db: DB):
    """Mark a single notification as read."""
    await db.execute(
        update(Notification)
        .where(Notification.id == notification_id, Notification.tenant_id == tenant.id)
        .values(is_read=True)
    )


@router.post("/mark-all-read", status_code=status.HTTP_204_NO_CONTENT)
async def mark_all_read(tenant: CurrentTenant, db: DB):
    """Mark all notifications as read."""
    await db.execute(
        update(Notification)
        .where(Notification.tenant_id == tenant.id, Notification.is_read == False)
        .values(is_read=True)
    )


@router.delete("/{notification_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_notification(notification_id: uuid.UUID, tenant: CurrentTenant, db: DB):
    """Delete a notification."""
    result = await db.execute(
        select(Notification).where(Notification.id == notification_id, Notification.tenant_id == tenant.id)
    )
    notif = result.scalar_one_or_none()
    if notif:
        await db.delete(notif)
