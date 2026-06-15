from app.agents.base_agent import BaseAgent


class ReportGenerationAgent(BaseAgent):
    name = "ReportGenerationAgent"
    prompt_file = "report_generation_agent.txt"
