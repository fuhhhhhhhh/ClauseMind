import json
import re
from pathlib import Path

from app.agents.llm_client import LLMClient


class BaseAgent:
    name = "BaseAgent"
    prompt_file = ""

    def __init__(self, llm_client: LLMClient | None = None) -> None:
        self.llm_client = llm_client or LLMClient()

    async def run(self, input_data: dict) -> dict:
        prompt = self.build_prompt(input_data)
        raw_output = await self.llm_client.chat(prompt)
        return self.parse_json(raw_output)

    def build_prompt(self, input_data: dict) -> str:
        template = self.load_prompt()
        return template.replace("{{input_json}}", json.dumps(input_data, ensure_ascii=False, indent=2))

    def load_prompt(self) -> str:
        path = Path(__file__).resolve().parents[1] / "prompts" / self.prompt_file
        return path.read_text(encoding="utf-8")

    def parse_json(self, raw_output: str) -> dict:
        try:
            return json.loads(raw_output)
        except json.JSONDecodeError:
            match = re.search(r"\{.*\}", raw_output, flags=re.DOTALL)
            if not match:
                raise
            return json.loads(match.group(0))
