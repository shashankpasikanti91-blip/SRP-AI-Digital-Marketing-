"""
Localization Models — Phase 14 Global Localization
====================================================

ORM models for:
- Country
- Language
- State (state-language mapping)
- LocalizationRule
"""

from __future__ import annotations

from datetime import datetime

import sqlalchemy as sa
from sqlalchemy import Boolean, DateTime, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Country(Base):
    """Supported marketing countries with currency and language metadata."""
    __tablename__ = "countries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(5), nullable=False, unique=True, index=True)
    name: Mapped[str] = mapped_column(String(80), nullable=False)
    currency_code: Mapped[str] = mapped_column(String(5), nullable=False, default="USD")
    currency_symbol: Mapped[str] = mapped_column(String(10), nullable=False, default="$")
    default_language: Mapped[str] = mapped_column(String(40), nullable=False, default="english")
    secondary_language: Mapped[str | None] = mapped_column(String(40), nullable=True)
    bilingual_supported: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    english_only: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    language_modes: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    marketing_style: Mapped[str | None] = mapped_column(Text, nullable=True)
    festival_calendar_reference: Mapped[str | None] = mapped_column(String(60), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    def __repr__(self) -> str:
        return f"<Country {self.code} — {self.name}>"


class Language(Base):
    """Global language registry with script and ISO metadata."""
    __tablename__ = "languages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(20), nullable=False, unique=True, index=True)
    iso_code: Mapped[str] = mapped_column(String(5), nullable=False)
    name: Mapped[str] = mapped_column(String(60), nullable=False)
    native_name: Mapped[str | None] = mapped_column(String(60), nullable=True)
    script: Mapped[str | None] = mapped_column(String(40), nullable=True)
    direction: Mapped[str] = mapped_column(String(5), default="ltr", nullable=False)
    countries: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    def __repr__(self) -> str:
        return f"<Language {self.code} ({self.iso_code})>"


class State(Base):
    """State/Province records with language mapping per country."""
    __tablename__ = "states"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    country_code: Mapped[str] = mapped_column(String(5), nullable=False, index=True)
    state_code: Mapped[str | None] = mapped_column(String(10), nullable=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    default_language: Mapped[str] = mapped_column(String(40), nullable=False, default="english")
    secondary_language: Mapped[str | None] = mapped_column(String(40), nullable=True)
    marketing_region: Mapped[str | None] = mapped_column(String(60), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    __table_args__ = (
        sa.UniqueConstraint("country_code", "name", name="uq_states_country_name"),
    )

    def __repr__(self) -> str:
        return f"<State {self.name} ({self.country_code}) → {self.secondary_language}>"


class LocalizationRule(Base):
    """Configurable localization rules by country/state/industry."""
    __tablename__ = "localization_rules"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    country_code: Mapped[str] = mapped_column(String(5), nullable=False, index=True)
    state_code: Mapped[str | None] = mapped_column(String(100), nullable=True)
    industry: Mapped[str | None] = mapped_column(String(60), nullable=True)
    # rule_type: language | tone | template | festival
    rule_type: Mapped[str] = mapped_column(String(40), nullable=False)
    rule_key: Mapped[str] = mapped_column(String(80), nullable=False)
    rule_value: Mapped[str] = mapped_column(Text, nullable=False)
    metadata_: Mapped[dict | None] = mapped_column("metadata", JSONB, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    def __repr__(self) -> str:
        return f"<LocalizationRule {self.country_code}/{self.rule_type}/{self.rule_key}>"
