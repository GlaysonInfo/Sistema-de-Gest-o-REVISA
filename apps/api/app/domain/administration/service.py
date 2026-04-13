from app.core.audit import audited_mutation
from app.core.access_scope import can_access_all_finance, can_access_all_polos, scoped_ids
from app.domain.administration.models import BudgetItem, Contract, FinancialMovement, FundingSource, PermanentAsset, PurchaseRequest, PurchaseRequestItem, StaffContract
from app.domain.administration.repository import AdministrationRepository
from decimal import Decimal

from app.domain.administration.schemas import (
    AccountabilityReportOut,
    AccountabilityTotals,
    BudgetItemCreate,
    ContractCreate,
    FiscalDocumentOut,
    FinancialMovementCreate,
    FundingSourceCreate,
    PermanentAssetCreate,
    PurchaseAlertOut,
    PurchaseRequestCreate,
    StaffContractCreate,
)

PARLIAMENTARY_SOURCE_TYPES = {"EMENDA_IMPOSITIVA", "EMENDA_PARLAMENTAR", "PROJETO_GABINETE"}


class AdministrationService:
    def __init__(self, repo: AdministrationRepository):
        self.repo = repo

    def list_funding_sources(self, status: str | None = None, source_type: str | None = None, current_user=None):
        scope = self._scope_for_administration(current_user)
        return self.repo.list_funding_sources(status=status, source_type=source_type, vereador_ids=scope["vereador_ids"], force_empty=scope["force_empty"])

    @audited_mutation(action="CREATE", entity_schema="administration", entity_name="funding_sources")
    def create_funding_source(self, payload: FundingSourceCreate, db=None, current_user=None):
        self._ensure_organization(payload.organization_id)
        if payload.source_type in PARLIAMENTARY_SOURCE_TYPES and payload.vereador_id is None:
            raise ValueError("vereador_required_for_source")
        self._ensure_vereador(payload.vereador_id)
        return self.repo.create_funding_source(FundingSource(**payload.model_dump()))

    def list_contracts(self, status: str | None = None, contract_type: str | None = None):
        return self.repo.list_contracts(status=status, contract_type=contract_type)

    @audited_mutation(action="CREATE", entity_schema="administration", entity_name="contracts")
    def create_contract(self, payload: ContractCreate, db=None, current_user=None):
        self._ensure_organization(payload.organization_id)
        self._ensure_partner(payload.partner_id)
        self._ensure_funding_source(payload.funding_source_id)
        return self.repo.create_contract(Contract(**payload.model_dump()))

    def list_budget_items(self, status: str | None = None, category: str | None = None, current_user=None):
        scope = self._scope_for_administration(current_user)
        return self.repo.list_budget_items(status=status, category=category, polo_ids=scope["polo_ids"], force_empty=scope["force_empty"])

    @audited_mutation(action="CREATE", entity_schema="administration", entity_name="budget_items")
    def create_budget_item(self, payload: BudgetItemCreate, db=None, current_user=None):
        self._ensure_organization(payload.organization_id)
        funding_source = self._ensure_funding_source(payload.funding_source_id)
        self._ensure_contract(payload.contract_id)
        polo = self._ensure_polo(payload.polo_id)
        self._ensure_same_vereador(funding_source, polo)
        self._ensure_field_event(payload.field_event_id)
        return self.repo.create_budget_item(BudgetItem(**payload.model_dump()))

    def list_financial_movements(self, funding_source_id=None, polo_id=None, movement_type: str | None = None, current_user=None):
        scope = self._scope_for_administration(current_user, explicit_polo_id=polo_id)
        return self.repo.list_financial_movements(funding_source_id=funding_source_id, polo_id=polo_id, movement_type=movement_type, **scope)

    @audited_mutation(action="CREATE", entity_schema="administration", entity_name="financial_movements")
    def create_financial_movement(self, payload: FinancialMovementCreate, db=None, current_user=None):
        funding_source = self._ensure_funding_source(payload.funding_source_id)
        self._ensure_organization(payload.organization_id)
        polo = self._ensure_polo(payload.polo_id)
        self._ensure_budget_item(payload.budget_item_id)
        self._ensure_contract(payload.contract_id)

        values = payload.model_dump()
        values["vereador_id"] = values["vereador_id"] or funding_source.vereador_id or (polo.vereador_id if polo else None)
        values["organization_id"] = values["organization_id"] or funding_source.organization_id
        self._ensure_vereador(values["vereador_id"])
        self._ensure_same_vereador(funding_source, polo)
        self._ensure_same_vereador(funding_source, values["vereador_id"])
        return self.repo.create_financial_movement(FinancialMovement(**values))

    def list_purchase_requests(self, status: str | None = None, polo_id=None, current_user=None):
        scope = self._scope_for_administration(current_user, explicit_polo_id=polo_id)
        return self.repo.list_purchase_requests(status=status, polo_id=polo_id, **scope)

    def get_purchase_alerts(self, current_user=None):
        scope = self._scope_for_administration(current_user)
        purchase_requests = self.repo.list_open_purchase_requests(**scope)
        return PurchaseAlertOut(
            open_purchase_requests=len(purchase_requests),
            purchase_requests=purchase_requests,
        )

    @audited_mutation(action="CREATE", entity_schema="administration", entity_name="purchase_requests")
    def create_purchase_request(self, payload: PurchaseRequestCreate, requested_by_user_id, db=None, current_user=None):
        self._ensure_organization(payload.organization_id)
        polo = self._ensure_polo(payload.polo_id)
        funding_source = self._ensure_funding_source(payload.funding_source_id)
        if polo is None and funding_source is None:
            raise ValueError("funding_or_polo_required")
        values = payload.model_dump()
        item_values = values.pop("items", [])
        values["vereador_id"] = values["vereador_id"] or (
            funding_source.vereador_id
            if funding_source
            else polo.vereador_id
            if polo
            else None
        )
        self._ensure_vereador(values["vereador_id"])
        self._ensure_same_vereador(funding_source, polo)
        self._ensure_same_vereador(polo, values["vereador_id"])
        self._ensure_same_vereador(funding_source, values["vereador_id"])
        values["requested_by_user_id"] = requested_by_user_id
        if values["estimated_amount"] is None:
            totals = [
                item.get("estimated_total") or (
                    item.get("quantity") * item.get("estimated_unit_price")
                    if item.get("estimated_unit_price") is not None
                    else None
                )
                for item in item_values
            ]
            totals = [item for item in totals if item is not None]
            values["estimated_amount"] = sum(totals, Decimal("0")) if totals else None
        entity = PurchaseRequest(**values)
        entity.items = [
            PurchaseRequestItem(
                line_number=item.get("line_number") or index,
                product=item["product"],
                size=item.get("size"),
                desired_brand=item.get("desired_brand"),
                quantity=item["quantity"],
                unit=item.get("unit"),
                estimated_unit_price=item.get("estimated_unit_price"),
                estimated_total=item.get("estimated_total"),
                approved_unit_price=item.get("approved_unit_price"),
                approved_total=item.get("approved_total"),
                supplier_name=item.get("supplier_name"),
                quote_ref=item.get("quote_ref"),
                notes=item.get("notes"),
            )
            for index, item in enumerate(item_values, start=1)
        ]
        return self.repo.create_purchase_request(entity)

    def list_staff_contracts(self, status: str | None = None, polo_id=None, current_user=None):
        scope = self._scope_for_administration(current_user, explicit_polo_id=polo_id)
        return self.repo.list_staff_contracts(status=status, polo_id=polo_id, **scope)

    def list_permanent_assets(self, status: str | None = None, polo_id=None, current_user=None):
        scope = self._scope_for_administration(current_user, explicit_polo_id=polo_id)
        return self.repo.list_permanent_assets(status=status, polo_id=polo_id, **scope)

    @audited_mutation(action="CREATE", entity_schema="administration", entity_name="permanent_assets")
    def create_permanent_asset(self, payload: PermanentAssetCreate, db=None, current_user=None):
        self._ensure_organization(payload.organization_id)
        polo = self._ensure_polo(payload.polo_id)
        funding_source = self._ensure_funding_source(payload.funding_source_id)
        purchase_request = self._ensure_purchase_request(payload.purchase_request_id)
        purchase_request_item = self._ensure_purchase_request_item(payload.purchase_request_item_id)

        values = payload.model_dump()
        values["vereador_id"] = values["vereador_id"] or (
            funding_source.vereador_id
            if funding_source
            else purchase_request.vereador_id
            if purchase_request
            else polo.vereador_id
            if polo
            else None
        )
        if values["vereador_id"] is None and funding_source is None and purchase_request is None and polo is None:
            raise ValueError("funding_context_required")
        self._ensure_vereador(values["vereador_id"])
        self._ensure_same_vereador(funding_source, values["vereador_id"])
        self._ensure_same_vereador(polo, values["vereador_id"])
        self._ensure_same_vereador(purchase_request, values["vereador_id"])
        if purchase_request_item is not None and purchase_request is not None:
            if str(purchase_request_item.purchase_request_id) != str(purchase_request.id):
                raise PermissionError("purchase_item_mismatch")
        values["asset_number"] = self.repo.next_asset_number()
        return self.repo.create_permanent_asset(PermanentAsset(**values))

    @audited_mutation(action="CREATE", entity_schema="administration", entity_name="staff_contracts")
    def create_staff_contract(self, payload: StaffContractCreate, db=None, current_user=None):
        self._ensure_organization(payload.organization_id)
        polo = self._ensure_polo(payload.polo_id)
        funding_source = self._ensure_funding_source(payload.funding_source_id)
        if polo is None and funding_source is None:
            raise ValueError("funding_or_polo_required")
        self._ensure_person(payload.person_id)
        values = payload.model_dump()
        values["vereador_id"] = values["vereador_id"] or (
            funding_source.vereador_id
            if funding_source
            else polo.vereador_id
            if polo
            else None
        )
        self._ensure_vereador(values["vereador_id"])
        self._ensure_same_vereador(funding_source, polo)
        self._ensure_same_vereador(polo, values["vereador_id"])
        self._ensure_same_vereador(funding_source, values["vereador_id"])
        return self.repo.create_staff_contract(StaffContract(**values))

    def get_accountability_report(self, vereador_id=None, funding_source_id=None, polo_id=None):
        explicit_vereador_id = vereador_id
        if vereador_id is not None:
            self._ensure_vereador(vereador_id)
        funding_source = self._ensure_funding_source(funding_source_id)
        polo = self._ensure_polo(polo_id)

        if funding_source is not None:
            if vereador_id is not None:
                self._ensure_same_vereador(funding_source, vereador_id)
            elif funding_source.vereador_id is not None:
                vereador_id = funding_source.vereador_id

        if polo is not None:
            if vereador_id is not None:
                self._ensure_same_vereador(polo, vereador_id)
            elif funding_source is None:
                vereador_id = polo.vereador_id
            self._ensure_same_vereador(funding_source, polo)

        funding_sources = self.repo.list_funding_sources_for_accountability(
            vereador_id=vereador_id if funding_source_id is None or explicit_vereador_id is not None else None,
            funding_source_id=funding_source_id,
        )
        funding_source_ids = [item.id for item in funding_sources]
        scoped_but_empty = (vereador_id is not None or funding_source_id is not None or polo_id is not None) and not funding_source_ids

        if scoped_but_empty:
            movements = []
            budget_items = []
            purchase_requests = []
            staff_contracts = []
            contracts = []
        else:
            movements = self.repo.list_financial_movements_for_accountability(
                funding_source_ids,
                vereador_id=vereador_id,
                polo_id=polo_id,
            )
            budget_items = self.repo.list_budget_items_for_accountability(
                funding_source_ids,
                polo_id=polo_id,
            )
            purchase_requests = self.repo.list_purchase_requests_for_accountability(
                funding_source_ids,
                vereador_id=vereador_id,
                polo_id=polo_id,
            )
            staff_contracts = self.repo.list_staff_contracts_for_accountability(
                funding_source_ids,
                vereador_id=vereador_id,
                polo_id=polo_id,
            )
            contracts = self.repo.list_contracts_for_accountability(funding_source_ids)

        return AccountabilityReportOut(
            vereador_id=vereador_id,
            funding_source_id=funding_source_id,
            polo_id=polo_id,
            totals=self._accountability_totals(funding_sources, movements, purchase_requests, staff_contracts),
            funding_sources=funding_sources,
            financial_movements=movements,
            budget_items=budget_items,
            purchase_requests=purchase_requests,
            staff_contracts=staff_contracts,
            contracts=contracts,
            fiscal_documents=self._fiscal_documents(movements, purchase_requests, contracts),
        )

    def export_accountability_csv(self, vereador_id=None, funding_source_id=None, polo_id=None):
        report = self.get_accountability_report(
            vereador_id=vereador_id,
            funding_source_id=funding_source_id,
            polo_id=polo_id,
        )
        rows = [
            ["secao", "id", "tipo", "descricao", "valor", "status", "documento"],
            ["totais", "", "valor_aprovado", "", str(report.totals.estimated_amount), "", ""],
            ["totais", "", "valor_depositado", "", str(report.totals.deposited_amount), "", ""],
            ["totais", "", "entradas", "", str(report.totals.movement_inflows), "", ""],
            ["totais", "", "saidas", "", str(report.totals.movement_outflows), "", ""],
            ["totais", "", "saldo_disponivel", "", str(report.totals.available_balance), "", ""],
        ]
        rows.extend(
            ["captacao", str(item.id), item.source_type, item.name, str(item.deposited_amount), item.status, item.appropriation_number or ""]
            for item in report.funding_sources
        )
        rows.extend(
            ["movimento", str(item.id), item.movement_type, item.description, str(item.amount), item.status, item.document_ref or ""]
            for item in report.financial_movements
        )
        rows.extend(
            ["compra", str(item.id), item.category, item.description, str(item.approved_amount or item.estimated_amount or 0), item.status, item.document_ref or ""]
            for item in report.purchase_requests
        )
        rows.extend(
            ["pessoal", str(item.id), item.contract_type, item.role_title, str(item.salary_amount), item.status, ""]
            for item in report.staff_contracts
        )
        return "\n".join(",".join(self._csv_cell(cell) for cell in row) for row in rows) + "\n"

    def _scope_for_administration(self, current_user, explicit_polo_id=None):
        if current_user is None or getattr(current_user, "is_global_admin", False) or can_access_all_finance(current_user) or can_access_all_polos(current_user):
            return {"polo_ids": None, "vereador_ids": None, "force_empty": False}
        polo_ids = scoped_ids(current_user, "POLO")
        vereador_ids = scoped_ids(current_user, "VEREADOR")
        force_empty = not polo_ids and not vereador_ids
        if explicit_polo_id is not None and polo_ids and str(explicit_polo_id) not in polo_ids:
            force_empty = True
        return {"polo_ids": polo_ids, "vereador_ids": vereador_ids, "force_empty": force_empty}

    def _ensure_organization(self, organization_id):
        if organization_id is not None and self.repo.get_organization(organization_id) is None:
            raise LookupError("organization_not_found")

    def _ensure_vereador(self, vereador_id):
        if vereador_id is not None and self.repo.get_vereador(vereador_id) is None:
            raise LookupError("vereador_not_found")

    def _ensure_partner(self, partner_id):
        if partner_id is not None and self.repo.get_partner(partner_id) is None:
            raise LookupError("partner_not_found")

    def _ensure_funding_source(self, funding_source_id):
        if funding_source_id is None:
            return None
        funding_source = self.repo.get_funding_source(funding_source_id)
        if funding_source is None:
            raise LookupError("funding_source_not_found")
        return funding_source

    def _ensure_contract(self, contract_id):
        if contract_id is None:
            return None
        contract = self.repo.get_contract(contract_id)
        if contract is None:
            raise LookupError("contract_not_found")
        return contract

    def _ensure_polo(self, polo_id):
        if polo_id is None:
            return None
        polo = self.repo.get_polo(polo_id)
        if polo is None:
            raise LookupError("polo_not_found")
        return polo

    def _ensure_field_event(self, field_event_id):
        if field_event_id is not None and self.repo.get_field_event(field_event_id) is None:
            raise LookupError("field_event_not_found")

    def _ensure_budget_item(self, budget_item_id):
        if budget_item_id is not None and self.repo.get_budget_item(budget_item_id) is None:
            raise LookupError("budget_item_not_found")

    def _ensure_purchase_request(self, purchase_request_id):
        if purchase_request_id is None:
            return None
        purchase_request = self.repo.get_purchase_request(purchase_request_id)
        if purchase_request is None:
            raise LookupError("purchase_request_not_found")
        return purchase_request

    def _ensure_purchase_request_item(self, purchase_request_item_id):
        if purchase_request_item_id is None:
            return None
        item = self.repo.get_purchase_request_item(purchase_request_item_id)
        if item is None:
            raise LookupError("purchase_request_item_not_found")
        return item

    def _ensure_person(self, person_id):
        if person_id is not None and self.repo.get_person(person_id) is None:
            raise LookupError("person_not_found")

    @staticmethod
    def _accountability_totals(funding_sources, movements, purchase_requests, staff_contracts):
        estimated = sum((item.estimated_amount or Decimal("0")) for item in funding_sources)
        secured = sum((item.secured_amount or Decimal("0")) for item in funding_sources)
        deposited = sum((item.deposited_amount or Decimal("0")) for item in funding_sources)
        inflow_types = {"PREFEITURA_DEPOSITO", "ENTRADA", "RECEITA", "AJUSTE_CREDITO"}
        inflows = sum((item.amount or Decimal("0")) for item in movements if item.movement_type in inflow_types)
        outflows = sum(abs(item.amount or Decimal("0")) for item in movements if item.movement_type not in inflow_types)
        purchase_estimated = sum((item.estimated_amount or Decimal("0")) for item in purchase_requests)
        purchase_approved = sum((item.approved_amount or Decimal("0")) for item in purchase_requests)
        payroll = sum((item.salary_amount or Decimal("0")) for item in staff_contracts if item.status != "TERMINATED")
        available_base = deposited if deposited > Decimal("0") else inflows
        return AccountabilityTotals(
            estimated_amount=estimated,
            secured_amount=secured,
            deposited_amount=deposited,
            movement_inflows=inflows,
            movement_outflows=outflows,
            purchase_estimated_amount=purchase_estimated,
            purchase_approved_amount=purchase_approved,
            staff_monthly_payroll=payroll,
            available_balance=available_base - outflows,
        )

    @staticmethod
    def _fiscal_documents(movements, purchase_requests, contracts):
        documents = []
        for item in movements:
            if item.document_ref:
                documents.append(FiscalDocumentOut(source="financial_movement", entity_id=item.id, label=item.description, document_ref=item.document_ref))
        for item in purchase_requests:
            if item.document_ref:
                documents.append(FiscalDocumentOut(source="purchase_request", entity_id=item.id, label=item.description, document_ref=item.document_ref))
        for item in contracts:
            if item.document_ref:
                documents.append(FiscalDocumentOut(source="contract", entity_id=item.id, label=item.title, document_ref=item.document_ref))
        return documents

    @staticmethod
    def _csv_cell(value) -> str:
        text = str(value or "")
        return f'"{text.replace("\"", "\"\"")}"'

    @staticmethod
    def _ensure_same_vereador(left, right):
        if left is None or right is None:
            return
        left_id = getattr(left, "vereador_id", left)
        right_id = getattr(right, "vereador_id", right)
        if left_id is None or right_id is None:
            return
        if str(left_id) != str(right_id):
            raise PermissionError("vereador_mismatch")
