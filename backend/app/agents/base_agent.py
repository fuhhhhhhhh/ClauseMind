"""Base agent with prompt loading, JSON parsing, and retry logic."""

import json
import re
from pathlib import Path

from app.agents.llm_client import LLMClient, LLMError


class AgentError(Exception):
    """Raised when an agent fails to produce valid output."""


class BaseAgent:
    name: str = "BaseAgent"
    prompt_file: str = ""

    def __init__(self, llm_client: LLMClient | None = None) -> None:
        self.llm_client = llm_client or LLMClient()

    async def run(self, input_data: dict) -> dict:
        """Run the agent: build prompt, call LLM, parse JSON with retry."""
        prompt = self.build_prompt(input_data)
        raw_output = await self._call_llm(prompt)

        try:
            return self.parse_json(raw_output)
        except (json.JSONDecodeError, ValueError) as first_error:
            # Retry once with explicit JSON instruction
            retry_prompt = (
                prompt
                + "\n\n【重要】上一次输出不是合法的 JSON，请严格只输出合法 JSON，不要添加任何解释、Markdown 代码块或前缀。"
            )
            try:
                retry_output = await self._call_llm(retry_prompt)
                return self.parse_json(retry_output)
            except (json.JSONDecodeError, ValueError) as second_error:
                raise AgentError(
                    f"Agent {self.name} JSON 解析失败（已重试1次）。"
                    f"首次错误: {first_error}。重试错误: {second_error}"
                ) from second_error

    async def _call_llm(self, prompt: str) -> str:
        """Call LLM and wrap errors as AgentError."""
        try:
            return await self.llm_client.chat(prompt)
        except LLMError as exc:
            raise AgentError(f"Agent {self.name} LLM 调用失败: {exc}") from exc

    def build_prompt(self, input_data: dict) -> str:
        """Build the full prompt from the template file and input data."""
        template = self.load_prompt()
        return template.replace(
            "{{input_json}}", json.dumps(input_data, ensure_ascii=False, indent=2)
        )

    def load_prompt(self) -> str:
        """Load the prompt template from the prompts directory."""
        path = Path(__file__).resolve().parents[1] / "prompts" / self.prompt_file
        return path.read_text(encoding="utf-8")

    def parse_json(self, raw_output: str) -> dict:
        """Parse JSON from LLM output, handling various formats.

        Supports:
        1. Pure JSON: {"key": "value"}
        2. Markdown fenced JSON: ```json ... ```
        3. Embedded JSON: extract first { ... } from text
        """
        text = raw_output.strip()

        # Method 1: pure JSON
        try:
            result = json.loads(text)
            if isinstance(result, dict):
                return result
        except (json.JSONDecodeError, ValueError):
            pass

        # Method 2: Markdown fenced JSON
        fence_match = re.search(r"```(?:json)?\s*\n?(.*?)\n?```", text, re.DOTALL)
        if fence_match:
            try:
                result = json.loads(fence_match.group(1).strip())
                if isinstance(result, dict):
                    return result
            except (json.JSONDecodeError, ValueError):
                pass

        # Method 3: extract first JSON object from text
        brace_match = re.search(r"\{.*\}", text, re.DOTALL)
        if brace_match:
            try:
                result = json.loads(brace_match.group(0))
                if isinstance(result, dict):
                    return result
            except (json.JSONDecodeError, ValueError):
                pass

        raise ValueError(f"无法从 LLM 输出中解析 JSON: {text[:200]}")
