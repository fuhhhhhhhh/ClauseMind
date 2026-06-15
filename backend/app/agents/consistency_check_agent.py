"""ConsistencyCheckAgent – check cross-agent output consistency."""

from app.agents.base_agent import AgentError, BaseAgent

REQUIRED_FIELDS = ["passed", "issues"]


class ConsistencyCheckAgent(BaseAgent):
    name = "ConsistencyCheckAgent"
    prompt_file = "consistency_check_agent.txt"

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
        if not isinstance(output["issues"], list):
            raise AgentError(f"{self.name} issues 必须是 list")
