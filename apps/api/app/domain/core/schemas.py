from datetime import date, datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel


class PersonCreate(BaseModel):
    full_name: str
    social_name: str | None = None
    cpf: str | None = None
    birth_date: date | None = None
    phone: str | None = None
    secondary_phone: str | None = None
    email: str | None = None
    gender: str | None = None
    notes: str | None = None


class PersonOut(BaseModel):
    id: UUID
    full_name: str
    social_name: str | None = None
    cpf: str | None = None
    birth_date: date | None = None
    phone: str | None = None
    secondary_phone: str | None = None
    email: str | None = None
    gender: str | None = None
    notes: str | None = None

    model_config = {"from_attributes": True}


class PersonTimelineItem(BaseModel):
    type: str
    id: UUID
    occurred_at: datetime
    title: str
    status: str | None = None
    description: str | None = None
    metadata_json: dict[str, Any] | None = None


class PersonCurrentPoloOut(BaseModel):
    id: UUID
    code: str | None = None
    address_label: str | None = None
    beneficiary_id: UUID
    beneficiary_status: str
    admitted_at: datetime | None = None


class PersonOperationalSummaryOut(BaseModel):
    person: PersonOut
    current_polo: PersonCurrentPoloOut | None = None
    beneficiary_status: str | None = None
    open_demands: int
    open_tasks: int
    last_attendance_at: date | None = None
    last_occurrence: PersonTimelineItem | None = None
    journey_status: str


class PersonTimelineOut(BaseModel):
    person: PersonOut
    summary: PersonOperationalSummaryOut
    items: list[PersonTimelineItem]


class PersonUpdate(BaseModel):
    full_name: str | None = None
    social_name: str | None = None
    cpf: str | None = None
    birth_date: date | None = None
    phone: str | None = None
    secondary_phone: str | None = None
    email: str | None = None
    gender: str | None = None
    notes: str | None = None


class AddressCreate(BaseModel):
    label: str | None = None
    street: str | None = None
    number: str | None = None
    complement: str | None = None
    district: str | None = None
    city: str | None = None
    state: str | None = None
    zip_code: str | None = None
    latitude: float | None = None
    longitude: float | None = None


class AddressOut(BaseModel):
    id: UUID
    person_id: UUID | None = None
    organization_id: UUID | None = None
    label: str | None = None
    street: str | None = None
    number: str | None = None
    complement: str | None = None
    district: str | None = None
    city: str | None = None
    state: str | None = None
    zip_code: str | None = None
    latitude: float | None = None
    longitude: float | None = None

    model_config = {"from_attributes": True}


class ConsentCreate(BaseModel):
    consent_type: str
    granted: bool
    version: str
    granted_at: datetime | None = None
    revoked_at: datetime | None = None
    evidence_ref: str | None = None


class ConsentOut(BaseModel):
    id: UUID
    person_id: UUID
    consent_type: str
    granted: bool
    version: str
    granted_at: datetime | None = None
    revoked_at: datetime | None = None
    captured_by_user_id: UUID | None = None
    evidence_ref: str | None = None

    model_config = {"from_attributes": True}


class PersonLinkCreate(BaseModel):
    organization_id: UUID | None = None
    vereador_id: UUID | None = None
    link_type: str
    status: str = "ACTIVE"
    start_date: date | None = None
    end_date: date | None = None
    metadata_json: dict[str, Any] | None = None


class PersonLinkOut(BaseModel):
    id: UUID
    person_id: UUID
    organization_id: UUID | None = None
    vereador_id: UUID | None = None
    link_type: str
    status: str
    start_date: date | None = None
    end_date: date | None = None
    metadata_json: dict[str, Any] | None = None

    model_config = {"from_attributes": True}
