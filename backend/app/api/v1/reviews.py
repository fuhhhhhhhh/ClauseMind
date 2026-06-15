"""Review APIs: start profile review, get task, get logs, get profile result."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_active_user, get_db
from app.core.exceptions import AppError
from app.core.response import success
from app.models.user import User
from app.schemas.review import (
    AgentExecutionLogResponse,
    ReviewTaskDetailResponse,
    ReviewTaskResponse,
)
from app.services.review_service import ReviewService

router = APIRouter()


# ── POST /api/v1/contracts/{contract_id}/review/profile ──────────────────────


@router.post("/contracts/{contract_id}/review/profile")
async def start_profile_review(
    contract_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    svc = ReviewService(db)
    try:
        result = await svc.run_profile_review(contract_id, current_user.id)
    except AppError:
        raise
    except Exception as exc:
        raise AppError(f"画像审查失败: {exc}", code=500, status_code=500)

    return success(
        {
            "task": ReviewTaskResponse.model_validate(result["task"]).model_dump(),
            "profile": result["profile"],
        },
        "合同画像审查完成",
    )


# ── GET /api/v1/review-tasks/{task_id} ───────────────────────────────────────


@router.get("/review-tasks/{task_id}")
def get_review_task(
    task_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    svc = ReviewService(db)
    task = svc.get_task(task_id, current_user.id)
    return success(
        ReviewTaskResponse.model_validate(task).model_dump(),
        "获取审查任务成功",
    )


@router.get("/review-tasks/{task_id}/agent-logs")
def get_agent_logs(
    task_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    svc = ReviewService(db)
    logs = svc.get_agent_logs(task_id, current_user.id)
    return success(
        [
            AgentExecutionLogResponse.model_validate(log).model_dump()
            for log in logs
        ],
        "获取 Agent 日志成功",
    )


@router.get("/review-tasks/{task_id}/profile")
def get_profile_result(
    task_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    svc = ReviewService(db)
    profile = svc.get_profile_result(task_id, current_user.id)
    if profile is None:
        raise AppError("画像结果不存在或 Agent 未成功执行", code=404, status_code=404)
    return success(profile, "获取合同画像成功")


# ── Placeholder routes for future phases (kept to avoid breaking router) ─────


@router.post("/contracts/{contract_id}/review")
def start_review_placeholder(contract_id: int):
    return success(
        {"contract_id": contract_id, "implemented": False},
        "审查任务接口骨架已创建",
    )


@router.get("/review-tasks/{task_id}/progress")
def review_progress_placeholder(task_id: int):
    return success(
        {"task_id": task_id, "steps": [], "implemented": False},
    )


@router.get("/review-tasks/{task_id}/clauses")
def clauses_placeholder(task_id: int):
    return success({"task_id": task_id, "items": [], "implemented": False})


@router.get("/review-tasks/{task_id}/risks")
def risks_placeholder(task_id: int):
    return success({"task_id": task_id, "items": [], "implemented": False})


@router.get("/review-tasks/{task_id}/suggestions")
def suggestions_placeholder(task_id: int):
    return success({"task_id": task_id, "items": [], "implemented": False})
