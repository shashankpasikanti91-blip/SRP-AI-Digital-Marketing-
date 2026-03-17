"""Conversations Router — unified inbox + AI replies"""
import uuid
from typing import Optional

from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy import func, select

from app.core.dependencies import DB, CurrentTenant
from app.models.conversation import (
    Conversation,
    ConversationChannel,
    ConversationMessage,
    ConversationStatus,
)

from enum import Enum as PyEnum


class SenderRole(str, PyEnum):
    CONTACT = "contact"
    AGENT = "agent"
    BOT = "bot"

router = APIRouter(prefix="/conversations", tags=["Conversations"])


class ConversationCreate(BaseModel):
    contact_name: str
    contact_identifier: Optional[str] = None  # email, phone, or page ID
    channel: ConversationChannel
    lead_id: Optional[uuid.UUID] = None
    external_thread_id: Optional[str] = None
    assigned_to: Optional[str] = None


class MessageCreate(BaseModel):
    content: str = Field(..., min_length=1)
    role: str = "user"   # user | assistant | system
    ai_generated: bool = False


class AIReplyRequest(BaseModel):
    context_notes: Optional[str] = None
    tone: str = "professional"
    reply_goal: Optional[str] = None


class StatusUpdate(BaseModel):
    status: ConversationStatus


@router.get("/")
async def list_conversations(
    tenant: CurrentTenant,
    db: DB,
    channel: Optional[ConversationChannel] = None,
    conv_status: Optional[ConversationStatus] = Query(None, alias="status"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    query = select(Conversation).where(Conversation.tenant_id == tenant.id)
    if channel:
        query = query.where(Conversation.channel == channel)
    if conv_status:
        query = query.where(Conversation.status == conv_status)
    total = (await db.execute(select(func.count()).select_from(query.subquery()))).scalar_one()
    query = query.order_by(Conversation.last_message_at.desc()).offset((page - 1) * page_size).limit(page_size)
    items = list((await db.execute(query)).scalars().all())
    return {"items": items, "total": total, "page": page, "page_size": page_size}


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_conversation(payload: ConversationCreate, tenant: CurrentTenant, db: DB):
    conv = Conversation(tenant_id=tenant.id, **payload.model_dump())
    db.add(conv)
    await db.flush()
    await db.refresh(conv)
    return conv


@router.get("/{conv_id}")
async def get_conversation(conv_id: uuid.UUID, tenant: CurrentTenant, db: DB):
    result = await db.execute(
        select(Conversation).where(Conversation.id == conv_id, Conversation.tenant_id == tenant.id)
    )
    conv = result.scalar_one_or_none()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return conv


@router.get("/{conv_id}/messages")
async def list_messages(
    conv_id: uuid.UUID,
    tenant: CurrentTenant,
    db: DB,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
):
    conv_res = await db.execute(
        select(Conversation).where(Conversation.id == conv_id, Conversation.tenant_id == tenant.id)
    )
    if not conv_res.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Conversation not found")

    query = select(ConversationMessage).where(ConversationMessage.conversation_id == conv_id)
    total = (await db.execute(select(func.count()).select_from(query.subquery()))).scalar_one()
    query = query.order_by(ConversationMessage.created_at.asc()).offset((page - 1) * page_size).limit(page_size)
    items = list((await db.execute(query)).scalars().all())
    return {"items": items, "total": total}


@router.post("/{conv_id}/messages", status_code=status.HTTP_201_CREATED)
async def add_message(conv_id: uuid.UUID, payload: MessageCreate, tenant: CurrentTenant, db: DB):
    conv_res = await db.execute(
        select(Conversation).where(Conversation.id == conv_id, Conversation.tenant_id == tenant.id)
    )
    conv = conv_res.scalar_one_or_none()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")

    msg = ConversationMessage(
        conversation_id=conv_id,
        tenant_id=tenant.id,
        content=payload.content,
        role=payload.role,
        ai_generated=payload.ai_generated,
    )
    db.add(msg)

    from datetime import datetime, timezone
    conv.last_message_at = datetime.now(timezone.utc)
    conv.unread_count = (conv.unread_count or 0) + 1
    conv.last_message_preview = payload.content[:200]

    await db.flush()
    await db.refresh(msg)
    return msg


@router.post("/{conv_id}/ai-reply")
async def generate_ai_reply(conv_id: uuid.UUID, payload: AIReplyRequest, tenant: CurrentTenant, db: DB):
    """Use Conversation Agent to generate a smart contextual reply."""
    conv_res = await db.execute(
        select(Conversation).where(Conversation.id == conv_id, Conversation.tenant_id == tenant.id)
    )
    conv = conv_res.scalar_one_or_none()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")

    messages_res = await db.execute(
        select(ConversationMessage)
        .where(ConversationMessage.conversation_id == conv_id)
        .order_by(ConversationMessage.created_at.desc())
        .limit(10)
    )
    messages = list(reversed(messages_res.scalars().all()))
    history = [{"role": m.role, "content": m.content} for m in messages]

    from app.agents.conversation_agent import ConversationAgent
    agent = ConversationAgent()
    try:
        reply = await agent.run(
            contact_name=conv.contact_name or "Customer",
            channel=(conv.channel.value if hasattr(conv.channel, 'value') else str(conv.channel)) if conv.channel else "email",
            conversation_history=history,
            context_notes=payload.context_notes,
            tone=payload.tone,
            reply_goal=payload.reply_goal,
        )

        if reply.should_escalate:
            conv.status = ConversationStatus.ESCALATED

        return {
            "reply": reply.reply_text,
            "suggested_subject": reply.suggested_subject,
            "should_escalate": reply.should_escalate,
            "escalation_reason": reply.escalation_reason,
            "next_action": reply.next_action,
            "confidence_score": reply.confidence_score,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI reply failed: {str(e)}")


@router.patch("/{conv_id}/status")
async def update_status(conv_id: uuid.UUID, payload: StatusUpdate, tenant: CurrentTenant, db: DB):
    conv_res = await db.execute(
        select(Conversation).where(Conversation.id == conv_id, Conversation.tenant_id == tenant.id)
    )
    conv = conv_res.scalar_one_or_none()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    conv.status = payload.status
    if payload.status in (ConversationStatus.RESOLVED, ConversationStatus.SPAM):
        conv.unread_count = 0
    await db.flush()
    await db.refresh(conv)
    return conv
