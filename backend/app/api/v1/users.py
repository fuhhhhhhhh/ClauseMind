from fastapi import APIRouter

from app.core.response import success

router = APIRouter()


@router.get("/me")
def current_user_placeholder():
    return success({"implemented": False}, "用户信息接口骨架已创建")
