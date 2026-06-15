"""ContractClause, RiskItem, ModifySuggestion, ReviewReport models."""

from datetime import datetime, timezone

from sqlalchemy import Boolean, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class ContractClause(Base):
    __tablename__ = "contract_clause"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    task_id: Mapped[int] = mapped_column(ForeignKey("review_task.id"), nullable=False, index=True)
    contract_id: Mapped[int] = mapped_column(ForeignKey("contract.id"), nullable=False)
    clause_id: Mapped[str] = mapped_column(String(32), nullable=False)
    section_id: Mapped[str | None] = mapped_column(String(32), nullable=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    text: Mapped[str | None] = mapped_column(Text, nullable=True)
    clause_type: Mapped[str | None] = mapped_column(String(64), nullable=True)
    page_number: Mapped[int | None] = mapped_column(Integer, nullable=True)
    source_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc), nullable=False)


class RiskItem(Base):
    __tablename__ = "risk_item"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    task_id: Mapped[int] = mapped_column(ForeignKey("review_task.id"), nullable=False, index=True)
    contract_id: Mapped[int] = mapped_column(ForeignKey("contract.id"), nullable=False)
    risk_id: Mapped[str] = mapped_column(String(32), nullable=False)
    clause_id: Mapped[str | None] = mapped_column(String(32), nullable=True)
    risk_level: Mapped[str] = mapped_column(String(32), nullable=False)
    risk_type: Mapped[str] = mapped_column(String(128), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    suggestion: Mapped[str | None] = mapped_column(Text, nullable=True)
    need_human_review: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc), nullable=False)


class ModifySuggestion(Base):
    __tablename__ = "modify_suggestion"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    task_id: Mapped[int] = mapped_column(ForeignKey("review_task.id"), nullable=False, index=True)
    contract_id: Mapped[int] = mapped_column(ForeignKey("contract.id"), nullable=False)
    suggestion_id: Mapped[str] = mapped_column(String(32), nullable=False)
    risk_id: Mapped[str | None] = mapped_column(String(32), nullable=True)
    clause_id: Mapped[str | None] = mapped_column(String(32), nullable=True)
    original_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    suggested_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc), nullable=False)


class ReviewReport(Base):
    __tablename__ = "review_report"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    task_id: Mapped[int] = mapped_column(ForeignKey("review_task.id"), nullable=False, index=True)
    contract_id: Mapped[int] = mapped_column(ForeignKey("contract.id"), nullable=False)
    report_title: Mapped[str | None] = mapped_column(String(255), nullable=True)
    overall_risk: Mapped[str | None] = mapped_column(String(32), nullable=True)
    markdown_report: Mapped[str | None] = mapped_column(Text, nullable=True)
    disclaimer: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc), nullable=False)
