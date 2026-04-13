from datetime import datetime
from pathlib import Path
from uuid import uuid4

from app.core.audit import audited_mutation
from app.core.access_scope import can_access_all_polos, scoped_ids
from app.core.settings import REPO_ROOT
from app.domain.polo.models import Frequencia, Modalidade, ModalityActionPlan, MonthlyReport, MonthlyReportAttachment, MonthlyReportModality, Ocorrencia, PoloBeneficiario, PoloUnit
from app.domain.polo.repository import PoloRepository
from app.domain.polo.schemas import (
    AttendanceCreate,
    AttendanceUpdate,
    ModalidadeCreate,
    ModalidadeUpdate,
    MonthlyReportBase,
    MonthlyReportCreate,
    MonthlyReportModalityCreate,
    MonthlyReportPreviewOut,
    OccurrenceCreate,
    OccurrenceUpdate,
    PoloOverviewMetrics,
    PoloOverviewOut,
    PoloBeneficiarioCreate,
    PoloBeneficiarioUpdate,
    PoloCreate,
    PoloUpdate,
)


class PoloService:
    def __init__(self, repo: PoloRepository):
        self.repo = repo

    def list_polos(self, active: bool | None = None, current_user=None):
        if current_user is None or getattr(current_user, "is_global_admin", False) or can_access_all_polos(current_user):
            return self.repo.list_polos(active=active)
        polo_ids = scoped_ids(current_user, "POLO")
        vereador_ids = scoped_ids(current_user, "VEREADOR")
        if not polo_ids and not vereador_ids:
            return self.repo.list_polos(active=active, force_empty=True)
        return self.repo.list_polos(active=active, polo_ids=polo_ids, vereador_ids=vereador_ids)

    def get_polo(self, polo_id):
        return self.repo.get_polo(polo_id)

    def get_overview(self, polo_id):
        polo = self._ensure_polo(polo_id)
        beneficiaries = self.repo.list_beneficiarios(polo_id)
        beneficiario_ids = {beneficiario.id for beneficiario in beneficiaries}
        attendances = [
            frequencia
            for frequencia in self.repo.list_frequencias()
            if frequencia.beneficiario_id in beneficiario_ids
        ]
        occurrences = self.repo.list_ocorrencias(polo_id)
        field_events = self.repo.list_field_events(polo_id)

        metrics = PoloOverviewMetrics(
            total_beneficiarios=len(beneficiaries),
            active_beneficiarios=sum(1 for item in beneficiaries if item.status == "ATIVO"),
            pre_registered_beneficiarios=sum(1 for item in beneficiaries if item.status == "PRE_CADASTRADO"),
            attendance_records=len(attendances),
            present_records=sum(1 for item in attendances if item.present),
            absent_records=sum(1 for item in attendances if not item.present),
            open_occurrences=sum(1 for item in occurrences if item.status == "OPEN"),
            closed_occurrences=sum(1 for item in occurrences if item.status == "CLOSED"),
            planned_events=sum(1 for item in field_events if item.status == "PLANNED"),
        )

        return PoloOverviewOut(
            polo=polo,
            metrics=metrics,
            beneficiaries=beneficiaries[:20],
            recent_attendances=attendances[:20],
            recent_occurrences=occurrences[:20],
            field_events=field_events,
        )

    @audited_mutation(action="CREATE", entity_schema="polo", entity_name="units")
    def create_polo(self, payload: PoloCreate, db=None, current_user=None):
        if self.repo.get_organization(payload.organization_id) is None:
            raise LookupError("organization_not_found")
        if self.repo.get_vereador(payload.vereador_id) is None:
            raise LookupError("vereador_not_found")
        if self.repo.get_polo_by_organization(payload.organization_id) is not None:
            raise ValueError("polo_already_exists")
        return self.repo.create_polo(PoloUnit(**payload.model_dump()))

    @audited_mutation(action="UPDATE", entity_schema="polo", entity_name="units")
    def update_polo(self, polo: PoloUnit, payload: PoloUpdate, db=None, current_user=None):
        if payload.vereador_id is not None and self.repo.get_vereador(payload.vereador_id) is None:
            raise LookupError("vereador_not_found")
        return self.repo.update_polo(polo, payload.model_dump(exclude_unset=True))

    def list_beneficiarios(self, polo_id, status: str | None = None):
        return self.repo.list_beneficiarios(polo_id, status=status)

    def get_beneficiario(self, beneficiario_id):
        return self.repo.get_beneficiario(beneficiario_id)

    @audited_mutation(action="CREATE", entity_schema="polo", entity_name="beneficiarios")
    def create_beneficiario(self, polo_id, payload: PoloBeneficiarioCreate, db=None, current_user=None):
        self._ensure_polo(polo_id)
        self._ensure_person(payload.person_id)
        if payload.source_capture_id is not None:
            self._ensure_capture(payload.source_capture_id)
        entity = PoloBeneficiario(
            polo_id=polo_id,
            person_id=payload.person_id,
            source_capture_id=payload.source_capture_id,
            status=payload.status,
            admitted_at=payload.admitted_at,
        )
        return self.repo.create_beneficiario(entity)

    @audited_mutation(action="UPDATE", entity_schema="polo", entity_name="beneficiarios")
    def update_beneficiario(self, beneficiario: PoloBeneficiario, payload: PoloBeneficiarioUpdate, db=None, current_user=None):
        if payload.source_capture_id is not None:
            self._ensure_capture(payload.source_capture_id)
        return self.repo.update_beneficiario(beneficiario, payload.model_dump(exclude_unset=True))

    def list_modalidades(self, polo_id, active: bool | None = None):
        self._ensure_polo(polo_id)
        return self.repo.list_modalidades(polo_id, active=active)

    def get_modalidade(self, modalidade_id):
        return self.repo.get_modalidade(modalidade_id)

    @audited_mutation(action="CREATE", entity_schema="polo", entity_name="modalidades")
    def create_modalidade(self, polo_id, payload: ModalidadeCreate, db=None, current_user=None):
        self._ensure_polo(polo_id)
        entity = Modalidade(
            polo_id=polo_id,
            name=payload.name,
            description=payload.description,
            active=payload.active,
        )
        return self.repo.create_modalidade(entity)

    @audited_mutation(action="UPDATE", entity_schema="polo", entity_name="modalidades")
    def update_modalidade(self, polo_id, modalidade: Modalidade, payload: ModalidadeUpdate, db=None, current_user=None):
        self._ensure_modalidade_in_polo(polo_id, modalidade.id)
        return self.repo.update_modalidade(modalidade, payload.model_dump(exclude_unset=True))

    def list_frequencias(self, polo_id, beneficiario_id=None):
        self._ensure_polo(polo_id)
        if beneficiario_id is not None:
            self._ensure_beneficiario_in_polo(polo_id, beneficiario_id)
            return self.repo.list_frequencias(beneficiario_id=beneficiario_id)
        beneficiarios = self.repo.list_beneficiarios(polo_id)
        beneficiario_ids = {beneficiario.id for beneficiario in beneficiarios}
        return [
            frequencia
            for frequencia in self.repo.list_frequencias()
            if frequencia.beneficiario_id in beneficiario_ids
        ]

    def get_frequencia(self, frequencia_id):
        return self.repo.get_frequencia(frequencia_id)

    @audited_mutation(action="CREATE", entity_schema="polo", entity_name="frequencias")
    def register_attendance(self, polo_id, registered_by_user_id, payload: AttendanceCreate, db=None, current_user=None):
        self._ensure_beneficiario_in_polo(polo_id, payload.beneficiario_id)
        if payload.modalidade_id is not None:
            self._ensure_modalidade_in_polo(polo_id, payload.modalidade_id)
        entity = Frequencia(
            beneficiario_id=payload.beneficiario_id,
            modalidade_id=payload.modalidade_id,
            registered_by_user_id=registered_by_user_id,
            activity_date=payload.activity_date,
            present=payload.present,
            notes=payload.notes,
        )
        return self.repo.create_frequencia(entity)

    @audited_mutation(action="UPDATE", entity_schema="polo", entity_name="frequencias")
    def update_attendance(self, polo_id, frequencia: Frequencia, payload: AttendanceUpdate, db=None, current_user=None):
        if payload.modalidade_id is not None:
            self._ensure_modalidade_in_polo(polo_id, payload.modalidade_id)
        return self.repo.update_frequencia(frequencia, payload.model_dump(exclude_unset=True))

    def list_ocorrencias(self, polo_id, status: str | None = None, beneficiario_id=None):
        self._ensure_polo(polo_id)
        if beneficiario_id is not None:
            self._ensure_beneficiario_in_polo(polo_id, beneficiario_id)
        return self.repo.list_ocorrencias(polo_id, status=status, beneficiario_id=beneficiario_id)

    def get_ocorrencia(self, ocorrencia_id):
        return self.repo.get_ocorrencia(ocorrencia_id)

    @audited_mutation(action="CREATE", entity_schema="polo", entity_name="ocorrencias")
    def create_ocorrencia(self, polo_id, registered_by_user_id, payload: OccurrenceCreate, db=None, current_user=None):
        self._ensure_polo(polo_id)
        if payload.beneficiario_id is not None:
            self._ensure_beneficiario_in_polo(polo_id, payload.beneficiario_id)
        entity = Ocorrencia(
            polo_id=polo_id,
            beneficiario_id=payload.beneficiario_id,
            registered_by_user_id=registered_by_user_id,
            severity=payload.severity,
            title=payload.title,
            description=payload.description,
            status=payload.status,
        )
        return self.repo.create_ocorrencia(entity)

    @audited_mutation(action="UPDATE", entity_schema="polo", entity_name="ocorrencias")
    def update_ocorrencia(self, polo_id, ocorrencia: Ocorrencia, payload: OccurrenceUpdate, db=None, current_user=None):
        if payload.beneficiario_id is not None:
            self._ensure_beneficiario_in_polo(polo_id, payload.beneficiario_id)
        return self.repo.update_ocorrencia(ocorrencia, payload.model_dump(exclude_unset=True))

    def list_monthly_reports(self, polo_id=None, status: str | None = None):
        if polo_id is not None:
            self._ensure_polo(polo_id)
        return self.repo.list_monthly_reports(polo_id=polo_id, status=status)

    def get_monthly_report(self, report_id):
        return self.repo.get_monthly_report(report_id)

    def preview_monthly_report(self, polo_id, payload: MonthlyReportBase):
        polo = self._ensure_polo(polo_id)
        self._ensure_report_modalities_in_polo(polo_id, payload.modalities)
        narrative = self._build_monthly_report_text(polo, payload)
        return MonthlyReportPreviewOut(
            narrative_text=narrative,
            active_modalities_count=sum(1 for item in payload.modalities if item.active),
            total_beneficiaries=sum(item.beneficiaries_count for item in payload.modalities),
        )

    @audited_mutation(action="CREATE", entity_schema="polo", entity_name="monthly_reports")
    def create_monthly_report(self, polo_id, created_by_user_id, payload: MonthlyReportCreate, db=None, current_user=None):
        polo = self._ensure_polo(polo_id)
        self._ensure_report_modalities_in_polo(polo_id, payload.modalities)
        base_payload = MonthlyReportBase(
            reference_month=payload.reference_month,
            occurrence_summary=payload.occurrence_summary,
            notes=payload.notes,
            modalities=payload.modalities,
        )
        narrative = payload.narrative_text or self._build_monthly_report_text(polo, base_payload)
        entity = MonthlyReport(
            polo_id=polo_id,
            vereador_id=polo.vereador_id,
            created_by_user_id=created_by_user_id,
            reference_month=payload.reference_month,
            submitted_at=datetime.now(),
            status=payload.status,
            active_modalities_count=sum(1 for item in payload.modalities if item.active),
            total_beneficiaries=sum(item.beneficiaries_count for item in payload.modalities),
            occurrence_summary=payload.occurrence_summary,
            narrative_text=narrative,
            notes=payload.notes,
            modalities=[
                MonthlyReportModality(
                    modalidade_id=item.modalidade_id,
                    modalidade_name=item.modalidade_name,
                    active=item.active,
                    beneficiaries_count=item.beneficiaries_count,
                    notes=item.notes,
                )
                for item in payload.modalities
            ],
        )
        return self.repo.create_monthly_report(entity)

    def attach_monthly_report_file(
        self,
        polo_id,
        report_id,
        attachment_type: str,
        filename: str,
        content_type: str | None,
        content: bytes,
        modalidade_id=None,
        description: str | None = None,
    ):
        self._ensure_polo(polo_id)
        report = self.repo.get_monthly_report(report_id)
        if report is None:
            raise LookupError("monthly_report_not_found")
        if str(report.polo_id) != str(polo_id):
            raise PermissionError("monthly_report_out_of_polo")
        if modalidade_id is not None:
            self._ensure_modalidade_in_polo(polo_id, modalidade_id)
        if not content:
            raise ValueError("empty_attachment")
        safe_filename = Path(filename or "arquivo").name.replace("\\", "_").replace("/", "_")
        storage_dir = REPO_ROOT / "storage" / "monthly_reports" / str(report.id)
        storage_dir.mkdir(parents=True, exist_ok=True)
        stored_name = f"{uuid4()}-{safe_filename}"
        stored_path = storage_dir / stored_name
        stored_path.write_bytes(content)
        attachment = MonthlyReportAttachment(
            monthly_report_id=report.id,
            modalidade_id=modalidade_id,
            attachment_type=attachment_type,
            original_filename=safe_filename,
            stored_path=str(stored_path.relative_to(REPO_ROOT)),
            content_type=content_type,
            file_size=len(content),
            description=description,
        )
        report.attachments.append(attachment)
        return self.repo.update_monthly_report(report)

    def list_action_plans(self, polo_id, modalidade_id=None, base_year: int | None = None):
        self._ensure_polo(polo_id)
        if modalidade_id is not None:
            self._ensure_modalidade_in_polo(polo_id, modalidade_id)
        return self.repo.list_action_plans(polo_id=polo_id, modalidade_id=modalidade_id, base_year=base_year)

    def get_action_plan(self, action_plan_id):
        return self.repo.get_action_plan(action_plan_id)

    def attach_action_plan_file(
        self,
        polo_id,
        modalidade_id,
        uploaded_by_user_id,
        base_year: int,
        title: str | None,
        professional_name: str | None,
        filename: str,
        content_type: str | None,
        content: bytes,
        notes: str | None = None,
    ):
        self._ensure_polo(polo_id)
        modalidade = self._ensure_modalidade_in_polo(polo_id, modalidade_id)
        if not modalidade.active:
            raise ValueError("modalidade_inactive")
        if not content:
            raise ValueError("empty_action_plan")

        safe_filename = Path(filename or "plano-de-acao").name.replace("\\", "_").replace("/", "_")
        plan_title = title or f"Plano de Acao {modalidade.name} - Ano Base {base_year}"
        storage_dir = REPO_ROOT / "storage" / "action_plans" / str(polo_id) / str(base_year)
        storage_dir.mkdir(parents=True, exist_ok=True)
        stored_name = f"{uuid4()}-{safe_filename}"
        stored_path = storage_dir / stored_name
        stored_path.write_bytes(content)

        entity = ModalityActionPlan(
            polo_id=polo_id,
            modalidade_id=modalidade_id,
            uploaded_by_user_id=uploaded_by_user_id,
            base_year=base_year,
            title=plan_title,
            professional_name=professional_name,
            original_filename=safe_filename,
            stored_path=str(stored_path.relative_to(REPO_ROOT)),
            content_type=content_type,
            file_size=len(content),
            status="SUBMITTED",
            notes=notes,
        )
        return self.repo.create_action_plan(entity)

    def _ensure_polo(self, polo_id):
        polo = self.repo.get_polo(polo_id)
        if polo is None:
            raise LookupError("polo_not_found")
        return polo

    def _ensure_person(self, person_id):
        person = self.repo.get_person(person_id)
        if person is None:
            raise LookupError("person_not_found")
        return person

    def _ensure_capture(self, capture_id):
        capture = self.repo.get_capture(capture_id)
        if capture is None:
            raise LookupError("capture_not_found")
        return capture

    def _ensure_beneficiario_in_polo(self, polo_id, beneficiario_id):
        beneficiario = self.repo.get_beneficiario(beneficiario_id)
        if beneficiario is None:
            raise LookupError("beneficiario_not_found")
        if str(beneficiario.polo_id) != str(polo_id):
            raise PermissionError("beneficiario_out_of_polo")
        return beneficiario

    def _ensure_modalidade_in_polo(self, polo_id, modalidade_id):
        modalidade = self.repo.get_modalidade(modalidade_id)
        if modalidade is None:
            raise LookupError("modalidade_not_found")
        if str(modalidade.polo_id) != str(polo_id):
            raise PermissionError("modalidade_out_of_polo")
        return modalidade

    def _ensure_report_modalities_in_polo(self, polo_id, modalities: list[MonthlyReportModalityCreate]):
        for item in modalities:
            if item.modalidade_id is not None:
                self._ensure_modalidade_in_polo(polo_id, item.modalidade_id)

    @staticmethod
    def _build_monthly_report_text(polo: PoloUnit, payload: MonthlyReportBase):
        month_label = payload.reference_month.strftime("%m/%Y")
        active = [item for item in payload.modalities if item.active]
        inactive = [item for item in payload.modalities if not item.active]
        lines = [
            f"RELATORIO MENSAL - POLO {polo.code or polo.id} - COMPETENCIA {month_label}",
            "",
            f"No periodo de referencia, o Polo registrou {len(active)} modalidade(s) ativa(s) e {sum(item.beneficiaries_count for item in payload.modalities)} beneficiario(s) informado(s) no consolidado por modalidade.",
            "",
            "Modalidades ativas:",
        ]
        if active:
            for item in active:
                note = f" Observacao: {item.notes}" if item.notes else ""
                lines.append(f"- {item.modalidade_name}: {item.beneficiaries_count} beneficiario(s).{note}")
        else:
            lines.append("- Nenhuma modalidade ativa informada.")
        if inactive:
            lines.extend(["", "Modalidades sem atividade no mes:"])
            for item in inactive:
                note = f" Motivo/observacao: {item.notes}" if item.notes else ""
                lines.append(f"- {item.modalidade_name}.{note}")
        lines.extend([
            "",
            "Ocorrencias e fatos relevantes:",
            payload.occurrence_summary or "Nao foram informadas ocorrencias relevantes no mes.",
            "",
            "Anexos obrigatorios e comprobatorios:",
            "O administrador do Polo declarou anexar as listas de presenca, o acervo fotografico das modalidades ativas e os demais documentos necessarios a comprovacao de atividades, despesas, afastamentos ou justificativas do periodo.",
        ])
        if payload.notes:
            lines.extend(["", "Observacoes adicionais:", payload.notes])
        return "\n".join(lines)
