from app.agents.base_agent import BaseAgent


class ConsistencyCheckAgent(BaseAgent):
    name = "ConsistencyCheckAgent"
    prompt_file = "consistency_check_agent.txt"
