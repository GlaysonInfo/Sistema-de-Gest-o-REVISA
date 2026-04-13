"""create analytics schema

Revision ID: 0008_create_analytics_schema
Revises: 0007_create_governance_schema
Create Date: 2026-04-10 00:00:08
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0008_create_analytics_schema"
down_revision = "0007_create_governance_schema"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE SCHEMA IF NOT EXISTS analytics")

    op.create_table(
        "feature_store_operational",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("person_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("core.persons.id"), nullable=False),
        sa.Column("ref_date", sa.Date(), nullable=False),
        sa.Column("interactions_30d", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("activities_90d", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("open_demands_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("active_beneficiary", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("linked_vereador_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("core.vereadores.id"), nullable=True),
        sa.Column("linked_polo_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("polo.units.id"), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
        sa.UniqueConstraint("person_id", "ref_date", name="uq_analytics_feature_store_person_ref_date"),
        schema="analytics",
    )

    op.execute(
        """
        create materialized view analytics.mv_vereador_dashboard as
        select
            v.id as vereador_id,
            count(distinct cc.id) as total_captures,
            count(distinct pb.id) as total_beneficiarios,
            count(distinct d.id) filter (where d.status = 'OPEN') as open_demands,
            count(distinct t.id) filter (where t.status = 'OPEN') as open_tasks
        from core.vereadores v
        left join territory.contacts_capture cc on cc.vereador_id = v.id
        left join territory.demands d on d.vereador_id = v.id
        left join workflow.tasks t on t.vereador_id = v.id
        left join territory.contacts_capture cc2 on cc2.vereador_id = v.id
        left join polo.beneficiarios pb on pb.source_capture_id = cc2.id
        group by v.id
        """
    )


def downgrade() -> None:
    op.execute("drop materialized view if exists analytics.mv_vereador_dashboard")
    op.drop_table("feature_store_operational", schema="analytics")
    op.execute("DROP SCHEMA IF EXISTS analytics CASCADE")
