"""Pydantic schemas for contract module."""

from datetime import datetime

from pydantic import BaseModel, Field


class ContractCreate(BaseModel):
    """Request schema for contract upload."""

    contract_type: str | None = Field(default=None, max_length=64)


class ContractResponse(BaseModel):
    """Response schema for a single contract."""

    id: int
    user_id: int
    file_name: str
    stored_file_name: str
    file_type: str
    file_size: int | None
    contract_type: str | None
    title: str | None
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ContractListItem(BaseModel):
    """Response schema for a contract in a list."""

    id: int
    file_name: str
    file_type: str
    file_size: int | None
    contract_type: str | None
    title: str | None
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}


class ContractListResponse(BaseModel):
    """Response schema for the contract list endpoint."""

    items: list[ContractListItem]
    total: int
