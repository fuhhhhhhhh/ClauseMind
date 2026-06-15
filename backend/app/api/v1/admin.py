"""Admin APIs — require get_current_admin_user."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_admin_user, get_db
from app.core.response import success
from app.models.contract import Contract
from app.models.review_results import RiskItem
from app.models.review_task import AgentExecutionLog, ReviewTask
from app.models.user import User

router = APIRouter()


# ── GET /api/v1/admin/users ──────────────────────────────────────────────────


@router.get("/users")
def admin_users(
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    users = db.query(User).order_by(User.created_at.desc()).all()
    return success(
        [
            {
                "id": u.id,
                "username": u.username,
                "email": u.email,
                "role": u.role,
                "status": u.status,
                "created_at": u.created_at.isoformat() if u.created_at else None,
            }
            for u in users
        ],
        "获取用户列表成功",
    )


# ── GET /api/v1/admin/contracts ──────────────────────────────────────────────


@router.get("/contracts")
def admin_contracts(
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    contracts = db.query(Contract).order_by(Contract.created_at.desc()).all()
    return success(
        [
            {
                "id": c.id,
                "user_id": c.user_id,
                "file_name": c.file_name,
                "contract_type": c.contract_type,
                "status": c.status,
                "created_at": c.created_at.isoformat() if c.created_at else None,
                "updated_at": c.updated_at.isoformat() if c.updated_at else None,
            }
            for c in contracts
        ],
        "获取合同列表成功",
    )


# ── GET /api/v1/admin/review-tasks ───────────────────────────────────────────


@router.get("/review-tasks")
def admin_review_tasks(
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    tasks = db.query(ReviewTask).order_by(ReviewTask.created_at.desc()).all()
    return success(
        [
            {
                "id": t.id,
                "contract_id": t.contract_id,
                "user_id": t.user_id,
                "status": t.status,
                "current_step": t.current_step,
                "error_message": t.error_message,
                "started_at": t.started_at.isoformat() if t.started_at else None,
                "finished_at": t.finished_at.isoformat() if t.finished_at else None,
                "created_at": t.created_at.isoformat() if t.created_at else None,
            }
            for t in tasks
        ],
        "获取审查任务列表成功",
    )


# ── GET /api/v1/admin/agent-logs ─────────────────────────────────────────────


@router.get("/agent-logs")
def admin_agent_logs(
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    logs = db.query(AgentExecutionLog).order_by(AgentExecutionLog.id.desc()).all()
    return success(
        [
            {
                "id": log.id,
                "task_id": log.task_id,
                "contract_id": log.contract_id,
                "agent_name": log.agent_name,
                "status": log.status,
                "error_message": log.error_message,
                "duration_ms": log.duration_ms,
                "started_at": log.started_at.isoformat() if log.started_at else None,
                "finished_at": log.finished_at.isoformat() if log.finished_at else None,
            }
            for log in logs
        ],
        "获取 Agent 日志列表成功",
    )


@router.get("/agent-logs/{log_id}")
def admin_agent_log_detail(
    log_id: int,
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    log = db.query(AgentExecutionLog).filter(AgentExecutionLog.id == log_id).first()
    if not log:
        return success(None, "日志不存在")
    return success(
        {
            "id": log.id,
            "task_id": log.task_id,
            "contract_id": log.contract_id,
            "agent_name": log.agent_name,
            "input_json": log.input_json,
            "output_json": log.output_json,
            "status": log.status,
            "error_message": log.error_message,
            "duration_ms": log.duration_ms,
            "started_at": log.started_at.isoformat() if log.started_at else None,
            "finished_at": log.finished_at.isoformat() if log.finished_at else None,
        },
        "获取 Agent 日志详情成功",
    )


# ── GET /api/v1/admin/statistics ─────────────────────────────────────────────


@router.get("/statistics")
def admin_statistics(
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    user_count = db.query(User).count()
    contract_count = db.query(Contract).count()
    review_task_count = db.query(ReviewTask).count()
    completed_review_count = db.query(ReviewTask).filter(ReviewTask.status == "SUCCESS").count()
    failed_review_count = db.query(ReviewTask).filter(ReviewTask.status == "FAILED").count()
    high_risk_count = db.query(RiskItem).filter(RiskItem.risk_level == "高风险").count()
    medium_risk_count = db.query(RiskItem).filter(RiskItem.risk_level == "中风险").count()
    low_risk_count = db.query(RiskItem).filter(RiskItem.risk_level == "低风险").count()

    recent_tasks = (
        db.query(ReviewTask)
        .order_by(ReviewTask.created_at.desc())
        .limit(5)
        .all()
    )

    return success(
        {
            "user_count": user_count,
            "contract_count": contract_count,
            "review_task_count": review_task_count,
            "completed_review_count": completed_review_count,
            "failed_review_count": failed_review_count,
            "high_risk_count": high_risk_count,
            "risk_level_counts": {
                "high": high_risk_count,
                "medium": medium_risk_count,
                "low": low_risk_count,
            },
            "recent_review_tasks": [
                {
                    "id": t.id,
                    "contract_id": t.contract_id,
                    "status": t.status,
                    "created_at": t.created_at.isoformat() if t.created_at else None,
                }
                for t in recent_tasks
            ],
        },
        "获取系统统计成功",
    )
