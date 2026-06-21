"""SQLAlchemy models — import all submodules so Base.metadata is populated."""

# Import each model module so SQLAlchemy registers tables on Base.metadata
# for Alembic autogenerate and create_all().
import app.models.contract  # noqa: F401
import app.models.parse_job  # noqa: F401
import app.models.review_results  # noqa: F401
import app.models.review_task  # noqa: F401
import app.models.user  # noqa: F401

__all__ = [
    "AgentExecutionLog",
    "Contract",
    "ContractClause",
    "DocumentParseResult",
    "ModifySuggestion",
    "ParseJob",
    "ReviewReport",
    "ReviewTask",
    "RiskItem",
    "User",
]
