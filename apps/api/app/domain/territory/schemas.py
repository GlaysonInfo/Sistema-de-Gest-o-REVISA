from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from app.domain.core.schemas import AddressOut, PersonOut


class ContactCaptureCreate(BaseModel):
    origin: str
    classification: str
    full_name: str
    phone: str | None = None
    district: str | None = None
    notes: str | None = None
    priority_level: str | None = None
    vereador_id: UUID | None = None
    team_id: UUID | None = None
    latitude: float | None = None
    longitude: float | None = None


class ContactCaptureOut(BaseModel):
    id: UUID
    captured_by_user_id: UUID
    person_id: UUID | None = None
    vereador_id: UUID | None = None
    team_id: UUID | None = None
    origin: str
    classification: str
    full_name: str
    phone: str | None = None
    district: str | None = None
    notes: str | None = None
    priority_level: str | None = None
    capture_status: str
    latitude: float | None = None
    longitude: float | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class ContactCaptureClassifyRequest(BaseModel):
    classification: str
    notes: str | None = None
    priority_level: str | None = None


class DemandCreate(BaseModel):
    person_id: UUID | None = None
    capture_id: UUID | None = None
    organization_id: UUID | None = None
    vereador_id: UUID | None = None
    assigned_to_user_id: UUID | None = None
    category: str
    title: str
    description: str | None = None
    priority: str = "MEDIUM"
    due_at: datetime | None = None


class DemandOut(BaseModel):
    id: UUID
    person_id: UUID | None = None
    capture_id: UUID | None = None
    organization_id: UUID | None = None
    vereador_id: UUID | None = None
    opened_by_user_id: UUID
    assigned_to_user_id: UUID | None = None
    category: str
    title: str
    description: str | None = None
    priority: str
    status: str
    due_at: datetime | None = None
    resolved_at: datetime | None = None
    resolution_notes: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class DemandUpdate(BaseModel):
    category: str | None = None
    title: str | None = None
    description: str | None = None
    priority: str | None = None
    status: str | None = None
    due_at: datetime | None = None
    assigned_to_user_id: UUID | None = None
    resolved_at: datetime | None = None
    resolution_notes: str | None = None


class DemandAssignRequest(BaseModel):
    assigned_to_user_id: UUID
    status: str = "ASSIGNED"


class DemandTaskCreate(BaseModel):
    assigned_to_user_id: UUID | None = None
    task_type: str = "DEMAND_FOLLOW_UP"
    title: str | None = None
    description: str | None = None
    priority: str | None = None
    due_at: datetime | None = None


class ContactCaptureConvertDemandRequest(BaseModel):
    person_id: UUID | None = None
    assigned_to_user_id: UUID | None = None
    category: str = "ATENDIMENTO"
    title: str | None = None
    description: str | None = None
    priority: str = "MEDIUM"
    due_at: datetime | None = None
    create_address: bool = True


class ContactCaptureConvertDemandOut(BaseModel):
    capture: ContactCaptureOut
    person: PersonOut
    demand: DemandOut
    address: AddressOut | None = None
    created_person: bool
