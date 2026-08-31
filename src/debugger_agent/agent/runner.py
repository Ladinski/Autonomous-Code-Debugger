import time

from debugger_agent.agent.decision import AgentDecisionService
from debugger_agent.agent.executor import ToolExecutor
from debugger_agent.agent.state import AgentState
from debugger_agent.agent.state_updates import record_step
from debugger_agent.observability.models import AgentTrace
from debugger_agent.observability.tracer import AgentTracer


class AgentRunner:
    def __init__(
        self,
        decision_service: AgentDecisionService,
        executor: ToolExecutor,
        max_iterations: int = 10,
        max_patch_attempts: int = 3,
    ):
        if max_iterations <= 0:
            raise ValueError(
                "max_iterations must be greater than 0."
            )

        if max_patch_attempts <= 0:
            raise ValueError(
                "max_patch_attempts must be greater than 0."
            )

        self.decision_service = decision_service
        self.executor = executor
        self.max_iterations = max_iterations
        self.max_patch_attempts = max_patch_attempts

        self.last_trace: AgentTrace | None = None

    def run(
        self,
        initial_state: AgentState,
    ) -> AgentState:
        state = initial_state

        model_name = self._get_model_name()

        tracer = AgentTracer(
            bug_report=state["bug_report"],
            model=model_name,
        )

        while (
            state["completion_status"] == "investigating"
            and state["iteration_count"] < self.max_iterations
        ):
            action = self.decision_service.choose_action(
                state
            )

            if (
                action.action == "apply_patch"
                and state["patch_attempts"]
                >= self.max_patch_attempts
            ):
                state["completion_status"] = "limit_reached"
                break

            if (
                action.action == "finish"
                and state["last_patch_step"] is not None
            ):
                last_test_step = state[
                    "last_successful_test_step"
                ]

                if (
                    last_test_step is None
                    or last_test_step
                    <= state["last_patch_step"]
                ):
                    observation = {
                        "tool": "finish",
                        "success": False,
                        "result": None,
                        "summary": (
                            "Finish rejected: the latest "
                            "successful patch has not been "
                            "verified by passing tests."
                        ),
                        "error_type": "VerificationRequired",
                    }

                    state = record_step(
                        state,
                        action,
                        observation,
                    )

                    self._record_trace_step(
                        tracer=tracer,
                        state=state,
                        observation=observation,
                        duration_ms=0.0,
                    )

                    continue

            started_at = time.perf_counter()

            observation = self.executor.execute(
                action
            )

            duration_ms = (
                time.perf_counter() - started_at
            ) * 1000

            state = record_step(
                state,
                action,
                observation,
            )

            self._record_trace_step(
                tracer=tracer,
                state=state,
                observation=observation,
                duration_ms=duration_ms,
            )

            if action.action == "finish":
                break

        if (
            state["completion_status"] == "investigating"
            and state["iteration_count"]
            >= self.max_iterations
        ):
            state["completion_status"] = "limit_reached"

        self.last_trace = tracer.finish(
            completion_status=state[
                "completion_status"
            ],
            final_diagnosis=state[
                "final_diagnosis"
            ],
        )

        return state

    def _record_trace_step(
        self,
        tracer: AgentTracer,
        state: AgentState,
        observation: dict,
        duration_ms: float,
    ) -> None:
        tool_call = state["tool_calls"][-1]

        tracer.record_step(
            step=tool_call["step"],
            action=tool_call["tool"],
            arguments=tool_call["arguments"],
            observation=observation,
            duration_ms=duration_ms,
        )

    def _get_model_name(
        self,
    ) -> str | None:
        decision_model = getattr(
            self.decision_service,
            "model",
            None,
        )

        if decision_model is None:
            return None

        return getattr(
            decision_model,
            "model_name",
            None,
        )