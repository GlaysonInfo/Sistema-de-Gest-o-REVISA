"""modality action plans

Revision ID: 0015_modality_action_plans
Revises: 0014_permanent_assets
Create Date: 2026-04-12 21:35:00
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0015_modality_action_plans"
down_revision = "0014_permanent_assets"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "modality_action_plans",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("polo_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("polo.units.id"), nullable=False),
        sa.Column("modalidade_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("polo.modalidades.id"), nullable=False),
        sa.Column("uploaded_by_user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("iam.users.id"), nullable=False),
        sa.Column("base_year", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("professional_name", sa.String(length=180), nullable=True),
        sa.Column("original_filename", sa.String(length=255), nullable=False),
        sa.Column("stored_path", sa.Text(), nullable=False),
        sa.Column("content_type", sa.String(length=120), nullable=True),
        sa.Column("file_size", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False, server_default="SUBMITTED"),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("uploaded_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
        schema="polo",
    )
    op.create_index(
        "ix_modality_action_plans_polo_year",
        "modality_action_plans",
        ["polo_id", "base_year"],
        schema="polo",
    )
    op.create_index(
        "ix_modality_action_plans_modalidade_year",
        "modality_action_plans",
        ["modalidade_id", "base_year"],
        schema="polo",
    )


def downgrade() -> None:
    op.drop_index("ix_modality_action_plans_modalidade_year", table_name="modality_action_plans", schema="polo")
    op.drop_index("ix_modality_action_plans_polo_year", table_name="modality_action_plans", schema="polo")
    op.drop_table("modality_action_plans", schema="polo")
