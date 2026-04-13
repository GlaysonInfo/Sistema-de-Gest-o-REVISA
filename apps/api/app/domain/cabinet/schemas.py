from uuid import UUID

from pydantic import BaseModel, Field

from app.domain.core.schemas import PersonOut
from app.domain.relationship.schemas import FieldEventOut
from app.domain.territory.schemas import ContactCaptureOut, DemandOut
from app.domain.workflow.schemas import TaskOut


class CabinetCreate(BaseModel):
    name: str
    legal_name: str | None = None
    document_number: str | None = None
    vereador_full_name: str
    vereador_phone: str | None = None
    vereador_email: str | None = None


class OrganizationOut(BaseModel):
    id: UUID
    type: str
    name: str
    legal_name: str | None = None
    document_number: str | None = None
    parent_organization_id: UUID | None = None
    active: bool

    model_config = {"from_attributes": True}


class VereadorOut(BaseModel):
    id: UUID
    person_id: UUID
    organization_id: UUID
    active: bool
    person: PersonOut | None = None


class CabinetOut(BaseModel):
    organization: OrganizationOut
    vereador: VereadorOut


class CabinetMetrics(BaseModel):
    linked_people: int
    captures: int
    demands: int
    open_demands: int
    tasks: int
    open_tasks: int
    planned_events: int


class CabinetOverviewOut(BaseModel):
    cabinet: CabinetOut
    metrics: CabinetMetrics
    recent_captures: list[ContactCaptureOut] = Field(default_factory=list)
    recent_demands: list[DemandOut] = Field(default_factory=list)
    recent_tasks: list[TaskOut] = Field(default_factory=list)
    field_events: list[FieldEventOut] = Field(default_factory=list)
