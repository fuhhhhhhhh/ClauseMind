"""Report APIs: query and export review reports."""

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


def _get_own_report(task_id: int, user_id: int, db: Session) -> ReviewReport:
    """Fetch a report, verify task ownership."""
    task = db.query(ReviewTask).filter(ReviewTask.id == task_id).first()
    if not task:
        raise AppError("审查任务不存在", code=404, status_code=404)
    if task.user_id != user_id:
        raise AppError("无权访问该报告", code=403, status_code=403)
    report = db.query(ReviewReport).filter(ReviewReport.task_id == task_id).first()
    if not report:
        raise AppError("审查报告不存在", code=404, status_code=404)
    return report


@router.get("/{task_id}")
def get_report(
    task_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    report = _get_own_report(task_id, current_user.id, db)
    return success(
        {
            "id": report.id,
            "task_id": report.task_id,
            "report_title": report.report_title,
            "overall_risk": report.overall_risk,
            "markdown_report": report.markdown_report,
            "disclaimer": report.disclaimer,
        },
        "获取审查报告成功",
    )


@router.get("/{task_id}/export")
def export_report_md(
    task_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Export the review report as a Markdown file."""
    report = _get_own_report(task_id, current_user.id, db)

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


@router.get("/{task_id}/export/html")
def export_report_html(
    task_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Export the review report as an HTML file."""
    report = _get_own_report(task_id, current_user.id, db)

    # Simple markdown-to-HTML conversion
    md_text = report.markdown_report or ""
    html_body = _md_to_html(md_text)

    title = report.report_title or "审查报告"
    overall_risk = report.overall_risk or "-"
    disclaimer = report.disclaimer or ""

    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<title>{title}</title>
<style>
body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; max-width: 800px; margin: 40px auto; padding: 0 20px; color: #1f2328; }}
h1 {{ font-size: 24px; border-bottom: 2px solid #1f6feb; padding-bottom: 8px; }}
h2 {{ font-size: 20px; margin-top: 24px; }}
.meta {{ background: #f5f7fb; padding: 12px 16px; border-radius: 6px; margin: 12px 0; }}
.disclaimer {{ background: #fff3cd; border: 1px solid #ffc107; padding: 12px 16px; border-radius: 6px; margin-top: 32px; font-size: 14px; color: #856404; }}
table {{ border-collapse: collapse; width: 100%; }}
th, td {{ border: 1px solid #d8dee8; padding: 8px 12px; text-align: left; }}
th {{ background: #f5f7fb; }}
pre, code {{ background: #f5f5f5; padding: 2px 6px; border-radius: 4px; }}
</style>
</head>
<body>
<h1>{title}</h1>
<div class="meta">
  <p><strong>综合风险等级：</strong>{overall_risk}</p>
</div>
{html_body}
<div class="disclaimer">{disclaimer}</div>
</body>
</html>"""

    return Response(
        content=html,
        media_type="text/html; charset=utf-8",
        headers={
            "Content-Disposition": f"attachment; filename=clausemind-report-{task_id}.html"
        },
    )


def _md_to_html(md: str) -> str:
    """Minimal markdown-to-HTML converter supporting headings, paragraphs, lists, bold, code."""
    import re

    lines = md.split("\n")
    out = []
    i = 0
    in_list = False

    while i < len(lines):
        line = lines[i]

        # headings
        m = re.match(r"^(#{1,6})\s+(.+)$", line)
        if m:
            if in_list:
                out.append("</ul>")
                in_list = False
            level = len(m.group(1))
            out.append(f"<h{level}>{_inline_md(m.group(2))}</h{level}>")
            i += 1
            continue

        # unordered list
        m = re.match(r"^[-*]\s+(.+)$", line)
        if m:
            if not in_list:
                out.append("<ul>")
                in_list = True
            out.append(f"<li>{_inline_md(m.group(1))}</li>")
            i += 1
            continue

        # close list if open
        if in_list and line.strip():
            out.append("</ul>")
            in_list = False

        # blank line → paragraph break
        if not line.strip():
            if in_list:
                out.append("</ul>")
                in_list = False
            i += 1
            continue

        # regular paragraph
        if in_list:
            out.append("</ul>")
            in_list = False
        out.append(f"<p>{_inline_md(line)}</p>")
        i += 1

    if in_list:
        out.append("</ul>")

    return "\n".join(out)


def _inline_md(text: str) -> str:
    """Convert inline markdown: bold, code, italic."""
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
    text = re.sub(r"\*(.+?)\*", r"<em>\1</em>", text)
    return text
