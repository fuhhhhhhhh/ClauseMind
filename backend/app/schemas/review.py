"""Pydantic schemas for review (agent) module."""

from datetime import datetime

from pydantic import BaseModel


class AgentExecutionLogResponse(BaseModel):
    id: int
    task_id: int
    contract_id: int
    agent_name: str
    input_json: str | None = None
    output_json: str | None = None
    status: str
    error_message: str | None = None
    started_at: datetime | None = None
    finished_at: datetime | None = None
    duration_ms: int | None = None

    model_config = {"from_attributes": True}


class ReviewTaskResponse(BaseModel):
    id: int
    contract_id: int
    user_id: int
    status: str
    current_step: str | None = None
    error_message: str | None = None
    started_at: datetime | None = None
    finished_at: datetime | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class ReviewTaskDetailResponse(BaseModel):
    task: ReviewTaskResponse
    agent_logs: list[AgentExecutionLogResponse]
    profile: dict | None = None
