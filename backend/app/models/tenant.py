"""Tenant Model – multi-tenancy support"""

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, String, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Tenant(Base):
    __tablename__ = "tenants"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    slug: Mapped[str] = mapped_column(String(80), unique=True, nullable=False, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False, default="")
    plan: Mapped[str] = mapped_column(String(30), default="starter")  # starter | pro | enterprise
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    api_key: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, default=lambda: uuid.uuid4().hex)
    settings: Mapped[dict | None] = mapped_column(JSONB, nullable=True)  # JSON blob for custom settings
    # Company / profile info
    company_name: Mapped[str | None] = mapped_column(String(120), nullable=True)
    website: Mapped[str | None] = mapped_column(String(255), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(30), nullable=True)
    timezone: Mapped[str] = mapped_column(String(60), default="UTC")
    logo_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    leads: Mapped[list["Lead"]] = relationship("Lead", back_populates="tenant", cascade="all, delete-orphan")  # noqa: F821
    pipelines: Mapped[list["CRMPipeline"]] = relationship("CRMPipeline", back_populates="tenant", cascade="all, delete-orphan")  # noqa: F821
    social_posts: Mapped[list["SocialPost"]] = relationship("SocialPost", back_populates="tenant", cascade="all, delete-orphan")  # noqa: F821
    email_campaigns: Mapped[list["EmailCampaign"]] = relationship("EmailCampaign", back_populates="tenant", cascade="all, delete-orphan")  # noqa: F821

    def __repr__(self) -> str:
        return f"<Tenant {self.slug}>"
