from datetime import date, datetime
from decimal import Decimal
from typing import Any
from uuid import uuid4

from sqlalchemy import Date, DateTime, ForeignKey, Integer, Numeric, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class FundingSource(Base):
    __tablename__ = "funding_sources"
    __table_args__ = {"schema": "administration"}

    id: Mapped[str] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    organization_id: Mapped[Any] = mapped_column(UUID(as_uuid=True), ForeignKey("core.organizations.id"), nullable=True)
    vereador_id: Mapped[Any] = mapped_column(UUID(as_uuid=True), ForeignKey("core.vereadores.id"), nullable=True)
    source_type: Mapped[str] = mapped_column(String(60), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Any] = mapped_column(Text, nullable=True)
    appropriation_number: Mapped[Any] = mapped_column(String(80), nullable=True)
    estimated_amount: Mapped[Any] = mapped_column(Numeric(14, 2), nullable=True)
    secured_amount: Mapped[Any] = mapped_column(Numeric(14, 2), nullable=True)
    deposited_amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=0, nullable=False)
    deposited_on: Mapped[Any] = mapped_column(Date, nullable=True)
    status: Mapped[str] = mapped_column(String(30), default="PLANNED", nullable=False)
    starts_on: Mapped[Any] = mapped_column(Date, nullable=True)
    ends_on: Mapped[Any] = mapped_column(Date, nullable=True)
    responsible_user_id: Mapped[Any] = mapped_column(UUID(as_uuid=True), ForeignKey("iam.users.id"), nullable=True)
    notes: Mapped[Any] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)


class Contract(Base):
    __tablename__ = "contracts"
    __table_args__ = {"schema": "administration"}

    id: Mapped[str] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    organization_id: Mapped[Any] = mapped_column(UUID(as_uuid=True), ForeignKey("core.organizations.id"), nullable=True)
    partner_id: Mapped[Any] = mapped_column(UUID(as_uuid=True), ForeignKey("relationship.partners.id"), nullable=True)
    funding_source_id: Mapped[Any] = mapped_column(UUID(as_uuid=True), ForeignKey("administration.funding_sources.id"), nullable=True)
    contract_type: Mapped[str] = mapped_column(String(60), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    party_name: Mapped[Any] = mapped_column(String(255), nullable=True)
    document_number: Mapped[Any] = mapped_column(String(60), nullable=True)
    amount: Mapped[Any] = mapped_column(Numeric(14, 2), nullable=True)
    status: Mapped[str] = mapped_column(String(30), default="DRAFT", nullable=False)
    starts_on: Mapped[Any] = mapped_column(Date, nullable=True)
    ends_on: Mapped[Any] = mapped_column(Date, nullable=True)
    document_ref: Mapped[Any] = mapped_column(Text, nullable=True)
    responsible_user_id: Mapped[Any] = mapped_column(UUID(as_uuid=True), ForeignKey("iam.users.id"), nullable=True)
    notes: Mapped[Any] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)


class BudgetItem(Base):
    __tablename__ = "budget_items"
    __table_args__ = {"schema": "administration"}

    id: Mapped[str] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    organization_id: Mapped[Any] = mapped_column(UUID(as_uuid=True), ForeignKey("core.organizations.id"), nullable=True)
    funding_source_id: Mapped[Any] = mapped_column(UUID(as_uuid=True), ForeignKey("administration.funding_sources.id"), nullable=True)
    contract_id: Mapped[Any] = mapped_column(UUID(as_uuid=True), ForeignKey("administration.contracts.id"), nullable=True)
    polo_id: Mapped[Any] = mapped_column(UUID(as_uuid=True), ForeignKey("polo.units.id"), nullable=True)
    field_event_id: Mapped[Any] = mapped_column(UUID(as_uuid=True), ForeignKey("relationship.field_events.id"), nullable=True)
    category: Mapped[str] = mapped_column(String(80), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    planned_amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=0, nullable=False)
    committed_amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=0, nullable=False)
    paid_amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=0, nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="PLANNED", nullable=False)
    due_on: Mapped[Any] = mapped_column(Date, nullable=True)
    responsible_user_id: Mapped[Any] = mapped_column(UUID(as_uuid=True), ForeignKey("iam.users.id"), nullable=True)
    notes: Mapped[Any] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)


class FinancialMovement(Base):
    __tablename__ = "financial_movements"
    __table_args__ = {"schema": "administration"}

    id: Mapped[str] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    funding_source_id: Mapped[str] = mapped_column(UUID(as_uuid=True), ForeignKey("administration.funding_sources.id"), nullable=False)
    organization_id: Mapped[Any] = mapped_column(UUID(as_uuid=True), ForeignKey("core.organizations.id"), nullable=True)
    vereador_id: Mapped[Any] = mapped_column(UUID(as_uuid=True), ForeignKey("core.vereadores.id"), nullable=True)
    polo_id: Mapped[Any] = mapped_column(UUID(as_uuid=True), ForeignKey("polo.units.id"), nullable=True)
    budget_item_id: Mapped[Any] = mapped_column(UUID(as_uuid=True), ForeignKey("administration.budget_items.id"), nullable=True)
    contract_id: Mapped[Any] = mapped_column(UUID(as_uuid=True), ForeignKey("administration.contracts.id"), nullable=True)
    movement_type: Mapped[str] = mapped_column(String(60), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    movement_date: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="CONFIRMED", nullable=False)
    document_ref: Mapped[Any] = mapped_column(Text, nullable=True)
    notes: Mapped[Any] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)


class PurchaseRequest(Base):
    __tablename__ = "purchase_requests"
    __table_args__ = {"schema": "administration"}

    id: Mapped[str] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    organization_id: Mapped[Any] = mapped_column(UUID(as_uuid=True), ForeignKey("core.organizations.id"), nullable=True)
    vereador_id: Mapped[Any] = mapped_column(UUID(as_uuid=True), ForeignKey("core.vereadores.id"), nullable=True)
    polo_id: Mapped[Any] = mapped_column(UUID(as_uuid=True), ForeignKey("polo.units.id"), nullable=True)
    funding_source_id: Mapped[Any] = mapped_column(UUID(as_uuid=True), ForeignKey("administration.funding_sources.id"), nullable=True)
    requested_by_user_id: Mapped[str] = mapped_column(UUID(as_uuid=True), ForeignKey("iam.users.id"), nullable=False)
    requester_name: Mapped[Any] = mapped_column(String(180), nullable=True)
    category: Mapped[str] = mapped_column(String(80), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    estimated_amount: Mapped[Any] = mapped_column(Numeric(14, 2), nullable=True)
    approved_amount: Mapped[Any] = mapped_column(Numeric(14, 2), nullable=True)
    status: Mapped[str] = mapped_column(String(30), default="REQUESTED", nullable=False)
    needed_on: Mapped[Any] = mapped_column(Date, nullable=True)
    approved_at: Mapped[Any] = mapped_column(DateTime, nullable=True)
    purchased_at: Mapped[Any] = mapped_column(DateTime, nullable=True)
    paid_at: Mapped[Any] = mapped_column(DateTime, nullable=True)
    supplier_name: Mapped[Any] = mapped_column(String(255), nullable=True)
    document_ref: Mapped[Any] = mapped_column(Text, nullable=True)
    notes: Mapped[Any] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    items: Mapped[list["PurchaseRequestItem"]] = relationship(
        cascade="all, delete-orphan",
        lazy="selectin",
    )


class PurchaseRequestItem(Base):
    __tablename__ = "purchase_request_items"
    __table_args__ = {"schema": "administration"}

    id: Mapped[str] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    purchase_request_id: Mapped[str] = mapped_column(UUID(as_uuid=True), ForeignKey("administration.purchase_requests.id"), nullable=False)
    line_number: Mapped[int] = mapped_column(Integer, nullable=False)
    product: Mapped[str] = mapped_column(String(255), nullable=False)
    size: Mapped[Any] = mapped_column(String(120), nullable=True)
    desired_brand: Mapped[Any] = mapped_column(String(180), nullable=True)
    quantity: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    unit: Mapped[Any] = mapped_column(String(80), nullable=True)
    estimated_unit_price: Mapped[Any] = mapped_column(Numeric(14, 2), nullable=True)
    estimated_total: Mapped[Any] = mapped_column(Numeric(14, 2), nullable=True)
    approved_unit_price: Mapped[Any] = mapped_column(Numeric(14, 2), nullable=True)
    approved_total: Mapped[Any] = mapped_column(Numeric(14, 2), nullable=True)
    supplier_name: Mapped[Any] = mapped_column(String(255), nullable=True)
    quote_ref: Mapped[Any] = mapped_column(Text, nullable=True)
    notes: Mapped[Any] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)


class StaffContract(Base):
    __tablename__ = "staff_contracts"
    __table_args__ = {"schema": "administration"}

    id: Mapped[str] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    organization_id: Mapped[Any] = mapped_column(UUID(as_uuid=True), ForeignKey("core.organizations.id"), nullable=True)
    vereador_id: Mapped[Any] = mapped_column(UUID(as_uuid=True), ForeignKey("core.vereadores.id"), nullable=True)
    polo_id: Mapped[Any] = mapped_column(UUID(as_uuid=True), ForeignKey("polo.units.id"), nullable=True)
    funding_source_id: Mapped[Any] = mapped_column(UUID(as_uuid=True), ForeignKey("administration.funding_sources.id"), nullable=True)
    person_id: Mapped[str] = mapped_column(UUID(as_uuid=True), ForeignKey("core.persons.id"), nullable=False)
    role_title: Mapped[str] = mapped_column(String(120), nullable=False)
    contract_type: Mapped[str] = mapped_column(String(60), nullable=False)
    salary_amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="ACTIVE", nullable=False)
    starts_on: Mapped[date] = mapped_column(Date, nullable=False)
    ends_on: Mapped[Any] = mapped_column(Date, nullable=True)
    terminated_on: Mapped[Any] = mapped_column(Date, nullable=True)
    notes: Mapped[Any] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)


class PermanentAsset(Base):
    __tablename__ = "permanent_assets"
    __table_args__ = {"schema": "administration"}

    id: Mapped[str] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    asset_number: Mapped[str] = mapped_column(String(40), unique=True, nullable=False)
    organization_id: Mapped[Any] = mapped_column(UUID(as_uuid=True), ForeignKey("core.organizations.id"), nullable=True)
    vereador_id: Mapped[Any] = mapped_column(UUID(as_uuid=True), ForeignKey("core.vereadores.id"), nullable=True)
    polo_id: Mapped[Any] = mapped_column(UUID(as_uuid=True), ForeignKey("polo.units.id"), nullable=True)
    funding_source_id: Mapped[Any] = mapped_column(UUID(as_uuid=True), ForeignKey("administration.funding_sources.id"), nullable=True)
    purchase_request_id: Mapped[Any] = mapped_column(UUID(as_uuid=True), ForeignKey("administration.purchase_requests.id"), nullable=True)
    purchase_request_item_id: Mapped[Any] = mapped_column(UUID(as_uuid=True), ForeignKey("administration.purchase_request_items.id"), nullable=True)
    asset_type: Mapped[str] = mapped_column(String(80), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    brand: Mapped[Any] = mapped_column(String(180), nullable=True)
    model: Mapped[Any] = mapped_column(String(180), nullable=True)
    serial_number: Mapped[Any] = mapped_column(String(120), nullable=True)
    acquisition_date: Mapped[Any] = mapped_column(Date, nullable=True)
    acquisition_value: Mapped[Any] = mapped_column(Numeric(14, 2), nullable=True)
    status: Mapped[str] = mapped_column(String(30), default="ACTIVE", nullable=False)
    location_label: Mapped[Any] = mapped_column(String(255), nullable=True)
    label_printed_at: Mapped[Any] = mapped_column(DateTime, nullable=True)
    notes: Mapped[Any] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)

    @property
    def label_text(self) -> str:
        return f"{self.asset_number} | {self.description}"
