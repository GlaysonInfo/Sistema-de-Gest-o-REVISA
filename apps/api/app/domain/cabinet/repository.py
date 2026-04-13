from sqlalchemy import false, func, or_, select
from sqlalchemy.orm import Session

from app.domain.core.models import Organization, Person, PersonLink, Vereador
from app.domain.relationship.models import FieldEvent
from app.domain.territory.models import ContactCapture, Demand
from app.domain.workflow.models import Task


class CabinetRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_cabinets(self, organization_ids: set[str] | None = None, vereador_ids: set[str] | None = None, force_empty: bool = False):
        statement = (
            select(Organization, Vereador, Person)
            .join(Vereador, Vereador.organization_id == Organization.id)
            .join(Person, Person.id == Vereador.person_id)
            .where(Organization.type == "GABINETE")
            .order_by(Organization.name)
        )
        if force_empty:
            statement = statement.where(false())
        else:
            filters = []
            if organization_ids:
                filters.append(Organization.id.in_(organization_ids))
            if vereador_ids:
                filters.append(Vereador.id.in_(vereador_ids))
            if filters:
                statement = statement.where(or_(*filters))
        return self.db.execute(statement).all()

    def get_cabinet(self, organization_id):
        statement = (
            select(Organization, Vereador, Person)
            .join(Vereador, Vereador.organization_id == Organization.id)
            .join(Person, Person.id == Vereador.person_id)
            .where(Organization.id == organization_id, Organization.type == "GABINETE")
        )
        return self.db.execute(statement).first()

    def find_cabinet_by_document(self, document_number: str | None):
        if not document_number:
            return None
        statement = (
            select(Organization, Vereador, Person)
            .join(Vereador, Vereador.organization_id == Organization.id)
            .join(Person, Person.id == Vereador.person_id)
            .where(Organization.type == "GABINETE", Organization.document_number == document_number)
        )
        return self.db.execute(statement).first()

    def create_organization(self, entity: Organization) -> Organization:
        self.db.add(entity)
        self.db.flush()
        self.db.refresh(entity)
        return entity

    def create_person(self, entity: Person) -> Person:
        self.db.add(entity)
        self.db.flush()
        self.db.refresh(entity)
        return entity

    def create_vereador(self, entity: Vereador) -> Vereador:
        self.db.add(entity)
        self.db.flush()
        self.db.refresh(entity)
        return entity

    def count_linked_people(self, organization_id, vereador_id) -> int:
        statement = select(func.count(func.distinct(PersonLink.person_id))).where(
            or_(
                PersonLink.organization_id == organization_id,
                PersonLink.vereador_id == vereador_id,
            )
        )
        return self.db.execute(statement).scalar_one()

    def list_captures(self, organization_id, vereador_id, limit: int = 10):
        statement = (
            select(ContactCapture)
            .where(
                or_(
                    ContactCapture.organization_id == organization_id,
                    ContactCapture.vereador_id == vereador_id,
                )
            )
            .order_by(ContactCapture.created_at.desc())
            .limit(limit)
        )
        return self.db.execute(statement).scalars().all()

    def list_demands(self, organization_id, vereador_id, limit: int = 10):
        statement = (
            select(Demand)
            .where(or_(Demand.organization_id == organization_id, Demand.vereador_id == vereador_id))
            .order_by(Demand.created_at.desc())
            .limit(limit)
        )
        return self.db.execute(statement).scalars().all()

    def list_tasks(self, organization_id, vereador_id, limit: int = 10):
        statement = (
            select(Task)
            .where(or_(Task.organization_id == organization_id, Task.vereador_id == vereador_id))
            .order_by(Task.created_at.desc())
            .limit(limit)
        )
        return self.db.execute(statement).scalars().all()

    def list_field_events(self, organization_id, limit: int = 10):
        statement = (
            select(FieldEvent)
            .where(FieldEvent.organization_id == organization_id)
            .order_by(FieldEvent.event_date.desc(), FieldEvent.created_at.desc())
            .limit(limit)
        )
        return self.db.execute(statement).scalars().all()
