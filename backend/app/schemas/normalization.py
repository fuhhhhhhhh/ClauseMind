"""Pydantic schemas for document normalization module."""

from pydantic import BaseModel


class NormalizedSection(BaseModel):
    id: str
    title: str
    order_index: int
    clause_ids: list[str] = []


class NormalizedClause(BaseModel):
    id: str
    section_id: str
    title: str
    text: str
    order_index: int
    clause_type: str | None = None
    page_number: int | None = None
    source: str | None = None


class NormalizedParty(BaseModel):
    name: str
    role: str
    source: str | None = None


class NormalizedTable(BaseModel):
    table_id: str
    html: str | None = None
    page: int | None = None
    caption: str | None = None


class NormalizedMetadata(BaseModel):
    parse_engine: str
    content_json_available: bool = False


class NormalizationResult(BaseModel):
    title: str | None = None
    contract_type: str | None = None
    parties: list[NormalizedParty] = []
    sections: list[NormalizedSection] = []
    clauses: list[NormalizedClause] = []
    tables: list[NormalizedTable] = []
    metadata: NormalizedMetadata = NormalizedMetadata(parse_engine="mineru")
