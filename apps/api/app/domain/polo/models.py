from datetime import date, datetime
from typing import Any
from uuid import uuid4

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class PoloUnit(Base):
    __tablename__ = "units"
    __table_args__ = {"schema": "polo"}

    id: Mapped[str] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    organization_id: Mapped[str] = mapped_column(UUID(as_uuid=True), ForeignKey("core.organizations.id"), unique=True)
    vereador_id: Mapped[str] = mapped_column(UUID(as_uuid=True), ForeignKey("core.vereadores.id"), nullable=False)
    code: Mapped[Any] = mapped_column(String(50), nullable=True)
    address_label: Mapped[Any] = mapped_column(String(255), nullable=True)
    active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)


class PoloBeneficiario(Base):
    __tablename__ = "beneficiarios"
    __table_args__ = {"schema": "polo"}

    id: Mapped[str] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    polo_id: Mapped[str] = mapped_column(UUID(as_uuid=True), ForeignKey("polo.units.id"), nullable=False)
    person_id: Mapped[str] = mapped_column(UUID(as_uuid=True), ForeignKey("core.persons.id"), nullable=False)
    source_capture_id: Mapped[Any] = mapped_column(UUID(as_uuid=True), ForeignKey("territory.contacts_capture.id"), nullable=True)
    status: Mapped[str] = mapped_column(String(30), default="PRE_CADASTRADO", nullable=False)
    admitted_at: Mapped[Any] = mapped_column(DateTime, nullable=True)
    discharged_at: Mapped[Any] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)


class Modalidade(Base):
    __tablename__ = "modalidades"
    __table_args__ = {"schema": "polo"}

    id: Mapped[str] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    polo_id: Mapped[str] = mapped_column(UUID(as_uuid=True), ForeignKey("polo.units.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Any] = mapped_column(Text, nullable=True)
    active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)


class Frequencia(Base):
    __tablename__ = "frequencias"
    __table_args__ = {"schema": "polo"}

    id: Mapped[str] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    beneficiario_id: Mapped[str] = mapped_column(UUID(as_uuid=True), ForeignKey("polo.beneficiarios.id"), nullable=False)
    modalidade_id: Mapped[Any] = mapped_column(UUID(as_uuid=True), ForeignKey("polo.modalidades.id"), nullable=True)
    registered_by_user_id: Mapped[str] = mapped_column(UUID(as_uuid=True), ForeignKey("iam.users.id"), nullable=False)
    activity_date: Mapped[date] = mapped_column(Date, nullable=False)
    present: Mapped[bool] = mapped_column(Boolean, nullable=False)
    notes: Mapped[Any] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)


class Ocorrencia(Base):
    __tablename__ = "ocorrencias"
    __table_args__ = {"schema": "polo"}

    id: Mapped[str] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    polo_id: Mapped[str] = mapped_column(UUID(as_uuid=True), ForeignKey("polo.units.id"), nullable=False)
    beneficiario_id: Mapped[Any] = mapped_column(UUID(as_uuid=True), ForeignKey("polo.beneficiarios.id"), nullable=True)
    registered_by_user_id: Mapped[str] = mapped_column(UUID(as_uuid=True), ForeignKey("iam.users.id"), nullable=False)
    severity: Mapped[str] = mapped_column(String(20), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="OPEN", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)


class MonthlyReport(Base):
    __tablename__ = "monthly_reports"
    __table_args__ = {"schema": "polo"}

    id: Mapped[str] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    polo_id: Mapped[str] = mapped_column(UUID(as_uuid=True), ForeignKey("polo.units.id"), nullable=False)
    vereador_id: Mapped[str] = mapped_column(UUID(as_uuid=True), ForeignKey("core.vereadores.id"), nullable=False)
    created_by_user_id: Mapped[str] = mapped_column(UUID(as_uuid=True), ForeignKey("iam.users.id"), nullable=False)
    reference_month: Mapped[date] = mapped_column(Date, nullable=False)
    submitted_at: Mapped[Any] = mapped_column(DateTime, nullable=True)
    status: Mapped[str] = mapped_column(String(30), default="SUBMITTED", nullable=False)
    active_modalities_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_beneficiaries: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    occurrence_summary: Mapped[Any] = mapped_column(Text, nullable=True)
    narrative_text: Mapped[str] = mapped_column(Text, nullable=False)
    notes: Mapped[Any] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    modalities: Mapped[list["MonthlyReportModality"]] = relationship(
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    attachments: Mapped[list["MonthlyReportAttachment"]] = relationship(
        cascade="all, delete-orphan",
        lazy="selectin",
    )


class MonthlyReportModality(Base):
    __tablename__ = "monthly_report_modalities"
    __table_args__ = {"schema": "polo"}

    id: Mapped[str] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    monthly_report_id: Mapped[str] = mapped_column(UUID(as_uuid=True), ForeignKey("polo.monthly_reports.id"), nullable=False)
    modalidade_id: Mapped[Any] = mapped_column(UUID(as_uuid=True), ForeignKey("polo.modalidades.id"), nullable=True)
    modalidade_name: Mapped[str] = mapped_column(String(255), nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    beneficiaries_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    notes: Mapped[Any] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)


class MonthlyReportAttachment(Base):
    __tablename__ = "monthly_report_attachments"
    __table_args__ = {"schema": "polo"}

    id: Mapped[str] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    monthly_report_id: Mapped[str] = mapped_column(UUID(as_uuid=True), ForeignKey("polo.monthly_reports.id"), nullable=False)
    modalidade_id: Mapped[Any] = mapped_column(UUID(as_uuid=True), ForeignKey("polo.modalidades.id"), nullable=True)
    attachment_type: Mapped[str] = mapped_column(String(60), nullable=False)
    original_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    stored_path: Mapped[str] = mapped_column(Text, nullable=False)
    content_type: Mapped[Any] = mapped_column(String(120), nullable=True)
    file_size: Mapped[int] = mapped_column(Integer, nullable=False)
    description: Mapped[Any] = mapped_column(Text, nullable=True)
    uploaded_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)


class ModalityActionPlan(Base):
    __tablename__ = "modality_action_plans"
    __table_args__ = {"schema": "polo"}

    id: Mapped[str] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    polo_id: Mapped[str] = mapped_column(UUID(as_uuid=True), ForeignKey("polo.units.id"), nullable=False)
    modalidade_id: Mapped[str] = mapped_column(UUID(as_uuid=True), ForeignKey("polo.modalidades.id"), nullable=False)
    uploaded_by_user_id: Mapped[str] = mapped_column(UUID(as_uuid=True), ForeignKey("iam.users.id"), nullable=False)
    base_year: Mapped[int] = mapped_column(Integer, nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    professional_name: Mapped[Any] = mapped_column(String(180), nullable=True)
    original_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    stored_path: Mapped[str] = mapped_column(Text, nullable=False)
    content_type: Mapped[Any] = mapped_column(String(120), nullable=True)
    file_size: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="SUBMITTED", nullable=False)
    notes: Mapped[Any] = mapped_column(Text, nullable=True)
    uploaded_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
