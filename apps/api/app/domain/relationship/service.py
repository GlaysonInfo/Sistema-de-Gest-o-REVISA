from app.core.audit import audited_mutation
from app.domain.relationship.models import FieldEvent, Leadership, Partner, RelationshipClassification
from app.domain.relationship.repository import RelationshipRepository
from app.domain.relationship.schemas import ClassificationCreate, FieldEventCreate, LeadershipCreate, PartnerCreate


class RelationshipService:
    def __init__(self, repo: RelationshipRepository):
        self.repo = repo

    def list_classifications(self, person_id=None, level: str | None = None):
        return self.repo.list_classifications(person_id=person_id, level=level)

    @audited_mutation(action="CREATE", entity_schema="relationship", entity_name="classifications")
    def create_classification(self, payload: ClassificationCreate, classified_by_user_id, db=None, current_user=None):
        self._ensure_person(payload.person_id)
        entity = RelationshipClassification(classified_by_user_id=classified_by_user_id, **payload.model_dump())
        return self.repo.create_classification(entity)

    def list_leaderships(self, district: str | None = None, active: bool | None = None):
        return self.repo.list_leaderships(district=district, active=active)

    @audited_mutation(action="CREATE", entity_schema="relationship", entity_name="leaderships")
    def create_leadership(self, payload: LeadershipCreate, db=None, current_user=None):
        self._ensure_person(payload.person_id)
        if payload.polo_id is not None:
            self._ensure_polo(payload.polo_id)
        return self.repo.create_leadership(Leadership(**payload.model_dump()))

    def list_partners(self, partner_type: str | None = None, status: str | None = None):
        return self.repo.list_partners(partner_type=partner_type, status=status)

    @audited_mutation(action="CREATE", entity_schema="relationship", entity_name="partners")
    def create_partner(self, payload: PartnerCreate, db=None, current_user=None):
        return self.repo.create_partner(Partner(**payload.model_dump()))

    def list_field_events(self, district: str | None = None, status: str | None = None):
        return self.repo.list_field_events(district=district, status=status)

    @audited_mutation(action="CREATE", entity_schema="relationship", entity_name="field_events")
    def create_field_event(self, payload: FieldEventCreate, created_by_user_id, db=None, current_user=None):
        if payload.polo_id is not None:
            self._ensure_polo(payload.polo_id)
        if payload.partner_id is not None and self.repo.get_partner(payload.partner_id) is None:
            raise LookupError("partner_not_found")
        entity = FieldEvent(created_by_user_id=created_by_user_id, **payload.model_dump())
        return self.repo.create_field_event(entity)

    def _ensure_person(self, person_id):
        if self.repo.get_person(person_id) is None:
            raise LookupError("person_not_found")

    def _ensure_polo(self, polo_id):
        if self.repo.get_polo(polo_id) is None:
            raise LookupError("polo_not_found")
