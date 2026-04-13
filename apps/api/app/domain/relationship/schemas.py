from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, Field


class ClassificationCreate(BaseModel):
    person_id: UUID
    organization_id: UUID | None = None
    vereador_id: UUID | None = None
    level: str
    influence: str | None = None
    engagement: str | None = None
    vote_2028: str | None = None
    priority: str | None = None
    status: str = "ACTIVE"
    responsible_user_id: UUID | None = None
    notes: str | None = Field(default=None, max_length=2000)


class ClassificationOut(ClassificationCreate):
    id: UUID
    classified_by_user_id: UUID

    model_config = {"from_attributes": True}


class LeadershipCreate(BaseModel):
    person_id: UUID
    organization_id: UUID | None = None
    vereador_id: UUID | None = None
    polo_id: UUID | None = None
    district: str | None = None
    leadership_type: str
    area_atuacao: str | None = None
    influence_count: int | None = None
    loyalty_level: str | None = None
    active: bool = True
    identified_at: datetime | None = None
    responsible_user_id: UUID | None = None
    notes: str | None = Field(default=None, max_length=2000)


class LeadershipOut(LeadershipCreate):
    id: UUID

    model_config = {"from_attributes": True}


class PartnerCreate(BaseModel):
    organization_id: UUID | None = None
    name: str
    legal_name: str | None = None
    document_number: str | None = None
    partner_type: str
    contact_name: str | None = None
    contact_phone: str | None = None
    contact_email: str | None = None
    district: str | None = None
    contribution_area: str | None = None
    service_offered: str | None = None
    capacity: str | None = None
    partnership_type: str | None = None
    status: str = "PROSPECT"
    responsible_user_id: UUID | None = None
    notes: str | None = Field(default=None, max_length=2000)


class PartnerOut(PartnerCreate):
    id: UUID

    model_config = {"from_attributes": True}


class FieldEventCreate(BaseModel):
    organization_id: UUID | None = None
    polo_id: UUID | None = None
    partner_id: UUID | None = None
    title: str
    district: str | None = None
    event_type: str
    event_date: date
    status: str = "PLANNED"
    expected_people: int | None = None
    actual_people: int | None = None
    captures_count: int | None = None
    leaders_identified: int | None = None
    next_action: str | None = None
    notes: str | None = Field(default=None, max_length=2000)


class FieldEventOut(FieldEventCreate):
    id: UUID
    created_by_user_id: UUID

    model_config = {"from_attributes": True}
