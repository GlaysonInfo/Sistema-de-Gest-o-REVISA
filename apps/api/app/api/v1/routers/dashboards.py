from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps.permissions import require_permission
from app.core.database import get_db
from app.domain.analytics.repository import AnalyticsRepository
from app.domain.analytics.service import AnalyticsService

router = APIRouter()


@router.get("/vereadores/{id}/dashboard")
def vereador_dashboard(
    id: UUID,
    current_user = Depends(require_permission("dashboard.vereador.read")),
    db: Session = Depends(get_db),
):
    data = AnalyticsService(AnalyticsRepository(db)).get_vereador_dashboard(id)
    if not data:
        raise HTTPException(status_code=404, detail="Dashboard não encontrado")
    return data
