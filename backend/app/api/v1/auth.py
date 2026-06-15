from fastapi import APIRouter

from app.core.response import success

router = APIRouter()


@router.post("/register")
def register_placeholder():
    return success({"implemented": False}, "注册接口骨架已创建")


@router.post("/login")
def login_placeholder():
    return success({"implemented": False}, "登录接口骨架已创建")


@router.get("/me")
def me_placeholder():
    return success({"implemented": False}, "当前用户接口骨架已创建")
