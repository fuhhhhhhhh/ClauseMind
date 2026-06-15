"""ContractProfileAgent – extract basic contract profile info."""

from app.agents.base_agent import AgentError, BaseAgent

REQUIRED_FIELDS = [
    "contract_type",
    "party_a",
    "party_b",
    "sign_date",
    "amount",
    "duration",
    "subject",
    "summary",
    "missing_fields",
]


class ContractProfileAgent(BaseAgent):
    name = "ContractProfileAgent"
    prompt_file = "contract_profile_agent.txt"

    async def run(self, input_data: dict) -> dict:
        """Run the agent and validate the output against the expected schema."""
        output = await super().run(input_data)
        self.validate(output)
        return output

    def validate(self, output: dict) -> None:
        """Validate output has all required fields and correct types."""
        if not isinstance(output, dict):
            raise AgentError(
                f"{self.name} 输出必须是 JSON 对象，实际: {type(output).__name__}"
            )

        for field in REQUIRED_FIELDS:
            if field not in output:
                raise AgentError(
                    f"{self.name} 输出缺少必需字段: {field}"
                )

        if not isinstance(output.get("missing_fields"), list):
            raise AgentError(
                f"{self.name} missing_fields 必须是 list，实际: "
                f"{type(output.get('missing_fields')).__name__}"
            )
