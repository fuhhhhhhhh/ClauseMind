"""Tests for LLM client URL normalization and error handling."""

import pytest

from app.agents.llm_client import LLMClient, LLMError


class TestLLMClientURLNormalize:
    def test_base_with_trailing_slash(self):
        c = LLMClient(api_base="http://localhost:11434/v1/")
        assert c.chat_completions_url == "http://localhost:11434/v1/chat/completions"

    def test_base_no_trailing_slash(self):
        c = LLMClient(api_base="http://localhost:11434/v1")
        assert c.chat_completions_url == "http://localhost:11434/v1/chat/completions"

    def test_base_already_full_path(self):
        c = LLMClient(api_base="https://api.openai.com/v1/chat/completions")
        assert c.chat_completions_url == "https://api.openai.com/v1/chat/completions"

    def test_base_no_v1_path(self):
        c = LLMClient(api_base="https://api.example.com")
        assert c.chat_completions_url == "https://api.example.com/v1/chat/completions"

    def test_base_with_v1_in_middle(self):
        c = LLMClient(api_base="https://api.example.com/v1/chat")
        assert c.chat_completions_url == "https://api.example.com/v1/chat/completions"
