"""MinerU parse APIs: start parse, check status, get result."""

from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_active_user, get_db
from app.core.config import settings
from app.core.exceptions import AppError
from app.core.response import success
from app.models.contract import Contract
from app.models.parse_job import DocumentParseResult, ParseJob
from app.models.user import User
from app.schemas.parse import (
    DocumentParseResultResponse,
    ParseJobResponse,
    ParseStatusResponse,
)
from app.services.mineru_service import MinerUService

router = APIRouter()
mineru = MinerUService()


def _get_own_contract(contract_id: int, user: User, db: Session) -> Contract:
    """Fetch a contract, ensure it belongs to *user*, raise 404/403 otherwise."""
    contract = db.query(Contract).filter(Contract.id == contract_id).first()
    if not contract:
        raise AppError("合同不存在", code=404, status_code=404)
    if contract.user_id != user.id:
        raise AppError("无权访问该合同", code=403, status_code=403)
    return contract


@router.post("/{contract_id}/parse")
def start_parse(
    contract_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    contract = _get_own_contract(contract_id, current_user, db)

    # Idempotency: already PARSED or PARSING
    if contract.status == "PARSING":
        raise AppError("合同正在解析中，请稍后再试", code=409, status_code=409)
    if contract.status == "PARSED":
        raise AppError("合同已解析完成", code=409, status_code=409)

    # Create output directory inside mineru_output/
    session_dir = settings.mineru_output_dir / str(contract_id) / uuid4().hex
    session_dir.mkdir(parents=True, exist_ok=True)

    # Create ParseJob
    job = ParseJob(
        contract_id=contract.id,
        input_path=contract.file_path,
        output_dir=str(session_dir),
        backend=settings.mineru_backend,
        status="RUNNING",
        started_at=datetime.now(timezone.utc),
    )
    db.add(job)
    contract.status = "PARSING"
    db.commit()
    db.refresh(job)

    # --- Run MinerU synchronously ---
    try:
        outputs = mineru.parse(contract.file_path, session_dir)
    except AppError as exc:
        job.status = "FAILED"
        job.error_message = exc.message
        job.finished_at = datetime.now(timezone.utc)
        contract.status = "FAILED"
        db.commit()
        raise  # re-raise to return error to client

    # Save result
    result = DocumentParseResult(
        contract_id=contract.id,
        parse_job_id=job.id,
        markdown_path=outputs.get("markdown_path"),
        content_json_path=outputs.get("content_json_path"),
        middle_json_path=outputs.get("middle_json_path"),
        layout_pdf_path=outputs.get("layout_pdf_path"),
        image_dir=outputs.get("image_dir"),
        raw_markdown=outputs.get("raw_markdown"),
    )
    db.add(result)
    job.status = "SUCCESS"
    job.finished_at = datetime.now(timezone.utc)
    contract.status = "PARSED"
    db.commit()
    db.refresh(job)

    return success(
        ParseJobResponse.model_validate(job).model_dump(),
        "解析任务已启动",
    )


@router.get("/{contract_id}/parse-status")
def parse_status(
    contract_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    contract = _get_own_contract(contract_id, current_user, db)
    job = (
        db.query(ParseJob)
        .filter(ParseJob.contract_id == contract_id)
        .order_by(ParseJob.created_at.desc())
        .first()
    )
    return success(
        ParseStatusResponse(
            contract_id=contract.id,
            contract_status=contract.status,
            parse_job=ParseJobResponse.model_validate(job) if job else None,
        ).model_dump(),
        "获取解析状态成功",
    )


@router.get("/{contract_id}/parse-result")
def parse_result(
    contract_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    contract = _get_own_contract(contract_id, current_user, db)
    job = (
        db.query(ParseJob)
        .filter(ParseJob.contract_id == contract_id)
        .order_by(ParseJob.created_at.desc())
        .first()
    )
    if not job:
        raise AppError("该合同尚未解析", code=404, status_code=404)

    result = db.query(DocumentParseResult).filter(
        DocumentParseResult.parse_job_id == job.id
    ).first()

    return success(
        DocumentParseResultResponse(
            parse_job=ParseJobResponse.model_validate(job),
            raw_markdown=result.raw_markdown if result else None,
            markdown_path=result.markdown_path if result else None,
            content_json_path=result.content_json_path if result else None,
            middle_json_path=result.middle_json_path if result else None,
            layout_pdf_path=result.layout_pdf_path if result else None,
            image_dir=result.image_dir if result else None,
            normalized_json=result.normalized_json if result else None,
        ).model_dump(),
        "获取解析结果成功",
    )
