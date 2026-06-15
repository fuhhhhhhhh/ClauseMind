"""Review APIs: full multi-agent review, task queries, agent logs, results."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_active_user, get_db
from app.core.exceptions import AppError
from app.core.response import success
from app.models.review_task import ReviewTask
from app.models.user import User
from app.schemas.review import (
    AgentExecutionLogResponse,
    ReviewTaskDetailResponse,
    ReviewTaskResponse,
)
from app.services.review_service import ReviewService

router = APIRouter()

# ══════════════════════════════════════════════════════════════════════════════
# Review endpoints
# ══════════════════════════════════════════════════════════════════════════════


@router.post("/contracts/{contract_id}/review")
async def start_full_review(
    contract_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Run the full 6-agent review workflow."""
    svc = ReviewService(db)
    try:
        result = await svc.run_full_review(contract_id, current_user.id)
    except AppError:
        raise
    except Exception as exc:
        raise AppError(f"审查失败: {exc}", code=500, status_code=500)

    return success(
        {
            "task": ReviewTaskResponse.model_validate(result["task"]).model_dump(),
            "profile": result.get("profile"),
        },
        "审查任务已启动",
    )


@router.post("/contracts/{contract_id}/review/profile")
async def start_profile_review(
    contract_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Run only ContractProfileAgent."""
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


# ══════════════════════════════════════════════════════════════════════════════
# Task query endpoints
# ══════════════════════════════════════════════════════════════════════════════


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


@router.get("/review-tasks/{task_id}/progress")
def get_review_progress(
    task_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    svc = ReviewService(db)
    task = svc.get_task(task_id, current_user.id)
    logs = svc.get_agent_logs(task_id, current_user.id)
    return success(
        {
            "task": ReviewTaskResponse.model_validate(task).model_dump(),
            "agent_logs": [
                AgentExecutionLogResponse.model_validate(log).model_dump()
                for log in logs
            ],
        },
        "获取审查进度成功",
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


@router.get("/review-tasks/{task_id}/clauses")
def get_review_clauses(
    task_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    svc = ReviewService(db)
    clauses = svc.get_clauses(task_id, current_user.id)
    return success(
        [c.model_dump() for c in clauses] if hasattr(clauses[0] if clauses else None, 'model_dump') else clauses,
        "获取条款列表成功",
    )


@router.get("/review-tasks/{task_id}/risks")
def get_review_risks(
    task_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    svc = ReviewService(db)
    risks = svc.get_risks(task_id, current_user.id)
    return success(risks, "获取风险列表成功")


@router.get("/review-tasks/{task_id}/suggestions")
def get_review_suggestions(
    task_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    svc = ReviewService(db)
    suggestions = svc.get_suggestions(task_id, current_user.id)
    return success(suggestions, "获取修改建议成功")


@router.get("/reports/{task_id}")
def get_review_report(
    task_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    svc = ReviewService(db)
    report = svc.get_report(task_id, current_user.id)
    if report is None:
        raise AppError("审查报告不存在或 Agent 未成功执行", code=404, status_code=404)
    return success(report, "获取审查报告成功")


# ══════════════════════════════════════════════════════════════════════════════
# Latest review for a contract
# ══════════════════════════════════════════════════════════════════════════════


@router.get("/contracts/{contract_id}/review/latest")
def get_latest_review(
    contract_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Get the most recent ReviewTask for a contract (own contracts only)."""
    svc = ReviewService(db)
    task = svc.get_latest_task(contract_id, current_user.id)
    if task is None:
        return success(None, "该合同尚未审查")
    return success(
        ReviewTaskResponse.model_validate(task).model_dump(),
        "获取最近审查任务成功",
    )
