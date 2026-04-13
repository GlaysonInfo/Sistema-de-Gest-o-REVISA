from datetime import datetime

from sqlalchemy import false, or_, select
from sqlalchemy.orm import Session

from app.domain.core.models import Address, Person
from app.domain.polo.models import PoloBeneficiario
from app.domain.territory.models import ContactCapture, Demand
from app.domain.workflow.models import Task


class TerritoryRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_captures(
        self,
        limit: int = 50,
        offset: int = 0,
        status: str | None = None,
        organization_ids: set[str] | None = None,
        vereador_ids: set[str] | None = None,
        polo_ids: set[str] | None = None,
        operational_polo_only: bool = False,
        force_empty: bool = False,
    ):
        statement = select(ContactCapture)
        if status:
            statement = statement.where(ContactCapture.capture_status == status)
        statement = self._apply_capture_scope(
            statement,
            organization_ids=organization_ids,
            vereador_ids=vereador_ids,
            polo_ids=polo_ids,
            operational_polo_only=operational_polo_only,
            force_empty=force_empty,
        )
        statement = statement.order_by(ContactCapture.created_at.desc()).offset(offset).limit(limit)
        return self.db.execute(statement).scalars().all()

    def get_capture(self, capture_id) -> ContactCapture | None:
        return self.db.get(ContactCapture, capture_id)

    def create_capture(self, entity: ContactCapture) -> ContactCapture:
        self.db.add(entity)
        self.db.flush()
        self.db.refresh(entity)
        return entity

    def update_capture(self, entity: ContactCapture, values: dict) -> ContactCapture:
        for field, value in values.items():
            setattr(entity, field, value)
        entity.updated_at = datetime.now()
        self.db.flush()
        self.db.refresh(entity)
        return entity

    def get_person(self, person_id) -> Person | None:
        return self.db.get(Person, person_id)

    def find_person_by_phone(self, phone: str | None) -> Person | None:
        if not phone:
            return None
        statement = select(Person).where(or_(Person.phone == phone, Person.secondary_phone == phone))
        return self.db.execute(statement).scalars().first()

    def create_person(self, entity: Person) -> Person:
        self.db.add(entity)
        self.db.flush()
        self.db.refresh(entity)
        return entity

    def create_address(self, entity: Address) -> Address:
        self.db.add(entity)
        self.db.flush()
        self.db.refresh(entity)
        return entity

    def list_demands(
        self,
        limit: int = 50,
        offset: int = 0,
        status: str | None = None,
        organization_ids: set[str] | None = None,
        vereador_ids: set[str] | None = None,
        polo_ids: set[str] | None = None,
        operational_polo_only: bool = False,
        force_empty: bool = False,
    ):
        statement = select(Demand)
        if status:
            statement = statement.where(Demand.status == status)
        statement = self._apply_demand_scope(
            statement,
            organization_ids=organization_ids,
            vereador_ids=vereador_ids,
            polo_ids=polo_ids,
            operational_polo_only=operational_polo_only,
            force_empty=force_empty,
        )
        statement = statement.order_by(Demand.created_at.desc()).offset(offset).limit(limit)
        return self.db.execute(statement).scalars().all()

    def create_demand(self, entity: Demand) -> Demand:
        self.db.add(entity)
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

    def create_task(self, entity: Task) -> Task:
        self.db.add(entity)
        self.db.flush()
        self.db.refresh(entity)
        return entity

    def _apply_capture_scope(self, statement, organization_ids, vereador_ids, polo_ids, operational_polo_only, force_empty):
        if force_empty:
            return statement.where(false())
        filters = []
        if organization_ids:
            filters.append(ContactCapture.organization_id.in_(organization_ids))
        if vereador_ids:
            filters.append(ContactCapture.vereador_id.in_(vereador_ids))
        if polo_ids:
            filters.append(
                select(PoloBeneficiario.id)
                .where(
                    PoloBeneficiario.source_capture_id == ContactCapture.id,
                    PoloBeneficiario.polo_id.in_(polo_ids),
                )
                .exists()
            )
        if operational_polo_only:
            filters.append(ContactCapture.classification == "BENEFICIARIO")
        return statement.where(or_(*filters)) if filters else statement

    def _apply_demand_scope(self, statement, organization_ids, vereador_ids, polo_ids, operational_polo_only, force_empty):
        if force_empty:
            return statement.where(false())
        filters = []
        if organization_ids:
            filters.append(Demand.organization_id.in_(organization_ids))
        if vereador_ids:
            filters.append(Demand.vereador_id.in_(vereador_ids))
        if polo_ids:
            filters.append(
                select(PoloBeneficiario.id)
                .where(
                    PoloBeneficiario.person_id == Demand.person_id,
                    PoloBeneficiario.polo_id.in_(polo_ids),
                )
                .exists()
            )
            filters.append(
                select(Task.id)
                .where(
                    Task.demand_id == Demand.id,
                    Task.polo_id.in_(polo_ids),
                )
                .exists()
            )
        if operational_polo_only:
            filters.append(Demand.category == "POLO_BENEFICIARIO")
            filters.append(select(PoloBeneficiario.id).where(PoloBeneficiario.person_id == Demand.person_id).exists())
        return statement.where(or_(*filters)) if filters else statement
