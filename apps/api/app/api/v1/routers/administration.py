from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.api.deps.permissions import require_permission
from app.core.access_scope import can_access_all_polos, scoped_ids
from app.core.database import get_db
from app.domain.administration.repository import AdministrationRepository
from app.domain.administration.schemas import (
    BudgetItemCreate,
    BudgetItemOut,
    AccountabilityReportOut,
    ContractCreate,
    ContractOut,
    FinancialMovementCreate,
    FinancialMovementOut,
    FundingSourceCreate,
    FundingSourceOut,
    PermanentAssetCreate,
    PermanentAssetOut,
    PurchaseAlertOut,
    PurchaseRequestCreate,
    PurchaseRequestOut,
    StaffContractCreate,
    StaffContractOut,
)
from app.domain.administration.service import AdministrationService
from app.domain.polo.repository import PoloRepository
from app.domain.polo.schemas import MonthlyReportOut
from app.domain.polo.service import PoloService

router = APIRouter()


def _service(db: Session) -> AdministrationService:
    return AdministrationService(AdministrationRepository(db))


def _polo_service(db: Session) -> PoloService:
    return PoloService(PoloRepository(db))


def _handle_domain_error(exc: Exception):
    detail_by_code = {
        "organization_not_found": "Organizacao nao encontrada",
        "partner_not_found": "Parceiro nao encontrado",
        "funding_source_not_found": "Fonte de recurso nao encontrada",
        "contract_not_found": "Contrato nao encontrado",
        "budget_item_not_found": "Item orcamentario nao encontrado",
        "polo_not_found": "Polo nao encontrado",
        "field_event_not_found": "Evento de campo nao encontrado",
        "person_not_found": "Pessoa nao encontrada",
        "vereador_not_found": "Vereador nao encontrado",
        "purchase_request_not_found": "Requisicao de compra nao encontrada",
        "purchase_request_item_not_found": "Item da requisicao de compra nao encontrado",
    }
    if isinstance(exc, PermissionError) and str(exc) == "vereador_mismatch":
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Recurso financeiro e polo pertencem a vereadores diferentes")
    if isinstance(exc, PermissionError) and str(exc) == "purchase_item_mismatch":
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Item nao pertence a requisicao de compra informada")
    if isinstance(exc, ValueError) and str(exc) == "vereador_required":
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Informe vereador, polo, emenda ou requisicao para gerar patrimonio")
    if isinstance(exc, ValueError) and str(exc) == "vereador_required_for_source":
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Informe vereador para captacoes parlamentares ou de gabinete")
    if isinstance(exc, ValueError) and str(exc) == "funding_or_polo_required":
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Informe captacao ou polo para executar esta despesa")
    if isinstance(exc, ValueError) and str(exc) == "funding_context_required":
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Informe captacao, polo ou requisicao para gerar patrimonio")
    if isinstance(exc, LookupError):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail_by_code.get(str(exc), "Registro nao encontrado"))
    raise exc


@router.get("/funding-sources", response_model=list[FundingSourceOut])
def list_funding_sources(
    status_filter: str | None = None,
    source_type: str | None = None,
    current_user = Depends(require_permission("administration.read")),
    db: Session = Depends(get_db),
):
    return _service(db).list_funding_sources(status=status_filter, source_type=source_type, current_user=current_user)


@router.post("/funding-sources", response_model=FundingSourceOut, status_code=201)
def create_funding_source(
    payload: FundingSourceCreate,
    current_user = Depends(require_permission("administration.manage_finance")),
    db: Session = Depends(get_db),
):
    try:
        result = _service(db).create_funding_source(payload, db=db, current_user=current_user)
    except Exception as exc:
        _handle_domain_error(exc)
    db.commit()
    return result


@router.get("/contracts", response_model=list[ContractOut])
def list_contracts(
    status_filter: str | None = None,
    contract_type: str | None = None,
    current_user = Depends(require_permission("administration.read")),
    db: Session = Depends(get_db),
):
    return _service(db).list_contracts(status=status_filter, contract_type=contract_type)


@router.post("/contracts", response_model=ContractOut, status_code=201)
def create_contract(
    payload: ContractCreate,
    current_user = Depends(require_permission("administration.manage_contract")),
    db: Session = Depends(get_db),
):
    try:
        result = _service(db).create_contract(payload, db=db, current_user=current_user)
    except Exception as exc:
        _handle_domain_error(exc)
    db.commit()
    return result


@router.get("/budget-items", response_model=list[BudgetItemOut])
def list_budget_items(
    status_filter: str | None = None,
    category: str | None = None,
    current_user = Depends(require_permission("administration.read")),
    db: Session = Depends(get_db),
):
    return _service(db).list_budget_items(status=status_filter, category=category, current_user=current_user)


@router.post("/budget-items", response_model=BudgetItemOut, status_code=201)
def create_budget_item(
    payload: BudgetItemCreate,
    current_user = Depends(require_permission("administration.manage_finance")),
    db: Session = Depends(get_db),
):
    try:
        result = _service(db).create_budget_item(payload, db=db, current_user=current_user)
    except Exception as exc:
        _handle_domain_error(exc)
    db.commit()
    return result


@router.get("/accountability-report", response_model=AccountabilityReportOut)
def get_accountability_report(
    vereador_id: UUID | None = None,
    funding_source_id: UUID | None = None,
    polo_id: UUID | None = None,
    current_user = Depends(require_permission("administration.read")),
    db: Session = Depends(get_db),
):
    try:
        return _service(db).get_accountability_report(
            vereador_id=vereador_id,
            funding_source_id=funding_source_id,
            polo_id=polo_id,
        )
    except Exception as exc:
        _handle_domain_error(exc)


@router.get("/accountability-report/export")
def export_accountability_report(
    vereador_id: UUID | None = None,
    funding_source_id: UUID | None = None,
    polo_id: UUID | None = None,
    current_user = Depends(require_permission("report.export")),
    db: Session = Depends(get_db),
):
    try:
        content = _service(db).export_accountability_csv(
            vereador_id=vereador_id,
            funding_source_id=funding_source_id,
            polo_id=polo_id,
        )
    except Exception as exc:
        _handle_domain_error(exc)
    return Response(
        content=content,
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": 'attachment; filename="prestacao-contas.csv"'},
    )


@router.get("/financial-movements", response_model=list[FinancialMovementOut])
def list_financial_movements(
    funding_source_id: UUID | None = None,
    polo_id: UUID | None = None,
    movement_type: str | None = None,
    current_user = Depends(require_permission("administration.read")),
    db: Session = Depends(get_db),
):
    return _service(db).list_financial_movements(
        funding_source_id=funding_source_id,
        polo_id=polo_id,
        movement_type=movement_type,
        current_user=current_user,
    )


@router.post("/financial-movements", response_model=FinancialMovementOut, status_code=201)
def create_financial_movement(
    payload: FinancialMovementCreate,
    current_user = Depends(require_permission("administration.manage_finance")),
    db: Session = Depends(get_db),
):
    try:
        result = _service(db).create_financial_movement(payload, db=db, current_user=current_user)
    except Exception as exc:
        _handle_domain_error(exc)
    db.commit()
    return result


@router.get("/purchase-requests", response_model=list[PurchaseRequestOut])
def list_purchase_requests(
    status_filter: str | None = None,
    polo_id: UUID | None = None,
    current_user = Depends(require_permission("administration.read")),
    db: Session = Depends(get_db),
):
    return _service(db).list_purchase_requests(status=status_filter, polo_id=polo_id, current_user=current_user)


@router.get("/purchase-alerts", response_model=PurchaseAlertOut)
def get_purchase_alerts(
    current_user = Depends(require_permission("administration.read")),
    db: Session = Depends(get_db),
):
    return _service(db).get_purchase_alerts(current_user=current_user)


@router.get("/monthly-reports", response_model=list[MonthlyReportOut])
def list_monthly_reports(
    polo_id: UUID | None = None,
    status_filter: str | None = None,
    current_user = Depends(require_permission("administration.read")),
    db: Session = Depends(get_db),
):
    if can_access_all_polos(current_user) or current_user.is_global_admin:
        return _polo_service(db).list_monthly_reports(polo_id=polo_id, status=status_filter)
    allowed_polo_ids = scoped_ids(current_user, "POLO")
    if polo_id is not None:
        if str(polo_id) not in allowed_polo_ids:
            return []
        return _polo_service(db).list_monthly_reports(polo_id=polo_id, status=status_filter)
    reports = []
    for allowed_polo_id in allowed_polo_ids:
        reports.extend(_polo_service(db).list_monthly_reports(polo_id=allowed_polo_id, status=status_filter))
    return reports


@router.get("/permanent-assets", response_model=list[PermanentAssetOut])
def list_permanent_assets(
    status_filter: str | None = None,
    polo_id: UUID | None = None,
    current_user = Depends(require_permission("administration.read")),
    db: Session = Depends(get_db),
):
    return _service(db).list_permanent_assets(status=status_filter, polo_id=polo_id, current_user=current_user)


@router.post("/permanent-assets", response_model=PermanentAssetOut, status_code=201)
def create_permanent_asset(
    payload: PermanentAssetCreate,
    current_user = Depends(require_permission("administration.manage_purchase")),
    db: Session = Depends(get_db),
):
    try:
        result = _service(db).create_permanent_asset(payload, db=db, current_user=current_user)
    except Exception as exc:
        _handle_domain_error(exc)
    db.commit()
    return result


@router.post("/purchase-requests", response_model=PurchaseRequestOut, status_code=201)
def create_purchase_request(
    payload: PurchaseRequestCreate,
    current_user = Depends(require_permission("administration.manage_purchase")),
    db: Session = Depends(get_db),
):
    try:
        result = _service(db).create_purchase_request(
            payload,
            requested_by_user_id=current_user.id,
            db=db,
            current_user=current_user,
        )
    except Exception as exc:
        _handle_domain_error(exc)
    db.commit()
    return result


@router.get("/staff-contracts", response_model=list[StaffContractOut])
def list_staff_contracts(
    status_filter: str | None = None,
    polo_id: UUID | None = None,
    current_user = Depends(require_permission("administration.read")),
    db: Session = Depends(get_db),
):
    return _service(db).list_staff_contracts(status=status_filter, polo_id=polo_id, current_user=current_user)


@router.post("/staff-contracts", response_model=StaffContractOut, status_code=201)
def create_staff_contract(
    payload: StaffContractCreate,
    current_user = Depends(require_permission("administration.manage_staff")),
    db: Session = Depends(get_db),
):
    try:
        result = _service(db).create_staff_contract(payload, db=db, current_user=current_user)
    except Exception as exc:
        _handle_domain_error(exc)
    db.commit()
    return result
