from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps.permissions import require_permission
from app.core.database import get_db
from app.domain.mobile.repository import MobileIntakeRepository
from app.domain.mobile.schemas import MobileIntakeCreate, MobileIntakeOut
from app.domain.mobile.service import MobileIntakeService

router = APIRouter()


def _service(db: Session) -> MobileIntakeService:
    return MobileIntakeService(MobileIntakeRepository(db))


@router.post("/intakes", response_model=MobileIntakeOut, status_code=201)
def create_mobile_intake(
    payload: MobileIntakeCreate,
    current_user = Depends(require_permission("capture.create")),
    db: Session = Depends(get_db),
):
    try:
        result = _service(db).create_intake(
            captured_by_user_id=current_user.id,
            payload=payload,
            db=db,
            current_user=current_user,
        )
    except LookupError as exc:
        detail_by_code = {
            "polo_required": "Polo obrigatorio para captacao de beneficiario",
            "polo_not_found": "Polo nao encontrado",
        }
        detail = detail_by_code.get(str(exc), "Registro nao encontrado")
        status_code = status.HTTP_422_UNPROCESSABLE_ENTITY if str(exc) == "polo_required" else status.HTTP_404_NOT_FOUND
        raise HTTPException(status_code=status_code, detail=detail)
    db.commit()
    return result
