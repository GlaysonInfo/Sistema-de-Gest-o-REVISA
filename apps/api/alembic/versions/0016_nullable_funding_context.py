"""nullable funding context

Revision ID: 0016_nullable_funding_context
Revises: 0015_modality_action_plans
Create Date: 2026-04-12 23:10:00
"""

from alembic import op

revision = "0016_nullable_funding_context"
down_revision = "0015_modality_action_plans"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column("funding_sources", "vereador_id", nullable=True, schema="administration")
    op.alter_column("financial_movements", "vereador_id", nullable=True, schema="administration")
    op.alter_column("purchase_requests", "vereador_id", nullable=True, schema="administration")
    op.alter_column("purchase_requests", "polo_id", nullable=True, schema="administration")
    op.alter_column("staff_contracts", "vereador_id", nullable=True, schema="administration")
    op.alter_column("staff_contracts", "polo_id", nullable=True, schema="administration")
    op.alter_column("permanent_assets", "vereador_id", nullable=True, schema="administration")


def downgrade() -> None:
    op.execute(
        """
        update administration.funding_sources
        set vereador_id = (select id from core.vereadores order by created_at limit 1)
        where vereador_id is null
        """
    )
    op.execute(
        """
        update administration.financial_movements
        set vereador_id = (select id from core.vereadores order by created_at limit 1)
        where vereador_id is null
        """
    )
    op.execute(
        """
        update administration.purchase_requests
        set vereador_id = (select id from core.vereadores order by created_at limit 1)
        where vereador_id is null
        """
    )
    op.execute(
        """
        update administration.purchase_requests
        set polo_id = (select id from polo.units order by created_at limit 1)
        where polo_id is null
        """
    )
    op.execute(
        """
        update administration.staff_contracts
        set vereador_id = (select id from core.vereadores order by created_at limit 1)
        where vereador_id is null
        """
    )
    op.execute(
        """
        update administration.staff_contracts
        set polo_id = (select id from polo.units order by created_at limit 1)
        where polo_id is null
        """
    )
    op.execute(
        """
        update administration.permanent_assets
        set vereador_id = (select id from core.vereadores order by created_at limit 1)
        where vereador_id is null
        """
    )
    op.alter_column("permanent_assets", "vereador_id", nullable=False, schema="administration")
    op.alter_column("staff_contracts", "polo_id", nullable=False, schema="administration")
    op.alter_column("staff_contracts", "vereador_id", nullable=False, schema="administration")
    op.alter_column("purchase_requests", "polo_id", nullable=False, schema="administration")
    op.alter_column("purchase_requests", "vereador_id", nullable=False, schema="administration")
    op.alter_column("financial_movements", "vereador_id", nullable=False, schema="administration")
    op.alter_column("funding_sources", "vereador_id", nullable=False, schema="administration")
