"""Lead Model – incoming leads from forms / integrations"""

import uuid
from datetime import datetime
from enum import Enum as PyEnum

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class LeadStatus(str, PyEnum):
    NEW = "new"
    CONTACTED = "contacted"
    QUALIFIED = "qualified"
    DISQUALIFIED = "disqualified"
    CONVERTED = "converted"


class Lead(Base):
    __tablename__ = "leads"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)

    # Core fields
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    phone: Mapped[str | None] = mapped_column(String(30), nullable=True)
    company: Mapped[str | None] = mapped_column(String(120), nullable=True)
    source: Mapped[str | None] = mapped_column(String(80), nullable=True)   # e.g. "facebook_ad", "website"
    campaign: Mapped[str | None] = mapped_column(String(120), nullable=True)
    medium: Mapped[str | None] = mapped_column(String(80), nullable=True)   # utm_medium
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # AI classification
    ai_score: Mapped[int | None] = mapped_column(nullable=True)             # 0-100 lead score
    ai_label: Mapped[str | None] = mapped_column(String(30), nullable=True) # hot | warm | cold

    status: Mapped[LeadStatus] = mapped_column(
        String(30), default=LeadStatus.NEW, index=True
    )

    # CRM reference
    pipeline_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("crm_pipelines.id", ondelete="SET NULL"), nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    tenant: Mapped["Tenant"] = relationship("Tenant", back_populates="leads")  # noqa: F821
    pipeline: Mapped["CRMPipeline | None"] = relationship("CRMPipeline", back_populates="leads")  # noqa: F821

    def __repr__(self) -> str:
        return f"<Lead {self.name} ({self.email})>"
