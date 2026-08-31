from typing import Literal, TypedDict


class ToolCallRecord(TypedDict):
    step: int
    tool: str
    arguments: dict


class ToolObservationRecord(TypedDict):
    step: int
    tool: str
    success: bool
    summary: str
    result: dict | None


class AgentState(TypedDict):
    bug_report: str

    iteration_count: int

    tool_calls: list[ToolCallRecord]
    tool_observations: list[ToolObservationRecord]
    last_patch_step: int | None
    last_successful_test_step: int | None
    files_inspected: list[str]

    current_hypothesis: str | None
    final_diagnosis: str | None

    patch_attempts: int
    tests_executed: int

    completion_status: Literal[
        "investigating",
        "diagnosed",
        "failed",
        "limit_reached",
    ]