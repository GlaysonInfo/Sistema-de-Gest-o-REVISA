from datetime import datetime

from sqlalchemy import false, or_, select
from sqlalchemy.orm import Session

from app.domain.territory.models import Demand
from app.domain.workflow.models import Task


class WorkflowRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_tasks(
        self,
        status: str | None = None,
        demand_id=None,
        limit: int = 50,
        offset: int = 0,
        organization_ids: set[str] | None = None,
        vereador_ids: set[str] | None = None,
        polo_ids: set[str] | None = None,
        operational_polo_only: bool = False,
        force_empty: bool = False,
    ):
        statement = select(Task)
        if status:
            statement = statement.where(Task.status == status)
        if demand_id:
            statement = statement.where(Task.demand_id == demand_id)
        if force_empty:
            statement = statement.where(false())
        else:
            filters = []
            if organization_ids:
                filters.append(Task.organization_id.in_(organization_ids))
            if vereador_ids:
                filters.append(Task.vereador_id.in_(vereador_ids))
            if polo_ids:
                filters.append(Task.polo_id.in_(polo_ids))
            if operational_polo_only:
                filters.append(Task.polo_id.is_not(None))
            if filters:
                statement = statement.where(or_(*filters))
        statement = statement.order_by(Task.created_at.desc()).offset(offset).limit(limit)
        return self.db.execute(statement).scalars().all()

    def get_task(self, task_id) -> Task | None:
        return self.db.get(Task, task_id)

    def create_task(self, entity: Task) -> Task:
        self.db.add(entity)
        self.db.flush()
        self.db.refresh(entity)
        return entity

    def update_task(self, entity: Task, values: dict) -> Task:
        for field, value in values.items():
            setattr(entity, field, value)
        entity.updated_at = datetime.now()
        self.db.flush()
        self.db.refresh(entity)
        return entity

    def get_demand(self, demand_id) -> Demand | None:
        return self.db.get(Demand, demand_id)

    def update_demand(self, entity: Demand, values: dict) -> Demand:
        for field, value in values.items():
            setattr(entity, field, value)
        entity.updated_at = datetime.now()
        self.db.flush()
        self.db.refresh(entity)
        return entity
