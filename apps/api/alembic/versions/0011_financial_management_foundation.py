"""financial management foundation

Revision ID: 0011_financial_management
Revises: 0010_create_admin_schema
Create Date: 2026-04-12 00:00:11
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0011_financial_management"
down_revision = "0010_create_admin_schema"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("units", sa.Column("vereador_id", postgresql.UUID(as_uuid=True), nullable=True), schema="polo")
    op.create_foreign_key(
        "fk_polo_units_vereador_id",
        "units",
        "vereadores",
        ["vereador_id"],
        ["id"],
        source_schema="polo",
        referent_schema="core",
    )
    op.execute(
        """
        update polo.units
        set vereador_id = (select id from core.vereadores order by created_at limit 1)
        where vereador_id is null
        """
    )
    op.alter_column("units", "vereador_id", nullable=False, schema="polo")

    op.add_column("funding_sources", sa.Column("vereador_id", postgresql.UUID(as_uuid=True), nullable=True), schema="administration")
    op.add_column("funding_sources", sa.Column("appropriation_number", sa.String(length=80), nullable=True), schema="administration")
    op.add_column("funding_sources", sa.Column("deposited_amount", sa.Numeric(14, 2), nullable=False, server_default="0"), schema="administration")
    op.add_column("funding_sources", sa.Column("deposited_on", sa.Date(), nullable=True), schema="administration")
    op.create_foreign_key(
        "fk_administration_funding_sources_vereador_id",
        "funding_sources",
        "vereadores",
        ["vereador_id"],
        ["id"],
        source_schema="administration",
        referent_schema="core",
    )
    op.execute(
        """
        update administration.funding_sources
        set vereador_id = (select id from core.vereadores order by created_at limit 1)
        where vereador_id is null
        """
    )
    op.alter_column("funding_sources", "vereador_id", nullable=False, schema="administration")

    op.create_table(
        "financial_movements",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("funding_source_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("administration.funding_sources.id"), nullable=False),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("core.organizations.id"), nullable=True),
        sa.Column("vereador_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("core.vereadores.id"), nullable=False),
        sa.Column("polo_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("polo.units.id"), nullable=True),
        sa.Column("budget_item_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("administration.budget_items.id"), nullable=True),
        sa.Column("contract_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("administration.contracts.id"), nullable=True),
        sa.Column("movement_type", sa.String(length=60), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("amount", sa.Numeric(14, 2), nullable=False),
        sa.Column("movement_date", sa.Date(), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False, server_default="CONFIRMED"),
        sa.Column("document_ref", sa.Text(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
        schema="administration",
    )

    op.create_table(
        "purchase_requests",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("core.organizations.id"), nullable=True),
        sa.Column("vereador_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("core.vereadores.id"), nullable=False),
        sa.Column("polo_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("polo.units.id"), nullable=False),
        sa.Column("funding_source_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("administration.funding_sources.id"), nullable=True),
        sa.Column("requested_by_user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("iam.users.id"), nullable=False),
        sa.Column("category", sa.String(length=80), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("estimated_amount", sa.Numeric(14, 2), nullable=True),
        sa.Column("approved_amount", sa.Numeric(14, 2), nullable=True),
        sa.Column("status", sa.String(length=30), nullable=False, server_default="REQUESTED"),
        sa.Column("needed_on", sa.Date(), nullable=True),
        sa.Column("approved_at", sa.DateTime(), nullable=True),
        sa.Column("purchased_at", sa.DateTime(), nullable=True),
        sa.Column("paid_at", sa.DateTime(), nullable=True),
        sa.Column("supplier_name", sa.String(length=255), nullable=True),
        sa.Column("document_ref", sa.Text(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
        schema="administration",
    )

    op.create_table(
        "staff_contracts",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("core.organizations.id"), nullable=True),
        sa.Column("vereador_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("core.vereadores.id"), nullable=False),
        sa.Column("polo_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("polo.units.id"), nullable=False),
        sa.Column("funding_source_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("administration.funding_sources.id"), nullable=True),
        sa.Column("person_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("core.persons.id"), nullable=False),
        sa.Column("role_title", sa.String(length=120), nullable=False),
        sa.Column("contract_type", sa.String(length=60), nullable=False),
        sa.Column("salary_amount", sa.Numeric(14, 2), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False, server_default="ACTIVE"),
        sa.Column("starts_on", sa.Date(), nullable=False),
        sa.Column("ends_on", sa.Date(), nullable=True),
        sa.Column("terminated_on", sa.Date(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
        schema="administration",
    )


def downgrade() -> None:
    op.drop_table("staff_contracts", schema="administration")
    op.drop_table("purchase_requests", schema="administration")
    op.drop_table("financial_movements", schema="administration")
    op.drop_constraint("fk_administration_funding_sources_vereador_id", "funding_sources", schema="administration", type_="foreignkey")
    op.drop_column("funding_sources", "deposited_on", schema="administration")
    op.drop_column("funding_sources", "deposited_amount", schema="administration")
    op.drop_column("funding_sources", "appropriation_number", schema="administration")
    op.drop_column("funding_sources", "vereador_id", schema="administration")
    op.drop_constraint("fk_polo_units_vereador_id", "units", schema="polo", type_="foreignkey")
    op.drop_column("units", "vereador_id", schema="polo")
