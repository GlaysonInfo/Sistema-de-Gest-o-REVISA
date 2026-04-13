from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.deps.permissions import require_permission
from app.api.deps.scope import ensure_scope
from app.core.database import get_db
from app.domain.polo.repository import PoloRepository
from app.domain.polo.schemas import (
    AttendanceCreate,
    AttendanceOut,
    AttendanceUpdate,
    ModalidadeCreate,
    ModalidadeOut,
    ModalidadeUpdate,
    ModalityActionPlanOut,
    MonthlyReportBase,
    MonthlyReportCreate,
    MonthlyReportOut,
    MonthlyReportPreviewOut,
    OccurrenceCreate,
    OccurrenceOut,
    OccurrenceUpdate,
    PoloBeneficiarioCreate,
    PoloBeneficiarioOut,
    PoloBeneficiarioUpdate,
    PoloCreate,
    PoloOverviewOut,
    PoloOut,
    PoloUpdate,
)
from app.domain.polo.service import PoloService

router = APIRouter()


def _service(db: Session) -> PoloService:
    return PoloService(PoloRepository(db))


def _handle_domain_error(exc: Exception):
    detail_by_code = {
        "organization_not_found": "Organizacao nao encontrada",
        "vereador_not_found": "Vereador nao encontrado",
        "polo_not_found": "Polo nao encontrado",
        "person_not_found": "Pessoa nao encontrada",
        "capture_not_found": "Captacao nao encontrada",
        "beneficiario_not_found": "Beneficiario nao encontrado",
        "modalidade_not_found": "Modalidade nao encontrada",
        "action_plan_not_found": "Plano de acao nao encontrado",
        "monthly_report_not_found": "Relatorio mensal nao encontrado",
    }
    if isinstance(exc, ValueError) and str(exc) == "empty_attachment":
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Anexo vazio")
    if isinstance(exc, ValueError) and str(exc) == "empty_action_plan":
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Plano de acao vazio")
    if isinstance(exc, ValueError) and str(exc) == "modalidade_inactive":
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Plano de acao deve ser vinculado a uma modalidade ativa")
    if isinstance(exc, PermissionError) and str(exc) == "monthly_report_out_of_polo":
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Relatorio mensal fora do polo")
    if isinstance(exc, PermissionError) and str(exc) == "action_plan_out_of_polo":
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Plano de acao fora do polo")
    if isinstance(exc, PermissionError) and str(exc) == "modalidade_out_of_polo":
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Modalidade fora do polo")
    if isinstance(exc, PermissionError):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Beneficiario fora do polo")
    if isinstance(exc, ValueError) and str(exc) == "polo_already_exists":
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Polo ja existe para esta organizacao")
    if isinstance(exc, IntegrityError):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Registro duplicado")
    if isinstance(exc, LookupError):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail_by_code.get(str(exc), "Registro nao encontrado"))
    raise exc


def _get_polo_or_404(service: PoloService, polo_id: UUID):
    polo = service.get_polo(polo_id)
    if polo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Polo nao encontrado")
    return polo


def _get_beneficiario_or_404(service: PoloService, polo_id: UUID, beneficiario_id: UUID):
    beneficiario = service.get_beneficiario(beneficiario_id)
    if beneficiario is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Beneficiario nao encontrado")
    if str(beneficiario.polo_id) != str(polo_id):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Beneficiario fora do polo")
    return beneficiario


def _get_frequencia_or_404(service: PoloService, polo_id: UUID, frequencia_id: UUID):
    frequencia = service.get_frequencia(frequencia_id)
    if frequencia is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Frequencia nao encontrada")
    beneficiario = _get_beneficiario_or_404(service, polo_id, frequencia.beneficiario_id)
    if str(beneficiario.polo_id) != str(polo_id):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Frequencia fora do polo")
    return frequencia


def _get_modalidade_or_404(service: PoloService, polo_id: UUID, modalidade_id: UUID):
    modalidade = service.get_modalidade(modalidade_id)
    if modalidade is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Modalidade nao encontrada")
    if str(modalidade.polo_id) != str(polo_id):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Modalidade fora do polo")
    return modalidade


def _get_ocorrencia_or_404(service: PoloService, polo_id: UUID, ocorrencia_id: UUID):
    ocorrencia = service.get_ocorrencia(ocorrencia_id)
    if ocorrencia is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ocorrencia nao encontrada")
    if str(ocorrencia.polo_id) != str(polo_id):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Ocorrencia fora do polo")
    return ocorrencia


def _get_monthly_report_or_404(service: PoloService, polo_id: UUID, report_id: UUID):
    report = service.get_monthly_report(report_id)
    if report is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Relatorio mensal nao encontrado")
    if str(report.polo_id) != str(polo_id):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Relatorio mensal fora do polo")
    return report


def _get_action_plan_or_404(service: PoloService, polo_id: UUID, action_plan_id: UUID):
    action_plan = service.get_action_plan(action_plan_id)
    if action_plan is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plano de acao nao encontrado")
    if str(action_plan.polo_id) != str(polo_id):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Plano de acao fora do polo")
    return action_plan


@router.get("", response_model=list[PoloOut])
def list_polos(
    active: bool | None = None,
    current_user = Depends(require_permission("polo.read")),
    db: Session = Depends(get_db),
):
    return _service(db).list_polos(active=active, current_user=current_user)


@router.post("", response_model=PoloOut, status_code=201)
def create_polo(
    payload: PoloCreate,
    current_user = Depends(require_permission("polo.create")),
    db: Session = Depends(get_db),
):
    try:
        result = _service(db).create_polo(payload, db=db, current_user=current_user)
    except Exception as exc:
        _handle_domain_error(exc)
    db.commit()
    return result


@router.get("/{polo_id}/monthly-reports", response_model=list[MonthlyReportOut])
def list_monthly_reports(
    polo_id: UUID,
    status_filter: str | None = Query(default=None, alias="status"),
    current_user = Depends(require_permission("polo.read")),
    db: Session = Depends(get_db),
):
    ensure_scope(current_user, "POLO", str(polo_id))
    try:
        return _service(db).list_monthly_reports(polo_id=polo_id, status=status_filter)
    except Exception as exc:
        _handle_domain_error(exc)


@router.post("/{polo_id}/monthly-reports/preview", response_model=MonthlyReportPreviewOut)
def preview_monthly_report(
    polo_id: UUID,
    payload: MonthlyReportBase,
    current_user = Depends(require_permission("polo.read")),
    db: Session = Depends(get_db),
):
    ensure_scope(current_user, "POLO", str(polo_id))
    try:
        return _service(db).preview_monthly_report(polo_id, payload)
    except Exception as exc:
        _handle_domain_error(exc)


@router.post("/{polo_id}/monthly-reports", response_model=MonthlyReportOut, status_code=201)
def create_monthly_report(
    polo_id: UUID,
    payload: MonthlyReportCreate,
    current_user = Depends(require_permission("polo.manage_beneficiary")),
    db: Session = Depends(get_db),
):
    ensure_scope(current_user, "POLO", str(polo_id))
    try:
        result = _service(db).create_monthly_report(polo_id, current_user.id, payload, db=db, current_user=current_user)
    except Exception as exc:
        _handle_domain_error(exc)
    db.commit()
    return result


@router.get("/{polo_id}/monthly-reports/{report_id}", response_model=MonthlyReportOut)
def get_monthly_report(
    polo_id: UUID,
    report_id: UUID,
    current_user = Depends(require_permission("polo.read")),
    db: Session = Depends(get_db),
):
    ensure_scope(current_user, "POLO", str(polo_id))
    return _get_monthly_report_or_404(_service(db), polo_id, report_id)


@router.post("/{polo_id}/monthly-reports/{report_id}/attachments", response_model=MonthlyReportOut)
async def upload_monthly_report_attachment(
    polo_id: UUID,
    report_id: UUID,
    attachment_type: str = Form(...),
    modalidade_id: UUID | None = Form(default=None),
    description: str | None = Form(default=None),
    files: list[UploadFile] = File(...),
    current_user = Depends(require_permission("polo.manage_beneficiary")),
    db: Session = Depends(get_db),
):
    ensure_scope(current_user, "POLO", str(polo_id))
    service = _service(db)
    result = _get_monthly_report_or_404(service, polo_id, report_id)
    try:
        for file in files:
            result = service.attach_monthly_report_file(
                polo_id=polo_id,
                report_id=report_id,
                attachment_type=attachment_type,
                filename=file.filename or "arquivo",
                content_type=file.content_type,
                content=await file.read(),
                modalidade_id=modalidade_id,
                description=description,
            )
    except Exception as exc:
        _handle_domain_error(exc)
    db.commit()
    return result


@router.get("/{polo_id}/action-plans", response_model=list[ModalityActionPlanOut])
def list_action_plans(
    polo_id: UUID,
    modalidade_id: UUID | None = None,
    base_year: int | None = None,
    current_user = Depends(require_permission("polo.read")),
    db: Session = Depends(get_db),
):
    ensure_scope(current_user, "POLO", str(polo_id))
    try:
        return _service(db).list_action_plans(polo_id=polo_id, modalidade_id=modalidade_id, base_year=base_year)
    except Exception as exc:
        _handle_domain_error(exc)


@router.get("/{polo_id}/action-plans/{action_plan_id}", response_model=ModalityActionPlanOut)
def get_action_plan(
    polo_id: UUID,
    action_plan_id: UUID,
    current_user = Depends(require_permission("polo.read")),
    db: Session = Depends(get_db),
):
    ensure_scope(current_user, "POLO", str(polo_id))
    return _get_action_plan_or_404(_service(db), polo_id, action_plan_id)


@router.post("/{polo_id}/modalidades/{modalidade_id}/action-plans", response_model=ModalityActionPlanOut, status_code=201)
async def upload_action_plan(
    polo_id: UUID,
    modalidade_id: UUID,
    base_year: int = Form(...),
    title: str | None = Form(default=None),
    professional_name: str | None = Form(default=None),
    notes: str | None = Form(default=None),
    file: UploadFile = File(...),
    current_user = Depends(require_permission("polo.manage_beneficiary")),
    db: Session = Depends(get_db),
):
    ensure_scope(current_user, "POLO", str(polo_id))
    try:
        result = _service(db).attach_action_plan_file(
            polo_id=polo_id,
            modalidade_id=modalidade_id,
            uploaded_by_user_id=current_user.id,
            base_year=base_year,
            title=title,
            professional_name=professional_name,
            filename=file.filename or "plano-de-acao",
            content_type=file.content_type,
            content=await file.read(),
            notes=notes,
        )
    except Exception as exc:
        _handle_domain_error(exc)
    db.commit()
    return result


@router.get("/{polo_id}", response_model=PoloOut)
def get_polo(
    polo_id: UUID,
    current_user = Depends(require_permission("polo.read")),
    db: Session = Depends(get_db),
):
    ensure_scope(current_user, "POLO", str(polo_id))
    return _get_polo_or_404(_service(db), polo_id)


@router.patch("/{polo_id}", response_model=PoloOut)
def update_polo(
    polo_id: UUID,
    payload: PoloUpdate,
    current_user = Depends(require_permission("polo.update")),
    db: Session = Depends(get_db),
):
    ensure_scope(current_user, "POLO", str(polo_id))
    service = _service(db)
    polo = _get_polo_or_404(service, polo_id)
    result = service.update_polo(polo, payload, db=db, current_user=current_user)
    db.commit()
    return result


@router.get("/{polo_id}/overview", response_model=PoloOverviewOut)
def get_polo_overview(
    polo_id: UUID,
    current_user = Depends(require_permission("polo.read")),
    db: Session = Depends(get_db),
):
    ensure_scope(current_user, "POLO", str(polo_id))
    try:
        return _service(db).get_overview(polo_id)
    except Exception as exc:
        _handle_domain_error(exc)


@router.get("/{polo_id}/beneficiarios", response_model=list[PoloBeneficiarioOut])
def list_beneficiarios(
    polo_id: UUID,
    status_filter: str | None = Query(default=None, alias="status"),
    current_user = Depends(require_permission("polo.manage_beneficiary")),
    db: Session = Depends(get_db),
):
    ensure_scope(current_user, "POLO", str(polo_id))
    return _service(db).list_beneficiarios(polo_id, status=status_filter)


@router.post("/{polo_id}/beneficiarios", response_model=PoloBeneficiarioOut, status_code=201)
def create_beneficiario(
    polo_id: UUID,
    payload: PoloBeneficiarioCreate,
    current_user = Depends(require_permission("polo.manage_beneficiary")),
    db: Session = Depends(get_db),
):
    ensure_scope(current_user, "POLO", str(polo_id))
    try:
        result = _service(db).create_beneficiario(polo_id, payload, db=db, current_user=current_user)
    except Exception as exc:
        _handle_domain_error(exc)
    db.commit()
    return result


@router.get("/{polo_id}/beneficiarios/{beneficiario_id}", response_model=PoloBeneficiarioOut)
def get_beneficiario(
    polo_id: UUID,
    beneficiario_id: UUID,
    current_user = Depends(require_permission("polo.manage_beneficiary")),
    db: Session = Depends(get_db),
):
    ensure_scope(current_user, "POLO", str(polo_id))
    return _get_beneficiario_or_404(_service(db), polo_id, beneficiario_id)


@router.patch("/{polo_id}/beneficiarios/{beneficiario_id}", response_model=PoloBeneficiarioOut)
def update_beneficiario(
    polo_id: UUID,
    beneficiario_id: UUID,
    payload: PoloBeneficiarioUpdate,
    current_user = Depends(require_permission("polo.manage_beneficiary")),
    db: Session = Depends(get_db),
):
    ensure_scope(current_user, "POLO", str(polo_id))
    service = _service(db)
    beneficiario = _get_beneficiario_or_404(service, polo_id, beneficiario_id)
    try:
        result = service.update_beneficiario(beneficiario, payload, db=db, current_user=current_user)
    except Exception as exc:
        _handle_domain_error(exc)
    db.commit()
    return result


@router.get("/{polo_id}/modalidades", response_model=list[ModalidadeOut])
def list_modalidades(
    polo_id: UUID,
    active: bool | None = None,
    current_user = Depends(require_permission("polo.read")),
    db: Session = Depends(get_db),
):
    ensure_scope(current_user, "POLO", str(polo_id))
    try:
        return _service(db).list_modalidades(polo_id, active=active)
    except Exception as exc:
        _handle_domain_error(exc)


@router.post("/{polo_id}/modalidades", response_model=ModalidadeOut, status_code=201)
def create_modalidade(
    polo_id: UUID,
    payload: ModalidadeCreate,
    current_user = Depends(require_permission("polo.manage_beneficiary")),
    db: Session = Depends(get_db),
):
    ensure_scope(current_user, "POLO", str(polo_id))
    try:
        result = _service(db).create_modalidade(polo_id, payload, db=db, current_user=current_user)
    except Exception as exc:
        _handle_domain_error(exc)
    db.commit()
    return result


@router.get("/{polo_id}/modalidades/{modalidade_id}", response_model=ModalidadeOut)
def get_modalidade(
    polo_id: UUID,
    modalidade_id: UUID,
    current_user = Depends(require_permission("polo.read")),
    db: Session = Depends(get_db),
):
    ensure_scope(current_user, "POLO", str(polo_id))
    return _get_modalidade_or_404(_service(db), polo_id, modalidade_id)


@router.patch("/{polo_id}/modalidades/{modalidade_id}", response_model=ModalidadeOut)
def update_modalidade(
    polo_id: UUID,
    modalidade_id: UUID,
    payload: ModalidadeUpdate,
    current_user = Depends(require_permission("polo.manage_beneficiary")),
    db: Session = Depends(get_db),
):
    ensure_scope(current_user, "POLO", str(polo_id))
    service = _service(db)
    modalidade = _get_modalidade_or_404(service, polo_id, modalidade_id)
    try:
        result = service.update_modalidade(polo_id, modalidade, payload, db=db, current_user=current_user)
    except Exception as exc:
        _handle_domain_error(exc)
    db.commit()
    return result


@router.get("/{polo_id}/frequencias", response_model=list[AttendanceOut])
def list_frequencias(
    polo_id: UUID,
    beneficiario_id: UUID | None = None,
    current_user = Depends(require_permission("attendance.read")),
    db: Session = Depends(get_db),
):
    ensure_scope(current_user, "POLO", str(polo_id))
    try:
        return _service(db).list_frequencias(polo_id, beneficiario_id=beneficiario_id)
    except Exception as exc:
        _handle_domain_error(exc)


@router.post("/{polo_id}/frequencias", response_model=AttendanceOut, status_code=201)
def register_attendance(
    polo_id: UUID,
    payload: AttendanceCreate,
    current_user = Depends(require_permission("attendance.create")),
    db: Session = Depends(get_db),
):
    ensure_scope(current_user, "POLO", str(polo_id))
    try:
        result = _service(db).register_attendance(polo_id, current_user.id, payload, db=db, current_user=current_user)
    except Exception as exc:
        _handle_domain_error(exc)
    db.commit()
    return result


@router.get("/{polo_id}/frequencias/{frequencia_id}", response_model=AttendanceOut)
def get_frequencia(
    polo_id: UUID,
    frequencia_id: UUID,
    current_user = Depends(require_permission("attendance.read")),
    db: Session = Depends(get_db),
):
    ensure_scope(current_user, "POLO", str(polo_id))
    return _get_frequencia_or_404(_service(db), polo_id, frequencia_id)


@router.patch("/{polo_id}/frequencias/{frequencia_id}", response_model=AttendanceOut)
def update_frequencia(
    polo_id: UUID,
    frequencia_id: UUID,
    payload: AttendanceUpdate,
    current_user = Depends(require_permission("attendance.create")),
    db: Session = Depends(get_db),
):
    ensure_scope(current_user, "POLO", str(polo_id))
    service = _service(db)
    frequencia = _get_frequencia_or_404(service, polo_id, frequencia_id)
    result = service.update_attendance(polo_id, frequencia, payload, db=db, current_user=current_user)
    db.commit()
    return result


@router.get("/{polo_id}/ocorrencias", response_model=list[OccurrenceOut])
def list_ocorrencias(
    polo_id: UUID,
    status_filter: str | None = Query(default=None, alias="status"),
    beneficiario_id: UUID | None = None,
    current_user = Depends(require_permission("occurrence.read")),
    db: Session = Depends(get_db),
):
    ensure_scope(current_user, "POLO", str(polo_id))
    try:
        return _service(db).list_ocorrencias(polo_id, status=status_filter, beneficiario_id=beneficiario_id)
    except Exception as exc:
        _handle_domain_error(exc)


@router.post("/{polo_id}/ocorrencias", response_model=OccurrenceOut, status_code=201)
def create_ocorrencia(
    polo_id: UUID,
    payload: OccurrenceCreate,
    current_user = Depends(require_permission("occurrence.create")),
    db: Session = Depends(get_db),
):
    ensure_scope(current_user, "POLO", str(polo_id))
    try:
        result = _service(db).create_ocorrencia(polo_id, current_user.id, payload, db=db, current_user=current_user)
    except Exception as exc:
        _handle_domain_error(exc)
    db.commit()
    return result


@router.get("/{polo_id}/ocorrencias/{ocorrencia_id}", response_model=OccurrenceOut)
def get_ocorrencia(
    polo_id: UUID,
    ocorrencia_id: UUID,
    current_user = Depends(require_permission("occurrence.read")),
    db: Session = Depends(get_db),
):
    ensure_scope(current_user, "POLO", str(polo_id))
    return _get_ocorrencia_or_404(_service(db), polo_id, ocorrencia_id)


@router.patch("/{polo_id}/ocorrencias/{ocorrencia_id}", response_model=OccurrenceOut)
def update_ocorrencia(
    polo_id: UUID,
    ocorrencia_id: UUID,
    payload: OccurrenceUpdate,
    current_user = Depends(require_permission("occurrence.create")),
    db: Session = Depends(get_db),
):
    ensure_scope(current_user, "POLO", str(polo_id))
    service = _service(db)
    ocorrencia = _get_ocorrencia_or_404(service, polo_id, ocorrencia_id)
    try:
        result = service.update_ocorrencia(polo_id, ocorrencia, payload, db=db, current_user=current_user)
    except Exception as exc:
        _handle_domain_error(exc)
    db.commit()
    return result
