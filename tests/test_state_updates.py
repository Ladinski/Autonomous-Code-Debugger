from debugger_agent.agent.actions import (
    AgentAction,
    FinishArgs,
    ReadFileArgs,
)
from debugger_agent.agent.state_updates import record_step


def create_state():
    return {
        "bug_report": "Refresh requests return 401.",
        "iteration_count": 0,
        "tool_calls": [],
        "tool_observations": [],
        "files_inspected": [],
        "current_hypothesis": None,
        "final_diagnosis": None,
        "completion_status": "investigating",
    }


def test_record_step_increments_iteration():
    state = create_state()

    action = AgentAction(
        action="read_file",
        reasoning_summary="Inspect auth.",
        read_file=ReadFileArgs(
            path="app/auth.py",
        ),
    )

    observation = {
        "tool": "read_file",
        "success": True,
        "result": {},
        "summary": "Read app/auth.py.",
    }

    updated = record_step(
        state,
        action,
        observation,
    )

    assert updated["iteration_count"] == 1


def test_record_step_records_tool_call():
    state = create_state()

    action = AgentAction(
        action="read_file",
        reasoning_summary="Inspect auth.",
        read_file=ReadFileArgs(
            path="app/auth.py",
        ),
    )

    observation = {
        "tool": "read_file",
        "success": True,
        "result": {},
        "summary": "Read app/auth.py.",
    }

    updated = record_step(
        state,
        action,
        observation,
    )

    assert len(updated["tool_calls"]) == 1

    call = updated["tool_calls"][0]

    assert call["step"] == 1
    assert call["tool"] == "read_file"
    assert call["arguments"]["path"] == "app/auth.py"


def test_successful_read_records_inspected_file():
    state = create_state()

    action = AgentAction(
        action="read_file",
        reasoning_summary="Inspect auth.",
        read_file=ReadFileArgs(
            path="app/auth.py",
        ),
    )

    observation = {
        "tool": "read_file",
        "success": True,
        "result": {},
        "summary": "Read app/auth.py.",
    }

    updated = record_step(
        state,
        action,
        observation,
    )

    assert updated["files_inspected"] == [
        "app/auth.py"
    ]


def test_failed_read_does_not_record_file():
    state = create_state()

    action = AgentAction(
        action="read_file",
        reasoning_summary="Inspect auth.",
        read_file=ReadFileArgs(
            path="missing.py",
        ),
    )

    observation = {
        "tool": "read_file",
        "success": False,
        "result": None,
        "summary": "File does not exist.",
        "error_type": "FileNotFoundError",
    }

    updated = record_step(
        state,
        action,
        observation,
    )

    assert updated["files_inspected"] == []


def test_finish_marks_investigation_diagnosed():
    state = create_state()

    action = AgentAction(
        action="finish",
        reasoning_summary="Enough evidence collected.",
        finish=FinishArgs(
            diagnosis="Token validation uses the wrong expiry.",
            confidence=0.9,
        ),
    )

    observation = {
        "tool": "finish",
        "success": True,
        "result": action.finish.model_dump(),
        "summary": action.finish.diagnosis,
    }

    updated = record_step(
        state,
        action,
        observation,
    )

    assert updated["completion_status"] == "diagnosed"
    assert (
        updated["final_diagnosis"]
        == "Token validation uses the wrong expiry."
    )




def test_record_step_preserves_observation_result():
    state = create_state()

    action = AgentAction(
        action="read_file",
        reasoning_summary="Inspect auth.",
        read_file=ReadFileArgs(
            path="app/auth.py",
        ),
    )

    observation = {
        "tool": "read_file",
        "success": True,
        "result": {
            "path": "app/auth.py",
            "content": "def login(): pass",
            "truncated": False,
            "total_lines": 1,
            "returned_lines": 1,
        },
        "summary": "Read 1 of 1 lines from app/auth.py.",
    }

    updated = record_step(
        state,
        action,
        observation,
    )

    stored = updated["tool_observations"][0]

    assert stored["result"] == observation["result"]
    assert (
        stored["result"]["content"]
        == "def login(): pass"
    )