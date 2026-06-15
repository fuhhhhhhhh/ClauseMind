from fastapi import APIRouter

from app.core.response import success

router = APIRouter()


@router.get("/users")
def admin_users_placeholder():
    return success({"items": [], "implemented": False})


@router.get("/contracts")
def admin_contracts_placeholder():
    return success({"items": [], "implemented": False})


@router.get("/review-tasks")
def admin_review_tasks_placeholder():
    return success({"items": [], "implemented": False})


@router.get("/agent-logs")
def admin_agent_logs_placeholder():
    return success({"items": [], "implemented": False})


@router.get("/statistics")
def admin_statistics_placeholder():
    return success({"contracts": 0, "reviews": 0, "risks": 0, "implemented": False})
