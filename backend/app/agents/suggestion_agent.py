"""SuggestionAgent – generate modification suggestions for risks."""

from app.agents.base_agent import AgentError, BaseAgent

REQUIRED_FIELDS = ["suggestions"]


class SuggestionAgent(BaseAgent):
    name = "SuggestionAgent"
    prompt_file = "suggestion_agent.txt"

    async def run(self, input_data: dict) -> dict:
        output = await super().run(input_data)
        self.validate(output)
        return output

    def validate(self, output: dict) -> None:
        if not isinstance(output, dict):
            raise AgentError(f"{self.name} 输出必须是 JSON 对象")
        if "suggestions" not in output:
            raise AgentError(f"{self.name} 输出缺少必需字段: suggestions")
        if not isinstance(output["suggestions"], list):
            raise AgentError(f"{self.name} suggestions 必须是 list")
