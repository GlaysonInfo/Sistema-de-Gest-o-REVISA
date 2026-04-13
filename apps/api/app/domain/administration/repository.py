from sqlalchemy import false, or_, select, text
from sqlalchemy.orm import Session

from app.domain.administration.models import BudgetItem, Contract, FinancialMovement, FundingSource, PermanentAsset, PurchaseRequest, PurchaseRequestItem, StaffContract
from app.domain.core.models import Organization, Person, Vereador
from app.domain.polo.models import PoloUnit
from app.domain.relationship.models import FieldEvent, Partner


class AdministrationRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_organization(self, organization_id) -> Organization | None:
        return self.db.get(Organization, organization_id)

    def get_vereador(self, vereador_id) -> Vereador | None:
        return self.db.get(Vereador, vereador_id)

    def get_person(self, person_id) -> Person | None:
        return self.db.get(Person, person_id)

    def get_partner(self, partner_id) -> Partner | None:
        return self.db.get(Partner, partner_id)

    def get_funding_source(self, funding_source_id) -> FundingSource | None:
        return self.db.get(FundingSource, funding_source_id)

    def get_contract(self, contract_id) -> Contract | None:
        return self.db.get(Contract, contract_id)

    def get_budget_item(self, budget_item_id) -> BudgetItem | None:
        return self.db.get(BudgetItem, budget_item_id)

    def get_purchase_request(self, purchase_request_id) -> PurchaseRequest | None:
        return self.db.get(PurchaseRequest, purchase_request_id)

    def get_purchase_request_item(self, purchase_request_item_id) -> PurchaseRequestItem | None:
        return self.db.get(PurchaseRequestItem, purchase_request_item_id)

    def get_polo(self, polo_id) -> PoloUnit | None:
        return self.db.get(PoloUnit, polo_id)

    def get_field_event(self, field_event_id) -> FieldEvent | None:
        return self.db.get(FieldEvent, field_event_id)

    def list_funding_sources(self, status: str | None = None, source_type: str | None = None, vereador_ids: set[str] | None = None, force_empty: bool = False):
        statement = select(FundingSource)
        if status:
            statement = statement.where(FundingSource.status == status)
        if source_type:
            statement = statement.where(FundingSource.source_type == source_type)
        statement = self._scope_by_vereador(statement, FundingSource, vereador_ids=vereador_ids, force_empty=force_empty)
        return self.db.execute(statement.order_by(FundingSource.created_at.desc())).scalars().all()

    def create_funding_source(self, entity: FundingSource) -> FundingSource:
        self.db.add(entity)
        self.db.flush()
        self.db.refresh(entity)
        return entity

    def list_contracts(self, status: str | None = None, contract_type: str | None = None):
        statement = select(Contract)
        if status:
            statement = statement.where(Contract.status == status)
        if contract_type:
            statement = statement.where(Contract.contract_type == contract_type)
        return self.db.execute(statement.order_by(Contract.created_at.desc())).scalars().all()

    def create_contract(self, entity: Contract) -> Contract:
        self.db.add(entity)
        self.db.flush()
        self.db.refresh(entity)
        return entity

    def list_budget_items(self, status: str | None = None, category: str | None = None, polo_ids: set[str] | None = None, force_empty: bool = False):
        statement = select(BudgetItem)
        if status:
            statement = statement.where(BudgetItem.status == status)
        if category:
            statement = statement.where(BudgetItem.category == category)
        statement = self._scope_by_polo(statement, BudgetItem, polo_ids=polo_ids, force_empty=force_empty)
        return self.db.execute(statement.order_by(BudgetItem.created_at.desc())).scalars().all()

    def create_budget_item(self, entity: BudgetItem) -> BudgetItem:
        self.db.add(entity)
        self.db.flush()
        self.db.refresh(entity)
        return entity

    def list_financial_movements(self, funding_source_id=None, polo_id=None, movement_type: str | None = None, polo_ids: set[str] | None = None, vereador_ids: set[str] | None = None, force_empty: bool = False):
        statement = select(FinancialMovement)
        if funding_source_id:
            statement = statement.where(FinancialMovement.funding_source_id == funding_source_id)
        if polo_id:
            statement = statement.where(FinancialMovement.polo_id == polo_id)
        if movement_type:
            statement = statement.where(FinancialMovement.movement_type == movement_type)
        statement = self._scope_by_polo_or_vereador(statement, FinancialMovement, polo_ids=polo_ids, vereador_ids=vereador_ids, force_empty=force_empty)
        return self.db.execute(statement.order_by(FinancialMovement.movement_date.desc(), FinancialMovement.created_at.desc())).scalars().all()

    def create_financial_movement(self, entity: FinancialMovement) -> FinancialMovement:
        self.db.add(entity)
        self.db.flush()
        self.db.refresh(entity)
        return entity

    def list_purchase_requests(self, status: str | None = None, polo_id=None, polo_ids: set[str] | None = None, vereador_ids: set[str] | None = None, force_empty: bool = False):
        statement = select(PurchaseRequest)
        if status:
            statement = statement.where(PurchaseRequest.status == status)
        if polo_id:
            statement = statement.where(PurchaseRequest.polo_id == polo_id)
        statement = self._scope_by_polo_or_vereador(statement, PurchaseRequest, polo_ids=polo_ids, vereador_ids=vereador_ids, force_empty=force_empty)
        return self.db.execute(statement.order_by(PurchaseRequest.created_at.desc())).scalars().all()

    def list_open_purchase_requests(self, polo_ids: set[str] | None = None, vereador_ids: set[str] | None = None, force_empty: bool = False):
        closed_statuses = ["CANCELLED", "CLOSED", "PAID", "NF_REGISTERED", "COMPLETED"]
        statement = select(PurchaseRequest).where(PurchaseRequest.status.not_in(closed_statuses))
        statement = self._scope_by_polo_or_vereador(statement, PurchaseRequest, polo_ids=polo_ids, vereador_ids=vereador_ids, force_empty=force_empty)
        return self.db.execute(statement.order_by(PurchaseRequest.created_at.desc())).scalars().all()

    def create_purchase_request(self, entity: PurchaseRequest) -> PurchaseRequest:
        self.db.add(entity)
        self.db.flush()
        self.db.refresh(entity)
        return entity

    def list_staff_contracts(self, status: str | None = None, polo_id=None, polo_ids: set[str] | None = None, vereador_ids: set[str] | None = None, force_empty: bool = False):
        statement = select(StaffContract)
        if status:
            statement = statement.where(StaffContract.status == status)
        if polo_id:
            statement = statement.where(StaffContract.polo_id == polo_id)
        statement = self._scope_by_polo_or_vereador(statement, StaffContract, polo_ids=polo_ids, vereador_ids=vereador_ids, force_empty=force_empty)
        return self.db.execute(statement.order_by(StaffContract.created_at.desc())).scalars().all()

    def create_staff_contract(self, entity: StaffContract) -> StaffContract:
        self.db.add(entity)
        self.db.flush()
        self.db.refresh(entity)
        return entity

    def next_asset_number(self) -> str:
        value = self.db.execute(text("select nextval('administration.permanent_asset_number_seq')")).scalar_one()
        return f"REVISA-PAT-{value:06d}"

    def list_permanent_assets(self, status: str | None = None, polo_id=None, polo_ids: set[str] | None = None, vereador_ids: set[str] | None = None, force_empty: bool = False):
        statement = select(PermanentAsset)
        if status:
            statement = statement.where(PermanentAsset.status == status)
        if polo_id:
            statement = statement.where(PermanentAsset.polo_id == polo_id)
        statement = self._scope_by_polo_or_vereador(statement, PermanentAsset, polo_ids=polo_ids, vereador_ids=vereador_ids, force_empty=force_empty)
        return self.db.execute(statement.order_by(PermanentAsset.created_at.desc())).scalars().all()

    def create_permanent_asset(self, entity: PermanentAsset) -> PermanentAsset:
        self.db.add(entity)
        self.db.flush()
        self.db.refresh(entity)
        return entity

    def list_funding_sources_for_accountability(self, vereador_id=None, funding_source_id=None):
        statement = select(FundingSource)
        if vereador_id:
            statement = statement.where(FundingSource.vereador_id == vereador_id)
        if funding_source_id:
            statement = statement.where(FundingSource.id == funding_source_id)
        return self.db.execute(statement.order_by(FundingSource.created_at.desc())).scalars().all()

    def list_financial_movements_for_accountability(self, funding_source_ids: list, vereador_id=None, polo_id=None):
        statement = select(FinancialMovement)
        if funding_source_ids:
            statement = statement.where(FinancialMovement.funding_source_id.in_(funding_source_ids))
        if vereador_id:
            statement = statement.where(FinancialMovement.vereador_id == vereador_id)
        if polo_id:
            statement = statement.where(FinancialMovement.polo_id == polo_id)
        return self.db.execute(statement.order_by(FinancialMovement.movement_date.desc(), FinancialMovement.created_at.desc())).scalars().all()

    def list_budget_items_for_accountability(self, funding_source_ids: list, polo_id=None):
        statement = select(BudgetItem)
        if funding_source_ids:
            statement = statement.where(BudgetItem.funding_source_id.in_(funding_source_ids))
        if polo_id:
            statement = statement.where(BudgetItem.polo_id == polo_id)
        return self.db.execute(statement.order_by(BudgetItem.created_at.desc())).scalars().all()

    def list_purchase_requests_for_accountability(self, funding_source_ids: list, vereador_id=None, polo_id=None):
        statement = select(PurchaseRequest)
        if funding_source_ids:
            statement = statement.where(PurchaseRequest.funding_source_id.in_(funding_source_ids))
        if vereador_id:
            statement = statement.where(PurchaseRequest.vereador_id == vereador_id)
        if polo_id:
            statement = statement.where(PurchaseRequest.polo_id == polo_id)
        return self.db.execute(statement.order_by(PurchaseRequest.created_at.desc())).scalars().all()

    def list_staff_contracts_for_accountability(self, funding_source_ids: list, vereador_id=None, polo_id=None):
        statement = select(StaffContract)
        if funding_source_ids:
            statement = statement.where(StaffContract.funding_source_id.in_(funding_source_ids))
        if vereador_id:
            statement = statement.where(StaffContract.vereador_id == vereador_id)
        if polo_id:
            statement = statement.where(StaffContract.polo_id == polo_id)
        return self.db.execute(statement.order_by(StaffContract.created_at.desc())).scalars().all()

    def list_contracts_for_accountability(self, funding_source_ids: list):
        statement = select(Contract)
        if funding_source_ids:
            statement = statement.where(Contract.funding_source_id.in_(funding_source_ids))
        return self.db.execute(statement.order_by(Contract.created_at.desc())).scalars().all()

    def _scope_by_polo(self, statement, model, polo_ids: set[str] | None = None, force_empty: bool = False):
        if force_empty:
            return statement.where(false())
        if polo_ids and hasattr(model, "polo_id"):
            return statement.where(model.polo_id.in_(polo_ids))
        return statement

    def _scope_by_vereador(self, statement, model, vereador_ids: set[str] | None = None, force_empty: bool = False):
        if force_empty:
            return statement.where(false())
        if vereador_ids and hasattr(model, "vereador_id"):
            return statement.where(model.vereador_id.in_(vereador_ids))
        return statement

    def _scope_by_polo_or_vereador(self, statement, model, polo_ids: set[str] | None = None, vereador_ids: set[str] | None = None, force_empty: bool = False):
        if force_empty:
            return statement.where(false())
        filters = []
        if polo_ids and hasattr(model, "polo_id"):
            filters.append(model.polo_id.in_(polo_ids))
        if vereador_ids and hasattr(model, "vereador_id"):
            filters.append(model.vereador_id.in_(vereador_ids))
        return statement.where(or_(*filters)) if filters else statement
