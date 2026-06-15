from app.agents.base_agent import BaseAgent


class SuggestionAgent(BaseAgent):
    name = "SuggestionAgent"
    prompt_file = "suggestion_agent.txt"
