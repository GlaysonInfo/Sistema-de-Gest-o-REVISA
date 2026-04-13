from sqlalchemy import and_, or_, select
from sqlalchemy.orm import Session

from app.domain.core.models import Address, Person, PersonLink
from app.domain.polo.models import PoloBeneficiario, PoloUnit
from app.domain.territory.models import ContactCapture, Demand


class MobileIntakeRepository:
    def __init__(self, db: Session):
        self.db = db

    def find_person(self, phone: str | None = None, cpf: str | None = None) -> Person | None:
        filters = []
        if phone:
            filters.append(or_(Person.phone == phone, Person.secondary_phone == phone))
        if cpf:
            filters.append(Person.cpf == cpf)
        if not filters:
            return None
        statement = select(Person).where(or_(*filters))
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

    def create_capture(self, entity: ContactCapture) -> ContactCapture:
        self.db.add(entity)
        self.db.flush()
        self.db.refresh(entity)
        return entity

    def create_demand(self, entity: Demand) -> Demand:
        self.db.add(entity)
        self.db.flush()
        self.db.refresh(entity)
        return entity

    def get_polo(self, polo_id) -> PoloUnit | None:
        return self.db.get(PoloUnit, polo_id)

    def get_beneficiary(self, polo_id, person_id) -> PoloBeneficiario | None:
        statement = select(PoloBeneficiario).where(
            and_(
                PoloBeneficiario.polo_id == polo_id,
                PoloBeneficiario.person_id == person_id,
            )
        )
        return self.db.execute(statement).scalars().first()

    def create_beneficiary(self, entity: PoloBeneficiario) -> PoloBeneficiario:
        self.db.add(entity)
        self.db.flush()
        self.db.refresh(entity)
        return entity

    def get_person_link(self, person_id, organization_id, vereador_id, link_type: str) -> PersonLink | None:
        statement = select(PersonLink).where(
            and_(
                PersonLink.person_id == person_id,
                PersonLink.organization_id == organization_id,
                PersonLink.vereador_id == vereador_id,
                PersonLink.link_type == link_type,
            )
        )
        return self.db.execute(statement).scalars().first()

    def create_person_link(self, entity: PersonLink) -> PersonLink:
        self.db.add(entity)
        self.db.flush()
        self.db.refresh(entity)
        return entity
