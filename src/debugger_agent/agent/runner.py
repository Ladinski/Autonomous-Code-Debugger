from debugger_agent.agent.decision import AgentDecisionService
from debugger_agent.agent.executor import ToolExecutor
from debugger_agent.agent.state import AgentState
from debugger_agent.agent.state_updates import record_step


class AgentRunner:
    def __init__(
        self,
        decision_service: AgentDecisionService,
        executor: ToolExecutor,
        max_iterations: int = 10,
    ):
        if max_iterations <= 0:
            raise ValueError(
                "max_iterations must be greater than 0."
            )

        self.decision_service = decision_service
        self.executor = executor
        self.max_iterations = max_iterations

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
            and state["iteration_count"] >= self.max_iterations
        ):
            state["completion_status"] = "limit_reached"

        return state