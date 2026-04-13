from datetime import datetime

from sqlalchemy import false, or_, select
from sqlalchemy.orm import Session

from app.domain.core.models import Address, Consent, Person, PersonLink
from app.domain.polo.models import Frequencia, Ocorrencia, PoloBeneficiario, PoloUnit
from app.domain.territory.models import ContactCapture, Demand
from app.domain.workflow.models import Task


class CoreRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_persons(
        self,
        search: str | None = None,
        cpf: str | None = None,
        phone: str | None = None,
        limit: int = 50,
        offset: int = 0,
        organization_ids: set[str] | None = None,
        vereador_ids: set[str] | None = None,
        polo_ids: set[str] | None = None,
        operational_polo_only: bool = False,
        force_empty: bool = False,
    ):
        statement = select(Person)
        if search:
            pattern = f"%{search.strip()}%"
            statement = statement.where(
                or_(
                    Person.full_name.ilike(pattern),
                    Person.social_name.ilike(pattern),
                    Person.cpf.ilike(pattern),
                    Person.phone.ilike(pattern),
                    Person.secondary_phone.ilike(pattern),
                    Person.email.ilike(pattern),
                )
            )
        if cpf:
            statement = statement.where(Person.cpf == cpf)
        if phone:
            statement = statement.where(or_(Person.phone == phone, Person.secondary_phone == phone))
        statement = self._apply_person_scope(
            statement,
            organization_ids=organization_ids,
            vereador_ids=vereador_ids,
            polo_ids=polo_ids,
            operational_polo_only=operational_polo_only,
            force_empty=force_empty,
        )

        statement = statement.order_by(Person.full_name).offset(offset).limit(limit)
        return self.db.execute(statement).scalars().all()

    def get_person(self, person_id) -> Person | None:
        return self.db.get(Person, person_id)

    def create_person(self, entity: Person) -> Person:
        self.db.add(entity)
        self.db.flush()
        self.db.refresh(entity)
        return entity

    def update_person(self, entity: Person, values: dict) -> Person:
        for field, value in values.items():
            setattr(entity, field, value)
        entity.updated_at = datetime.now()
        self.db.flush()
        self.db.refresh(entity)
        return entity

    def list_person_addresses(self, person_id):
        statement = select(Address).where(Address.person_id == person_id).order_by(Address.created_at)
        return self.db.execute(statement).scalars().all()

    def create_address(self, entity: Address) -> Address:
        self.db.add(entity)
        self.db.flush()
        self.db.refresh(entity)
        return entity

    def list_person_consents(self, person_id):
        statement = select(Consent).where(Consent.person_id == person_id).order_by(Consent.created_at)
        return self.db.execute(statement).scalars().all()

    def create_consent(self, entity: Consent) -> Consent:
        self.db.add(entity)
        self.db.flush()
        self.db.refresh(entity)
        return entity

    def list_person_links(self, person_id):
        statement = select(PersonLink).where(PersonLink.person_id == person_id).order_by(PersonLink.created_at)
        return self.db.execute(statement).scalars().all()

    def create_person_link(self, entity: PersonLink) -> PersonLink:
        self.db.add(entity)
        self.db.flush()
        self.db.refresh(entity)
        return entity

    def list_person_captures(self, person_id):
        statement = select(ContactCapture).where(ContactCapture.person_id == person_id).order_by(ContactCapture.created_at.desc())
        return self.db.execute(statement).scalars().all()

    def list_person_demands(self, person_id):
        statement = select(Demand).where(Demand.person_id == person_id).order_by(Demand.created_at.desc())
        return self.db.execute(statement).scalars().all()

    def list_person_tasks(self, person_id, demand_ids: list | None = None):
        filters = [Task.person_id == person_id]
        if demand_ids:
            filters.append(Task.demand_id.in_(demand_ids))
        statement = select(Task).where(or_(*filters)).order_by(Task.created_at.desc())
        return self.db.execute(statement).scalars().all()

    def list_person_beneficiarios(self, person_id):
        statement = select(PoloBeneficiario).where(PoloBeneficiario.person_id == person_id).order_by(PoloBeneficiario.created_at.desc())
        return self.db.execute(statement).scalars().all()

    def list_beneficiario_frequencias(self, beneficiario_ids: list):
        if not beneficiario_ids:
            return []
        statement = select(Frequencia).where(Frequencia.beneficiario_id.in_(beneficiario_ids)).order_by(Frequencia.created_at.desc())
        return self.db.execute(statement).scalars().all()

    def list_beneficiario_ocorrencias(self, beneficiario_ids: list):
        if not beneficiario_ids:
            return []
        statement = select(Ocorrencia).where(Ocorrencia.beneficiario_id.in_(beneficiario_ids)).order_by(Ocorrencia.created_at.desc())
        return self.db.execute(statement).scalars().all()

    def get_polo(self, polo_id) -> PoloUnit | None:
        return self.db.get(PoloUnit, polo_id)

    def _apply_person_scope(self, statement, organization_ids, vereador_ids, polo_ids, operational_polo_only, force_empty):
        if force_empty:
            return statement.where(false())
        filters = []
        if organization_ids:
            filters.append(
                select(PersonLink.id)
                .where(PersonLink.person_id == Person.id, PersonLink.organization_id.in_(organization_ids))
                .exists()
            )
            filters.append(
                select(ContactCapture.id)
                .where(ContactCapture.person_id == Person.id, ContactCapture.organization_id.in_(organization_ids))
                .exists()
            )
            filters.append(
                select(Demand.id)
                .where(Demand.person_id == Person.id, Demand.organization_id.in_(organization_ids))
                .exists()
            )
            filters.append(
                select(Task.id)
                .where(Task.person_id == Person.id, Task.organization_id.in_(organization_ids))
                .exists()
            )
        if vereador_ids:
            filters.append(
                select(PersonLink.id)
                .where(PersonLink.person_id == Person.id, PersonLink.vereador_id.in_(vereador_ids))
                .exists()
            )
            filters.append(
                select(ContactCapture.id)
                .where(ContactCapture.person_id == Person.id, ContactCapture.vereador_id.in_(vereador_ids))
                .exists()
            )
            filters.append(
                select(Demand.id)
                .where(Demand.person_id == Person.id, Demand.vereador_id.in_(vereador_ids))
                .exists()
            )
            filters.append(
                select(Task.id)
                .where(Task.person_id == Person.id, Task.vereador_id.in_(vereador_ids))
                .exists()
            )
        if polo_ids:
            filters.append(
                select(PoloBeneficiario.id)
                .where(PoloBeneficiario.person_id == Person.id, PoloBeneficiario.polo_id.in_(polo_ids))
                .exists()
            )
            filters.append(
                select(Task.id)
                .where(Task.person_id == Person.id, Task.polo_id.in_(polo_ids))
                .exists()
            )
        if operational_polo_only:
            filters.append(select(PoloBeneficiario.id).where(PoloBeneficiario.person_id == Person.id).exists())
        return statement.where(or_(*filters)) if filters else statement
