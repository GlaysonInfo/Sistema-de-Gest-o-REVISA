from fastapi import APIRouter

router = APIRouter()


@router.get("")
def list_users() -> list[dict]:
    return []


@router.post("", status_code=201)
def create_user() -> dict:
    return {"status": "created"}
