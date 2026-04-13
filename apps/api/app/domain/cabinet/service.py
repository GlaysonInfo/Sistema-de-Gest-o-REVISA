from app.core.audit import audited_mutation
from app.core.access_scope import can_access_all_cabinets, scoped_ids
from app.domain.cabinet.repository import CabinetRepository
from app.domain.cabinet.schemas import CabinetCreate, CabinetMetrics, CabinetOut, CabinetOverviewOut, VereadorOut
from app.domain.core.models import Organization, Person, Vereador


class CabinetService:
    def __init__(self, repo: CabinetRepository):
        self.repo = repo

    def list_cabinets(self, current_user=None):
        if current_user is None or can_access_all_cabinets(current_user):
            rows = self.repo.list_cabinets()
        else:
            organization_ids = scoped_ids(current_user, "GABINETE")
            vereador_ids = scoped_ids(current_user, "VEREADOR")
            rows = self.repo.list_cabinets(
                organization_ids=organization_ids,
                vereador_ids=vereador_ids,
                force_empty=not organization_ids and not vereador_ids,
            )
        return [self._cabinet_out(*row) for row in rows]

    def get_cabinet(self, organization_id):
        row = self.repo.get_cabinet(organization_id)
        return self._cabinet_out(*row) if row else None

    @audited_mutation(action="CREATE", entity_schema="core", entity_name="organizations")
    def create_cabinet(self, payload: CabinetCreate, db=None, current_user=None):
        existing = self.repo.find_cabinet_by_document(payload.document_number)
        if existing:
            raise ValueError("cabinet_already_exists")

        organization = self.repo.create_organization(
            Organization(
                type="GABINETE",
                name=payload.name,
                legal_name=payload.legal_name,
                document_number=payload.document_number,
            )
        )
        person = self.repo.create_person(
            Person(
                full_name=payload.vereador_full_name,
                phone=payload.vereador_phone,
                email=payload.vereador_email,
                notes="Vereador criado a partir do modulo de gabinete.",
            )
        )
        vereador = self.repo.create_vereador(
            Vereador(
                person_id=person.id,
                organization_id=organization.id,
            )
        )
        return organization

    def get_overview(self, organization_id):
        row = self.repo.get_cabinet(organization_id)
        if row is None:
            raise LookupError("cabinet_not_found")

        organization, vereador, person = row
        captures = self.repo.list_captures(organization.id, vereador.id)
        demands = self.repo.list_demands(organization.id, vereador.id)
        tasks = self.repo.list_tasks(organization.id, vereador.id)
        events = self.repo.list_field_events(organization.id)
        metrics = CabinetMetrics(
            linked_people=self.repo.count_linked_people(organization.id, vereador.id),
            captures=len(captures),
            demands=len(demands),
            open_demands=sum(1 for item in demands if item.status not in {"RESOLVED", "CLOSED", "CANCELLED"}),
            tasks=len(tasks),
            open_tasks=sum(1 for item in tasks if item.status not in {"COMPLETED", "DONE", "CANCELLED"}),
            planned_events=sum(1 for item in events if item.status == "PLANNED"),
        )
        return CabinetOverviewOut(
            cabinet=self._cabinet_out(organization, vereador, person),
            metrics=metrics,
            recent_captures=captures,
            recent_demands=demands,
            recent_tasks=tasks,
            field_events=events,
        )

    def _cabinet_out(self, organization, vereador, person):
        return CabinetOut(
            organization=organization,
            vereador=VereadorOut(
                id=vereador.id,
                person_id=vereador.person_id,
                organization_id=vereador.organization_id,
                active=vereador.active,
                person=person,
            ),
        )
