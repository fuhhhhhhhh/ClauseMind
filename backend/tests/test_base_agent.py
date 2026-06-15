"""Tests for BaseAgent JSON parsing logic."""

from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest

from app.agents.base_agent import AgentError, BaseAgent
from app.agents.llm_client import LLMError


class FakeAgent(BaseAgent):
    name = "FakeAgent"
    prompt_file = "contract_profile_agent.txt"  # real file exists


@pytest.fixture
def fake_agent():
    return FakeAgent()


class TestBaseAgentJSONParsing:
    def test_parse_pure_json(self, fake_agent):
        result = fake_agent.parse_json('{"key": "value"}')
        assert result == {"key": "value"}

    def test_parse_fenced_json(self, fake_agent):
        raw = '```json\n{"key": "value"}\n```'
        result = fake_agent.parse_json(raw)
        assert result == {"key": "value"}

    def test_parse_fenced_no_tag(self, fake_agent):
        raw = '```\n{"key": "value"}\n```'
        result = fake_agent.parse_json(raw)
        assert result == {"key": "value"}

    def test_parse_embedded_json(self, fake_agent):
        raw = 'Here is some text {"key": "value"} and more text'
        result = fake_agent.parse_json(raw)
        assert result == {"key": "value"}

    def test_parse_invalid_json_raises(self, fake_agent):
        with pytest.raises(ValueError, match="无法从 LLM 输出中解析 JSON"):
            fake_agent.parse_json("This is not JSON at all")

    def test_parse_json_array_raises(self, fake_agent):
        with pytest.raises(ValueError, match="无法从 LLM 输出中解析 JSON"):
            fake_agent.parse_json("[1, 2, 3]")

    @patch.object(BaseAgent, "_call_llm")
    def test_retry_on_first_parse_failure(self, mock_call, fake_agent):
        """First response is invalid, retry succeeds."""
        mock_call.side_effect = [
            "not json at all",
            '{"key": "retried"}',
        ]
        result = fake_agent.run_sync({"test": True})
        assert result == {"key": "retried"}
        assert mock_call.call_count == 2

    @patch.object(BaseAgent, "_call_llm")
    def test_retry_failure_raises_agent_error(self, mock_call, fake_agent):
        """Both attempts fail -> AgentError."""
        mock_call.side_effect = [
            "still not json",
            "also not json",
        ]
        with pytest.raises(AgentError, match="JSON 解析失败"):
            fake_agent.run_sync({"test": True})
        assert mock_call.call_count == 2

    @patch.object(BaseAgent, "_call_llm")
    def test_llm_error_propagates(self, mock_call, fake_agent):
        """LLM _call_llm raises AgentError (which wraps LLMError)."""
        mock_call.side_effect = AgentError("LLM API down")
        with pytest.raises(AgentError, match="LLM API down"):
            fake_agent.run_sync({"test": True})


# Helper: sync wrapper for BaseAgent.run
def _sync_run(self, input_data: dict) -> dict:
    """Run agent synchronously — only for testing!"""
    import asyncio
    return asyncio.get_event_loop().run_until_complete(BaseAgent.run(self, input_data))


BaseAgent.run_sync = _sync_run
