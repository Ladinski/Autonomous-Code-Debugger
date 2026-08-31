import json

from debugger_agent.observability.models import (
    AgentTrace,
    TraceStep,
)
from debugger_agent.observability.storage import (
    save_trace,
)


def test_save_trace_creates_json_file(
    tmp_path,
):
    trace = AgentTrace(
        trace_id="test-trace-123",
        bug_report="Example bug.",
        model="test-model",
        steps=[
            TraceStep(
                step=1,
                action="read_file",
                arguments={
                    "path": "app/main.py",
                },
                success=True,
                summary="Read file.",
                duration_ms=10.5,
            )
        ],
        completion_status="diagnosed",
        final_diagnosis="Example diagnosis.",
        total_duration_ms=25.0,
    )

    output_path = save_trace(
        trace,
        tmp_path,
    )

    assert output_path.exists()
    assert output_path.name == (
        "test-trace-123.json"
    )

    data = json.loads(
        output_path.read_text(
            encoding="utf-8"
        )
    )

    assert data["trace_id"] == (
        "test-trace-123"
    )

    assert data["model"] == "test-model"

    assert data["completion_status"] == (
        "diagnosed"
    )

    assert len(data["steps"]) == 1

    assert data["steps"][0]["action"] == (
        "read_file"
    )


def test_save_trace_creates_directory(
    tmp_path,
):
    output_directory = (
        tmp_path / "traces" / "nested"
    )

    trace = AgentTrace(
        trace_id="trace-456",
        bug_report="Example bug.",
    )

    output_path = save_trace(
        trace,
        output_directory,
    )

    assert output_directory.exists()
    assert output_path.exists()