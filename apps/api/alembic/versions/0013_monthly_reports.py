"""monthly reports

Revision ID: 0013_monthly_reports
Revises: 0012_purchase_request_items
Create Date: 2026-04-12 18:45:00
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0013_monthly_reports"
down_revision = "0012_purchase_request_items"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "monthly_reports",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("polo_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("polo.units.id"), nullable=False),
        sa.Column("vereador_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("core.vereadores.id"), nullable=False),
        sa.Column("created_by_user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("iam.users.id"), nullable=False),
        sa.Column("reference_month", sa.Date(), nullable=False),
        sa.Column("submitted_at", sa.DateTime(), nullable=True),
        sa.Column("status", sa.String(length=30), nullable=False, server_default="SUBMITTED"),
        sa.Column("active_modalities_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("total_beneficiaries", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("occurrence_summary", sa.Text(), nullable=True),
        sa.Column("narrative_text", sa.Text(), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
        schema="polo",
    )
    op.create_table(
        "monthly_report_modalities",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("monthly_report_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("polo.monthly_reports.id"), nullable=False),
        sa.Column("modalidade_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("polo.modalidades.id"), nullable=True),
        sa.Column("modalidade_name", sa.String(length=255), nullable=False),
        sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("beneficiaries_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
        schema="polo",
    )
    op.create_table(
        "monthly_report_attachments",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("monthly_report_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("polo.monthly_reports.id"), nullable=False),
        sa.Column("modalidade_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("polo.modalidades.id"), nullable=True),
        sa.Column("attachment_type", sa.String(length=60), nullable=False),
        sa.Column("original_filename", sa.String(length=255), nullable=False),
        sa.Column("stored_path", sa.Text(), nullable=False),
        sa.Column("content_type", sa.String(length=120), nullable=True),
        sa.Column("file_size", sa.Integer(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("uploaded_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
        schema="polo",
    )


def downgrade() -> None:
    op.drop_table("monthly_report_attachments", schema="polo")
    op.drop_table("monthly_report_modalities", schema="polo")
    op.drop_table("monthly_reports", schema="polo")
