"""Demo seed script for ClauseMind.

Creates admin + demo users, a sample contract record with parse result,
normalized JSON, review task, agent execution logs, and review report.

Usage:
    cd backend
    uv run python scripts/seed_demo.py

Idempotent: running multiple times won't create duplicate users or contracts.
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import SessionLocal, engine
from app.core.security import hash_password
from app.models.contract import Contract
from app.models.parse_job import DocumentParseResult, ParseJob
from app.models.review_results import (
    ContractClause,
    ModifySuggestion,
    ReviewReport,
    RiskItem,
)
from app.models.review_task import AgentExecutionLog, ReviewTask
from app.models.user import User
from app.services.document_normalizer import DocumentNormalizer

# ── Demo data ────────────────────────────────────────────────────────────────

DEMO_USERS = [
    {"username": "admin", "password": "admin123456", "email": "admin@clausemind.local", "role": "admin"},
    {"username": "demo", "password": "demo123456", "email": "demo@clausemind.local", "role": "USER"},
]

SAMPLE_MARKDOWN = """\
# 房屋租赁合同

甲方：张三（身份证号：110101199001011234）
乙方：李四（身份证号：110101199202021234）

第一条 租赁房屋
甲方将位于北京市朝阳区某街道 100 号的房屋出租给乙方使用，房屋面积 80 平方米。

第二条 租赁期限
租赁期限自 2026 年 1 月 1 日至 2027 年 1 月 1 日，共计 12 个月。

第三条 租金及支付方式
月租金为人民币 3000 元整，乙方应于每月 5 日前将当月租金支付给甲方。
支付方式为银行转账，甲方收款账户信息另行提供。

第四条 押金
乙方应于本合同签订之日向甲方支付押金人民币 6000 元整。
租赁期满且乙方无违约行为的，甲方应在 7 日内退还押金。

第五条 违约责任
任何一方违反本合同约定的，应承担相应的违约责任。

第六条 争议解决
因本合同产生的争议，双方应协商解决；协商不成的，向房屋所在地人民法院提起诉讼。
"""

SAMPLE_PROFILE = {
    "contract_type": "房屋租赁合同",
    "party_a": "张三",
    "party_b": "李四",
    "sign_date": "2026-01-01",
    "amount": "3000元/月",
    "duration": "2026-01-01 至 2027-01-01",
    "subject": "房屋租赁",
    "summary": "张三将北京朝阳区房屋出租给李四，月租 3000 元，租期 12 个月。",
    "missing_fields": [],
}

SAMPLE_CLAUSES_OUTPUT = {
    "clauses": [
        {"clause_id": "C1", "clause_type": "主体条款", "title": "租赁房屋", "content": "甲方将位于北京市朝阳区...", "source_section_id": "S2", "page": 1, "status": "found"},
        {"clause_id": "C2", "clause_type": "履行条款", "title": "租赁期限", "content": "2026-01-01 至 2027-01-01", "source_section_id": "S3", "page": 1, "status": "found"},
        {"clause_id": "C3", "clause_type": "付款条款", "title": "租金及支付方式", "content": "月租金3000元，每月5日前支付", "source_section_id": "S4", "page": 1, "status": "found"},
        {"clause_id": "C4", "clause_type": "付款条款", "title": "押金", "content": "押金6000元", "source_section_id": "S5", "page": 1, "status": "found"},
        {"clause_id": "C5", "clause_type": "违约责任", "title": "违约责任", "content": "任何一方违约应承担相应违约责任", "source_section_id": "S6", "page": 1, "status": "found"},
        {"clause_id": "C6", "clause_type": "争议解决", "title": "争议解决", "content": "协商→房屋所在地法院诉讼", "source_section_id": "S7", "page": 1, "status": "found"},
    ],
    "missing_clause_types": ["解除条款", "保密条款", "不可抗力"],
}

SAMPLE_RISKS_OUTPUT = {
    "risks": [
        {"risk_id": "R1", "risk_level": "中风险", "risk_type": "违约责任模糊", "related_clause_id": "C5",
         "source_text": "任何一方违反本合同约定的，应承担相应的违约责任。",
         "reason": "违约责任条款过于笼统，未明确具体违约金金额、赔偿范围和计算方式。",
         "impact": "发生违约时可能难以确定赔偿标准，增加争议风险。",
         "need_human_review": True},
        {"risk_id": "R2", "risk_level": "低风险", "risk_type": "重要条款缺失", "related_clause_id": None,
         "source_text": "",
         "reason": "合同缺少解除条款和不可抗力条款。",
         "impact": "发生特殊情况时缺少处理依据。",
         "need_human_review": False},
    ],
    "overall_risk": "中风险",
}

SAMPLE_SUGGESTIONS_OUTPUT = {
    "suggestions": [
        {"suggestion_id": "SUG1", "risk_id": "R1",
         "original_text": "任何一方违反本合同约定的，应承担相应的违约责任。",
         "suggested_text": "任何一方违反本合同约定并给对方造成损失的，应赔偿因此产生的直接损失；如逾期付款，每逾期一日按未付款金额的 0.05% 支付违约金。",
         "reason": "建议明确违约责任承担方式、赔偿范围和计算标准。",
         "rewrite_type": "明确化"},
    ],
}

SAMPLE_CHECK_OUTPUT = {"passed": True, "issues": []}

SAMPLE_REPORT_OUTPUT = {
    "report_title": "房屋租赁合同智能审查报告",
    "overall_risk": "中风险",
    "summary": "本合同主体信息较明确，租金和期限条款清晰。但违约责任条款过于笼统，且缺少解除和不可抗力条款。建议在签署前完善相关条款。",
    "risk_statistics": {"high": 0, "medium": 1, "low": 1},
    "markdown_report": """\
# 房屋租赁合同智能审查报告

## 合同基本信息
- **合同类型**：房屋租赁合同
- **甲方**：张三
- **乙方**：李四
- **签署日期**：2026-01-01
- **合同金额**：3000元/月
- **合同期限**：2026-01-01 至 2027-01-01

## 风险总览
- 高风险：0 项
- 中风险：1 项
- 低风险：1 项

## 风险明细
### R1: 违约责任模糊（中风险）
违约责任条款过于笼统，未明确具体违约金金额、赔偿范围和计算方式。
建议明确违约责任承担方式、赔偿标准和计算方式。

### R2: 重要条款缺失（低风险）
合同缺少解除条款和不可抗力条款。建议补充。

## 修改建议
### SUG1: 违约责任明确化
- **原条款**：任何一方违反本合同约定的，应承担相应的违约责任。
- **建议修改为**：任何一方违反本合同约定并给对方造成损失的，应赔偿因此产生的直接损失；如逾期付款，每逾期一日按未付款金额的 0.05% 支付违约金。

## 审查结论
本合同整体风险等级为 **中风险**。建议在签署前：
1. 明确违约责任的具体金额和计算方式
2. 补充解除条款和不可抗力条款
3. 与对方协商完善争议解决机制的小细节
""",
    "disclaimer": "本报告由 AI 系统自动生成，仅用于合同阅读辅助和风险提示，不构成正式法律意见。重要合同请咨询专业律师或法律顾问。",
}

DISCLAIMER = "本报告由 AI 系统自动生成，仅用于合同阅读辅助和风险提示，不构成正式法律意见。重要合同请咨询专业律师或法律顾问。"

AGENT_NAMES = [
    "ContractProfileAgent",
    "ClauseExtractionAgent",
    "RiskDetectionAgent",
    "SuggestionAgent",
    "ConsistencyCheckAgent",
    "ReportGenerationAgent",
]

AGENT_OUTPUTS = [
    SAMPLE_PROFILE,
    SAMPLE_CLAUSES_OUTPUT,
    SAMPLE_RISKS_OUTPUT,
    SAMPLE_SUGGESTIONS_OUTPUT,
    SAMPLE_CHECK_OUTPUT,
    SAMPLE_REPORT_OUTPUT,
]


def ensure_users(db: Session) -> dict[str, User]:
    """Create demo users if they don't exist. Returns {username: User}."""
    result = {}
    for spec in DEMO_USERS:
        user = db.query(User).filter(User.username == spec["username"]).first()
        if user is None:
            user = User(
                username=spec["username"],
                password_hash=hash_password(spec["password"]),
                email=spec["email"],
                role=spec["role"],
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            print(f"  Created user: {spec['username']} / {spec['password']}")
        else:
            print(f"  User exists: {spec['username']}")
        result[spec["username"]] = user
    return result


def seed(db: Session) -> None:
    """Run the demo seeding."""
    print("=== ClauseMind Demo Seed ===")

    # 1. Users
    print("\n[1/5] Creating users...")
    users = ensure_users(db)
    demo_user = users["demo"]

    # 2. Contract
    print("\n[2/5] Creating demo contract...")
    contract = db.query(Contract).filter(
        Contract.user_id == demo_user.id,
        Contract.file_name == "demo-房屋租赁合同.pdf",
    ).first()
    if contract is None:
        contract = Contract(
            user_id=demo_user.id,
            file_name="demo-房屋租赁合同.pdf",
            stored_file_name="demo-seed-contract.pdf",
            file_path="/tmp/demo-seed-contract.pdf",
            file_type="pdf",
            file_size=1024,
            contract_type="房屋租赁合同",
            title="房屋租赁合同",
            status="COMPLETED",
        )
        db.add(contract)
        db.commit()
        db.refresh(contract)
        print(f"  Created contract: id={contract.id}")
    else:
        print(f"  Contract exists: id={contract.id}")

    # 3. Parse result + normalized JSON
    print("\n[3/5] Creating parse result + normalized JSON...")
    existing_job = db.query(ParseJob).filter(ParseJob.contract_id == contract.id).first()
    if existing_job is None:
        job = ParseJob(
            contract_id=contract.id,
            input_path="/tmp/demo-seed-contract.pdf",
            output_dir="/tmp/demo-mineru-output",
            status="SUCCESS",
            started_at=datetime.now(timezone.utc),
            finished_at=datetime.now(timezone.utc),
        )
        db.add(job)
        db.commit()
        db.refresh(job)

        normalizer = DocumentNormalizer()
        normalized = normalizer.normalize(SAMPLE_MARKDOWN)
        normalized_json = json.dumps(normalized, ensure_ascii=False)

        result = DocumentParseResult(
            contract_id=contract.id,
            parse_job_id=job.id,
            markdown_path="/tmp/demo-mineru-output/demo.md",
            raw_markdown=SAMPLE_MARKDOWN,
            normalized_json=normalized_json,
        )
        db.add(result)
        db.commit()
        print(f"  Created parse_job={job.id}, parse_result={result.id}")
    else:
        print(f"  Parse result exists: job_id={existing_job.id}")

    # 4. Review task
    print("\n[4/5] Creating review task + agent logs...")
    existing_task = db.query(ReviewTask).filter(ReviewTask.contract_id == contract.id).first()
    if existing_task is None:
        task = ReviewTask(
            contract_id=contract.id,
            user_id=demo_user.id,
            status="SUCCESS",
            current_step="ReportGenerationAgent",
            started_at=datetime.now(timezone.utc),
            finished_at=datetime.now(timezone.utc),
        )
        db.add(task)
        db.commit()
        db.refresh(task)

        # Agent execution logs
        for i, name in enumerate(AGENT_NAMES):
            log = AgentExecutionLog(
                task_id=task.id,
                contract_id=contract.id,
                agent_name=name,
                input_json=json.dumps({"contract_document": {"title": "房屋租赁合同"}}, ensure_ascii=False),
                output_json=json.dumps(AGENT_OUTPUTS[i], ensure_ascii=False),
                status="SUCCESS",
                duration_ms=1200 + i * 300,
                started_at=datetime.now(timezone.utc),
                finished_at=datetime.now(timezone.utc),
            )
            db.add(log)
        db.commit()
        print(f"  Created review_task={task.id} with {len(AGENT_NAMES)} agent logs")
    else:
        task = existing_task
        print(f"  Review task exists: id={task.id}")

    # 5. Clauses, risks, suggestions, report
    print("\n[5/5] Creating clauses/risks/suggestions/report...")

    existing_clause = db.query(ContractClause).filter(ContractClause.task_id == task.id).first()
    if existing_clause is None:
        for c in SAMPLE_CLAUSES_OUTPUT["clauses"]:
            db.add(ContractClause(
                task_id=task.id, contract_id=contract.id,
                clause_id=c["clause_id"], section_id=c.get("source_section_id", "S1"),
                title=c["title"], text=c["content"], clause_type=c["clause_type"],
                page_number=c.get("page"), source_text=c.get("content", ""),
            ))

        for r in SAMPLE_RISKS_OUTPUT["risks"]:
            db.add(RiskItem(
                task_id=task.id, contract_id=contract.id,
                risk_id=r["risk_id"], clause_id=r.get("related_clause_id"),
                risk_level=r["risk_level"], risk_type=r["risk_type"],
                description=r.get("impact", ""), reason=r["reason"],
                suggestion="", need_human_review=r.get("need_human_review", False),
            ))

        for s in SAMPLE_SUGGESTIONS_OUTPUT["suggestions"]:
            db.add(ModifySuggestion(
                task_id=task.id, contract_id=contract.id,
                suggestion_id=s["suggestion_id"], risk_id=s["risk_id"],
                original_text=s["original_text"], suggested_text=s["suggested_text"],
                reason=s["reason"],
            ))

        db.add(ReviewReport(
            task_id=task.id, contract_id=contract.id,
            report_title=SAMPLE_REPORT_OUTPUT["report_title"],
            overall_risk=SAMPLE_REPORT_OUTPUT["overall_risk"],
            markdown_report=SAMPLE_REPORT_OUTPUT["markdown_report"],
            disclaimer=DISCLAIMER,
        ))
        db.commit()
        n_clauses = db.query(ContractClause).filter(ContractClause.task_id == task.id).count()
        n_risks = db.query(RiskItem).filter(RiskItem.task_id == task.id).count()
        n_sug = db.query(ModifySuggestion).filter(ModifySuggestion.task_id == task.id).count()
        print(f"  Created {n_clauses} clauses, {n_risks} risks, {n_sug} suggestions, 1 report")
    else:
        print("  Results exist — skipping")

    print("\n=== Seed complete! ===")
    print("Demo accounts:")
    print("  Admin:  admin / admin123456")
    print("  User:   demo / demo123456")
    print(f"Demo contract ID: {contract.id}")
    print(f"Demo review task ID: {task.id}")


def main():
    db = SessionLocal()
    try:
        seed(db)
    finally:
        db.close()


if __name__ == "__main__":
    main()
