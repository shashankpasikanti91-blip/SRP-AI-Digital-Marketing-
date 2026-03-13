"""Campaign Model — marketing campaigns with full plan data"""
import uuid
from datetime import datetime
from enum import Enum as PyEnum

from sqlalchemy import Date, DateTime, Enum, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class CampaignStatus(str, PyEnum):
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class Campaign(Base):
    __tablename__ = "campaigns"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )

    name: Mapped[str] = mapped_column(String(200), nullable=False)
    objective: Mapped[str] = mapped_column(String(200), nullable=False)
    status: Mapped[CampaignStatus] = mapped_column(
        Enum(CampaignStatus, name="campaign_status_enum", native_enum=False), default=CampaignStatus.DRAFT
    )

    # Targeting
    target_audience: Mapped[str | None] = mapped_column(Text, nullable=True)
    industry: Mapped[str | None] = mapped_column(String(120), nullable=True)
    channels: Mapped[list | None] = mapped_column(JSONB, nullable=True)   # ["facebook", "email", "linkedin"]

    # Timeline & budget
    start_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    end_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    duration_weeks: Mapped[int] = mapped_column(Integer, default=4)
    budget_total: Mapped[int] = mapped_column(Integer, default=0)        # in cents
    budget_spent: Mapped[int] = mapped_column(Integer, default=0)        # in cents
    currency: Mapped[str] = mapped_column(String(10), default="USD")

    # AI generated plan
    ai_plan_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    # Performance counters (updated by workers)
    leads_generated: Mapped[int] = mapped_column(Integer, default=0)
    impressions: Mapped[int] = mapped_column(Integer, default=0)
    clicks: Mapped[int] = mapped_column(Integer, default=0)
    conversions: Mapped[int] = mapped_column(Integer, default=0)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    tenant: Mapped["Tenant"] = relationship("Tenant")  # noqa: F821
    content_pieces: Mapped[list["ContentPiece"]] = relationship(  # noqa: F821
        "ContentPiece", back_populates="campaign", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Campaign {self.name} [{self.status}]>"
