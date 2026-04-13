"""purchase request items

Revision ID: 0012_purchase_request_items
Revises: 0011_financial_management
Create Date: 2026-04-12 14:45:00
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0012_purchase_request_items"
down_revision = "0011_financial_management"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "purchase_requests",
        sa.Column("requester_name", sa.String(length=180), nullable=True),
        schema="administration",
    )
    op.create_table(
        "purchase_request_items",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("purchase_request_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("administration.purchase_requests.id"), nullable=False),
        sa.Column("line_number", sa.Integer(), nullable=False),
        sa.Column("product", sa.String(length=255), nullable=False),
        sa.Column("size", sa.String(length=120), nullable=True),
        sa.Column("desired_brand", sa.String(length=180), nullable=True),
        sa.Column("quantity", sa.Numeric(14, 2), nullable=False),
        sa.Column("unit", sa.String(length=80), nullable=True),
        sa.Column("estimated_unit_price", sa.Numeric(14, 2), nullable=True),
        sa.Column("estimated_total", sa.Numeric(14, 2), nullable=True),
        sa.Column("approved_unit_price", sa.Numeric(14, 2), nullable=True),
        sa.Column("approved_total", sa.Numeric(14, 2), nullable=True),
        sa.Column("supplier_name", sa.String(length=255), nullable=True),
        sa.Column("quote_ref", sa.Text(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
        schema="administration",
    )


def downgrade() -> None:
    op.drop_table("purchase_request_items", schema="administration")
    op.drop_column("purchase_requests", "requester_name", schema="administration")
