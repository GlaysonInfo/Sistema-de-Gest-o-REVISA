from datetime import datetime
from typing import Any
from uuid import uuid4

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Task(Base):
    __tablename__ = "tasks"
    __table_args__ = {"schema": "workflow"}

    id: Mapped[str] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    organization_id: Mapped[Any] = mapped_column(UUID(as_uuid=True), ForeignKey("core.organizations.id"), nullable=True)
    vereador_id: Mapped[Any] = mapped_column(UUID(as_uuid=True), ForeignKey("core.vereadores.id"), nullable=True)
    polo_id: Mapped[Any] = mapped_column(UUID(as_uuid=True), ForeignKey("polo.units.id"), nullable=True)
    person_id: Mapped[Any] = mapped_column(UUID(as_uuid=True), ForeignKey("core.persons.id"), nullable=True)
    demand_id: Mapped[Any] = mapped_column(UUID(as_uuid=True), ForeignKey("territory.demands.id"), nullable=True)
    assigned_to_user_id: Mapped[Any] = mapped_column(UUID(as_uuid=True), ForeignKey("iam.users.id"), nullable=True)
    created_by_user_id: Mapped[str] = mapped_column(UUID(as_uuid=True), ForeignKey("iam.users.id"), nullable=False)
    task_type: Mapped[str] = mapped_column(String(50), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Any] = mapped_column(Text, nullable=True)
    priority: Mapped[str] = mapped_column(String(20), default="MEDIUM", nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="OPEN", nullable=False)
    due_at: Mapped[Any] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[Any] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
