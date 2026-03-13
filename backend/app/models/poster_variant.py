"""Poster Variant Model — generated campaign output for each social media platform"""
import uuid
from datetime import datetime
from enum import Enum as PyEnum

from sqlalchemy import DateTime, Enum, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class SocialPlatformVariant(str, PyEnum):
    INSTAGRAM_SQUARE = "instagram_square"      # 1080x1080
    INSTAGRAM_STORY = "instagram_story"        # 1080x1920
    FACEBOOK_POST = "facebook_post"            # 1200x630
    WHATSAPP_SHARE = "whatsapp_share"          # 1080x1080 with compact text
    LINKEDIN_BANNER = "linkedin_banner"        # 1200x628
    TWITTER_POST = "twitter_post"              # 1200x675
    YOUTUBE_THUMBNAIL = "youtube_thumbnail"    # 1280x720


class VariantStatus(str, PyEnum):
    DRAFT = "draft"
    READY = "ready"
    SCHEDULED = "scheduled"
    PUBLISHED = "published"


class PosterVariant(Base):
    """
    Generated poster output — combines brand template + campaign template + dynamic content.
    Each variant targets a specific social media platform with adapted dimensions.
    The poster_json field contains the full structured JSON for frontend rendering.
    """
    __tablename__ = "poster_variants"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    campaign_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("campaigns.id", ondelete="SET NULL"),
        nullable=True, index=True,
    )
    template_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("poster_templates.id", ondelete="SET NULL"),
        nullable=True,
    )
    brand_profile_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("brand_profiles.id", ondelete="SET NULL"),
        nullable=True,
    )

    # Platform targeting
    platform: Mapped[SocialPlatformVariant] = mapped_column(
        Enum(SocialPlatformVariant, name="social_platform_variant_enum", native_enum=False),
        default=SocialPlatformVariant.INSTAGRAM_SQUARE,
    )
    width: Mapped[str] = mapped_column(String(10), default="1080")
    height: Mapped[str] = mapped_column(String(10), default="1080")

    # Campaign dynamic content used to generate this variant
    campaign_data: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    # {city, locality, department, doctor_name, offer_price, date_range, services, ...}

    # Language content
    language_primary: Mapped[str] = mapped_column(String(20), default="english")    # english
    language_secondary: Mapped[str | None] = mapped_column(String(20), nullable=True)  # telugu|hindi|tamil|...

    # Generated bilingual text blocks
    bilingual_content: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    # {
    #   "english_title": "Free Orthopaedic Camp",
    #   "regional_title": "ఉచిత అస్థి చికిత్స శిబిరం",
    #   "english_subtitle": "Expert care for joint & bone problems",
    #   "regional_subtitle": "కీళ్ళ నొప్పులకు నిపుణ వైద్యం",
    #   "english_cta": "Call Now - Free Registration",
    #   "regional_cta": "ఇప్పుడే కాల్ చేయండి - ఉచిత నమోదు",
    #   "services": ["X-Ray", "Consultation", "Physiotherapy"],
    #   "services_regional": ["ఎక్స్-రే", "సంప్రదింపు", "ఫిజియోథెరపీ"]
    # }

    # Full structured poster JSON — used by frontend PosterRenderer component
    poster_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    # {
    #   "layout_type": "square",
    #   "dimensions": {"width": 1080, "height": 1080},
    #   "background": {"type": "gradient", "colors": ["#1E40AF", "#1E3A8A"]},
    #   "layers": [
    #     {"type": "logo", "src": "...", "x": 40, "y": 40, "w": 120, "h": 60},
    #     {"type": "text", "role": "title", "text": "Free Orthopaedic Camp", ...},
    #     {"type": "text", "role": "regional_title", "text": "ఉచిత అస్థి...", ...},
    #     {"type": "checklist", "items": [...], ...},
    #     {"type": "price_block", "price": "₹299", "original": "₹1500", ...},
    #     {"type": "cta_button", "text": "Call Now", ...},
    #     {"type": "footer", "phone": "...", "address": "...", ...}
    #   ]
    # }

    # AI-generated social caption
    social_caption: Mapped[str | None] = mapped_column(Text, nullable=True)
    hashtags: Mapped[list | None] = mapped_column(JSONB, nullable=True)

    # Output URLs (after rendering)
    image_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    thumbnail_url: Mapped[str | None] = mapped_column(String(500), nullable=True)

    status: Mapped[VariantStatus] = mapped_column(
        Enum(VariantStatus, name="variant_status_enum", native_enum=False),
        default=VariantStatus.DRAFT,
    )

    scheduled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    brand_profile: Mapped["BrandProfile | None"] = relationship("BrandProfile", back_populates="poster_variants")  # noqa: F821
    template: Mapped["PosterTemplate | None"] = relationship("PosterTemplate", back_populates="variants")  # noqa: F821
    tenant: Mapped["Tenant"] = relationship("Tenant")  # noqa: F821

    def __repr__(self) -> str:
        return f"<PosterVariant {self.platform} [{self.status}]>"
