"""
Phase 14 — Global Localization Tables

Creates:
  - countries
  - states
  - languages
  - localization_rules

All tables are purely additive — no existing table is altered.
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

revision = "008_global_localization"
down_revision = "007"
branch_labels = None
depends_on = None


def upgrade() -> None:

    # ── countries ──────────────────────────────────────────────────────
    op.create_table(
        "countries",
        sa.Column("id", sa.Integer(), autoincrement=True, primary_key=True),
        sa.Column("code", sa.String(5), nullable=False, unique=True, index=True),   # ISO 3166-1 alpha-2
        sa.Column("name", sa.String(80), nullable=False),
        sa.Column("currency_code", sa.String(5), nullable=False, default="USD"),
        sa.Column("currency_symbol", sa.String(10), nullable=False, default="$"),
        sa.Column("default_language", sa.String(40), nullable=False, default="english"),
        sa.Column("secondary_language", sa.String(40), nullable=True),
        sa.Column("bilingual_supported", sa.Boolean(), default=False, nullable=False),
        sa.Column("english_only", sa.Boolean(), default=False, nullable=False),
        sa.Column("language_modes", JSONB, nullable=True),
        sa.Column("marketing_style", sa.Text(), nullable=True),
        sa.Column("festival_calendar_reference", sa.String(60), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text('true'), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # Seed supported countries
    op.execute("""
        INSERT INTO countries (code, name, currency_code, currency_symbol, default_language, secondary_language,
                               bilingual_supported, english_only, language_modes, marketing_style, festival_calendar_reference)
        VALUES
            ('IN',  'India',       'INR', '₹',   'english', 'regional',         TRUE,  FALSE, '["english","local","bilingual"]', 'vibrant, emotional, family-oriented, trust-focused', 'india'),
            ('MY',  'Malaysia',    'MYR', 'RM',  'english', 'malay',            TRUE,  FALSE, '["english","local","bilingual"]', 'multicultural, inclusive, modern, warm', 'malaysia'),
            ('ID',  'Indonesia',   'IDR', 'Rp',  'english', 'bahasa_indonesia', TRUE,  FALSE, '["english","local","bilingual"]', 'community-driven, respectful, aspirational', 'indonesia'),
            ('TH',  'Thailand',    'THB', '฿',   'english', 'thai',             TRUE,  FALSE, '["english","local","bilingual"]', 'polite, visual-heavy, festive, royalty-respectful', 'thailand'),
            ('SG',  'Singapore',   'SGD', 'S$',  'english', NULL,               FALSE, TRUE,  '["english"]', 'professional, efficiency-focused, premium, multi-ethnic', 'singapore'),
            ('AU',  'Australia',   'AUD', 'A$',  'english', NULL,               FALSE, TRUE,  '["english"]', 'casual, direct, outdoors-friendly, humorous', 'australia'),
            ('NZ',  'New Zealand', 'NZD', 'NZ$', 'english', NULL,               FALSE, TRUE,  '["english"]', 'friendly, eco-conscious, community-focused', 'new_zealand')
        ON CONFLICT (code) DO NOTHING
    """)

    # ── languages ──────────────────────────────────────────────────────
    op.create_table(
        "languages",
        sa.Column("id", sa.Integer(), autoincrement=True, primary_key=True),
        sa.Column("code", sa.String(20), nullable=False, unique=True, index=True),   # internal key e.g. "telugu"
        sa.Column("iso_code", sa.String(5), nullable=False),                          # BCP-47 e.g. "te"
        sa.Column("name", sa.String(60), nullable=False),
        sa.Column("native_name", sa.String(60), nullable=True),
        sa.Column("script", sa.String(40), nullable=True),
        sa.Column("direction", sa.String(5), default="ltr", nullable=False),
        sa.Column("countries", JSONB, nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text('true'), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.execute("""
        INSERT INTO languages (code, iso_code, name, native_name, script, direction, countries)
        VALUES
            ('english',           'en', 'English',          'English',            'Latin',      'ltr', '["IN","MY","ID","TH","SG","AU","NZ"]'),
            ('telugu',            'te', 'Telugu',            'తెలుగు',             'Telugu',     'ltr', '["IN"]'),
            ('hindi',             'hi', 'Hindi',             'हिन्दी',             'Devanagari', 'ltr', '["IN"]'),
            ('tamil',             'ta', 'Tamil',             'தமிழ்',              'Tamil',      'ltr', '["IN","SG","MY"]'),
            ('kannada',           'kn', 'Kannada',           'ಕನ್ನಡ',             'Kannada',    'ltr', '["IN"]'),
            ('malayalam',         'ml', 'Malayalam',         'മലയാളം',             'Malayalam',  'ltr', '["IN"]'),
            ('marathi',           'mr', 'Marathi',           'मराठी',              'Devanagari', 'ltr', '["IN"]'),
            ('gujarati',          'gu', 'Gujarati',          'ગુજરાતી',           'Gujarati',   'ltr', '["IN"]'),
            ('bengali',           'bn', 'Bengali',           'বাংলা',              'Bengali',    'ltr', '["IN"]'),
            ('punjabi',           'pa', 'Punjabi',           'ਪੰਜਾਬੀ',            'Gurmukhi',   'ltr', '["IN"]'),
            ('malay',             'ms', 'Bahasa Melayu',     'Bahasa Melayu',      'Latin',      'ltr', '["MY"]'),
            ('bahasa_indonesia',  'id', 'Bahasa Indonesia',  'Bahasa Indonesia',   'Latin',      'ltr', '["ID"]'),
            ('thai',              'th', 'Thai',              'ภาษาไทย',            'Thai',       'ltr', '["TH"]')
        ON CONFLICT (code) DO NOTHING
    """)

    # ── states ────────────────────────────────────────────────────────
    op.create_table(
        "states",
        sa.Column("id", sa.Integer(), autoincrement=True, primary_key=True),
        sa.Column("country_code", sa.String(5), nullable=False, index=True),
        sa.Column("state_code", sa.String(10), nullable=True),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("default_language", sa.String(40), nullable=False, default="english"),
        sa.Column("secondary_language", sa.String(40), nullable=True),
        sa.Column("marketing_region", sa.String(60), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint("country_code", "name", name="uq_states_country_name"),
    )

    # Seed India states
    op.execute("""
        INSERT INTO states (country_code, name, default_language, secondary_language, marketing_region) VALUES
            ('IN', 'Telangana',                        'english', 'telugu',           'South India'),
            ('IN', 'Andhra Pradesh',                   'english', 'telugu',           'South India'),
            ('IN', 'Tamil Nadu',                       'english', 'tamil',            'South India'),
            ('IN', 'Karnataka',                        'english', 'kannada',          'South India'),
            ('IN', 'Kerala',                           'english', 'malayalam',        'South India'),
            ('IN', 'Maharashtra',                      'english', 'marathi',          'West India'),
            ('IN', 'Gujarat',                          'english', 'gujarati',         'West India'),
            ('IN', 'Uttar Pradesh',                    'english', 'hindi',            'North India'),
            ('IN', 'Rajasthan',                        'english', 'hindi',            'North India'),
            ('IN', 'Madhya Pradesh',                   'english', 'hindi',            'North India'),
            ('IN', 'Delhi',                            'english', 'hindi',            'North India'),
            ('IN', 'Haryana',                          'english', 'hindi',            'North India'),
            ('IN', 'Punjab',                           'english', 'punjabi',          'North India'),
            ('IN', 'Bihar',                            'english', 'hindi',            'North India'),
            ('IN', 'West Bengal',                      'english', 'bengali',          'East India'),
            ('IN', 'Odisha',                           'english', 'odia',             'East India'),
            ('IN', 'Assam',                            'english', 'assamese',         'Northeast India'),
            ('IN', 'Jharkhand',                        'english', 'hindi',            'East India'),
            ('IN', 'Chhattisgarh',                     'english', 'hindi',            'Central India'),
            ('IN', 'Uttarakhand',                      'english', 'hindi',            'North India'),
            ('IN', 'Himachal Pradesh',                 'english', 'hindi',            'North India'),
            ('IN', 'Puducherry',                       'english', 'tamil',            'South India'),
            ('IN', 'Goa',                              'english', 'english',          'West India'),
            ('IN', 'Jammu and Kashmir',                'english', 'hindi',            'North India'),
            ('IN', 'Ladakh',                           'english', 'hindi',            'North India')
        ON CONFLICT (country_code, name) DO NOTHING
    """)

    # ── localization_rules ────────────────────────────────────────────
    op.create_table(
        "localization_rules",
        sa.Column("id", sa.Integer(), autoincrement=True, primary_key=True),
        sa.Column("country_code", sa.String(5), nullable=False, index=True),
        sa.Column("state_code", sa.String(100), nullable=True),   # NULL = applies to all states
        sa.Column("industry", sa.String(60), nullable=True),      # NULL = applies to all industries
        sa.Column("rule_type", sa.String(40), nullable=False),    # language | tone | template | festival
        sa.Column("rule_key", sa.String(80), nullable=False),
        sa.Column("rule_value", sa.Text(), nullable=False),
        sa.Column("metadata", JSONB, nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text('true'), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # Seed core localization rules
    op.execute("""
        INSERT INTO localization_rules (country_code, rule_type, rule_key, rule_value) VALUES
            ('IN', 'language', 'bilingual_default', 'true'),
            ('IN', 'tone', 'marketing_tone', 'vibrant, emotional, trust-first, family-oriented'),
            ('MY', 'language', 'secondary_language', 'malay'),
            ('MY', 'tone', 'marketing_tone', 'multicultural, polite, inclusive'),
            ('ID', 'language', 'secondary_language', 'bahasa_indonesia'),
            ('ID', 'tone', 'marketing_tone', 'community-driven, aspirational'),
            ('TH', 'language', 'secondary_language', 'thai'),
            ('TH', 'tone', 'marketing_tone', 'polite, festive, royalty-respectful'),
            ('SG', 'language', 'language_mode', 'english'),
            ('AU', 'language', 'language_mode', 'english'),
            ('NZ', 'language', 'language_mode', 'english')
        ON CONFLICT DO NOTHING
    """)

    # ── Add localization columns to tenants table (additive only) ─────
    op.add_column("tenants", sa.Column("country", sa.String(5), nullable=True))
    op.add_column("tenants", sa.Column("state", sa.String(100), nullable=True))
    op.add_column("tenants", sa.Column("city", sa.String(100), nullable=True))
    op.add_column("tenants", sa.Column("primary_language", sa.String(40), nullable=True, default="english"))
    op.add_column("tenants", sa.Column("language_mode", sa.String(20), nullable=True, default="english"))
    op.add_column("tenants", sa.Column("price_usd", sa.Numeric(10, 2), nullable=True))


def downgrade() -> None:
    # Remove columns from tenants
    op.drop_column("tenants", "price_usd")
    op.drop_column("tenants", "language_mode")
    op.drop_column("tenants", "primary_language")
    op.drop_column("tenants", "city")
    op.drop_column("tenants", "state")
    op.drop_column("tenants", "country")

    op.drop_table("localization_rules")
    op.drop_table("states")
    op.drop_table("languages")
    op.drop_table("countries")
