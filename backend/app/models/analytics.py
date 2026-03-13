"""Analytics Event Model"""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class AnalyticsEvent(Base):
    __tablename__ = "analytics_events"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True
    )

    event_type: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    # e.g. lead_created, lead_converted, post_published, email_opened, email_clicked

    source: Mapped[str | None] = mapped_column(String(80), nullable=True, index=True)
    campaign: Mapped[str | None] = mapped_column(String(120), nullable=True, index=True)
    platform: Mapped[str | None] = mapped_column(String(30), nullable=True, index=True)

    # Flexible JSONB payload for event-specific data
    event_metadata: Mapped[dict | None] = mapped_column("metadata", JSONB, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), index=True
    )

    def __repr__(self) -> str:
        return f"<AnalyticsEvent {self.event_type} [{self.created_at}]>"
