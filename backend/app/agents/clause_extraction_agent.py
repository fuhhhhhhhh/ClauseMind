"""ClauseExtractionAgent – extract key clauses from contract document."""

from app.agents.base_agent import AgentError, BaseAgent

REQUIRED_FIELDS = ["clauses"]


class ClauseExtractionAgent(BaseAgent):
    name = "ClauseExtractionAgent"
    prompt_file = "clause_extraction_agent.txt"

    async def run(self, input_data: dict) -> dict:
        output = await super().run(input_data)
        self.validate(output)
        return output

    def validate(self, output: dict) -> None:
        if not isinstance(output, dict):
            raise AgentError(f"{self.name} 输出必须是 JSON 对象")
        if "clauses" not in output:
            raise AgentError(f"{self.name} 输出缺少必需字段: clauses")
        if not isinstance(output["clauses"], list):
            raise AgentError(f"{self.name} clauses 必须是 list")
