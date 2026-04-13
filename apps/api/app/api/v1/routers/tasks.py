from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps.permissions import require_permission
from app.core.database import get_db
from app.domain.workflow.repository import WorkflowRepository
from app.domain.workflow.schemas import TaskCompleteRequest, TaskCreate, TaskOut, TaskUpdate
from app.domain.workflow.service import WorkflowService

router = APIRouter()


def _service(db: Session) -> WorkflowService:
    return WorkflowService(WorkflowRepository(db))


def _get_task_or_404(service: WorkflowService, task_id: UUID):
    task = service.get_task(task_id)
    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tarefa nao encontrada")
    return task


@router.get("", response_model=list[TaskOut])
def list_tasks(
    status: str | None = None,
    demand_id: UUID | None = None,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    current_user = Depends(require_permission("task.read")),
    db: Session = Depends(get_db),
):
    return _service(db).list_tasks(status=status, demand_id=demand_id, limit=limit, offset=offset, current_user=current_user)


@router.post("", response_model=TaskOut, status_code=201)
def create_task(
    payload: TaskCreate,
    current_user = Depends(require_permission("task.create")),
    db: Session = Depends(get_db),
):
    result = _service(db).create_task(
        created_by_user_id=current_user.id,
        payload=payload,
        db=db,
        current_user=current_user,
    )
    db.commit()
    return result


@router.get("/{task_id}", response_model=TaskOut)
def get_task(
    task_id: UUID,
    current_user = Depends(require_permission("task.read")),
    db: Session = Depends(get_db),
):
    return _get_task_or_404(_service(db), task_id)


@router.patch("/{task_id}", response_model=TaskOut)
def update_task(
    task_id: UUID,
    payload: TaskUpdate,
    current_user = Depends(require_permission("task.update")),
    db: Session = Depends(get_db),
):
    service = _service(db)
    task = _get_task_or_404(service, task_id)
    result = service.update_task(task, payload, db=db, current_user=current_user)
    db.commit()
    return result


@router.post("/{task_id}/complete", response_model=TaskOut)
def complete_task(
    task_id: UUID,
    payload: TaskCompleteRequest | None = None,
    current_user = Depends(require_permission("task.complete")),
    db: Session = Depends(get_db),
):
    service = _service(db)
    task = _get_task_or_404(service, task_id)
    result = service.complete_task(task, payload or TaskCompleteRequest(), db=db, current_user=current_user)
    db.commit()
    return result
