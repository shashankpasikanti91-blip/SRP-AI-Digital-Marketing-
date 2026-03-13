"""Design Brief Model"""
import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class DesignBrief(Base):
    __tablename__ = "design_briefs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    campaign_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("campaigns.id", ondelete="SET NULL"),
        nullable=True,
    )

    campaign_name: Mapped[str] = mapped_column(String(200), nullable=False)
    format_type: Mapped[str] = mapped_column(String(50), nullable=False)  # image_ad|reel|carousel|banner|story
    platform: Mapped[str] = mapped_column(String(50), nullable=False)
    headline: Mapped[str] = mapped_column(String(300), nullable=False)
    subheadline: Mapped[str | None] = mapped_column(String(300), nullable=True)
    cta_text: Mapped[str | None] = mapped_column(String(100), nullable=True)
    color_palette: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    mood: Mapped[str | None] = mapped_column(String(100), nullable=True)
    imagery_description: Mapped[str | None] = mapped_column(Text, nullable=True)
    full_brief_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    tenant: Mapped["Tenant"] = relationship("Tenant")  # noqa: F821

    def __repr__(self) -> str:
        return f"<DesignBrief {self.campaign_name} [{self.format_type}]>"
