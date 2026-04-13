"""permanent assets

Revision ID: 0014_permanent_assets
Revises: 0013_monthly_reports
Create Date: 2026-04-12 19:20:00
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0014_permanent_assets"
down_revision = "0013_monthly_reports"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE SEQUENCE IF NOT EXISTS administration.permanent_asset_number_seq START WITH 1 INCREMENT BY 1")
    op.create_table(
        "permanent_assets",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("asset_number", sa.String(length=40), nullable=False, unique=True),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("core.organizations.id"), nullable=True),
        sa.Column("vereador_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("core.vereadores.id"), nullable=False),
        sa.Column("polo_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("polo.units.id"), nullable=True),
        sa.Column("funding_source_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("administration.funding_sources.id"), nullable=True),
        sa.Column("purchase_request_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("administration.purchase_requests.id"), nullable=True),
        sa.Column("purchase_request_item_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("administration.purchase_request_items.id"), nullable=True),
        sa.Column("asset_type", sa.String(length=80), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("brand", sa.String(length=180), nullable=True),
        sa.Column("model", sa.String(length=180), nullable=True),
        sa.Column("serial_number", sa.String(length=120), nullable=True),
        sa.Column("acquisition_date", sa.Date(), nullable=True),
        sa.Column("acquisition_value", sa.Numeric(14, 2), nullable=True),
        sa.Column("status", sa.String(length=30), nullable=False, server_default="ACTIVE"),
        sa.Column("location_label", sa.String(length=255), nullable=True),
        sa.Column("label_printed_at", sa.DateTime(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
        schema="administration",
    )


def downgrade() -> None:
    op.drop_table("permanent_assets", schema="administration")
    op.execute("DROP SEQUENCE IF EXISTS administration.permanent_asset_number_seq")
