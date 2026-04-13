"""create polo schema

Revision ID: 0004_create_polo_schema
Revises: 0003_create_territory_schema
Create Date: 2026-04-10 00:00:04
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0004_create_polo_schema"
down_revision = "0003_create_territory_schema"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE SCHEMA IF NOT EXISTS polo")

    op.create_table(
        "units",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("core.organizations.id"), nullable=False, unique=True),
        sa.Column("code", sa.String(length=50), nullable=True),
        sa.Column("address_label", sa.String(length=255), nullable=True),
        sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
        schema="polo",
    )

    op.create_table(
        "beneficiarios",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("polo_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("polo.units.id"), nullable=False),
        sa.Column("person_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("core.persons.id"), nullable=False),
        sa.Column("source_capture_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("territory.contacts_capture.id"), nullable=True),
        sa.Column("status", sa.String(length=30), nullable=False, server_default="PRE_CADASTRADO"),
        sa.Column("admitted_at", sa.DateTime(), nullable=True),
        sa.Column("discharged_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
        sa.UniqueConstraint("polo_id", "person_id", name="uq_polo_beneficiarios_polo_person"),
        schema="polo",
    )

    op.create_table(
        "modalidades",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("polo_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("polo.units.id"), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
        schema="polo",
    )

    op.create_table(
        "matriculas_modalidade",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("beneficiario_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("polo.beneficiarios.id", ondelete="CASCADE"), nullable=False),
        sa.Column("modalidade_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("polo.modalidades.id"), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False, server_default="ATIVA"),
        sa.Column("start_date", sa.Date(), nullable=False),
        sa.Column("end_date", sa.Date(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
        schema="polo",
    )

    op.create_table(
        "frequencias",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("beneficiario_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("polo.beneficiarios.id", ondelete="CASCADE"), nullable=False),
        sa.Column("modalidade_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("polo.modalidades.id"), nullable=True),
        sa.Column("registered_by_user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("iam.users.id"), nullable=False),
        sa.Column("activity_date", sa.Date(), nullable=False),
        sa.Column("present", sa.Boolean(), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
        sa.UniqueConstraint("beneficiario_id", "modalidade_id", "activity_date", name="uq_polo_frequencias_unique"),
        schema="polo",
    )

    op.create_table(
        "ocorrencias",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("polo_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("polo.units.id"), nullable=False),
        sa.Column("beneficiario_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("polo.beneficiarios.id"), nullable=True),
        sa.Column("registered_by_user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("iam.users.id"), nullable=False),
        sa.Column("severity", sa.String(length=20), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="OPEN"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
        schema="polo",
    )

    op.create_table(
        "daily_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("polo_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("polo.units.id"), nullable=False),
        sa.Column("created_by_user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("iam.users.id"), nullable=False),
        sa.Column("log_date", sa.Date(), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
        sa.UniqueConstraint("polo_id", "log_date", "created_by_user_id", name="uq_polo_daily_logs_unique"),
        schema="polo",
    )

    op.create_table(
        "purchase_requests",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("polo_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("polo.units.id"), nullable=False),
        sa.Column("requested_by_user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("iam.users.id"), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="OPEN"),
        sa.Column("priority", sa.String(length=20), nullable=False, server_default="MEDIUM"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
        schema="polo",
    )


def downgrade() -> None:
    op.drop_table("purchase_requests", schema="polo")
    op.drop_table("daily_logs", schema="polo")
    op.drop_table("ocorrencias", schema="polo")
    op.drop_table("frequencias", schema="polo")
    op.drop_table("matriculas_modalidade", schema="polo")
    op.drop_table("modalidades", schema="polo")
    op.drop_table("beneficiarios", schema="polo")
    op.drop_table("units", schema="polo")
    op.execute("DROP SCHEMA IF EXISTS polo CASCADE")
