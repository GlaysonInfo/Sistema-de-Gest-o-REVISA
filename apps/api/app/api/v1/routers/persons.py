from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps.permissions import require_permission
from app.core.database import get_db
from app.domain.core.repository import CoreRepository
from app.domain.core.schemas import (
    AddressCreate,
    AddressOut,
    ConsentCreate,
    ConsentOut,
    PersonOperationalSummaryOut,
    PersonCreate,
    PersonLinkCreate,
    PersonLinkOut,
    PersonOut,
    PersonTimelineOut,
    PersonUpdate,
)
from app.domain.core.service import CoreService

router = APIRouter()


def _service(db: Session) -> CoreService:
    return CoreService(CoreRepository(db))


def _get_person_or_404(service: CoreService, person_id: UUID):
    person = service.get_person(person_id)
    if person is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pessoa nao encontrada")
    return person


@router.get("", response_model=list[PersonOut])
def list_persons(
    search: str | None = None,
    cpf: str | None = None,
    phone: str | None = None,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    current_user = Depends(require_permission("person.read")),
    db: Session = Depends(get_db),
):
    return _service(db).list_persons(search=search, cpf=cpf, phone=phone, limit=limit, offset=offset, current_user=current_user)


@router.post("", response_model=PersonOut, status_code=201)
def create_person(
    payload: PersonCreate,
    current_user = Depends(require_permission("person.create")),
    db: Session = Depends(get_db),
):
    result = _service(db).create_person(payload, db=db, current_user=current_user)
    db.commit()
    return result


@router.get("/{person_id}", response_model=PersonOut)
def get_person(
    person_id: UUID,
    current_user = Depends(require_permission("person.read")),
    db: Session = Depends(get_db),
):
    return _get_person_or_404(_service(db), person_id)


@router.patch("/{person_id}", response_model=PersonOut)
def update_person(
    person_id: UUID,
    payload: PersonUpdate,
    current_user = Depends(require_permission("person.update")),
    db: Session = Depends(get_db),
):
    service = _service(db)
    person = _get_person_or_404(service, person_id)
    result = service.update_person(person, payload, db=db, current_user=current_user)
    db.commit()
    return result


@router.get("/{person_id}/operational-summary", response_model=PersonOperationalSummaryOut)
def get_person_operational_summary(
    person_id: UUID,
    current_user = Depends(require_permission("person.read")),
    db: Session = Depends(get_db),
):
    service = _service(db)
    person = _get_person_or_404(service, person_id)
    return service.get_operational_summary(person)


@router.get("/{person_id}/timeline", response_model=PersonTimelineOut)
def get_person_timeline(
    person_id: UUID,
    current_user = Depends(require_permission("person.read")),
    db: Session = Depends(get_db),
):
    service = _service(db)
    person = _get_person_or_404(service, person_id)
    return service.get_person_timeline(person)


@router.get("/{person_id}/addresses", response_model=list[AddressOut])
def list_person_addresses(
    person_id: UUID,
    current_user = Depends(require_permission("person.read")),
    db: Session = Depends(get_db),
):
    service = _service(db)
    _get_person_or_404(service, person_id)
    return service.list_person_addresses(person_id)


@router.post("/{person_id}/addresses", response_model=AddressOut, status_code=201)
def create_person_address(
    person_id: UUID,
    payload: AddressCreate,
    current_user = Depends(require_permission("person.update")),
    db: Session = Depends(get_db),
):
    service = _service(db)
    _get_person_or_404(service, person_id)
    result = service.create_person_address(person_id, payload, db=db, current_user=current_user)
    db.commit()
    return result


@router.get("/{person_id}/consents", response_model=list[ConsentOut])
def list_person_consents(
    person_id: UUID,
    current_user = Depends(require_permission("consent.read")),
    db: Session = Depends(get_db),
):
    service = _service(db)
    _get_person_or_404(service, person_id)
    return service.list_person_consents(person_id)


@router.post("/{person_id}/consents", response_model=ConsentOut, status_code=201)
def create_person_consent(
    person_id: UUID,
    payload: ConsentCreate,
    current_user = Depends(require_permission("consent.create")),
    db: Session = Depends(get_db),
):
    service = _service(db)
    _get_person_or_404(service, person_id)
    result = service.create_person_consent(person_id, payload, db=db, current_user=current_user)
    db.commit()
    return result


@router.get("/{person_id}/links", response_model=list[PersonLinkOut])
def list_person_links(
    person_id: UUID,
    current_user = Depends(require_permission("person.read")),
    db: Session = Depends(get_db),
):
    service = _service(db)
    _get_person_or_404(service, person_id)
    return service.list_person_links(person_id)


@router.post("/{person_id}/links", response_model=PersonLinkOut, status_code=201)
def create_person_link(
    person_id: UUID,
    payload: PersonLinkCreate,
    current_user = Depends(require_permission("person.link")),
    db: Session = Depends(get_db),
):
    service = _service(db)
    _get_person_or_404(service, person_id)
    result = service.create_person_link(person_id, payload, db=db, current_user=current_user)
    db.commit()
    return result
