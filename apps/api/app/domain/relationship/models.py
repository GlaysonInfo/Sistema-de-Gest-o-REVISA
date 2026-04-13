from datetime import date, datetime
from typing import Any
from uuid import uuid4

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class RelationshipClassification(Base):
    __tablename__ = "classifications"
    __table_args__ = {"schema": "relationship"}

    id: Mapped[str] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    person_id: Mapped[str] = mapped_column(UUID(as_uuid=True), ForeignKey("core.persons.id"), nullable=False)
    organization_id: Mapped[Any] = mapped_column(UUID(as_uuid=True), ForeignKey("core.organizations.id"), nullable=True)
    vereador_id: Mapped[Any] = mapped_column(UUID(as_uuid=True), ForeignKey("core.vereadores.id"), nullable=True)
    classified_by_user_id: Mapped[str] = mapped_column(UUID(as_uuid=True), ForeignKey("iam.users.id"), nullable=False)
    level: Mapped[str] = mapped_column(String(40), nullable=False)
    influence: Mapped[Any] = mapped_column(String(40), nullable=True)
    engagement: Mapped[Any] = mapped_column(String(40), nullable=True)
    vote_2028: Mapped[Any] = mapped_column(String(40), nullable=True)
    priority: Mapped[Any] = mapped_column(String(20), nullable=True)
    status: Mapped[str] = mapped_column(String(30), default="ACTIVE", nullable=False)
    responsible_user_id: Mapped[Any] = mapped_column(UUID(as_uuid=True), ForeignKey("iam.users.id"), nullable=True)
    notes: Mapped[Any] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)


class Leadership(Base):
    __tablename__ = "leaderships"
    __table_args__ = {"schema": "relationship"}

    id: Mapped[str] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    person_id: Mapped[str] = mapped_column(UUID(as_uuid=True), ForeignKey("core.persons.id"), nullable=False)
    organization_id: Mapped[Any] = mapped_column(UUID(as_uuid=True), ForeignKey("core.organizations.id"), nullable=True)
    vereador_id: Mapped[Any] = mapped_column(UUID(as_uuid=True), ForeignKey("core.vereadores.id"), nullable=True)
    polo_id: Mapped[Any] = mapped_column(UUID(as_uuid=True), ForeignKey("polo.units.id"), nullable=True)
    district: Mapped[Any] = mapped_column(String(120), nullable=True)
    leadership_type: Mapped[str] = mapped_column(String(60), nullable=False)
    area_atuacao: Mapped[Any] = mapped_column(String(120), nullable=True)
    influence_count: Mapped[Any] = mapped_column(Integer, nullable=True)
    loyalty_level: Mapped[Any] = mapped_column(String(40), nullable=True)
    active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    identified_at: Mapped[Any] = mapped_column(DateTime, nullable=True)
    responsible_user_id: Mapped[Any] = mapped_column(UUID(as_uuid=True), ForeignKey("iam.users.id"), nullable=True)
    notes: Mapped[Any] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)


class Partner(Base):
    __tablename__ = "partners"
    __table_args__ = {"schema": "relationship"}

    id: Mapped[str] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    organization_id: Mapped[Any] = mapped_column(UUID(as_uuid=True), ForeignKey("core.organizations.id"), nullable=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    legal_name: Mapped[Any] = mapped_column(String(255), nullable=True)
    document_number: Mapped[Any] = mapped_column(String(30), nullable=True)
    partner_type: Mapped[str] = mapped_column(String(60), nullable=False)
    contact_name: Mapped[Any] = mapped_column(String(180), nullable=True)
    contact_phone: Mapped[Any] = mapped_column(String(30), nullable=True)
    contact_email: Mapped[Any] = mapped_column(String(180), nullable=True)
    district: Mapped[Any] = mapped_column(String(120), nullable=True)
    contribution_area: Mapped[Any] = mapped_column(String(120), nullable=True)
    service_offered: Mapped[Any] = mapped_column(Text, nullable=True)
    capacity: Mapped[Any] = mapped_column(String(120), nullable=True)
    partnership_type: Mapped[Any] = mapped_column(String(60), nullable=True)
    status: Mapped[str] = mapped_column(String(30), default="PROSPECT", nullable=False)
    responsible_user_id: Mapped[Any] = mapped_column(UUID(as_uuid=True), ForeignKey("iam.users.id"), nullable=True)
    notes: Mapped[Any] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)


class FieldEvent(Base):
    __tablename__ = "field_events"
    __table_args__ = {"schema": "relationship"}

    id: Mapped[str] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    organization_id: Mapped[Any] = mapped_column(UUID(as_uuid=True), ForeignKey("core.organizations.id"), nullable=True)
    polo_id: Mapped[Any] = mapped_column(UUID(as_uuid=True), ForeignKey("polo.units.id"), nullable=True)
    partner_id: Mapped[Any] = mapped_column(UUID(as_uuid=True), ForeignKey("relationship.partners.id"), nullable=True)
    created_by_user_id: Mapped[str] = mapped_column(UUID(as_uuid=True), ForeignKey("iam.users.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    district: Mapped[Any] = mapped_column(String(120), nullable=True)
    event_type: Mapped[str] = mapped_column(String(60), nullable=False)
    event_date: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="PLANNED", nullable=False)
    expected_people: Mapped[Any] = mapped_column(Integer, nullable=True)
    actual_people: Mapped[Any] = mapped_column(Integer, nullable=True)
    captures_count: Mapped[Any] = mapped_column(Integer, nullable=True)
    leaders_identified: Mapped[Any] = mapped_column(Integer, nullable=True)
    next_action: Mapped[Any] = mapped_column(Text, nullable=True)
    notes: Mapped[Any] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
