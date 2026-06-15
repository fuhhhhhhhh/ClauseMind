from fastapi import APIRouter

from app.core.response import success

router = APIRouter()


@router.post("/contracts/{contract_id}/review")
def start_review_placeholder(contract_id: int):
    return success({"contract_id": contract_id, "implemented": False}, "审查任务接口骨架已创建")


@router.get("/review-tasks/{task_id}")
def review_task_placeholder(task_id: int):
    return success({"task_id": task_id, "implemented": False})


@router.get("/review-tasks/{task_id}/progress")
def review_progress_placeholder(task_id: int):
    return success({"task_id": task_id, "steps": [], "implemented": False})


@router.get("/review-tasks/{task_id}/agent-logs")
def agent_logs_placeholder(task_id: int):
    return success({"task_id": task_id, "items": [], "implemented": False})


@router.get("/review-tasks/{task_id}/profile")
def profile_placeholder(task_id: int):
    return success({"task_id": task_id, "profile": None, "implemented": False})


@router.get("/review-tasks/{task_id}/clauses")
def clauses_placeholder(task_id: int):
    return success({"task_id": task_id, "items": [], "implemented": False})


@router.get("/review-tasks/{task_id}/risks")
def risks_placeholder(task_id: int):
    return success({"task_id": task_id, "items": [], "implemented": False})


@router.get("/review-tasks/{task_id}/suggestions")
def suggestions_placeholder(task_id: int):
    return success({"task_id": task_id, "items": [], "implemented": False})
