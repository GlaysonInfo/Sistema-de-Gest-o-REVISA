from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.core.models import Person
from app.domain.polo.models import PoloUnit
from app.domain.relationship.models import FieldEvent, Leadership, Partner, RelationshipClassification


class RelationshipRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_person(self, person_id) -> Person | None:
        return self.db.get(Person, person_id)

    def get_polo(self, polo_id) -> PoloUnit | None:
        return self.db.get(PoloUnit, polo_id)

    def get_partner(self, partner_id) -> Partner | None:
        return self.db.get(Partner, partner_id)

    def list_classifications(self, person_id=None, level: str | None = None):
        statement = select(RelationshipClassification)
        if person_id:
            statement = statement.where(RelationshipClassification.person_id == person_id)
        if level:
            statement = statement.where(RelationshipClassification.level == level)
        return self.db.execute(statement.order_by(RelationshipClassification.created_at.desc())).scalars().all()

    def create_classification(self, entity: RelationshipClassification) -> RelationshipClassification:
        self.db.add(entity)
        self.db.flush()
        self.db.refresh(entity)
        return entity

    def list_leaderships(self, district: str | None = None, active: bool | None = None):
        statement = select(Leadership)
        if district:
            statement = statement.where(Leadership.district == district)
        if active is not None:
            statement = statement.where(Leadership.active == active)
        return self.db.execute(statement.order_by(Leadership.created_at.desc())).scalars().all()

    def create_leadership(self, entity: Leadership) -> Leadership:
        self.db.add(entity)
        self.db.flush()
        self.db.refresh(entity)
        return entity

    def list_partners(self, partner_type: str | None = None, status: str | None = None):
        statement = select(Partner)
        if partner_type:
            statement = statement.where(Partner.partner_type == partner_type)
        if status:
            statement = statement.where(Partner.status == status)
        return self.db.execute(statement.order_by(Partner.created_at.desc())).scalars().all()

    def create_partner(self, entity: Partner) -> Partner:
        self.db.add(entity)
        self.db.flush()
        self.db.refresh(entity)
        return entity

    def list_field_events(self, district: str | None = None, status: str | None = None):
        statement = select(FieldEvent)
        if district:
            statement = statement.where(FieldEvent.district == district)
        if status:
            statement = statement.where(FieldEvent.status == status)
        return self.db.execute(statement.order_by(FieldEvent.event_date.desc(), FieldEvent.created_at.desc())).scalars().all()

    def create_field_event(self, entity: FieldEvent) -> FieldEvent:
        self.db.add(entity)
        self.db.flush()
        self.db.refresh(entity)
        return entity
