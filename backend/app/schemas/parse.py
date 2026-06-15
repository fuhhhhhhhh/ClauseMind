"""Pydantic schemas for parse (MinerU) module."""

from datetime import datetime

from pydantic import BaseModel, Field


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
    markdown_path: str | None = None
    content_json_path: str | None = None
    middle_json_path: str | None = None
    layout_pdf_path: str | None = None
    image_dir: str | None = None
    normalized_json: str | None = None

    model_config = {"from_attributes": True}
