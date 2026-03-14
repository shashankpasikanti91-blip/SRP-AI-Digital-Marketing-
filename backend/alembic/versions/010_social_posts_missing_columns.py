"""Add campaign and ai_generated columns to social_posts

Revision ID: 010
Revises: 009
Create Date: 2025-01-01 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

revision = "010_social_posts_missing_columns"
down_revision = "009_ai_usage_tracking"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("social_posts", sa.Column("campaign", sa.String(120), nullable=True))
    op.add_column("social_posts", sa.Column("ai_generated", sa.Boolean(), nullable=False, server_default="false"))
    op.create_index("ix_social_posts_campaign", "social_posts", ["campaign"])


def downgrade() -> None:
    op.drop_index("ix_social_posts_campaign", table_name="social_posts")
    op.drop_column("social_posts", "ai_generated")
    op.drop_column("social_posts", "campaign")
