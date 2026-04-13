from datetime import datetime
from typing import Any
from uuid import uuid4

from sqlalchemy import DateTime, ForeignKey, Numeric, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class ContactCapture(Base):
    __tablename__ = "contacts_capture"
    __table_args__ = {"schema": "territory"}

    id: Mapped[str] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    captured_by_user_id: Mapped[str] = mapped_column(UUID(as_uuid=True), ForeignKey("iam.users.id"), nullable=False)
    organization_id: Mapped[Any] = mapped_column(UUID(as_uuid=True), ForeignKey("core.organizations.id"), nullable=True)
    vereador_id: Mapped[Any] = mapped_column(UUID(as_uuid=True), ForeignKey("core.vereadores.id"), nullable=True)
    team_id: Mapped[Any] = mapped_column(UUID(as_uuid=True), ForeignKey("core.teams.id"), nullable=True)
    person_id: Mapped[Any] = mapped_column(UUID(as_uuid=True), ForeignKey("core.persons.id"), nullable=True)
    origin: Mapped[str] = mapped_column(String(30), nullable=False)
    classification: Mapped[str] = mapped_column(String(30), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[Any] = mapped_column(String(30), nullable=True)
    district: Mapped[Any] = mapped_column(String(120), nullable=True)
    notes: Mapped[Any] = mapped_column(Text, nullable=True)
    priority_level: Mapped[Any] = mapped_column(String(20), nullable=True)
    capture_status: Mapped[str] = mapped_column(String(30), default="NEW", nullable=False)
    latitude: Mapped[Any] = mapped_column(Numeric(10, 7), nullable=True)
    longitude: Mapped[Any] = mapped_column(Numeric(10, 7), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)


class Demand(Base):
    __tablename__ = "demands"
    __table_args__ = {"schema": "territory"}

    id: Mapped[str] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    person_id: Mapped[Any] = mapped_column(UUID(as_uuid=True), ForeignKey("core.persons.id"), nullable=True)
    capture_id: Mapped[Any] = mapped_column(UUID(as_uuid=True), ForeignKey("territory.contacts_capture.id"), nullable=True)
    organization_id: Mapped[Any] = mapped_column(UUID(as_uuid=True), ForeignKey("core.organizations.id"), nullable=True)
    vereador_id: Mapped[Any] = mapped_column(UUID(as_uuid=True), ForeignKey("core.vereadores.id"), nullable=True)
    opened_by_user_id: Mapped[str] = mapped_column(UUID(as_uuid=True), ForeignKey("iam.users.id"), nullable=False)
    assigned_to_user_id: Mapped[Any] = mapped_column(UUID(as_uuid=True), ForeignKey("iam.users.id"), nullable=True)
    category: Mapped[str] = mapped_column(String(60), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Any] = mapped_column(Text, nullable=True)
    priority: Mapped[str] = mapped_column(String(20), default="MEDIUM", nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="OPEN", nullable=False)
    due_at: Mapped[Any] = mapped_column(DateTime, nullable=True)
    resolved_at: Mapped[Any] = mapped_column(DateTime, nullable=True)
    resolution_notes: Mapped[Any] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
