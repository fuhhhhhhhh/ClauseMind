from fastapi import APIRouter

from app.core.response import success

router = APIRouter()


@router.get("/{task_id}")
def report_placeholder(task_id: int):
    return success({"task_id": task_id, "markdown": "", "implemented": False})


@router.get("/{task_id}/export")
def export_report_placeholder(task_id: int):
    return success({"task_id": task_id, "implemented": False}, "报告导出接口骨架已创建")
