"""RiskDetectionAgent – identify risks in contract clauses."""

from app.agents.base_agent import AgentError, BaseAgent

REQUIRED_FIELDS = ["risks", "overall_risk"]


class RiskDetectionAgent(BaseAgent):
    name = "RiskDetectionAgent"
    prompt_file = "risk_detection_agent.txt"

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
        if not isinstance(output["risks"], list):
            raise AgentError(f"{self.name} risks 必须是 list")
