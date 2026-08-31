from debugger_agent.agent.decision import AgentDecisionService
from debugger_agent.agent.executor import ToolExecutor
from debugger_agent.agent.state import AgentState
from debugger_agent.agent.state_updates import record_step
from debugger_agent.evaluation.models import (
    EvaluationCase,
    EvaluationResult,
    EvaluationSummary,
)

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

    def run(
        self,
        initial_state: AgentState,
    ) -> AgentState:
        state = initial_state

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

                    continue

            observation = self.executor.execute(
                action
            )

            state = record_step(
                state,
                action,
                observation,
            )

            if action.action == "finish":
                break

        if (
            state["completion_status"] == "investigating"
            and state["iteration_count"]
            >= self.max_iterations
        ):
            state["completion_status"] = "limit_reached"

        return state

def summarize_results(
    results: list[EvaluationResult],
) -> EvaluationSummary:
    if not results:
        return EvaluationSummary(
            total_cases=0,
            diagnosed_cases=0,
            successful_fixes=0,
            verified_fixes=0,
            fix_rate=0.0,
            verification_rate=0.0,
            average_iterations=0.0,
            average_patch_attempts=0.0,
            average_test_runs=0.0,
        )

    total_cases = len(results)

    diagnosed_cases = sum(
        result.diagnosed
        for result in results
    )

    successful_fixes = sum(
        result.expected_fix_present
        for result in results
    )

    verified_fixes = sum(
        result.tests_passed_after_patch
        for result in results
    )

    return EvaluationSummary(
        total_cases=total_cases,
        diagnosed_cases=diagnosed_cases,
        successful_fixes=successful_fixes,
        verified_fixes=verified_fixes,
        fix_rate=successful_fixes / total_cases,
        verification_rate=verified_fixes / total_cases,
        average_iterations=sum(
            result.iterations
            for result in results
        ) / total_cases,
        average_patch_attempts=sum(
            result.patch_attempts
            for result in results
        ) / total_cases,
        average_test_runs=sum(
            result.tests_executed
            for result in results
        ) / total_cases,
    )