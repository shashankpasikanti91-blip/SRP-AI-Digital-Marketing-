"""CRM Pipeline Model"""

import uuid
from datetime import datetime
from enum import Enum as PyEnum

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class CRMStage(str, PyEnum):
    NEW = "new"
    CONTACTED = "contacted"
    QUALIFIED = "qualified"
    INTERESTED = "interested"
    APPOINTMENT_BOOKED = "appointment_booked"
    PROPOSAL_SENT = "proposal_sent"
    WON = "won"
    LOST = "lost"


class CRMPipeline(Base):
    __tablename__ = "crm_pipelines"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    stage: Mapped[CRMStage] = mapped_column(
        String(50), default=CRMStage.NEW, index=True
    )
    value: Mapped[int | None] = mapped_column(Integer, nullable=True)  # deal value in cents
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    assigned_to: Mapped[str | None] = mapped_column(String(120), nullable=True)
    expected_close: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    lost_reason: Mapped[str | None] = mapped_column(String(255), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    tenant: Mapped["Tenant"] = relationship("Tenant", back_populates="pipelines")  # noqa: F821
    leads: Mapped[list["Lead"]] = relationship("Lead", back_populates="pipeline")  # noqa: F821

    def __repr__(self) -> str:
        return f"<CRMPipeline {self.title} [{self.stage}]>"
