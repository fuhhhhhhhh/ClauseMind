"""Pydantic schemas for parse (MinerU) module."""

from datetime import datetime

from pydantic import BaseModel


class ParseJobResponse(BaseModel):
    id: int
    contract_id: int
    backend: str
    status: str
    error_message: str | None = None
    started_at: datetime | None = None
    finished_at: datetime | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class ParseStatusResponse(BaseModel):
    contract_id: int
    contract_status: str
    parse_job: ParseJobResponse | None = None


class DocumentParseResultResponse(BaseModel):
    parse_job: ParseJobResponse
    raw_markdown: str | None = None
    normalized_json: str | None = None
    # Safety: never expose server internal paths to frontend.
    # Use boolean flags to indicate output file presence instead.
    has_markdown: bool = False
    has_content_json: bool = False
    has_middle_json: bool = False
    has_layout_pdf: bool = False
    has_images: bool = False

    model_config = {"from_attributes": True}
