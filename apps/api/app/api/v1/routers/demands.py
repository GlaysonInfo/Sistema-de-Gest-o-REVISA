from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps.permissions import require_permission
from app.core.database import get_db
from app.domain.territory.repository import TerritoryRepository
from app.domain.territory.schemas import DemandAssignRequest, DemandCreate, DemandOut, DemandTaskCreate, DemandUpdate
from app.domain.territory.service import TerritoryService
from app.domain.workflow.schemas import TaskOut

router = APIRouter()


def _service(db: Session) -> TerritoryService:
    return TerritoryService(TerritoryRepository(db))


def _get_demand_or_404(service: TerritoryService, demand_id: UUID):
    demand = service.get_demand(demand_id)
    if demand is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Demanda nao encontrada")
    return demand


@router.get("", response_model=list[DemandOut])
def list_demands(
    status: str | None = None,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    current_user = Depends(require_permission("demand.read")),
    db: Session = Depends(get_db),
):
    return _service(db).list_demands(limit=limit, offset=offset, status=status, current_user=current_user)


@router.post("", response_model=DemandOut, status_code=201)
def create_demand(
    payload: DemandCreate,
    current_user = Depends(require_permission("demand.create")),
    db: Session = Depends(get_db),
):
    result = _service(db).create_demand(
        opened_by_user_id=current_user.id,
        payload=payload,
        db=db,
        current_user=current_user,
    )
    db.commit()
    return result


@router.get("/{demand_id}", response_model=DemandOut)
def get_demand(
    demand_id: UUID,
    current_user = Depends(require_permission("demand.read")),
    db: Session = Depends(get_db),
):
    return _get_demand_or_404(_service(db), demand_id)


@router.patch("/{demand_id}", response_model=DemandOut)
def update_demand(
    demand_id: UUID,
    payload: DemandUpdate,
    current_user = Depends(require_permission("demand.update")),
    db: Session = Depends(get_db),
):
    service = _service(db)
    demand = _get_demand_or_404(service, demand_id)
    result = service.update_demand(demand, payload, db=db, current_user=current_user)
    db.commit()
    return result


@router.post("/{demand_id}/assign", response_model=DemandOut)
def assign_demand(
    demand_id: UUID,
    payload: DemandAssignRequest,
    current_user = Depends(require_permission("demand.assign")),
    db: Session = Depends(get_db),
):
    service = _service(db)
    demand = _get_demand_or_404(service, demand_id)
    result = service.assign_demand(demand, payload, db=db, current_user=current_user)
    db.commit()
    return result


@router.post("/{demand_id}/tasks", response_model=TaskOut, status_code=201)
def create_task_from_demand(
    demand_id: UUID,
    payload: DemandTaskCreate,
    current_user = Depends(require_permission("task.create")),
    db: Session = Depends(get_db),
):
    service = _service(db)
    demand = _get_demand_or_404(service, demand_id)
    result = service.create_task_from_demand(
        demand,
        payload,
        created_by_user_id=current_user.id,
        db=db,
        current_user=current_user,
    )
    db.commit()
    return result
