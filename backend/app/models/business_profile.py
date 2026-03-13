"""Business Profile Model — stores the business setup per tenant"""
import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class BusinessProfile(Base):
    __tablename__ = "business_profiles"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False, unique=True, index=True,
    )

    # Core business info
    business_name: Mapped[str] = mapped_column(String(200), nullable=False)
    business_type: Mapped[str] = mapped_column(String(120), nullable=False)   # e.g. "B2B SaaS", "Retail"
    industry: Mapped[str] = mapped_column(String(120), nullable=False)
    location: Mapped[str | None] = mapped_column(String(200), nullable=True)
    website: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Marketing context
    target_audience: Mapped[str | None] = mapped_column(Text, nullable=True)
    main_offer: Mapped[str | None] = mapped_column(Text, nullable=True)
    unique_selling_proposition: Mapped[str | None] = mapped_column(Text, nullable=True)
    brand_voice: Mapped[str | None] = mapped_column(String(100), nullable=True)  # professional|casual|friendly
    brand_colors: Mapped[list | None] = mapped_column(JSONB, nullable=True)      # ["#FF0000", "#FFFFFF"]
    competitors: Mapped[str | None] = mapped_column(Text, nullable=True)
    current_challenges: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Budget & goals
    monthly_budget: Mapped[str | None] = mapped_column(String(50), nullable=True)
    primary_goal: Mapped[str | None] = mapped_column(String(200), nullable=True)
    channels: Mapped[list | None] = mapped_column(JSONB, nullable=True)          # ["facebook", "email"]

    # Contact & business hours
    contact_phone: Mapped[str | None] = mapped_column(String(30), nullable=True)
    contact_email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    business_hours: Mapped[str | None] = mapped_column(String(200), nullable=True)

    # Generated strategy (stored for reference)
    strategy_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    onboarding_completed: Mapped[bool] = mapped_column(Boolean, default=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    tenant: Mapped["Tenant"] = relationship("Tenant")  # noqa: F821

    def __repr__(self) -> str:
        return f"<BusinessProfile {self.business_name}>"
