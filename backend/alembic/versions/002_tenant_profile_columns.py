"""Add tenant profile columns

Revision ID: 002
Revises: 001
Create Date: 2025-01-01 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

revision = "002"
down_revision = "001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("tenants", sa.Column("company_name", sa.String(length=120), nullable=True))
    op.add_column("tenants", sa.Column("website", sa.String(length=255), nullable=True))
    op.add_column("tenants", sa.Column("phone", sa.String(length=30), nullable=True))
    op.add_column("tenants", sa.Column("timezone", sa.String(length=60), nullable=True, server_default="UTC"))
    op.add_column("tenants", sa.Column("logo_url", sa.String(length=512), nullable=True))


def downgrade() -> None:
    op.drop_column("tenants", "logo_url")
    op.drop_column("tenants", "timezone")
    op.drop_column("tenants", "phone")
    op.drop_column("tenants", "website")
    op.drop_column("tenants", "company_name")
