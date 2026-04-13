import json
from datetime import datetime

from app.core.audit import audited_mutation
from app.core.access_scope import can_access_all_cabinets, can_access_all_polos, scoped_ids
from app.domain.workflow.models import Task
from app.domain.workflow.repository import WorkflowRepository
from app.domain.workflow.schemas import TaskCompleteRequest, TaskCreate, TaskUpdate
from app.shared.audit import write_audit_log


class WorkflowService:
    def __init__(self, repo: WorkflowRepository):
        self.repo = repo

    def list_tasks(self, status: str | None = None, demand_id=None, limit: int = 50, offset: int = 0, current_user=None):
        scope = self._scope_for_workflow(current_user)
        return self.repo.list_tasks(status=status, demand_id=demand_id, limit=limit, offset=offset, **scope)

    def get_task(self, task_id):
        return self.repo.get_task(task_id)

    @audited_mutation(action="CREATE", entity_schema="workflow", entity_name="tasks")
    def create_task(self, created_by_user_id, payload: TaskCreate, db=None, current_user=None):
        entity = Task(
            organization_id=payload.organization_id,
            vereador_id=payload.vereador_id,
            polo_id=payload.polo_id,
            person_id=payload.person_id,
            demand_id=payload.demand_id,
            assigned_to_user_id=payload.assigned_to_user_id,
            created_by_user_id=created_by_user_id,
            task_type=payload.task_type,
            title=payload.title,
            description=payload.description,
            priority=payload.priority,
            due_at=payload.due_at,
        )
        return self.repo.create_task(entity)

    @audited_mutation(action="UPDATE", entity_schema="workflow", entity_name="tasks")
    def update_task(self, task: Task, payload: TaskUpdate, db=None, current_user=None):
        return self.repo.update_task(task, payload.model_dump(exclude_unset=True))

    @audited_mutation(action="COMPLETE", entity_schema="workflow", entity_name="tasks")
    def complete_task(self, task: Task, payload: TaskCompleteRequest, db=None, current_user=None):
        completed_at = payload.completed_at or datetime.now()
        task = self.repo.update_task(
            task,
            {
                "status": "COMPLETED",
                "completed_at": completed_at,
            },
        )

        if payload.resolve_demand and task.demand_id:
            demand = self.repo.get_demand(task.demand_id)
            if demand is not None:
                self.repo.update_demand(
                    demand,
                    {
                        "status": "RESOLVED",
                        "resolved_at": completed_at,
                        "resolution_notes": payload.resolution_notes,
                    },
                )
                self._audit(
                    db,
                    getattr(current_user, "id", None),
                    "RESOLVE",
                    "territory",
                    "demands",
                    demand.id,
                    new_values_json=json.dumps(
                        {
                            "id": str(demand.id),
                            "status": demand.status,
                            "resolved_at": completed_at.isoformat(),
                        }
                    ),
                )

        return task

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

    def _scope_for_workflow(self, current_user):
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
