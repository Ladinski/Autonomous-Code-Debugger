from pydantic import BaseModel, Field


class TraceStep(BaseModel):
    step: int
    action: str
    arguments: dict
    success: bool
    summary: str
    error_type: str | None = None
    duration_ms: float | None = None


class AgentTrace(BaseModel):
    trace_id: str
    bug_report: str
    model: str | None = None
    steps: list[TraceStep] = Field(
        default_factory=list
    )
    completion_status: str | None = None
    final_diagnosis: str | None = None
    total_duration_ms: float | None = None