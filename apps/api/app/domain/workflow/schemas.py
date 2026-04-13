from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class TaskCreate(BaseModel):
    organization_id: UUID | None = None
    vereador_id: UUID | None = None
    polo_id: UUID | None = None
    person_id: UUID | None = None
    demand_id: UUID | None = None
    assigned_to_user_id: UUID | None = None
    task_type: str
    title: str
    description: str | None = None
    priority: str = "MEDIUM"
    due_at: datetime | None = None


class TaskUpdate(BaseModel):
    organization_id: UUID | None = None
    vereador_id: UUID | None = None
    polo_id: UUID | None = None
    person_id: UUID | None = None
    demand_id: UUID | None = None
    assigned_to_user_id: UUID | None = None
    task_type: str | None = None
    title: str | None = None
    description: str | None = None
    priority: str | None = None
    status: str | None = None
    due_at: datetime | None = None
    completed_at: datetime | None = None


class TaskCompleteRequest(BaseModel):
    completed_at: datetime | None = None
    resolution_notes: str | None = None
    resolve_demand: bool = True


class TaskOut(BaseModel):
    id: UUID
    organization_id: UUID | None = None
    vereador_id: UUID | None = None
    polo_id: UUID | None = None
    person_id: UUID | None = None
    demand_id: UUID | None = None
    assigned_to_user_id: UUID | None = None
    task_type: str
    title: str
    description: str | None = None
    priority: str
    status: str
    due_at: datetime | None = None
    completed_at: datetime | None = None

    model_config = {"from_attributes": True}
