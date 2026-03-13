"""Conversation & Message Models — multi-channel inbox"""
import uuid
from datetime import datetime
from enum import Enum as PyEnum

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class ConversationChannel(str, PyEnum):
    FACEBOOK = "facebook"
    INSTAGRAM = "instagram"
    WHATSAPP = "whatsapp"
    EMAIL = "email"
    WEBSITE_CHAT = "website_chat"
    LINKEDIN = "linkedin"


class ConversationStatus(str, PyEnum):
    OPEN = "open"
    WAITING = "waiting"        # waiting for customer reply
    RESOLVED = "resolved"
    ESCALATED = "escalated"   # needs human
    SPAM = "spam"


class Conversation(Base):
    __tablename__ = "conversations"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    lead_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("leads.id", ondelete="SET NULL"),
        nullable=True, index=True,
    )

    channel: Mapped[ConversationChannel] = mapped_column(
        Enum(ConversationChannel, name="conversation_channel_enum", native_enum=False), nullable=False
    )
    status: Mapped[ConversationStatus] = mapped_column(
        Enum(ConversationStatus, name="conversation_status_enum", native_enum=False), default=ConversationStatus.OPEN
    )

    contact_name: Mapped[str | None] = mapped_column(String(120), nullable=True)
    contact_identifier: Mapped[str | None] = mapped_column(String(255), nullable=True)  # email/phone/page_id
    external_thread_id: Mapped[str | None] = mapped_column(String(255), nullable=True)  # platform thread id

    assigned_to: Mapped[str | None] = mapped_column(String(120), nullable=True)
    unread_count: Mapped[int] = mapped_column(default=0)
    last_message_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_message_preview: Mapped[str | None] = mapped_column(String(500), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    tenant: Mapped["Tenant"] = relationship("Tenant")  # noqa: F821
    lead: Mapped["Lead | None"] = relationship("Lead")  # noqa: F821
    messages: Mapped[list["ConversationMessage"]] = relationship(
        "ConversationMessage", back_populates="conversation",
        cascade="all, delete-orphan", order_by="ConversationMessage.created_at"
    )

    def __repr__(self) -> str:
        return f"<Conversation {self.channel} [{self.status}]>"


class ConversationMessage(Base):
    __tablename__ = "conversation_messages"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conversation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("conversations.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)

    role: Mapped[str] = mapped_column(String(20), nullable=False)   # user | assistant | system
    content: Mapped[str] = mapped_column(Text, nullable=False)
    ai_generated: Mapped[bool] = mapped_column(Boolean, default=False)
    ai_metadata: Mapped[dict | None] = mapped_column(JSONB, nullable=True)  # intent, confidence etc.

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), index=True
    )

    conversation: Mapped["Conversation"] = relationship("Conversation", back_populates="messages")  # noqa: F821

    def __repr__(self) -> str:
        return f"<Message {self.role}: {self.content[:40]}>"
