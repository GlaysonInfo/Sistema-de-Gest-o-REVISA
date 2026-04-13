from datetime import date, datetime
from typing import Any
from uuid import uuid4

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Numeric, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Organization(Base):
    __tablename__ = "organizations"
    __table_args__ = {"schema": "core"}

    id: Mapped[str] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    type: Mapped[str] = mapped_column(String(30), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    legal_name: Mapped[Any] = mapped_column(String(255), nullable=True)
    document_number: Mapped[Any] = mapped_column(String(30), nullable=True)
    parent_organization_id: Mapped[Any] = mapped_column(UUID(as_uuid=True), ForeignKey("core.organizations.id"), nullable=True)
    active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)


class Person(Base):
    __tablename__ = "persons"
    __table_args__ = {"schema": "core"}

    id: Mapped[str] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    social_name: Mapped[Any] = mapped_column(String(255), nullable=True)
    cpf: Mapped[Any] = mapped_column(String(20), nullable=True)
    birth_date: Mapped[Any] = mapped_column(Date, nullable=True)
    phone: Mapped[Any] = mapped_column(String(30), nullable=True)
    secondary_phone: Mapped[Any] = mapped_column(String(30), nullable=True)
    email: Mapped[Any] = mapped_column(String(180), nullable=True)
    gender: Mapped[Any] = mapped_column(String(30), nullable=True)
    notes: Mapped[Any] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)


class Address(Base):
    __tablename__ = "addresses"
    __table_args__ = {"schema": "core"}

    id: Mapped[str] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    person_id: Mapped[Any] = mapped_column(UUID(as_uuid=True), ForeignKey("core.persons.id", ondelete="CASCADE"), nullable=True)
    organization_id: Mapped[Any] = mapped_column(UUID(as_uuid=True), ForeignKey("core.organizations.id", ondelete="CASCADE"), nullable=True)
    label: Mapped[Any] = mapped_column(String(60), nullable=True)
    street: Mapped[Any] = mapped_column(String(255), nullable=True)
    number: Mapped[Any] = mapped_column(String(30), nullable=True)
    complement: Mapped[Any] = mapped_column(String(120), nullable=True)
    district: Mapped[Any] = mapped_column(String(120), nullable=True)
    city: Mapped[Any] = mapped_column(String(120), nullable=True)
    state: Mapped[Any] = mapped_column(String(10), nullable=True)
    zip_code: Mapped[Any] = mapped_column(String(20), nullable=True)
    latitude: Mapped[Any] = mapped_column(Numeric(10, 7), nullable=True)
    longitude: Mapped[Any] = mapped_column(Numeric(10, 7), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)


class Vereador(Base):
    __tablename__ = "vereadores"
    __table_args__ = {"schema": "core"}

    id: Mapped[str] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    person_id: Mapped[str] = mapped_column(UUID(as_uuid=True), ForeignKey("core.persons.id"), nullable=False)
    organization_id: Mapped[str] = mapped_column(UUID(as_uuid=True), ForeignKey("core.organizations.id"), nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)


class Team(Base):
    __tablename__ = "teams"
    __table_args__ = {"schema": "core"}

    id: Mapped[str] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    organization_id: Mapped[str] = mapped_column(UUID(as_uuid=True), ForeignKey("core.organizations.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    team_type: Mapped[str] = mapped_column(String(30), nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)


class PersonLink(Base):
    __tablename__ = "person_links"
    __table_args__ = {"schema": "core"}

    id: Mapped[str] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    person_id: Mapped[str] = mapped_column(UUID(as_uuid=True), ForeignKey("core.persons.id"), nullable=False)
    organization_id: Mapped[Any] = mapped_column(UUID(as_uuid=True), ForeignKey("core.organizations.id"), nullable=True)
    vereador_id: Mapped[Any] = mapped_column(UUID(as_uuid=True), ForeignKey("core.vereadores.id"), nullable=True)
    link_type: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="ACTIVE", nullable=False)
    start_date: Mapped[Any] = mapped_column(Date, nullable=True)
    end_date: Mapped[Any] = mapped_column(Date, nullable=True)
    metadata_json: Mapped[Any] = mapped_column("metadata", JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)


class Consent(Base):
    __tablename__ = "consents"
    __table_args__ = {"schema": "core"}

    id: Mapped[str] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    person_id: Mapped[str] = mapped_column(UUID(as_uuid=True), ForeignKey("core.persons.id"), nullable=False)
    consent_type: Mapped[str] = mapped_column(String(50), nullable=False)
    granted: Mapped[bool] = mapped_column(Boolean, nullable=False)
    version: Mapped[str] = mapped_column(String(20), nullable=False)
    granted_at: Mapped[Any] = mapped_column(DateTime, nullable=True)
    revoked_at: Mapped[Any] = mapped_column(DateTime, nullable=True)
    captured_by_user_id: Mapped[Any] = mapped_column(UUID(as_uuid=True), ForeignKey("iam.users.id"), nullable=True)
    evidence_ref: Mapped[Any] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
