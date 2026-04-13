from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps.permissions import require_permission
from app.core.database import get_db
from app.domain.territory.repository import TerritoryRepository
from app.domain.territory.schemas import (
    ContactCaptureClassifyRequest,
    ContactCaptureConvertDemandOut,
    ContactCaptureConvertDemandRequest,
    ContactCaptureCreate,
    ContactCaptureOut,
)
from app.domain.territory.service import TerritoryService

router = APIRouter()


def _service(db: Session) -> TerritoryService:
    return TerritoryService(TerritoryRepository(db))


def _get_capture_or_404(service: TerritoryService, capture_id: UUID):
    capture = service.get_capture(capture_id)
    if capture is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Captacao nao encontrada")
    return capture


@router.get("", response_model=list[ContactCaptureOut])
def list_captures(
    capture_status: str | None = None,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    current_user = Depends(require_permission("capture.read")),
    db: Session = Depends(get_db),
):
    return _service(db).list_captures(limit=limit, offset=offset, status=capture_status, current_user=current_user)


@router.post("", response_model=ContactCaptureOut, status_code=201)
def create_capture(
    payload: ContactCaptureCreate,
    current_user = Depends(require_permission("capture.create")),
    db: Session = Depends(get_db),
):
    result = _service(db).create_capture(
        captured_by_user_id=current_user.id,
        payload=payload,
        db=db,
        current_user=current_user,
    )
    db.commit()
    return result


@router.get("/{capture_id}", response_model=ContactCaptureOut)
def get_capture(
    capture_id: UUID,
    current_user = Depends(require_permission("capture.read")),
    db: Session = Depends(get_db),
):
    return _get_capture_or_404(_service(db), capture_id)


@router.post("/{capture_id}/classify", response_model=ContactCaptureOut)
def classify_capture(
    capture_id: UUID,
    payload: ContactCaptureClassifyRequest,
    current_user = Depends(require_permission("capture.classify")),
    db: Session = Depends(get_db),
):
    service = _service(db)
    capture = _get_capture_or_404(service, capture_id)
    result = service.classify_capture(capture, payload, db=db, current_user=current_user)
    db.commit()
    return result


@router.post("/{capture_id}/convert-demand", response_model=ContactCaptureConvertDemandOut, status_code=201)
def convert_capture_to_demand(
    capture_id: UUID,
    payload: ContactCaptureConvertDemandRequest,
    current_user = Depends(require_permission("capture.convert")),
    db: Session = Depends(get_db),
):
    service = _service(db)
    capture = _get_capture_or_404(service, capture_id)
    try:
        result = service.convert_capture_to_demand(
            capture,
            payload,
            opened_by_user_id=current_user.id,
            db=db,
            current_user=current_user,
        )
    except LookupError as exc:
        if str(exc) == "person_not_found":
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pessoa nao encontrada")
        raise
    db.commit()
    return result
