from datetime import date
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field

from app.domain.core.schemas import PersonLinkOut, PersonOut
from app.domain.polo.schemas import PoloBeneficiarioOut
from app.domain.territory.schemas import ContactCaptureOut, DemandOut


class MobileIntakeCreate(BaseModel):
    intake_type: Literal["POLO_BENEFICIARIO", "MANDATO_ACOMPANHAMENTO"]
    full_name: str = Field(min_length=2, max_length=255)
    phone: str | None = Field(default=None, max_length=30)
    cpf: str | None = Field(default=None, max_length=20)
    birth_date: date | None = None
    email: str | None = Field(default=None, max_length=180)
    gender: str | None = Field(default=None, max_length=30)
    district: str | None = Field(default=None, max_length=120)
    notes: str | None = Field(default=None, max_length=2000)
    priority_level: str | None = Field(default="MEDIUM", max_length=20)
    organization_id: UUID | None = None
    vereador_id: UUID | None = None
    team_id: UUID | None = None
    polo_id: UUID | None = None
    create_demand: bool = True


class MobileIntakeOut(BaseModel):
    intake_type: str
    capture: ContactCaptureOut
    person: PersonOut
    demand: DemandOut | None = None
    beneficiary: PoloBeneficiarioOut | None = None
    person_link: PersonLinkOut | None = None
    created_person: bool
    created_beneficiary: bool = False
    created_person_link: bool = False
