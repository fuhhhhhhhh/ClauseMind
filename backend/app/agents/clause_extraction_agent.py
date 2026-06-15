from app.agents.base_agent import BaseAgent


class ClauseExtractionAgent(BaseAgent):
    name = "ClauseExtractionAgent"
    prompt_file = "clause_extraction_agent.txt"
