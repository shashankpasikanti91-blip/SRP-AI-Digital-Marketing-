"""Follow-up Sequence & Step Models — automated nurture flows"""
import uuid
from datetime import datetime
from enum import Enum as PyEnum

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class SequenceStatus(str, PyEnum):
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    ARCHIVED = "archived"


class FollowupSequence(Base):
    __tablename__ = "followup_sequences"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )

    name: Mapped[str] = mapped_column(String(200), nullable=False)
    trigger: Mapped[str] = mapped_column(String(100), nullable=False)   # new_lead|no_reply|won|lost
    sequence_type: Mapped[str] = mapped_column(String(60), default="new_lead")
    status: Mapped[SequenceStatus] = mapped_column(
        Enum(SequenceStatus, name="sequence_status_enum", native_enum=False), default=SequenceStatus.DRAFT
    )

    target_segment: Mapped[str | None] = mapped_column(String(100), nullable=True)
    exit_conditions: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    ai_generated_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    # Stats
    enrolled_count: Mapped[int] = mapped_column(Integer, default=0)
    completed_count: Mapped[int] = mapped_column(Integer, default=0)
    reply_count: Mapped[int] = mapped_column(Integer, default=0)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    tenant: Mapped["Tenant"] = relationship("Tenant")  # noqa: F821
    steps: Mapped[list["FollowupStep"]] = relationship(
        "FollowupStep", back_populates="sequence",
        cascade="all, delete-orphan", order_by="FollowupStep.step_number"
    )

    def __repr__(self) -> str:
        return f"<FollowupSequence {self.name}>"


class FollowupStep(Base):
    __tablename__ = "followup_steps"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sequence_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("followup_sequences.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)

    step_number: Mapped[int] = mapped_column(Integer, nullable=False)
    delay_days: Mapped[int] = mapped_column(Integer, default=0)
    channel: Mapped[str] = mapped_column(String(30), nullable=False)   # email|whatsapp|sms|call_reminder
    subject: Mapped[str | None] = mapped_column(String(300), nullable=True)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    cta: Mapped[str | None] = mapped_column(String(200), nullable=True)
    goal: Mapped[str | None] = mapped_column(String(200), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    sequence: Mapped["FollowupSequence"] = relationship("FollowupSequence", back_populates="steps")  # noqa: F821

    def __repr__(self) -> str:
        return f"<FollowupStep {self.step_number} [{self.channel}] +{self.delay_days}d>"
