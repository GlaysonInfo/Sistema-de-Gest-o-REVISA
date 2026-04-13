from datetime import datetime, time

from app.core.audit import audited_mutation
from app.core.access_scope import can_access_all_cabinets, can_access_all_polos, scoped_ids
from app.domain.core.models import Address, Consent, Person, PersonLink
from app.domain.core.repository import CoreRepository
from app.domain.core.schemas import (
    AddressCreate,
    ConsentCreate,
    PersonCreate,
    PersonLinkCreate,
    PersonOperationalSummaryOut,
    PersonTimelineItem,
    PersonTimelineOut,
    PersonUpdate,
)


class CoreService:
    def __init__(self, repo: CoreRepository):
        self.repo = repo

    def list_persons(
        self,
        search: str | None = None,
        cpf: str | None = None,
        phone: str | None = None,
        limit: int = 50,
        offset: int = 0,
        current_user=None,
    ):
        scope = self._scope_for_people(current_user)
        return self.repo.list_persons(search=search, cpf=cpf, phone=phone, limit=limit, offset=offset, **scope)

    def get_person(self, person_id):
        return self.repo.get_person(person_id)

    @audited_mutation(action="CREATE", entity_schema="core", entity_name="persons")
    def create_person(self, payload: PersonCreate, db=None, current_user=None):
        entity = Person(**payload.model_dump())
        return self.repo.create_person(entity)

    @audited_mutation(action="UPDATE", entity_schema="core", entity_name="persons")
    def update_person(self, person: Person, payload: PersonUpdate, db=None, current_user=None):
        return self.repo.update_person(person, payload.model_dump(exclude_unset=True))

    def list_person_addresses(self, person_id):
        return self.repo.list_person_addresses(person_id)

    @audited_mutation(action="CREATE", entity_schema="core", entity_name="addresses")
    def create_person_address(self, person_id, payload: AddressCreate, db=None, current_user=None):
        entity = Address(person_id=person_id, **payload.model_dump())
        return self.repo.create_address(entity)

    def list_person_consents(self, person_id):
        return self.repo.list_person_consents(person_id)

    @audited_mutation(action="CREATE", entity_schema="core", entity_name="consents")
    def create_person_consent(self, person_id, payload: ConsentCreate, db=None, current_user=None):
        values = payload.model_dump()
        if values["granted"] and values["granted_at"] is None:
            values["granted_at"] = datetime.now()
        entity = Consent(
            person_id=person_id,
            captured_by_user_id=getattr(current_user, "id", None),
            **values,
        )
        return self.repo.create_consent(entity)

    def list_person_links(self, person_id):
        return self.repo.list_person_links(person_id)

    @audited_mutation(action="CREATE", entity_schema="core", entity_name="person_links")
    def create_person_link(self, person_id, payload: PersonLinkCreate, db=None, current_user=None):
        entity = PersonLink(person_id=person_id, **payload.model_dump())
        return self.repo.create_person_link(entity)

    def get_operational_summary(self, person):
        graph = self._load_person_operational_graph(person.id)
        return self._build_operational_summary(person, graph)

    def get_person_timeline(self, person):
        graph = self._load_person_operational_graph(person.id)
        summary = self._build_operational_summary(person, graph)
        return PersonTimelineOut(person=person, summary=summary, items=self._build_timeline_items(graph))

    def _load_person_operational_graph(self, person_id):
        demands = self.repo.list_person_demands(person_id)
        demand_ids = [demand.id for demand in demands]
        beneficiarios = self.repo.list_person_beneficiarios(person_id)
        beneficiario_ids = [beneficiario.id for beneficiario in beneficiarios]
        return {
            "captures": self.repo.list_person_captures(person_id),
            "demands": demands,
            "tasks": self.repo.list_person_tasks(person_id, demand_ids=demand_ids),
            "beneficiarios": beneficiarios,
            "frequencias": self.repo.list_beneficiario_frequencias(beneficiario_ids),
            "ocorrencias": self.repo.list_beneficiario_ocorrencias(beneficiario_ids),
        }

    def _build_operational_summary(self, person, graph):
        beneficiario = self._select_current_beneficiario(graph["beneficiarios"])
        polo = self.repo.get_polo(beneficiario.polo_id) if beneficiario else None
        last_attendance = max(graph["frequencias"], key=lambda item: item.activity_date, default=None)
        last_occurrence = max(graph["ocorrencias"], key=lambda item: item.created_at, default=None)
        open_demands = sum(1 for demand in graph["demands"] if demand.status not in {"RESOLVED", "CLOSED", "CANCELLED"})
        open_tasks = sum(1 for task in graph["tasks"] if task.status not in {"DONE", "CANCELLED"})

        if open_demands or open_tasks:
            journey_status = "EM_ACOMPANHAMENTO"
        elif beneficiario and beneficiario.status == "ATIVO":
            journey_status = "EM_POLO"
        elif graph["captures"]:
            journey_status = "CAPTADO"
        else:
            journey_status = "CADASTRADO"

        current_polo = None
        if beneficiario and polo:
            current_polo = {
                "id": polo.id,
                "code": polo.code,
                "address_label": polo.address_label,
                "beneficiary_id": beneficiario.id,
                "beneficiary_status": beneficiario.status,
                "admitted_at": beneficiario.admitted_at,
            }

        return PersonOperationalSummaryOut(
            person=person,
            current_polo=current_polo,
            beneficiary_status=beneficiario.status if beneficiario else None,
            open_demands=open_demands,
            open_tasks=open_tasks,
            last_attendance_at=last_attendance.activity_date if last_attendance else None,
            last_occurrence=self._occurrence_item(last_occurrence) if last_occurrence else None,
            journey_status=journey_status,
        )

    def _build_timeline_items(self, graph):
        items = []
        for capture in graph["captures"]:
            items.append(
                PersonTimelineItem(
                    type="CAPTACAO",
                    id=capture.id,
                    occurred_at=capture.created_at,
                    title=f"Captacao {capture.origin}",
                    status=capture.capture_status,
                    description=capture.notes,
                    metadata_json={
                        "classification": capture.classification,
                        "phone": capture.phone,
                        "district": capture.district,
                        "priority_level": capture.priority_level,
                    },
                )
            )
        for demand in graph["demands"]:
            items.append(
                PersonTimelineItem(
                    type="DEMANDA",
                    id=demand.id,
                    occurred_at=demand.created_at,
                    title=demand.title,
                    status=demand.status,
                    description=demand.description,
                    metadata_json={
                        "category": demand.category,
                        "priority": demand.priority,
                        "capture_id": str(demand.capture_id) if demand.capture_id else None,
                        "due_at": demand.due_at.isoformat() if demand.due_at else None,
                    },
                )
            )
        for task in graph["tasks"]:
            items.append(
                PersonTimelineItem(
                    type="TAREFA",
                    id=task.id,
                    occurred_at=task.created_at,
                    title=task.title,
                    status=task.status,
                    description=task.description,
                    metadata_json={
                        "task_type": task.task_type,
                        "priority": task.priority,
                        "demand_id": str(task.demand_id) if task.demand_id else None,
                        "polo_id": str(task.polo_id) if task.polo_id else None,
                    },
                )
            )
        for beneficiario in graph["beneficiarios"]:
            items.append(
                PersonTimelineItem(
                    type="BENEFICIARIO_POLO",
                    id=beneficiario.id,
                    occurred_at=beneficiario.admitted_at or beneficiario.created_at,
                    title="Vinculo com polo",
                    status=beneficiario.status,
                    metadata_json={
                        "polo_id": str(beneficiario.polo_id),
                        "source_capture_id": str(beneficiario.source_capture_id) if beneficiario.source_capture_id else None,
                        "discharged_at": beneficiario.discharged_at.isoformat() if beneficiario.discharged_at else None,
                    },
                )
            )
        for frequencia in graph["frequencias"]:
            items.append(
                PersonTimelineItem(
                    type="FREQUENCIA",
                    id=frequencia.id,
                    occurred_at=datetime.combine(frequencia.activity_date, time.min),
                    title="Frequencia registrada",
                    status="PRESENTE" if frequencia.present else "AUSENTE",
                    description=frequencia.notes,
                    metadata_json={
                        "beneficiario_id": str(frequencia.beneficiario_id),
                        "modalidade_id": str(frequencia.modalidade_id) if frequencia.modalidade_id else None,
                    },
                )
            )
        for ocorrencia in graph["ocorrencias"]:
            items.append(self._occurrence_item(ocorrencia))
        return sorted(items, key=lambda item: item.occurred_at, reverse=True)

    def _select_current_beneficiario(self, beneficiarios):
        if not beneficiarios:
            return None
        active = [beneficiario for beneficiario in beneficiarios if beneficiario.status == "ATIVO"]
        candidates = active or beneficiarios
        return max(candidates, key=lambda item: item.admitted_at or item.created_at)

    def _occurrence_item(self, ocorrencia):
        return PersonTimelineItem(
            type="OCORRENCIA",
            id=ocorrencia.id,
            occurred_at=ocorrencia.created_at,
            title=ocorrencia.title,
            status=ocorrencia.status,
            description=ocorrencia.description,
            metadata_json={
                "polo_id": str(ocorrencia.polo_id),
                "beneficiario_id": str(ocorrencia.beneficiario_id) if ocorrencia.beneficiario_id else None,
                "severity": ocorrencia.severity,
            },
        )

    def _scope_for_people(self, current_user):
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
