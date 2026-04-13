from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, Field


class PoloCreate(BaseModel):
    organization_id: UUID
    vereador_id: UUID
    code: str | None = None
    address_label: str | None = None


class PoloUpdate(BaseModel):
    vereador_id: UUID | None = None
    code: str | None = None
    address_label: str | None = None
    active: bool | None = None


class PoloOut(BaseModel):
    id: UUID
    organization_id: UUID
    vereador_id: UUID
    code: str | None = None
    address_label: str | None = None
    active: bool

    model_config = {"from_attributes": True}


class PoloBeneficiarioCreate(BaseModel):
    person_id: UUID
    source_capture_id: UUID | None = None
    status: str = "PRE_CADASTRADO"
    admitted_at: datetime | None = None


class PoloBeneficiarioOut(BaseModel):
    id: UUID
    polo_id: UUID
    person_id: UUID
    source_capture_id: UUID | None = None
    status: str
    admitted_at: datetime | None = None
    discharged_at: datetime | None = None

    model_config = {"from_attributes": True}


class PoloBeneficiarioUpdate(BaseModel):
    status: str | None = None
    source_capture_id: UUID | None = None
    admitted_at: datetime | None = None
    discharged_at: datetime | None = None


class ModalidadeCreate(BaseModel):
    name: str
    description: str | None = Field(default=None, max_length=2000)
    active: bool = True


class ModalidadeUpdate(BaseModel):
    name: str | None = None
    description: str | None = Field(default=None, max_length=2000)
    active: bool | None = None


class ModalidadeOut(BaseModel):
    id: UUID
    polo_id: UUID
    name: str
    description: str | None = None
    active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class AttendanceCreate(BaseModel):
    beneficiario_id: UUID
    modalidade_id: UUID | None = None
    activity_date: date
    present: bool
    notes: str | None = Field(default=None, max_length=2000)


class AttendanceOut(BaseModel):
    id: UUID
    beneficiario_id: UUID
    modalidade_id: UUID | None = None
    activity_date: date
    present: bool
    notes: str | None = None

    model_config = {"from_attributes": True}


class AttendanceUpdate(BaseModel):
    modalidade_id: UUID | None = None
    activity_date: date | None = None
    present: bool | None = None
    notes: str | None = Field(default=None, max_length=2000)


class OccurrenceCreate(BaseModel):
    beneficiario_id: UUID | None = None
    severity: str
    title: str
    description: str
    status: str = "OPEN"


class OccurrenceUpdate(BaseModel):
    beneficiario_id: UUID | None = None
    severity: str | None = None
    title: str | None = None
    description: str | None = None
    status: str | None = None


class OccurrenceOut(BaseModel):
    id: UUID
    polo_id: UUID
    beneficiario_id: UUID | None = None
    severity: str
    title: str
    description: str
    status: str

    model_config = {"from_attributes": True}


class MonthlyReportModalityCreate(BaseModel):
    modalidade_id: UUID | None = None
    modalidade_name: str
    active: bool = True
    beneficiaries_count: int = Field(default=0, ge=0)
    notes: str | None = Field(default=None, max_length=2000)


class MonthlyReportModalityOut(MonthlyReportModalityCreate):
    id: UUID
    monthly_report_id: UUID

    model_config = {"from_attributes": True}


class MonthlyReportAttachmentOut(BaseModel):
    id: UUID
    monthly_report_id: UUID
    modalidade_id: UUID | None = None
    attachment_type: str
    original_filename: str
    stored_path: str
    content_type: str | None = None
    file_size: int
    description: str | None = None
    uploaded_at: datetime

    model_config = {"from_attributes": True}


class MonthlyReportBase(BaseModel):
    reference_month: date
    occurrence_summary: str | None = Field(default=None, max_length=10000)
    notes: str | None = Field(default=None, max_length=4000)
    modalities: list[MonthlyReportModalityCreate]


class MonthlyReportPreviewOut(BaseModel):
    narrative_text: str
    active_modalities_count: int
    total_beneficiaries: int


class MonthlyReportCreate(MonthlyReportBase):
    narrative_text: str | None = None
    status: str = "SUBMITTED"


class MonthlyReportOut(BaseModel):
    id: UUID
    polo_id: UUID
    vereador_id: UUID
    created_by_user_id: UUID
    reference_month: date
    submitted_at: datetime | None = None
    status: str
    active_modalities_count: int
    total_beneficiaries: int
    occurrence_summary: str | None = None
    narrative_text: str
    notes: str | None = None
    modalities: list[MonthlyReportModalityOut]
    attachments: list[MonthlyReportAttachmentOut]

    model_config = {"from_attributes": True}


class ModalityActionPlanOut(BaseModel):
    id: UUID
    polo_id: UUID
    modalidade_id: UUID
    uploaded_by_user_id: UUID
    base_year: int
    title: str
    professional_name: str | None = None
    original_filename: str
    stored_path: str
    content_type: str | None = None
    file_size: int
    status: str
    notes: str | None = None
    uploaded_at: datetime

    model_config = {"from_attributes": True}


class PoloOverviewMetrics(BaseModel):
    total_beneficiarios: int
    active_beneficiarios: int
    pre_registered_beneficiarios: int
    attendance_records: int
    present_records: int
    absent_records: int
    open_occurrences: int
    closed_occurrences: int
    planned_events: int


class PoloFieldEventOut(BaseModel):
    id: UUID
    title: str
    district: str | None = None
    event_type: str
    event_date: date
    status: str
    expected_people: int | None = None
    actual_people: int | None = None
    captures_count: int | None = None
    leaders_identified: int | None = None

    model_config = {"from_attributes": True}


class PoloOverviewOut(BaseModel):
    polo: PoloOut
    metrics: PoloOverviewMetrics
    beneficiaries: list[PoloBeneficiarioOut]
    recent_attendances: list[AttendanceOut]
    recent_occurrences: list[OccurrenceOut]
    field_events: list[PoloFieldEventOut]
