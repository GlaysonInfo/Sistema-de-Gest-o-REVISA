from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps.permissions import require_permission
from app.core.access_scope import can_access_all_cabinets, scoped_ids
from app.core.database import get_db
from app.domain.cabinet.repository import CabinetRepository
from app.domain.cabinet.schemas import CabinetCreate, CabinetOut, CabinetOverviewOut
from app.domain.cabinet.service import CabinetService

router = APIRouter()


def _service(db: Session) -> CabinetService:
    return CabinetService(CabinetRepository(db))


def _handle_domain_error(exc: Exception):
    if isinstance(exc, LookupError) and str(exc) == "cabinet_not_found":
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Gabinete nao encontrado")
    if isinstance(exc, ValueError) and str(exc) == "cabinet_already_exists":
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Gabinete ja existe")
    raise exc


def _ensure_cabinet_scope(current_user, cabinet: CabinetOut):
    if can_access_all_cabinets(current_user):
        return
    organization_ids = scoped_ids(current_user, "GABINETE")
    vereador_ids = scoped_ids(current_user, "VEREADOR")
    if str(cabinet.organization.id) in organization_ids or str(cabinet.vereador.id) in vereador_ids:
        return
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Gabinete fora do escopo")


@router.get("", response_model=list[CabinetOut])
def list_cabinets(
    current_user = Depends(require_permission("cabinet.read")),
    db: Session = Depends(get_db),
):
    return _service(db).list_cabinets(current_user=current_user)


@router.post("", response_model=CabinetOut, status_code=201)
def create_cabinet(
    payload: CabinetCreate,
    current_user = Depends(require_permission("vereador.create")),
    db: Session = Depends(get_db),
):
    service = _service(db)
    try:
        organization = service.create_cabinet(payload, db=db, current_user=current_user)
    except Exception as exc:
        _handle_domain_error(exc)
    db.commit()
    return service.get_cabinet(organization.id)


@router.get("/{cabinet_id}", response_model=CabinetOut)
def get_cabinet(
    cabinet_id: UUID,
    current_user = Depends(require_permission("cabinet.read")),
    db: Session = Depends(get_db),
):
    cabinet = _service(db).get_cabinet(cabinet_id)
    if cabinet is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Gabinete nao encontrado")
    _ensure_cabinet_scope(current_user, cabinet)
    return cabinet


@router.get("/{cabinet_id}/overview", response_model=CabinetOverviewOut)
def get_cabinet_overview(
    cabinet_id: UUID,
    current_user = Depends(require_permission("cabinet.read")),
    db: Session = Depends(get_db),
):
    try:
        overview = _service(db).get_overview(cabinet_id)
    except Exception as exc:
        _handle_domain_error(exc)
    _ensure_cabinet_scope(current_user, overview.cabinet)
    return overview
