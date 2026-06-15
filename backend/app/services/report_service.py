DISCLAIMER = "本报告由 AI 系统自动生成，仅用于合同阅读辅助和风险提示，不构成正式法律意见。重要合同请咨询专业律师或法律顾问。"


class ReportService:
    def empty_report(self) -> dict:
        return {
            "report_title": "合同智能审查报告",
            "overall_risk": None,
            "summary": "",
            "risk_statistics": {"high": 0, "medium": 0, "low": 0},
            "markdown_report": "",
            "disclaimer": DISCLAIMER,
        }
