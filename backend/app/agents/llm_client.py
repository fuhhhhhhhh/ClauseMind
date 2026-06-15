"""LLM client wrapping OpenAI-compatible Chat Completions API."""

from typing import Any

import httpx

from app.core.config import settings


class LLMError(Exception):
    """Raised when LLM API call fails."""


class LLMClient:
    """OpenAI-compatible Chat Completions client."""

    def __init__(
        self,
        api_base: str | None = None,
        api_key: str | None = None,
        model: str | None = None,
        timeout: int | None = None,
    ) -> None:
        self.api_base = (api_base or settings.llm_api_base).rstrip("/")
        self.api_key = api_key or settings.llm_api_key
        self.model = model or settings.llm_model
        self.timeout = timeout or settings.llm_timeout

    @property
    def chat_completions_url(self) -> str:
        """Normalize the base URL into a full chat/completions endpoint."""
        base = self.api_base
        if base.endswith("/chat/completions"):
            return base
        if base.endswith("/v1"):
            return f"{base}/chat/completions"
        parts = base.split("/")
        if "v1" in parts:
            if not base.endswith("/completions"):
                return f"{base}/completions"
            return base
        return f"{base}/v1/chat/completions"

    async def chat(self, prompt: str, system_prompt: str | None = None) -> str:
        """Send a chat completion request and return the assistant message text.

        Raises LLMError on HTTP errors, timeouts, or unexpected payloads.
        """
        messages: list[dict[str, str]] = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload: dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.2,
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    self.chat_completions_url, headers=headers, json=payload
                )
                response.raise_for_status()
                data = response.json()
        except httpx.TimeoutException:
            raise LLMError(f"LLM 请求超时（{self.timeout}秒）")
        except httpx.HTTPStatusError as exc:
            raise LLMError(
                f"LLM API 返回 HTTP {exc.response.status_code}: "
                f"{exc.response.text[:300]}"
            )
        except Exception as exc:
            raise LLMError(f"LLM 请求失败: {exc}")

        try:
            return data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise LLMError("LLM 响应结构不符合 Chat Completions 格式") from exc
