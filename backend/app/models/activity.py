"""Activity / Audit Log Model"""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class ActivityLog(Base):
    __tablename__ = "activity_logs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True
    )
    entity_type: Mapped[str] = mapped_column(String(60), nullable=False)   # lead | deal | post | campaign | auth
    entity_id: Mapped[str | None] = mapped_column(String(36), nullable=True, index=True)
    action: Mapped[str] = mapped_column(String(80), nullable=False)        # created | updated | deleted | scored | sent
    actor: Mapped[str | None] = mapped_column(String(120), nullable=True)  # email or "system"
    details: Mapped[str | None] = mapped_column(Text, nullable=True)       # JSON string with change details
    ip_address: Mapped[str | None] = mapped_column(String(45), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), index=True
    )

    tenant: Mapped["Tenant"] = relationship("Tenant")  # noqa: F821

    def __repr__(self) -> str:
        return f"<ActivityLog {self.entity_type}/{self.action}>"
