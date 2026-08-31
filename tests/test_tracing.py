from debugger_agent.observability.tracer import (
    AgentTracer,
)


def test_tracer_records_agent_step():
    tracer = AgentTracer(
        bug_report="Example bug.",
        model="test-model",
    )

    tracer.record_step(
        step=1,
        action="read_file",
        arguments={
            "path": "app/main.py",
        },
        observation={
            "success": True,
            "summary": "Read file.",
            "result": {},
        },
        duration_ms=12.5,
    )

    trace = tracer.finish(
        completion_status="diagnosed",
        final_diagnosis="Example diagnosis.",
    )

    assert trace.trace_id
    assert trace.model == "test-model"
    assert len(trace.steps) == 1

    step = trace.steps[0]

    assert step.step == 1
    assert step.action == "read_file"
    assert step.success is True
    assert step.duration_ms == 12.5

    assert trace.completion_status == "diagnosed"
    assert (
        trace.final_diagnosis
        == "Example diagnosis."
    )

    assert trace.total_duration_ms is not None
    assert trace.total_duration_ms >= 0


def test_tracer_records_tool_error():
    tracer = AgentTracer(
        bug_report="Example bug."
    )

    tracer.record_step(
        step=1,
        action="read_file",
        arguments={
            "path": "missing.py",
        },
        observation={
            "success": False,
            "summary": "File does not exist.",
            "result": None,
            "error_type": "FileNotFoundError",
        },
    )

    trace = tracer.finish(
        completion_status="failed",
        final_diagnosis=None,
    )

    step = trace.steps[0]

    assert step.success is False
    assert (
        step.error_type
        == "FileNotFoundError"
    )