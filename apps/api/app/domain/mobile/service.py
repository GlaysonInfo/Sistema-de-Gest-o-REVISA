import json

from app.domain.core.models import Address, Person, PersonLink
from app.domain.mobile.repository import MobileIntakeRepository
from app.domain.mobile.schemas import MobileIntakeCreate
from app.domain.polo.models import PoloBeneficiario
from app.domain.territory.models import ContactCapture, Demand
from app.shared.audit import write_audit_log


class MobileIntakeService:
    def __init__(self, repo: MobileIntakeRepository):
        self.repo = repo

    def create_intake(self, captured_by_user_id, payload: MobileIntakeCreate, db=None, current_user=None):
        user_id = getattr(current_user, "id", captured_by_user_id)
        person = self.repo.find_person(phone=payload.phone, cpf=payload.cpf)
        created_person = person is None
        if person is None:
            person = self.repo.create_person(
                Person(
                    full_name=payload.full_name,
                    cpf=payload.cpf,
                    birth_date=payload.birth_date,
                    phone=payload.phone,
                    email=payload.email,
                    gender=payload.gender,
                    notes=payload.notes,
                )
            )
            self._audit(db, user_id, "CREATE", "core", "persons", person.id)
            if payload.district:
                address = self.repo.create_address(Address(person_id=person.id, label="Mobile", district=payload.district))
                self._audit(db, user_id, "CREATE", "core", "addresses", address.id)

        capture = self.repo.create_capture(
            ContactCapture(
                captured_by_user_id=captured_by_user_id,
                organization_id=payload.organization_id,
                vereador_id=payload.vereador_id,
                team_id=payload.team_id,
                person_id=person.id,
                origin="MOBILE",
                classification=self._classification(payload.intake_type),
                full_name=payload.full_name,
                phone=payload.phone,
                district=payload.district,
                notes=payload.notes,
                priority_level=payload.priority_level,
                capture_status="REGISTERED",
            )
        )
        self._audit(db, user_id, "CREATE", "territory", "contacts_capture", capture.id)

        demand = self._create_demand_if_requested(captured_by_user_id, payload, person, capture, db, user_id)
        beneficiary, created_beneficiary = self._create_beneficiary_if_requested(payload, person, capture, db, user_id)
        person_link, created_person_link = self._create_person_link_if_requested(payload, person, db, user_id)

        return {
            "intake_type": payload.intake_type,
            "capture": capture,
            "person": person,
            "demand": demand,
            "beneficiary": beneficiary,
            "person_link": person_link,
            "created_person": created_person,
            "created_beneficiary": created_beneficiary,
            "created_person_link": created_person_link,
        }

    def _create_demand_if_requested(self, opened_by_user_id, payload, person, capture, db, user_id):
        if not payload.create_demand:
            return None
        demand = self.repo.create_demand(
            Demand(
                person_id=person.id,
                capture_id=capture.id,
                organization_id=payload.organization_id,
                vereador_id=payload.vereador_id,
                opened_by_user_id=opened_by_user_id,
                category=self._demand_category(payload.intake_type),
                title=self._demand_title(payload.intake_type, payload.full_name),
                description=payload.notes,
                priority=payload.priority_level or "MEDIUM",
            )
        )
        self._audit(db, user_id, "CREATE", "territory", "demands", demand.id)
        return demand

    def _create_beneficiary_if_requested(self, payload, person, capture, db, user_id):
        if payload.intake_type != "POLO_BENEFICIARIO":
            return None, False
        if payload.polo_id is None:
            raise LookupError("polo_required")
        if self.repo.get_polo(payload.polo_id) is None:
            raise LookupError("polo_not_found")
        beneficiary = self.repo.get_beneficiary(payload.polo_id, person.id)
        if beneficiary is not None:
            return beneficiary, False
        beneficiary = self.repo.create_beneficiary(
            PoloBeneficiario(
                polo_id=payload.polo_id,
                person_id=person.id,
                source_capture_id=capture.id,
                status="PRE_CADASTRADO",
            )
        )
        self._audit(db, user_id, "CREATE", "polo", "beneficiarios", beneficiary.id)
        return beneficiary, True

    def _create_person_link_if_requested(self, payload, person, db, user_id):
        if payload.intake_type != "MANDATO_ACOMPANHAMENTO":
            return None, False
        if payload.organization_id is None and payload.vereador_id is None:
            return None, False
        link_type = "MANDATO_ACOMPANHAMENTO"
        link = self.repo.get_person_link(person.id, payload.organization_id, payload.vereador_id, link_type)
        if link is not None:
            return link, False
        link = self.repo.create_person_link(
            PersonLink(
                person_id=person.id,
                organization_id=payload.organization_id,
                vereador_id=payload.vereador_id,
                link_type=link_type,
                status="ACTIVE",
                metadata_json={"source": "mobile_intake"},
            )
        )
        self._audit(db, user_id, "CREATE", "core", "person_links", link.id)
        return link, True

    @staticmethod
    def _classification(intake_type: str) -> str:
        return "BENEFICIARIO" if intake_type == "POLO_BENEFICIARIO" else "ACOMPANHAMENTO"

    @staticmethod
    def _demand_category(intake_type: str) -> str:
        return "POLO_BENEFICIARIO" if intake_type == "POLO_BENEFICIARIO" else "ACOMPANHAMENTO_MANDATO"

    @staticmethod
    def _demand_title(intake_type: str, full_name: str) -> str:
        prefix = "Captacao polo" if intake_type == "POLO_BENEFICIARIO" else "Acompanhamento mandato"
        return f"{prefix} - {full_name}"

    @staticmethod
    def _audit(db, user_id, action: str, entity_schema: str, entity_name: str, entity_id) -> None:
        if db is None:
            return
        write_audit_log(
            db,
            user_id=user_id,
            action=action,
            entity_schema=entity_schema,
            entity_name=entity_name,
            entity_id=entity_id,
            new_values_json=json.dumps({"id": str(entity_id), "source": "mobile_intake"}),
        )
