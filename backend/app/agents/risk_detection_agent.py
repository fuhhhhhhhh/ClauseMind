from app.agents.base_agent import BaseAgent


class RiskDetectionAgent(BaseAgent):
    name = "RiskDetectionAgent"
    prompt_file = "risk_detection_agent.txt"
