"""Pydantic schemas for auth module."""

from datetime import datetime

from pydantic import BaseModel, Field


class UserRegisterRequest(BaseModel):
    username: str = Field(min_length=2, max_length=64)
    email: str | None = Field(default=None, max_length=128)
    password: str = Field(min_length=6, max_length=128)


class UserLoginRequest(BaseModel):
    username: str = Field(min_length=1)
    password: str = Field(min_length=1)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    id: int
    username: str
    email: str | None
    role: str
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}
