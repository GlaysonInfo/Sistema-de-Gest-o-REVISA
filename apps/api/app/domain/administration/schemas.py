from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field


class FundingSourceCreate(BaseModel):
    organization_id: UUID | None = None
    vereador_id: UUID | None = None
    source_type: str
    name: str
    description: str | None = None
    appropriation_number: str | None = None
    estimated_amount: Decimal | None = None
    secured_amount: Decimal | None = None
    deposited_amount: Decimal = Decimal("0")
    deposited_on: date | None = None
    status: str = "PLANNED"
    starts_on: date | None = None
    ends_on: date | None = None
    responsible_user_id: UUID | None = None
    notes: str | None = Field(default=None, max_length=2000)


class FundingSourceOut(FundingSourceCreate):
    id: UUID

    model_config = {"from_attributes": True}


class ContractCreate(BaseModel):
    organization_id: UUID | None = None
    partner_id: UUID | None = None
    funding_source_id: UUID | None = None
    contract_type: str
    title: str
    party_name: str | None = None
    document_number: str | None = None
    amount: Decimal | None = None
    status: str = "DRAFT"
    starts_on: date | None = None
    ends_on: date | None = None
    document_ref: str | None = None
    responsible_user_id: UUID | None = None
    notes: str | None = Field(default=None, max_length=2000)


class ContractOut(ContractCreate):
    id: UUID

    model_config = {"from_attributes": True}


class BudgetItemCreate(BaseModel):
    organization_id: UUID | None = None
    funding_source_id: UUID | None = None
    contract_id: UUID | None = None
    polo_id: UUID | None = None
    field_event_id: UUID | None = None
    category: str
    description: str
    planned_amount: Decimal = Decimal("0")
    committed_amount: Decimal = Decimal("0")
    paid_amount: Decimal = Decimal("0")
    status: str = "PLANNED"
    due_on: date | None = None
    responsible_user_id: UUID | None = None
    notes: str | None = Field(default=None, max_length=2000)


class BudgetItemOut(BudgetItemCreate):
    id: UUID

    model_config = {"from_attributes": True}


class FinancialMovementCreate(BaseModel):
    funding_source_id: UUID
    organization_id: UUID | None = None
    vereador_id: UUID | None = None
    polo_id: UUID | None = None
    budget_item_id: UUID | None = None
    contract_id: UUID | None = None
    movement_type: str
    description: str
    amount: Decimal
    movement_date: date
    status: str = "CONFIRMED"
    document_ref: str | None = None
    notes: str | None = Field(default=None, max_length=2000)


class FinancialMovementOut(FinancialMovementCreate):
    id: UUID
    vereador_id: UUID | None = None

    model_config = {"from_attributes": True}


class PurchaseRequestItemCreate(BaseModel):
    line_number: int | None = None
    product: str
    size: str | None = None
    desired_brand: str | None = None
    quantity: Decimal
    unit: str | None = None
    estimated_unit_price: Decimal | None = None
    estimated_total: Decimal | None = None
    approved_unit_price: Decimal | None = None
    approved_total: Decimal | None = None
    supplier_name: str | None = None
    quote_ref: str | None = None
    notes: str | None = Field(default=None, max_length=2000)


class PurchaseRequestItemOut(PurchaseRequestItemCreate):
    id: UUID
    purchase_request_id: UUID
    line_number: int

    model_config = {"from_attributes": True}


class PurchaseRequestCreate(BaseModel):
    organization_id: UUID | None = None
    vereador_id: UUID | None = None
    polo_id: UUID | None = None
    funding_source_id: UUID | None = None
    requester_name: str | None = None
    category: str
    description: str
    estimated_amount: Decimal | None = None
    approved_amount: Decimal | None = None
    status: str = "REQUESTED"
    needed_on: date | None = None
    supplier_name: str | None = None
    document_ref: str | None = None
    notes: str | None = Field(default=None, max_length=2000)
    items: list[PurchaseRequestItemCreate] = Field(default_factory=list)


class PurchaseRequestOut(PurchaseRequestCreate):
    id: UUID
    vereador_id: UUID | None = None
    requested_by_user_id: UUID
    items: list[PurchaseRequestItemOut] = Field(default_factory=list)

    model_config = {"from_attributes": True}


class PurchaseAlertOut(BaseModel):
    open_purchase_requests: int
    purchase_requests: list[PurchaseRequestOut]


class StaffContractCreate(BaseModel):
    organization_id: UUID | None = None
    vereador_id: UUID | None = None
    polo_id: UUID | None = None
    funding_source_id: UUID | None = None
    person_id: UUID
    role_title: str
    contract_type: str
    salary_amount: Decimal
    status: str = "ACTIVE"
    starts_on: date
    ends_on: date | None = None
    terminated_on: date | None = None
    notes: str | None = Field(default=None, max_length=2000)


class StaffContractOut(StaffContractCreate):
    id: UUID
    vereador_id: UUID | None = None

    model_config = {"from_attributes": True}


class PermanentAssetCreate(BaseModel):
    organization_id: UUID | None = None
    vereador_id: UUID | None = None
    polo_id: UUID | None = None
    funding_source_id: UUID | None = None
    purchase_request_id: UUID | None = None
    purchase_request_item_id: UUID | None = None
    asset_type: str = "BEM_PERMANENTE"
    description: str
    brand: str | None = None
    model: str | None = None
    serial_number: str | None = None
    acquisition_date: date | None = None
    acquisition_value: Decimal | None = None
    status: str = "ACTIVE"
    location_label: str | None = None
    notes: str | None = Field(default=None, max_length=2000)


class PermanentAssetOut(PermanentAssetCreate):
    id: UUID
    asset_number: str
    vereador_id: UUID | None = None
    label_printed_at: datetime | None = None
    label_text: str

    model_config = {"from_attributes": True}


class FiscalDocumentOut(BaseModel):
    source: str
    entity_id: UUID
    label: str
    document_ref: str


class AccountabilityTotals(BaseModel):
    estimated_amount: Decimal = Decimal("0")
    secured_amount: Decimal = Decimal("0")
    deposited_amount: Decimal = Decimal("0")
    movement_inflows: Decimal = Decimal("0")
    movement_outflows: Decimal = Decimal("0")
    purchase_estimated_amount: Decimal = Decimal("0")
    purchase_approved_amount: Decimal = Decimal("0")
    staff_monthly_payroll: Decimal = Decimal("0")
    available_balance: Decimal = Decimal("0")


class AccountabilityReportOut(BaseModel):
    vereador_id: UUID | None = None
    funding_source_id: UUID | None = None
    polo_id: UUID | None = None
    totals: AccountabilityTotals
    funding_sources: list[FundingSourceOut]
    financial_movements: list[FinancialMovementOut]
    budget_items: list[BudgetItemOut]
    purchase_requests: list[PurchaseRequestOut]
    staff_contracts: list[StaffContractOut]
    contracts: list[ContractOut]
    fiscal_documents: list[FiscalDocumentOut]
