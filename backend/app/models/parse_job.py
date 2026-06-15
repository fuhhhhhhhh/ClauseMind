"""ParseJob model matching the project spec."""

from datetime import datetime, timezone

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class ParseJob(Base):
    __tablename__ = "parse_job"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    contract_id: Mapped[int] = mapped_column(ForeignKey("contract.id"), nullable=False, index=True)
    input_path: Mapped[str] = mapped_column(String(500), nullable=False)
    output_dir: Mapped[str | None] = mapped_column(String(500), nullable=True)
    backend: Mapped[str] = mapped_column(String(64), default="mineru", nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="WAITING")
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    started_at: Mapped[datetime | None] = mapped_column(nullable=True)
    finished_at: Mapped[datetime | None] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc), nullable=False)


class DocumentParseResult(Base):
    __tablename__ = "document_parse_result"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    contract_id: Mapped[int] = mapped_column(ForeignKey("contract.id"), nullable=False, index=True)
    parse_job_id: Mapped[int] = mapped_column(ForeignKey("parse_job.id"), nullable=False)
    markdown_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    content_json_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    middle_json_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    layout_pdf_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    image_dir: Mapped[str | None] = mapped_column(String(500), nullable=True)
    raw_markdown: Mapped[str | None] = mapped_column(Text, nullable=True)
    normalized_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc), nullable=False)
