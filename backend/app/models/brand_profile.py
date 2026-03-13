"""Brand Profile Model — tenant brand identity for template-driven poster generation"""
import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class BrandProfile(Base):
    """
    Static brand layer — set once per tenant, reused across all campaigns.
    Visual consistency comes from this model, not from AI generation.
    """
    __tablename__ = "brand_profiles"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False, unique=True, index=True,
    )

    # Brand identity
    brand_name: Mapped[str] = mapped_column(String(200), nullable=False)
    tagline: Mapped[str | None] = mapped_column(String(300), nullable=True)
    logo_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    logo_dark_url: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # Visual identity
    primary_color: Mapped[str] = mapped_column(String(7), default="#1E40AF")    # hex
    secondary_color: Mapped[str] = mapped_column(String(7), default="#FFFFFF")
    accent_color: Mapped[str] = mapped_column(String(7), default="#F59E0B")
    background_color: Mapped[str] = mapped_column(String(7), default="#F8FAFC")
    text_color: Mapped[str] = mapped_column(String(7), default="#1F2937")
    font_family: Mapped[str] = mapped_column(String(100), default="Inter")
    regional_font_family: Mapped[str] = mapped_column(String(100), default="Noto Sans")

    # Contact & footer
    footer_text: Mapped[str | None] = mapped_column(String(500), nullable=True)
    phone_numbers: Mapped[list | None] = mapped_column(JSONB, nullable=True)    # ["040-12345678", "+91-9876543210"]
    address: Mapped[str | None] = mapped_column(Text, nullable=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    website: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Social links
    social_links: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    # e.g. {"facebook": "https://...", "instagram": "...", "linkedin": "...", "youtube": "..."}

    # Industry context
    industry: Mapped[str | None] = mapped_column(String(120), nullable=True)
    # hospital | marketing_agency | recruitment_agency | restaurant | retail | other

    # Regional settings
    default_languages: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    # ["english", "telugu"] — used as default for all campaigns
    city: Mapped[str | None] = mapped_column(String(100), nullable=True)
    state: Mapped[str | None] = mapped_column(String(100), nullable=True)
    country: Mapped[str] = mapped_column(String(10), default="IN")

    # Watermark / stamp
    watermark_text: Mapped[str | None] = mapped_column(String(200), nullable=True)
    accreditation_logos: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    # [{"name": "NABH", "url": "https://..."}]

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    tenant: Mapped["Tenant"] = relationship("Tenant")  # noqa: F821
    poster_templates: Mapped[list["PosterTemplate"]] = relationship(  # noqa: F821
        "PosterTemplate", back_populates="brand_profile", cascade="all, delete-orphan"
    )
    poster_variants: Mapped[list["PosterVariant"]] = relationship(  # noqa: F821
        "PosterVariant", back_populates="brand_profile", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<BrandProfile {self.brand_name}>"
