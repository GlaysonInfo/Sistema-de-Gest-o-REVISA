"""create relationship schema

Revision ID: 0009_create_relationship_schema
Revises: 0008_create_analytics_schema
Create Date: 2026-04-11 00:00:09
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0009_create_relationship_schema"
down_revision = "0008_create_analytics_schema"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE SCHEMA IF NOT EXISTS relationship")

    op.create_table(
        "classifications",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("person_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("core.persons.id"), nullable=False),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("core.organizations.id"), nullable=True),
        sa.Column("vereador_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("core.vereadores.id"), nullable=True),
        sa.Column("classified_by_user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("iam.users.id"), nullable=False),
        sa.Column("level", sa.String(length=40), nullable=False),
        sa.Column("influence", sa.String(length=40), nullable=True),
        sa.Column("engagement", sa.String(length=40), nullable=True),
        sa.Column("vote_2028", sa.String(length=40), nullable=True),
        sa.Column("priority", sa.String(length=20), nullable=True),
        sa.Column("status", sa.String(length=30), nullable=False, server_default="ACTIVE"),
        sa.Column("responsible_user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("iam.users.id"), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
        schema="relationship",
    )

    op.create_table(
        "leaderships",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("person_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("core.persons.id"), nullable=False),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("core.organizations.id"), nullable=True),
        sa.Column("vereador_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("core.vereadores.id"), nullable=True),
        sa.Column("polo_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("polo.units.id"), nullable=True),
        sa.Column("district", sa.String(length=120), nullable=True),
        sa.Column("leadership_type", sa.String(length=60), nullable=False),
        sa.Column("area_atuacao", sa.String(length=120), nullable=True),
        sa.Column("influence_count", sa.Integer(), nullable=True),
        sa.Column("loyalty_level", sa.String(length=40), nullable=True),
        sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("identified_at", sa.DateTime(), nullable=True),
        sa.Column("responsible_user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("iam.users.id"), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
        schema="relationship",
    )

    op.create_table(
        "partners",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("core.organizations.id"), nullable=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("legal_name", sa.String(length=255), nullable=True),
        sa.Column("document_number", sa.String(length=30), nullable=True),
        sa.Column("partner_type", sa.String(length=60), nullable=False),
        sa.Column("contact_name", sa.String(length=180), nullable=True),
        sa.Column("contact_phone", sa.String(length=30), nullable=True),
        sa.Column("contact_email", sa.String(length=180), nullable=True),
        sa.Column("district", sa.String(length=120), nullable=True),
        sa.Column("contribution_area", sa.String(length=120), nullable=True),
        sa.Column("service_offered", sa.Text(), nullable=True),
        sa.Column("capacity", sa.String(length=120), nullable=True),
        sa.Column("partnership_type", sa.String(length=60), nullable=True),
        sa.Column("status", sa.String(length=30), nullable=False, server_default="PROSPECT"),
        sa.Column("responsible_user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("iam.users.id"), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
        schema="relationship",
    )

    op.create_table(
        "field_events",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("core.organizations.id"), nullable=True),
        sa.Column("polo_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("polo.units.id"), nullable=True),
        sa.Column("partner_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("relationship.partners.id"), nullable=True),
        sa.Column("created_by_user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("iam.users.id"), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("district", sa.String(length=120), nullable=True),
        sa.Column("event_type", sa.String(length=60), nullable=False),
        sa.Column("event_date", sa.Date(), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False, server_default="PLANNED"),
        sa.Column("expected_people", sa.Integer(), nullable=True),
        sa.Column("actual_people", sa.Integer(), nullable=True),
        sa.Column("captures_count", sa.Integer(), nullable=True),
        sa.Column("leaders_identified", sa.Integer(), nullable=True),
        sa.Column("next_action", sa.Text(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
        schema="relationship",
    )


def downgrade() -> None:
    op.drop_table("field_events", schema="relationship")
    op.drop_table("partners", schema="relationship")
    op.drop_table("leaderships", schema="relationship")
    op.drop_table("classifications", schema="relationship")
    op.execute("DROP SCHEMA IF EXISTS relationship CASCADE")
