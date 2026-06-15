"""ReportGenerationAgent – generate final review report with disclaimer."""

from app.agents.base_agent import AgentError, BaseAgent

REQUIRED_FIELDS = ["report_title", "overall_risk", "markdown_report", "disclaimer"]
REQUIRED_DISCLAIMER = (
    "本报告由 AI 系统自动生成，仅用于合同阅读辅助和风险提示，"
    "不构成正式法律意见。重要合同请咨询专业律师或法律顾问。"
)


class ReportGenerationAgent(BaseAgent):
    name = "ReportGenerationAgent"
    prompt_file = "report_generation_agent.txt"

    async def run(self, input_data: dict) -> dict:
        output = await super().run(input_data)
        self.validate(output)
        return output

    def validate(self, output: dict) -> None:
        if not isinstance(output, dict):
            raise AgentError(f"{self.name} 输出必须是 JSON 对象")
        for field in REQUIRED_FIELDS:
            if field not in output:
                raise AgentError(f"{self.name} 输出缺少必需字段: {field}")
        # Ensure disclaimer is present
        disclaimer = output.get("disclaimer", "")
        if not disclaimer or "不构成正式法律意见" not in disclaimer:
            output["disclaimer"] = REQUIRED_DISCLAIMER
