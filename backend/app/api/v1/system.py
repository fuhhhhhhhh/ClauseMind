from fastapi import APIRouter

from app.core.config import settings
from app.core.response import success

router = APIRouter()


@router.get("/config")
def get_public_config():
    return success(settings.public_config())
