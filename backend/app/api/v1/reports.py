"""Report APIs: export report as Markdown file."""

from fastapi import APIRouter, Depends
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.api.deps import get_current_active_user, get_db
from app.core.exceptions import AppError
from app.core.response import success
from app.models.review_results import ReviewReport
from app.models.review_task import ReviewTask
from app.models.user import User

router = APIRouter()


@router.get("/{task_id}/export")
def export_report(
    task_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Export the review report as a Markdown file."""
    task = db.query(ReviewTask).filter(ReviewTask.id == task_id).first()
    if not task:
        raise AppError("审查任务不存在", code=404, status_code=404)
    if task.user_id != current_user.id:
        raise AppError("无权访问该报告", code=403, status_code=403)

    report = db.query(ReviewReport).filter(ReviewReport.task_id == task_id).first()
    if not report:
        raise AppError("审查报告不存在", code=404, status_code=404)

    content = report.markdown_report or ""
    if report.disclaimer:
        content += f"\n\n---\n\n{report.disclaimer}"

    return Response(
        content=content,
        media_type="text/markdown; charset=utf-8",
        headers={
            "Content-Disposition": f"attachment; filename=clausemind-report-{task_id}.md"
        },
    )


# Placeholder — real report query is in reviews.py
@router.get("/{task_id}")
def report_placeholder(task_id: int):
    return success(None, "报告查询请使用 GET /api/v1/review-tasks/{task_id} 或 GET /api/v1/reports/{task_id}/export")
