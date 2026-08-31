import shutil
import tempfile
from pathlib import Path

from debugger_agent.agent.decision import AgentDecisionService
from debugger_agent.agent.executor import ToolExecutor
from debugger_agent.agent.runner import AgentRunner
from debugger_agent.evaluation.models import (
    EvaluationCase,
    EvaluationResult,
)
from debugger_agent.llm.openai import OpenAIDecisionModel
from debugger_agent.repository.workspace import RepositoryWorkspace


def run_evaluation_case(
    case: EvaluationCase,
    max_iterations: int = 15,
    max_patch_attempts: int = 3,
) -> EvaluationResult:
    with tempfile.TemporaryDirectory() as temp_dir:
        workspace_path = Path(temp_dir) / "repo"

        shutil.copytree(
            case.fixture_path,
            workspace_path,
        )

        workspace = RepositoryWorkspace(
            workspace_path
        )

        runner = AgentRunner(
            decision_service=AgentDecisionService(
                OpenAIDecisionModel()
            ),
            executor=ToolExecutor(workspace),
            max_iterations=max_iterations,
            max_patch_attempts=max_patch_attempts,
        )

        state = {
            "bug_report": case.bug_report,
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

        final_state = runner.run(state)

        expected_file = workspace.resolve_path(
            case.expected_file
        )

        expected_fix_present = False

        if expected_file.exists():
            content = expected_file.read_text(
                encoding="utf-8"
            )

            expected_fix_present = (
                case.expected_text in content
            )

        return EvaluationResult(
            case_name=case.name,
            completion_status=final_state[
                "completion_status"
            ],
            diagnosed=(
                final_state["completion_status"]
                == "diagnosed"
            ),
            expected_fix_present=expected_fix_present,
            tests_passed_after_patch=_has_verified_patch(
                final_state
            ),
            iterations=final_state[
                "iteration_count"
            ],
            patch_attempts=final_state[
                "patch_attempts"
            ],
            tests_executed=final_state[
                "tests_executed"
            ],
            final_diagnosis=final_state[
                "final_diagnosis"
            ],
        )


def _has_verified_patch(
    state: dict,
) -> bool:
    last_patch_step = state.get(
        "last_patch_step"
    )

    last_test_step = state.get(
        "last_successful_test_step"
    )

    if last_patch_step is None:
        return False

    if last_test_step is None:
        return False

    return last_test_step > last_patch_step