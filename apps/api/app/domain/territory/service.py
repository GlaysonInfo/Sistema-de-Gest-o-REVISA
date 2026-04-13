import json

from app.core.audit import audited_mutation
from app.core.access_scope import can_access_all_cabinets, can_access_all_polos, scoped_ids
from app.domain.core.models import Address, Person
from app.domain.territory.models import ContactCapture, Demand
from app.domain.territory.repository import TerritoryRepository
from app.domain.territory.schemas import (
    ContactCaptureClassifyRequest,
    ContactCaptureConvertDemandRequest,
    ContactCaptureCreate,
    DemandAssignRequest,
    DemandCreate,
    DemandTaskCreate,
    DemandUpdate,
)
from app.domain.workflow.models import Task
from app.shared.audit import write_audit_log


class TerritoryService:
    def __init__(self, repo: TerritoryRepository):
        self.repo = repo

    def list_captures(self, limit: int = 50, offset: int = 0, status: str | None = None, current_user=None):
        scope = self._scope_for_territory(current_user)
        return self.repo.list_captures(limit=limit, offset=offset, status=status, **scope)

    def get_capture(self, capture_id):
        return self.repo.get_capture(capture_id)

    @audited_mutation(action="CREATE", entity_schema="territory", entity_name="contacts_capture")
    def create_capture(self, captured_by_user_id, payload: ContactCaptureCreate, db=None, current_user=None):
        entity = ContactCapture(
            captured_by_user_id=captured_by_user_id,
            vereador_id=payload.vereador_id,
            team_id=payload.team_id,
            origin=payload.origin,
            classification=payload.classification,
            full_name=payload.full_name,
            phone=payload.phone,
            district=payload.district,
            notes=payload.notes,
            priority_level=payload.priority_level,
            latitude=payload.latitude,
            longitude=payload.longitude,
        )
        return self.repo.create_capture(entity)

    @audited_mutation(action="UPDATE", entity_schema="territory", entity_name="contacts_capture")
    def classify_capture(self, capture: ContactCapture, payload: ContactCaptureClassifyRequest, db=None, current_user=None):
        values = {
            "classification": payload.classification,
            "capture_status": "CLASSIFIED",
        }
        if payload.notes is not None:
            values["notes"] = payload.notes
        if payload.priority_level is not None:
            values["priority_level"] = payload.priority_level
        return self.repo.update_capture(capture, values)

    def list_demands(self, limit: int = 50, offset: int = 0, status: str | None = None, current_user=None):
        scope = self._scope_for_territory(current_user)
        return self.repo.list_demands(limit=limit, offset=offset, status=status, **scope)

    def get_demand(self, demand_id):
        return self.repo.get_demand(demand_id)

    @audited_mutation(action="CREATE", entity_schema="territory", entity_name="demands")
    def create_demand(self, opened_by_user_id, payload: DemandCreate, db=None, current_user=None):
        entity = Demand(
            person_id=payload.person_id,
            capture_id=payload.capture_id,
            organization_id=payload.organization_id,
            vereador_id=payload.vereador_id,
            opened_by_user_id=opened_by_user_id,
            assigned_to_user_id=payload.assigned_to_user_id,
            category=payload.category,
            title=payload.title,
            description=payload.description,
            priority=payload.priority,
            due_at=payload.due_at,
        )
        return self.repo.create_demand(entity)

    @audited_mutation(action="UPDATE", entity_schema="territory", entity_name="demands")
    def update_demand(self, demand: Demand, payload: DemandUpdate, db=None, current_user=None):
        return self.repo.update_demand(demand, payload.model_dump(exclude_unset=True))

    @audited_mutation(action="ASSIGN", entity_schema="territory", entity_name="demands")
    def assign_demand(self, demand: Demand, payload: DemandAssignRequest, db=None, current_user=None):
        return self.repo.update_demand(
            demand,
            {
                "assigned_to_user_id": payload.assigned_to_user_id,
                "status": payload.status,
            },
        )

    def create_task_from_demand(
        self,
        demand: Demand,
        payload: DemandTaskCreate,
        created_by_user_id,
        db=None,
        current_user=None,
    ):
        user_id = getattr(current_user, "id", created_by_user_id)
        task = self.repo.create_task(
            Task(
                organization_id=demand.organization_id,
                vereador_id=demand.vereador_id,
                person_id=demand.person_id,
                demand_id=demand.id,
                assigned_to_user_id=payload.assigned_to_user_id or demand.assigned_to_user_id,
                created_by_user_id=created_by_user_id,
                task_type=payload.task_type,
                title=payload.title or demand.title,
                description=payload.description if payload.description is not None else demand.description,
                priority=payload.priority or demand.priority,
                due_at=payload.due_at if payload.due_at is not None else demand.due_at,
            )
        )
        self._audit(db, user_id, "CREATE", "workflow", "tasks", task.id)

        if demand.status in {"OPEN", "ASSIGNED"}:
            demand = self.repo.update_demand(demand, {"status": "IN_PROGRESS"})
            self._audit(
                db,
                user_id,
                "UPDATE",
                "territory",
                "demands",
                demand.id,
                new_values_json=json.dumps({"id": str(demand.id), "status": demand.status}),
            )

        return task

    def convert_capture_to_demand(
        self,
        capture: ContactCapture,
        payload: ContactCaptureConvertDemandRequest,
        opened_by_user_id,
        db=None,
        current_user=None,
    ):
        user_id = getattr(current_user, "id", opened_by_user_id)
        person = self._resolve_person(capture, payload)
        created_person = person is None
        if person is None:
            person = self.repo.create_person(
                Person(
                    full_name=capture.full_name,
                    phone=capture.phone,
                    notes="Criado a partir de captacao territorial",
                )
            )
            self._audit(db, user_id, "CREATE", "core", "persons", person.id)

        address = None
        has_address_data = capture.district or capture.latitude is not None or capture.longitude is not None
        if payload.create_address and created_person and has_address_data:
            address = self.repo.create_address(
                Address(
                    person_id=person.id,
                    label="Territorial",
                    district=capture.district,
                    latitude=capture.latitude,
                    longitude=capture.longitude,
                )
            )
            self._audit(db, user_id, "CREATE", "core", "addresses", address.id)

        demand = self.repo.create_demand(
            Demand(
                person_id=person.id,
                capture_id=capture.id,
                organization_id=capture.organization_id,
                vereador_id=capture.vereador_id,
                opened_by_user_id=opened_by_user_id,
                assigned_to_user_id=payload.assigned_to_user_id,
                category=payload.category,
                title=payload.title or f"Demanda territorial - {capture.full_name}",
                description=payload.description if payload.description is not None else capture.notes,
                priority=payload.priority,
                due_at=payload.due_at,
            )
        )
        self._audit(db, user_id, "CREATE", "territory", "demands", demand.id)

        old_status = capture.capture_status
        capture = self.repo.update_capture(
            capture,
            {
                "person_id": person.id,
                "capture_status": "CONVERTED_TO_DEMAND",
            },
        )
        self._audit(
            db,
            user_id,
            "CONVERT",
            "territory",
            "contacts_capture",
            capture.id,
            old_values_json=json.dumps({"capture_status": old_status}),
            new_values_json=json.dumps(
                {
                    "person_id": str(person.id),
                    "demand_id": str(demand.id),
                    "capture_status": capture.capture_status,
                }
            ),
        )

        return {
            "capture": capture,
            "person": person,
            "demand": demand,
            "address": address,
            "created_person": created_person,
        }

    def _resolve_person(self, capture: ContactCapture, payload: ContactCaptureConvertDemandRequest):
        if payload.person_id:
            person = self.repo.get_person(payload.person_id)
            if person is None:
                raise LookupError("person_not_found")
            return person
        if capture.person_id:
            person = self.repo.get_person(capture.person_id)
            if person:
                return person
        return self.repo.find_person_by_phone(capture.phone)

    def _scope_for_territory(self, current_user):
        if current_user is None or getattr(current_user, "is_global_admin", False):
            return {}
        if can_access_all_cabinets(current_user):
            return {}
        if can_access_all_polos(current_user):
            return {"operational_polo_only": True}

        organization_ids = scoped_ids(current_user, "GABINETE")
        vereador_ids = scoped_ids(current_user, "VEREADOR")
        polo_ids = scoped_ids(current_user, "POLO")
        if not organization_ids and not vereador_ids and not polo_ids:
            return {"force_empty": True}
        return {
            "organization_ids": organization_ids,
            "vereador_ids": vereador_ids,
            "polo_ids": polo_ids,
        }

    @staticmethod
    def _audit(
        db,
        user_id,
        action: str,
        entity_schema: str,
        entity_name: str,
        entity_id,
        old_values_json=None,
        new_values_json=None,
    ) -> None:
        if db is None:
            return
        write_audit_log(
            db,
            user_id=user_id,
            action=action,
            entity_schema=entity_schema,
            entity_name=entity_name,
            entity_id=entity_id,
            old_values_json=old_values_json,
            new_values_json=new_values_json or json.dumps({"id": str(entity_id)}),
        )
