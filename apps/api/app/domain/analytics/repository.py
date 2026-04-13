from sqlalchemy import text
from sqlalchemy.orm import Session


class AnalyticsRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_vereador_dashboard(self, vereador_id):
        stmt = text(
            """
            select vereador_id, total_captures, total_beneficiarios, open_demands, open_tasks
            from analytics.mv_vereador_dashboard
            where vereador_id = :vereador_id
            """
        )
        row = self.db.execute(stmt, {"vereador_id": vereador_id}).mappings().first()
        return dict(row) if row else None
