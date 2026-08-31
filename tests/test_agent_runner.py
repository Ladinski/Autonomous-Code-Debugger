from pathlib import Path

from debugger_agent.agent.actions import (
    AgentAction,
    FinishArgs,
    ListDirectoryArgs,
)
from debugger_agent.agent.decision import (
    AgentDecisionService,
)
from debugger_agent.agent.executor import ToolExecutor
from debugger_agent.agent.runner import AgentRunner
from debugger_agent.repository.workspace import (
    RepositoryWorkspace,
)


class SequencedDecisionModel:
    def __init__(self):
        self.calls = 0

    def decide(
        self,
        system_prompt: str,
        user_prompt: str,
    ) -> AgentAction:
        self.calls += 1

        if self.calls == 1:
            return AgentAction(
                action="list_directory",
                reasoning_summary="Inspect repository.",
                list_directory=ListDirectoryArgs(
                    path=".",
                ),
            )

        return AgentAction(
            action="finish",
            reasoning_summary="Enough evidence.",
            finish=FinishArgs(
                diagnosis="Example diagnosis.",
                confidence=0.9,
            ),
        )


class NeverFinishDecisionModel:
    def decide(
        self,
        system_prompt: str,
        user_prompt: str,
    ) -> AgentAction:
        return AgentAction(
            action="list_directory",
            reasoning_summary="Keep investigating.",
            list_directory=ListDirectoryArgs(
                path=".",
            ),
        )


def create_state():
    return {
        "bug_report": "Example bug.",
        "iteration_count": 0,
        "tool_calls": [],
        "tool_observations": [],
        "files_inspected": [],
        "current_hypothesis": None,
        "final_diagnosis": None,
        "completion_status": "investigating",
    }


def create_workspace(
    tmp_path: Path,
) -> RepositoryWorkspace:
    repo = tmp_path / "repo"
    repo.mkdir()

    (repo / "app.py").write_text(
        "print('hello')",
        encoding="utf-8",
    )

    return RepositoryWorkspace(repo)


def test_runner_stops_when_agent_finishes(
    tmp_path: Path,
):
    workspace = create_workspace(tmp_path)

    decision_service = AgentDecisionService(
        SequencedDecisionModel()
    )

    executor = ToolExecutor(workspace)

    runner = AgentRunner(
        decision_service=decision_service,
        executor=executor,
        max_iterations=5,
    )

    final_state = runner.run(
        create_state()
    )

    assert (
        final_state["completion_status"]
        == "diagnosed"
    )
    assert final_state["iteration_count"] == 2
    assert (
        final_state["final_diagnosis"]
        == "Example diagnosis."
    )


def test_runner_stops_at_iteration_limit(
    tmp_path: Path,
):
    workspace = create_workspace(tmp_path)

    decision_service = AgentDecisionService(
        NeverFinishDecisionModel()
    )

    executor = ToolExecutor(workspace)

    runner = AgentRunner(
        decision_service=decision_service,
        executor=executor,
        max_iterations=3,
    )

    final_state = runner.run(
        create_state()
    )

    assert (
        final_state["completion_status"]
        == "limit_reached"
    )
    assert final_state["iteration_count"] == 3


def test_runner_rejects_invalid_iteration_limit(
    tmp_path: Path,
):
    workspace = create_workspace(tmp_path)

    decision_service = AgentDecisionService(
        NeverFinishDecisionModel()
    )

    executor = ToolExecutor(workspace)

    try:
        AgentRunner(
            decision_service=decision_service,
            executor=executor,
            max_iterations=0,
        )
    except ValueError:
        return

    raise AssertionError(
        "Expected invalid max_iterations to fail."
    )