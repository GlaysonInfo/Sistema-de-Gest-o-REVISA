"""create administration schema

Revision ID: 0010_create_admin_schema
Revises: 0009_create_relationship_schema
Create Date: 2026-04-11 00:00:10
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0010_create_admin_schema"
down_revision = "0009_create_relationship_schema"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE SCHEMA IF NOT EXISTS administration")

    op.create_table(
        "funding_sources",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("core.organizations.id"), nullable=True),
        sa.Column("source_type", sa.String(length=60), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("estimated_amount", sa.Numeric(14, 2), nullable=True),
        sa.Column("secured_amount", sa.Numeric(14, 2), nullable=True),
        sa.Column("status", sa.String(length=30), nullable=False, server_default="PLANNED"),
        sa.Column("starts_on", sa.Date(), nullable=True),
        sa.Column("ends_on", sa.Date(), nullable=True),
        sa.Column("responsible_user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("iam.users.id"), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
        schema="administration",
    )

    op.create_table(
        "contracts",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("core.organizations.id"), nullable=True),
        sa.Column("partner_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("relationship.partners.id"), nullable=True),
        sa.Column("funding_source_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("administration.funding_sources.id"), nullable=True),
        sa.Column("contract_type", sa.String(length=60), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("party_name", sa.String(length=255), nullable=True),
        sa.Column("document_number", sa.String(length=60), nullable=True),
        sa.Column("amount", sa.Numeric(14, 2), nullable=True),
        sa.Column("status", sa.String(length=30), nullable=False, server_default="DRAFT"),
        sa.Column("starts_on", sa.Date(), nullable=True),
        sa.Column("ends_on", sa.Date(), nullable=True),
        sa.Column("document_ref", sa.Text(), nullable=True),
        sa.Column("responsible_user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("iam.users.id"), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
        schema="administration",
    )

    op.create_table(
        "budget_items",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("core.organizations.id"), nullable=True),
        sa.Column("funding_source_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("administration.funding_sources.id"), nullable=True),
        sa.Column("contract_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("administration.contracts.id"), nullable=True),
        sa.Column("polo_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("polo.units.id"), nullable=True),
        sa.Column("field_event_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("relationship.field_events.id"), nullable=True),
        sa.Column("category", sa.String(length=80), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("planned_amount", sa.Numeric(14, 2), nullable=False, server_default="0"),
        sa.Column("committed_amount", sa.Numeric(14, 2), nullable=False, server_default="0"),
        sa.Column("paid_amount", sa.Numeric(14, 2), nullable=False, server_default="0"),
        sa.Column("status", sa.String(length=30), nullable=False, server_default="PLANNED"),
        sa.Column("due_on", sa.Date(), nullable=True),
        sa.Column("responsible_user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("iam.users.id"), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
        schema="administration",
    )


def downgrade() -> None:
    op.drop_table("budget_items", schema="administration")
    op.drop_table("contracts", schema="administration")
    op.drop_table("funding_sources", schema="administration")
    op.execute("DROP SCHEMA IF EXISTS administration CASCADE")
