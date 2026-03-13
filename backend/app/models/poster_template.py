"""Poster Template Model — reusable layout blueprints for campaign poster generation"""
import uuid
from datetime import datetime
from enum import Enum as PyEnum

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class TemplateCategory(str, PyEnum):
    HEALTH_CAMP = "health_camp"
    JOB_OPENING = "job_opening"
    WALKIN_DRIVE = "walkin_drive"
    RESTAURANT_OFFER = "restaurant_offer"
    PRODUCT_SALE = "product_sale"
    EVENT = "event"
    AWARENESS = "awareness"
    GENERAL = "general"


class TemplateLayout(str, PyEnum):
    SQUARE = "square"           # 1080x1080 Instagram
    PORTRAIT = "portrait"       # 1080x1920 Story
    LANDSCAPE = "landscape"     # 1200x628 Facebook/LinkedIn
    WIDE = "wide"               # 1080x566 WhatsApp/Twitter


class PosterTemplate(Base):
    """
    Campaign template layer — reusable layout blocks per campaign type.
    Each template defines where title, subtitle, checklist, CTA, footer go.
    AI generates content; templates control layout.
    """
    __tablename__ = "poster_templates"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    brand_profile_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("brand_profiles.id", ondelete="SET NULL"),
        nullable=True, index=True,
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )

    # Template identity
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    # orthopedic_health_camp | diabetes_health_camp | job_opening | walkin_drive ...

    category: Mapped[TemplateCategory] = mapped_column(
        Enum(TemplateCategory, name="template_category_enum", native_enum=False),
        default=TemplateCategory.GENERAL,
    )
    layout_type: Mapped[TemplateLayout] = mapped_column(
        Enum(TemplateLayout, name="template_layout_enum", native_enum=False),
        default=TemplateLayout.SQUARE,
    )

    # Canvas dimensions
    width: Mapped[int] = mapped_column(Integer, default=1080)
    height: Mapped[int] = mapped_column(Integer, default=1080)

    # Layout structure — defines blocks and their positions
    layout_blocks: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    # Example:
    # {
    #   "background": {"type": "gradient", "colors": ["#1E40AF", "#1E3A8A"]},
    #   "logo": {"x": 40, "y": 40, "w": 120, "h": 60, "position": "top-left"},
    #   "title": {"x": 40, "y": 120, "w": 1000, "font_size": 48, "bold": true, "align": "center"},
    #   "subtitle": {"x": 40, "y": 180, "w": 1000, "font_size": 28, "align": "center"},
    #   "badge": {"x": 40, "y": 240, "type": "pill", "bg": "#F59E0B"},
    #   "checklist": {"x": 60, "y": 320, "font_size": 22, "icon": "checkmark", "columns": 2},
    #   "price_block": {"x": 40, "y": 680, "font_size": 64, "color": "#F59E0B"},
    #   "date_block": {"x": 40, "y": 760, "font_size": 28},
    #   "cta": {"x": 40, "y": 840, "w": 1000, "h": 80, "bg": "#F59E0B", "font_size": 32},
    #   "footer": {"x": 0, "y": 960, "w": 1080, "h": 120, "bg": "#1E3A8A"}
    # }

    # Default content hints (override per campaign)
    default_title_pattern: Mapped[str | None] = mapped_column(String(300), nullable=True)
    # e.g. "{department} Health Camp at {city}"
    default_cta_text: Mapped[str | None] = mapped_column(String(200), nullable=True)
    default_badge_text: Mapped[str | None] = mapped_column(String(100), nullable=True)
    # e.g. "FREE CHECKUP" | "NOW HIRING" | "FLAT 30% OFF"

    # Available variable slots
    required_fields: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    # ["city", "date_range", "doctor_name", "phone"]
    optional_fields: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    # ["offer_price", "original_price", "locality"]

    is_system: Mapped[bool] = mapped_column(Boolean, default=False)   # built-in template
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    brand_profile: Mapped["BrandProfile | None"] = relationship(  # noqa: F821
        "BrandProfile", back_populates="poster_templates"
    )
    tenant: Mapped["Tenant"] = relationship("Tenant")  # noqa: F821
    variants: Mapped[list["PosterVariant"]] = relationship(  # noqa: F821
        "PosterVariant", back_populates="template", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<PosterTemplate {self.slug} [{self.layout_type}]>"
