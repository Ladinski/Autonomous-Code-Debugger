from pathlib import Path

import pytest

from debugger_agent.agent.actions import (
    AgentAction,
    ApplyPatchArgs,
    FinishArgs,
    ListDirectoryArgs,
    RunTestsArgs,
)
from debugger_agent.agent.decision import AgentDecisionService
from debugger_agent.agent.executor import ToolExecutor
from debugger_agent.agent.runner import AgentRunner
from debugger_agent.repository.workspace import RepositoryWorkspace


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


class PatchThenFinishThenTestModel:
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
                action="apply_patch",
                reasoning_summary="Apply fix.",
                apply_patch=ApplyPatchArgs(
                    path="app.py",
                    old_text="value = False",
                    new_text="value = True",
                ),
            )

        if self.calls == 2:
            return AgentAction(
                action="finish",
                reasoning_summary="Fix is complete.",
                finish=FinishArgs(
                    diagnosis="Fixed value.",
                    confidence=0.9,
                ),
            )

        return AgentAction(
            action="run_tests",
            reasoning_summary="Verify the patch.",
            run_tests=RunTestsArgs(
                command=["pytest", "-q"],
                timeout_seconds=30,
            ),
        )


class AlwaysPatchDecisionModel:
    def decide(
        self,
        system_prompt: str,
        user_prompt: str,
    ) -> AgentAction:
        return AgentAction(
            action="apply_patch",
            reasoning_summary="Attempt another patch.",
            apply_patch=ApplyPatchArgs(
                path="app.py",
                old_text="value = False",
                new_text="value = True",
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
        "patch_attempts": 0,
        "tests_executed": 0,
        "last_patch_step": None,
        "last_successful_test_step": None,
    }


def create_workspace(
    tmp_path: Path,
) -> RepositoryWorkspace:
    repo = tmp_path / "repo"
    repo.mkdir()

    (repo / "app.py").write_text(
        "value = False\n",
        encoding="utf-8",
    )

    return RepositoryWorkspace(repo)


def test_runner_rejects_finish_after_unverified_patch(
    tmp_path: Path,
):
    workspace = create_workspace(tmp_path)

    decision_service = AgentDecisionService(
        PatchThenFinishThenTestModel()
    )

    executor = ToolExecutor(workspace)

    runner = AgentRunner(
        decision_service=decision_service,
        executor=executor,
        max_iterations=2,
    )

    final_state = runner.run(
        create_state()
    )

    observations = final_state["tool_observations"]

    assert len(observations) == 2

    assert observations[1]["success"] is False

    assert (
        observations[1]["error_type"]
        == "VerificationRequired"
    )

    assert (
        "not been verified"
        in observations[1]["summary"]
    )

    assert (
        final_state["completion_status"]
        == "limit_reached"
    )


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

    with pytest.raises(ValueError):
        AgentRunner(
            decision_service=decision_service,
            executor=executor,
            max_iterations=0,
        )


def test_runner_rejects_invalid_patch_limit(
    tmp_path: Path,
):
    workspace = create_workspace(tmp_path)

    decision_service = AgentDecisionService(
        NeverFinishDecisionModel()
    )

    executor = ToolExecutor(workspace)

    with pytest.raises(ValueError):
        AgentRunner(
            decision_service=decision_service,
            executor=executor,
            max_patch_attempts=0,
        )


def test_runner_stops_at_patch_limit(
    tmp_path: Path,
):
    workspace = create_workspace(tmp_path)

    decision_service = AgentDecisionService(
        AlwaysPatchDecisionModel()
    )

    executor = ToolExecutor(workspace)

    runner = AgentRunner(
        decision_service=decision_service,
        executor=executor,
        max_iterations=10,
        max_patch_attempts=1,
    )

    final_state = runner.run(
        create_state()
    )

    assert (
        final_state["completion_status"]
        == "limit_reached"
    )

    assert final_state["patch_attempts"] == 1