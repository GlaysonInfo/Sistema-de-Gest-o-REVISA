from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps.permissions import require_permission
from app.core.database import get_db
from app.domain.relationship.repository import RelationshipRepository
from app.domain.relationship.schemas import (
    ClassificationCreate,
    ClassificationOut,
    FieldEventCreate,
    FieldEventOut,
    LeadershipCreate,
    LeadershipOut,
    PartnerCreate,
    PartnerOut,
)
from app.domain.relationship.service import RelationshipService

router = APIRouter()


def _service(db: Session) -> RelationshipService:
    return RelationshipService(RelationshipRepository(db))


def _handle_domain_error(exc: Exception):
    detail_by_code = {
        "person_not_found": "Pessoa nao encontrada",
        "polo_not_found": "Polo nao encontrado",
        "partner_not_found": "Parceiro nao encontrado",
    }
    if isinstance(exc, LookupError):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail_by_code.get(str(exc), "Registro nao encontrado"))
    raise exc


@router.get("/classifications", response_model=list[ClassificationOut])
def list_classifications(
    person_id: UUID | None = None,
    level: str | None = None,
    current_user = Depends(require_permission("relationship.read")),
    db: Session = Depends(get_db),
):
    return _service(db).list_classifications(person_id=person_id, level=level)


@router.post("/classifications", response_model=ClassificationOut, status_code=201)
def create_classification(
    payload: ClassificationCreate,
    current_user = Depends(require_permission("relationship.classify")),
    db: Session = Depends(get_db),
):
    try:
        result = _service(db).create_classification(
            payload,
            classified_by_user_id=current_user.id,
            db=db,
            current_user=current_user,
        )
    except Exception as exc:
        _handle_domain_error(exc)
    db.commit()
    return result


@router.get("/leaderships", response_model=list[LeadershipOut])
def list_leaderships(
    district: str | None = None,
    active: bool | None = None,
    current_user = Depends(require_permission("relationship.read")),
    db: Session = Depends(get_db),
):
    return _service(db).list_leaderships(district=district, active=active)


@router.post("/leaderships", response_model=LeadershipOut, status_code=201)
def create_leadership(
    payload: LeadershipCreate,
    current_user = Depends(require_permission("relationship.manage_leadership")),
    db: Session = Depends(get_db),
):
    try:
        result = _service(db).create_leadership(payload, db=db, current_user=current_user)
    except Exception as exc:
        _handle_domain_error(exc)
    db.commit()
    return result


@router.get("/partners", response_model=list[PartnerOut])
def list_partners(
    partner_type: str | None = None,
    status_filter: str | None = None,
    current_user = Depends(require_permission("relationship.read")),
    db: Session = Depends(get_db),
):
    return _service(db).list_partners(partner_type=partner_type, status=status_filter)


@router.post("/partners", response_model=PartnerOut, status_code=201)
def create_partner(
    payload: PartnerCreate,
    current_user = Depends(require_permission("relationship.manage_partner")),
    db: Session = Depends(get_db),
):
    result = _service(db).create_partner(payload, db=db, current_user=current_user)
    db.commit()
    return result


@router.get("/field-events", response_model=list[FieldEventOut])
def list_field_events(
    district: str | None = None,
    status_filter: str | None = None,
    current_user = Depends(require_permission("relationship.read")),
    db: Session = Depends(get_db),
):
    return _service(db).list_field_events(district=district, status=status_filter)


@router.post("/field-events", response_model=FieldEventOut, status_code=201)
def create_field_event(
    payload: FieldEventCreate,
    current_user = Depends(require_permission("relationship.manage_event")),
    db: Session = Depends(get_db),
):
    try:
        result = _service(db).create_field_event(
            payload,
            created_by_user_id=current_user.id,
            db=db,
            current_user=current_user,
        )
    except Exception as exc:
        _handle_domain_error(exc)
    db.commit()
    return result
