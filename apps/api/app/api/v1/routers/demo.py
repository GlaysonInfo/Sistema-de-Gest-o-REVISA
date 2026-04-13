import json
from datetime import date, datetime

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps.permissions import require_permission
from app.core.database import get_db
from app.domain.core.models import Address, Organization, Person, Vereador
from app.domain.polo.models import Frequencia, Modalidade, Ocorrencia, PoloBeneficiario, PoloUnit
from app.domain.territory.models import ContactCapture, Demand
from app.domain.workflow.models import Task
from app.shared.audit import write_audit_log

router = APIRouter()


DEMO_DOCUMENT = "REVISA-DEMO-POLO"
DEMO_CABINET_DOCUMENT = "REVISA-DEMO-GABINETE"
DEMO_PHONE = "11900000001"
DEMO_VEREADOR_PHONE = "11900000002"
DEMO_CAPTURE_ORIGIN = "WEB_DEMO"
DEMO_TASK_TITLE = "Retorno - Atendimento demo"
DEMO_OCCURRENCE_TITLE = "Ocorrencia de demo"
DEMO_MODALIDADE_NAME = "Futebol"


@router.post("/bootstrap")
def bootstrap_demo(
    current_user = Depends(require_permission("dashboard.admin.read")),
    db: Session = Depends(get_db),
):
    created: list[str] = []

    organization = db.execute(
        select(Organization).where(Organization.document_number == DEMO_DOCUMENT)
    ).scalars().first()
    if organization is None:
        organization = Organization(
            type="POLO",
            name="Organizacao Demo REVISA",
            legal_name="Organizacao Demo REVISA",
            document_number=DEMO_DOCUMENT,
        )
        _add(db, organization)
        _audit(db, current_user.id, "core", "organizations", organization.id)
        created.append("organization")

    gabinete = db.execute(
        select(Organization).where(Organization.document_number == DEMO_CABINET_DOCUMENT)
    ).scalars().first()
    if gabinete is None:
        gabinete = Organization(
            type="GABINETE",
            name="Gabinete Demo REVISA",
            legal_name="Gabinete Demo REVISA",
            document_number=DEMO_CABINET_DOCUMENT,
        )
        _add(db, gabinete)
        _audit(db, current_user.id, "core", "organizations", gabinete.id)
        created.append("cabinet")

    vereador_person = db.execute(select(Person).where(Person.phone == DEMO_VEREADOR_PHONE)).scalars().first()
    if vereador_person is None:
        vereador_person = Person(
            full_name="Vereador Demo",
            phone=DEMO_VEREADOR_PHONE,
            email="vereador.demo@revisa.local",
            notes="Vereador criado pelo bootstrap de demonstracao.",
        )
        _add(db, vereador_person)
        _audit(db, current_user.id, "core", "persons", vereador_person.id)
        created.append("vereador_person")

    vereador = db.execute(select(Vereador).where(Vereador.organization_id == gabinete.id)).scalars().first()
    if vereador is None:
        vereador = Vereador(
            organization_id=gabinete.id,
            person_id=vereador_person.id,
        )
        _add(db, vereador)
        _audit(db, current_user.id, "core", "vereadores", vereador.id)
        created.append("vereador")

    polo = db.execute(select(PoloUnit).where(PoloUnit.organization_id == organization.id)).scalars().first()
    if polo is None:
        polo = PoloUnit(
            organization_id=organization.id,
            vereador_id=vereador.id,
            code="DEMO",
            address_label="Unidade de demonstracao",
        )
        _add(db, polo)
        _audit(db, current_user.id, "polo", "units", polo.id)
        created.append("polo")
    elif polo.vereador_id is None:
        polo.vereador_id = vereador.id
        db.flush()

    person = db.execute(select(Person).where(Person.phone == DEMO_PHONE)).scalars().first()
    if person is None:
        person = Person(
            full_name="Maria Cliente Demo",
            phone=DEMO_PHONE,
            email="maria.demo@revisa.local",
            notes="Pessoa criada pelo bootstrap de demonstracao.",
        )
        _add(db, person)
        _audit(db, current_user.id, "core", "persons", person.id)
        created.append("person")

    address = db.execute(
        select(Address).where(Address.person_id == person.id, Address.label == "Demo")
    ).scalars().first()
    if address is None:
        address = Address(
            person_id=person.id,
            label="Demo",
            district="Centro",
            city="Sao Paulo",
            state="SP",
            zip_code="01001000",
        )
        _add(db, address)
        _audit(db, current_user.id, "core", "addresses", address.id)
        created.append("address")

    capture = db.execute(
        select(ContactCapture).where(
            ContactCapture.origin == DEMO_CAPTURE_ORIGIN,
            ContactCapture.phone == DEMO_PHONE,
        )
    ).scalars().first()
    if capture is None:
        capture = ContactCapture(
            captured_by_user_id=current_user.id,
            organization_id=organization.id,
            vereador_id=vereador.id,
            person_id=person.id,
            origin=DEMO_CAPTURE_ORIGIN,
            classification="DEMANDA",
            full_name=person.full_name,
            phone=person.phone,
            district="Centro",
            notes="Captação criada para demonstracao do fluxo territorial.",
            priority_level="HIGH",
            capture_status="CONVERTED_TO_DEMAND",
        )
        _add(db, capture)
        _audit(db, current_user.id, "territory", "contacts_capture", capture.id)
        created.append("capture")
    else:
        changed = False
        if capture.person_id is None:
            capture.person_id = person.id
            changed = True
        if capture.vereador_id is None:
            capture.vereador_id = vereador.id
            changed = True
        if capture.capture_status != "CONVERTED_TO_DEMAND":
            capture.capture_status = "CONVERTED_TO_DEMAND"
            changed = True
        if changed:
            capture.updated_at = datetime.now()
            db.flush()

    demand = db.execute(
        select(Demand).where(Demand.capture_id == capture.id, Demand.title == "Atendimento demo")
    ).scalars().first()
    if demand is None:
        demand = Demand(
            person_id=person.id,
            capture_id=capture.id,
            organization_id=organization.id,
            vereador_id=vereador.id,
            opened_by_user_id=current_user.id,
            category="ATENDIMENTO",
            title="Atendimento demo",
            description="Demanda criada para demonstracao do fluxo operacional.",
            priority="HIGH",
            status="IN_PROGRESS",
        )
        _add(db, demand)
        _audit(db, current_user.id, "territory", "demands", demand.id)
        created.append("demand")
    else:
        changed = False
        if demand.vereador_id is None:
            demand.vereador_id = vereador.id
            changed = True
        if changed:
            demand.updated_at = datetime.now()
            db.flush()

    task = db.execute(
        select(Task).where(Task.demand_id == demand.id, Task.title == DEMO_TASK_TITLE)
    ).scalars().first()
    if task is None:
        task = Task(
            organization_id=organization.id,
            vereador_id=vereador.id,
            polo_id=polo.id,
            person_id=person.id,
            demand_id=demand.id,
            assigned_to_user_id=current_user.id,
            created_by_user_id=current_user.id,
            task_type="DEMAND_FOLLOW_UP",
            title=DEMO_TASK_TITLE,
            description="Tarefa criada para demonstracao do acompanhamento.",
            priority="HIGH",
            status="OPEN",
        )
        _add(db, task)
        _audit(db, current_user.id, "workflow", "tasks", task.id)
        created.append("task")
    else:
        changed = False
        if task.vereador_id is None:
            task.vereador_id = vereador.id
            changed = True
        if changed:
            task.updated_at = datetime.now()
            db.flush()

    beneficiary = db.execute(
        select(PoloBeneficiario).where(
            PoloBeneficiario.polo_id == polo.id,
            PoloBeneficiario.person_id == person.id,
        )
    ).scalars().first()
    if beneficiary is None:
        beneficiary = PoloBeneficiario(
            polo_id=polo.id,
            person_id=person.id,
            source_capture_id=capture.id,
            status="ATIVO",
            admitted_at=datetime.now(),
        )
        _add(db, beneficiary)
        _audit(db, current_user.id, "polo", "beneficiarios", beneficiary.id)
        created.append("beneficiary")

    modalidade = db.execute(
        select(Modalidade).where(
            Modalidade.polo_id == polo.id,
            Modalidade.name == DEMO_MODALIDADE_NAME,
        )
    ).scalars().first()
    if modalidade is None:
        modalidade = Modalidade(
            polo_id=polo.id,
            name=DEMO_MODALIDADE_NAME,
            description="Modalidade criada para demonstracao do Modulo Polo.",
            active=True,
        )
        _add(db, modalidade)
        _audit(db, current_user.id, "polo", "modalidades", modalidade.id)
        created.append("modalidade")

    attendance = db.execute(
        select(Frequencia).where(
            Frequencia.beneficiario_id == beneficiary.id,
            Frequencia.activity_date == date.today(),
        )
    ).scalars().first()
    if attendance is None:
        attendance = Frequencia(
            beneficiario_id=beneficiary.id,
            modalidade_id=modalidade.id,
            registered_by_user_id=current_user.id,
            activity_date=date.today(),
            present=True,
            notes="Presenca criada no bootstrap de demo.",
        )
        _add(db, attendance)
        _audit(db, current_user.id, "polo", "frequencias", attendance.id)
        created.append("attendance")
    elif attendance.modalidade_id is None:
        attendance.modalidade_id = modalidade.id
        db.flush()

    occurrence = db.execute(
        select(Ocorrencia).where(
            Ocorrencia.polo_id == polo.id,
            Ocorrencia.title == DEMO_OCCURRENCE_TITLE,
        )
    ).scalars().first()
    if occurrence is None:
        occurrence = Ocorrencia(
            polo_id=polo.id,
            beneficiario_id=beneficiary.id,
            registered_by_user_id=current_user.id,
            severity="MEDIUM",
            title=DEMO_OCCURRENCE_TITLE,
            description="Registro criado para demonstracao do painel de polos.",
            status="OPEN",
        )
        _add(db, occurrence)
        _audit(db, current_user.id, "polo", "ocorrencias", occurrence.id)
        created.append("occurrence")

    db.commit()

    return {
        "created": created,
        "organization": _ref(organization),
        "cabinet": _ref(gabinete, name=gabinete.name),
        "vereador": _ref(vereador, person_id=vereador.person_id, full_name=vereador_person.full_name),
        "polo": _ref(polo),
        "person": _ref(person, full_name=person.full_name),
        "address": _ref(address),
        "capture": _ref(capture, status=capture.capture_status, full_name=capture.full_name),
        "demand": _ref(demand, status=demand.status, title=demand.title),
        "task": _ref(task, status=task.status, title=task.title),
        "beneficiary": _ref(beneficiary, status=beneficiary.status),
        "modalidade": _ref(modalidade, name=modalidade.name),
        "attendance": _ref(attendance),
        "occurrence": _ref(occurrence, status=occurrence.status, title=occurrence.title),
    }


def _add(db: Session, entity):
    db.add(entity)
    db.flush()
    db.refresh(entity)


def _audit(db: Session, user_id, entity_schema: str, entity_name: str, entity_id):
    write_audit_log(
        db,
        user_id=user_id,
        action="CREATE",
        entity_schema=entity_schema,
        entity_name=entity_name,
        entity_id=entity_id,
        new_values_json=json.dumps({"id": str(entity_id), "source": "demo_bootstrap"}),
    )


def _ref(entity, **extra):
    payload = {"id": str(entity.id)}
    payload.update(extra)
    return payload
