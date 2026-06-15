from app.agents.base_agent import BaseAgent


class ContractProfileAgent(BaseAgent):
    name = "ContractProfileAgent"
    prompt_file = "contract_profile_agent.txt"
