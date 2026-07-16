from fastapi import APIRouter
from .health_controller import get_health_response

router = APIRouter()


@router.get("/health")
def health_check() -> dict:
    return get_health_response()
