from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_active_user, get_db
from app.core.response import success
from app.core.security import create_access_token, hash_password, verify_password
from app.models.user import User
from app.schemas.auth import (
    TokenResponse,
    UserLoginRequest,
    UserRegisterRequest,
    UserResponse,
)

router = APIRouter()


@router.post("/register")
def register(payload: UserRegisterRequest, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.username == payload.username).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="用户名已存在",
        )

    user = User(
        username=payload.username,
        password_hash=hash_password(payload.password),
        email=payload.email,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token(user.id)

    return success(
        {
            "user": UserResponse.model_validate(user).model_dump(),
            "access_token": token,
            "token_type": "bearer",
        },
        "注册成功",
    )


@router.post("/login")
def login(payload: UserLoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == payload.username).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
        )

    token = create_access_token(user.id)

    return success(
        {
            "user": UserResponse.model_validate(user).model_dump(),
            "access_token": token,
            "token_type": "bearer",
        },
        "登录成功",
    )


@router.get("/me")
def me(current_user: User = Depends(get_current_active_user)):
    return success(
        UserResponse.model_validate(current_user).model_dump(),
        "获取用户信息成功",
    )
