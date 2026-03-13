"""Content Piece Model — AI-generated content for posts, ads, emails"""
import uuid
from datetime import datetime
from enum import Enum as PyEnum

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class ContentType(str, PyEnum):
    SOCIAL_POST = "social_post"
    AD_COPY = "ad_copy"
    EMAIL = "email"
    BLOG = "blog"
    CAPTION = "caption"
    CTA = "cta"
    SMS = "sms"


class ContentStatus(str, PyEnum):
    DRAFT = "draft"
    APPROVED = "approved"
    SCHEDULED = "scheduled"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class ContentPiece(Base):
    __tablename__ = "content_pieces"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    campaign_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("campaigns.id", ondelete="SET NULL"),
        nullable=True, index=True,
    )

    type: Mapped[ContentType] = mapped_column(
        Enum(ContentType, name="content_type_enum", native_enum=False), nullable=False
    )
    status: Mapped[ContentStatus] = mapped_column(
        Enum(ContentStatus, name="content_status_enum", native_enum=False), default=ContentStatus.DRAFT
    )

    headline: Mapped[str | None] = mapped_column(String(300), nullable=True)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    cta: Mapped[str | None] = mapped_column(String(300), nullable=True)
    platform: Mapped[str | None] = mapped_column(String(50), nullable=True)  # facebook|instagram|linkedin|email
    tone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    hashtags: Mapped[list | None] = mapped_column(JSONB, nullable=True)

    # AI metadata
    ai_generated: Mapped[bool] = mapped_column(default=True)
    ai_full_output: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    tokens_used: Mapped[int] = mapped_column(Integer, default=0)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    tenant: Mapped["Tenant"] = relationship("Tenant")  # noqa: F821
    campaign: Mapped["Campaign | None"] = relationship("Campaign", back_populates="content_pieces")  # noqa: F821

    def __repr__(self) -> str:
        return f"<ContentPiece {self.type} [{self.status}]>"
