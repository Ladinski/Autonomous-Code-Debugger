import time
import uuid

from debugger_agent.observability.models import (
    AgentTrace,
    TraceStep,
)


class AgentTracer:
    def __init__(
        self,
        bug_report: str,
        model: str | None = None,
    ):
        self.trace = AgentTrace(
            trace_id=str(uuid.uuid4()),
            bug_report=bug_report,
            model=model,
        )

        self._started_at = time.perf_counter()

    def record_step(
        self,
        step: int,
        action: str,
        arguments: dict,
        observation: dict,
        duration_ms: float | None = None,
    ) -> None:
        self.trace.steps.append(
            TraceStep(
                step=step,
                action=action,
                arguments=arguments,
                success=observation["success"],
                summary=observation["summary"],
                error_type=observation.get(
                    "error_type"
                ),
                duration_ms=duration_ms,
            )
        )

    def finish(
        self,
        completion_status: str,
        final_diagnosis: str | None,
    ) -> AgentTrace:
        total_duration_ms = (
            time.perf_counter()
            - self._started_at
        ) * 1000

        self.trace.completion_status = (
            completion_status
        )

        self.trace.final_diagnosis = (
            final_diagnosis
        )

        self.trace.total_duration_ms = (
            total_duration_ms
        )

        return self.trace