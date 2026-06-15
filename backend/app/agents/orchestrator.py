from app.agents.clause_extraction_agent import ClauseExtractionAgent
from app.agents.consistency_check_agent import ConsistencyCheckAgent
from app.agents.contract_profile_agent import ContractProfileAgent
from app.agents.risk_detection_agent import RiskDetectionAgent
from app.agents.suggestion_agent import SuggestionAgent
from app.agents.report_generation_agent import ReportGenerationAgent


class AgentOrchestrator:
    def __init__(self) -> None:
        self.profile_agent = ContractProfileAgent()
        self.clause_agent = ClauseExtractionAgent()
        self.risk_agent = RiskDetectionAgent()
        self.suggestion_agent = SuggestionAgent()
        self.check_agent = ConsistencyCheckAgent()
        self.report_agent = ReportGenerationAgent()

    async def run_review(self, normalized_document: dict) -> dict:
        profile = await self.profile_agent.run({"contract_document": normalized_document})
        clauses = await self.clause_agent.run(
            {"contract_document": normalized_document, "contract_profile": profile}
        )
        risks = await self.risk_agent.run({"contract_profile": profile, "clauses": clauses})
        suggestions = await self.suggestion_agent.run({"risks": risks, "clauses": clauses})
        check = await self.check_agent.run(
            {
                "contract_document": normalized_document,
                "profile": profile,
                "clauses": clauses,
                "risks": risks,
                "suggestions": suggestions,
            }
        )
        report = await self.report_agent.run(
            {
                "profile": profile,
                "clauses": clauses,
                "risks": risks,
                "suggestions": suggestions,
                "check": check,
            }
        )
        return {
            "profile": profile,
            "clauses": clauses,
            "risks": risks,
            "suggestions": suggestions,
            "consistency_check": check,
            "report": report,
        }
