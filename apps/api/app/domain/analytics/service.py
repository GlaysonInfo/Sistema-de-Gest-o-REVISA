from app.domain.analytics.repository import AnalyticsRepository


class AnalyticsService:
    def __init__(self, repo: AnalyticsRepository):
        self.repo = repo

    def get_vereador_dashboard(self, vereador_id):
        return self.repo.get_vereador_dashboard(vereador_id)
