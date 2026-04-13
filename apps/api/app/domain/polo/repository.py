from datetime import datetime

from sqlalchemy import false, or_, select
from sqlalchemy.orm import Session

from app.domain.core.models import Organization, Person, Vereador
from app.domain.polo.models import Frequencia, Modalidade, ModalityActionPlan, MonthlyReport, Ocorrencia, PoloBeneficiario, PoloUnit
from app.domain.relationship.models import FieldEvent
from app.domain.territory.models import ContactCapture


class PoloRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_polos(self, active: bool | None = None, polo_ids: set[str] | None = None, vereador_ids: set[str] | None = None, force_empty: bool = False):
        statement = select(PoloUnit)
        if active is not None:
            statement = statement.where(PoloUnit.active == active)
        if force_empty:
            statement = statement.where(false())
        else:
            filters = []
            if polo_ids:
                filters.append(PoloUnit.id.in_(polo_ids))
            if vereador_ids:
                filters.append(PoloUnit.vereador_id.in_(vereador_ids))
            if filters:
                statement = statement.where(or_(*filters))
        return self.db.execute(statement.order_by(PoloUnit.created_at.desc())).scalars().all()

    def get_polo(self, polo_id) -> PoloUnit | None:
        return self.db.get(PoloUnit, polo_id)

    def get_polo_by_organization(self, organization_id) -> PoloUnit | None:
        statement = select(PoloUnit).where(PoloUnit.organization_id == organization_id)
        return self.db.execute(statement).scalars().first()

    def get_organization(self, organization_id) -> Organization | None:
        return self.db.get(Organization, organization_id)

    def get_vereador(self, vereador_id) -> Vereador | None:
        return self.db.get(Vereador, vereador_id)

    def create_polo(self, entity: PoloUnit) -> PoloUnit:
        self.db.add(entity)
        self.db.flush()
        self.db.refresh(entity)
        return entity

    def update_polo(self, entity: PoloUnit, values: dict) -> PoloUnit:
        for field, value in values.items():
            setattr(entity, field, value)
        self.db.flush()
        self.db.refresh(entity)
        return entity

    def get_person(self, person_id) -> Person | None:
        return self.db.get(Person, person_id)

    def get_capture(self, capture_id) -> ContactCapture | None:
        return self.db.get(ContactCapture, capture_id)

    def list_beneficiarios(self, polo_id, status: str | None = None):
        statement = select(PoloBeneficiario).where(PoloBeneficiario.polo_id == polo_id)
        if status:
            statement = statement.where(PoloBeneficiario.status == status)
        return self.db.execute(statement.order_by(PoloBeneficiario.created_at.desc())).scalars().all()

    def get_beneficiario(self, beneficiario_id) -> PoloBeneficiario | None:
        return self.db.get(PoloBeneficiario, beneficiario_id)

    def create_beneficiario(self, entity: PoloBeneficiario) -> PoloBeneficiario:
        self.db.add(entity)
        self.db.flush()
        self.db.refresh(entity)
        return entity

    def update_beneficiario(self, entity: PoloBeneficiario, values: dict) -> PoloBeneficiario:
        for field, value in values.items():
            setattr(entity, field, value)
        self.db.flush()
        self.db.refresh(entity)
        return entity

    def list_modalidades(self, polo_id, active: bool | None = None):
        statement = select(Modalidade).where(Modalidade.polo_id == polo_id)
        if active is not None:
            statement = statement.where(Modalidade.active == active)
        return self.db.execute(statement.order_by(Modalidade.created_at.desc())).scalars().all()

    def get_modalidade(self, modalidade_id) -> Modalidade | None:
        return self.db.get(Modalidade, modalidade_id)

    def create_modalidade(self, entity: Modalidade) -> Modalidade:
        self.db.add(entity)
        self.db.flush()
        self.db.refresh(entity)
        return entity

    def update_modalidade(self, entity: Modalidade, values: dict) -> Modalidade:
        for field, value in values.items():
            setattr(entity, field, value)
        self.db.flush()
        self.db.refresh(entity)
        return entity

    def list_frequencias(self, beneficiario_id=None):
        statement = select(Frequencia)
        if beneficiario_id:
            statement = statement.where(Frequencia.beneficiario_id == beneficiario_id)
        return self.db.execute(statement.order_by(Frequencia.created_at.desc())).scalars().all()

    def get_frequencia(self, frequencia_id) -> Frequencia | None:
        return self.db.get(Frequencia, frequencia_id)

    def create_frequencia(self, entity: Frequencia) -> Frequencia:
        self.db.add(entity)
        self.db.flush()
        self.db.refresh(entity)
        return entity

    def update_frequencia(self, entity: Frequencia, values: dict) -> Frequencia:
        for field, value in values.items():
            setattr(entity, field, value)
        self.db.flush()
        self.db.refresh(entity)
        return entity

    def list_ocorrencias(self, polo_id, status: str | None = None, beneficiario_id=None):
        statement = select(Ocorrencia).where(Ocorrencia.polo_id == polo_id)
        if status:
            statement = statement.where(Ocorrencia.status == status)
        if beneficiario_id:
            statement = statement.where(Ocorrencia.beneficiario_id == beneficiario_id)
        return self.db.execute(statement.order_by(Ocorrencia.created_at.desc())).scalars().all()

    def list_field_events(self, polo_id, limit: int = 10):
        statement = (
            select(FieldEvent)
            .where(FieldEvent.polo_id == polo_id)
            .order_by(FieldEvent.event_date.desc(), FieldEvent.created_at.desc())
            .limit(limit)
        )
        return self.db.execute(statement).scalars().all()

    def get_ocorrencia(self, ocorrencia_id) -> Ocorrencia | None:
        return self.db.get(Ocorrencia, ocorrencia_id)

    def create_ocorrencia(self, entity: Ocorrencia) -> Ocorrencia:
        self.db.add(entity)
        self.db.flush()
        self.db.refresh(entity)
        return entity

    def update_ocorrencia(self, entity: Ocorrencia, values: dict) -> Ocorrencia:
        for field, value in values.items():
            setattr(entity, field, value)
        entity.updated_at = datetime.now()
        self.db.flush()
        self.db.refresh(entity)
        return entity

    def list_monthly_reports(self, polo_id=None, status: str | None = None):
        statement = select(MonthlyReport)
        if polo_id is not None:
            statement = statement.where(MonthlyReport.polo_id == polo_id)
        if status:
            statement = statement.where(MonthlyReport.status == status)
        return self.db.execute(statement.order_by(MonthlyReport.reference_month.desc(), MonthlyReport.created_at.desc())).scalars().all()

    def get_monthly_report(self, report_id) -> MonthlyReport | None:
        return self.db.get(MonthlyReport, report_id)

    def create_monthly_report(self, entity: MonthlyReport) -> MonthlyReport:
        self.db.add(entity)
        self.db.flush()
        self.db.refresh(entity)
        return entity

    def update_monthly_report(self, entity: MonthlyReport) -> MonthlyReport:
        entity.updated_at = datetime.now()
        self.db.flush()
        self.db.refresh(entity)
        return entity

    def list_action_plans(self, polo_id, modalidade_id=None, base_year: int | None = None):
        statement = select(ModalityActionPlan).where(ModalityActionPlan.polo_id == polo_id)
        if modalidade_id is not None:
            statement = statement.where(ModalityActionPlan.modalidade_id == modalidade_id)
        if base_year is not None:
            statement = statement.where(ModalityActionPlan.base_year == base_year)
        return self.db.execute(
            statement.order_by(ModalityActionPlan.base_year.desc(), ModalityActionPlan.uploaded_at.desc())
        ).scalars().all()

    def get_action_plan(self, action_plan_id) -> ModalityActionPlan | None:
        return self.db.get(ModalityActionPlan, action_plan_id)

    def create_action_plan(self, entity: ModalityActionPlan) -> ModalityActionPlan:
        self.db.add(entity)
        self.db.flush()
        self.db.refresh(entity)
        return entity
