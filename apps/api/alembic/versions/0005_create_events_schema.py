"""create events schema

Revision ID: 0005_create_events_schema
Revises: 0004_create_polo_schema
Create Date: 2026-04-10 00:00:05
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0005_create_events_schema"
down_revision = "0004_create_polo_schema"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE SCHEMA IF NOT EXISTS events")

    op.create_table(
        "events",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("core.organizations.id"), nullable=True),
        sa.Column("vereador_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("core.vereadores.id"), nullable=True),
        sa.Column("created_by_user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("iam.users.id"), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("event_type", sa.String(length=40), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="PLANNED"),
        sa.Column("start_at", sa.DateTime(), nullable=False),
        sa.Column("end_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
        schema="events",
    )

    op.create_table(
        "activities",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("event_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("events.events.id", ondelete="CASCADE"), nullable=True),
        sa.Column("polo_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("polo.units.id"), nullable=True),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("core.organizations.id"), nullable=True),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("activity_type", sa.String(length=40), nullable=False),
        sa.Column("starts_at", sa.DateTime(), nullable=False),
        sa.Column("ends_at", sa.DateTime(), nullable=True),
        sa.Column("recurrence_rule", sa.String(length=255), nullable=True),
        sa.Column("created_by_user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("iam.users.id"), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
        schema="events",
    )

    op.create_table(
        "participations",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("activity_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("events.activities.id", ondelete="CASCADE"), nullable=False),
        sa.Column("person_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("core.persons.id"), nullable=False),
        sa.Column("registered_by_user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("iam.users.id"), nullable=False),
        sa.Column("checkin_at", sa.DateTime(), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="REGISTERED"),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
        sa.UniqueConstraint("activity_id", "person_id", name="uq_events_participations_activity_person"),
        schema="events",
    )


def downgrade() -> None:
    op.drop_table("participations", schema="events")
    op.drop_table("activities", schema="events")
    op.drop_table("events", schema="events")
    op.execute("DROP SCHEMA IF EXISTS events CASCADE")
