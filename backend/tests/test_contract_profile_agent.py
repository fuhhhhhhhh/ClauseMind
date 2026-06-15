"""Tests for ContractProfileAgent validation."""

import pytest

from app.agents.base_agent import AgentError
from app.agents.contract_profile_agent import ContractProfileAgent


class TestContractProfileAgentValidation:
    def test_valid_output_passes(self):
        agent = ContractProfileAgent()
        output = {
            "contract_type": "房屋租赁合同",
            "party_a": "张三",
            "party_b": "李四",
            "sign_date": "2026-06-01",
            "amount": "3000元/月",
            "duration": "2026-06-01 至 2027-06-01",
            "subject": "房屋租赁",
            "summary": "租赁合同摘要",
            "missing_fields": [],
        }
        agent.validate(output)  # should not raise

    def test_missing_field_raises(self):
        agent = ContractProfileAgent()
        output = {"contract_type": "租赁合同", "party_a": "张三"}
        with pytest.raises(AgentError, match="缺少必需字段"):
            agent.validate(output)

    def test_missing_fields_not_list_raises(self):
        agent = ContractProfileAgent()
        output = {
            "contract_type": "租赁合同",
            "party_a": "张三",
            "party_b": "李四",
            "sign_date": "2026-06-01",
            "amount": "3000元/月",
            "duration": "1年",
            "subject": "房屋租赁",
            "summary": "摘要",
            "missing_fields": "should be list",
        }
        with pytest.raises(AgentError, match="missing_fields 必须是 list"):
            agent.validate(output)

    def test_non_dict_output_raises(self):
        agent = ContractProfileAgent()
        with pytest.raises(AgentError, match="必须是 JSON 对象"):
            agent.validate(["not", "a", "dict"])

    def test_valid_with_nulls(self):
        agent = ContractProfileAgent()
        output = {
            "contract_type": None,
            "party_a": None,
            "party_b": None,
            "sign_date": None,
            "amount": None,
            "duration": None,
            "subject": None,
            "summary": None,
            "missing_fields": [
                "contract_type", "party_a", "party_b", "sign_date",
                "amount", "duration", "subject", "summary",
            ],
        }
        agent.validate(output)  # should pass — all fields present
