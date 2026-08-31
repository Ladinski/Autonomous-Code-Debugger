from copy import deepcopy

from debugger_agent.agent.actions import AgentAction
from debugger_agent.agent.state import AgentState


def record_step(
    state: AgentState,
    action: AgentAction,
    observation: dict,
) -> AgentState:
    updated = deepcopy(state)

    step = updated["iteration_count"] + 1
    updated["iteration_count"] = step

    updated["tool_calls"].append(
        {
            "step": step,
            "tool": action.action,
            "arguments": _extract_arguments(action),
        }
    )

    updated["tool_observations"].append(
    {
        "step": step,
        "tool": action.action,
        "success": observation["success"],
        "summary": observation["summary"],
        "result": observation.get("result"),
        "error_type": observation.get("error_type"),
    }
)

    if (
        action.action == "apply_patch"
        and observation["success"]
    ):
        updated["patch_attempts"] += 1
        updated["last_patch_step"] = step

    if action.action == "run_tests":
        updated["tests_executed"] += 1

        result = observation.get("result")

        if (
            observation["success"]
            and result is not None
            and result.get("exit_code") == 0
            and not result.get("timed_out", False)
        ):
            updated["last_successful_test_step"] = step

    if (
        action.action == "read_file"
        and observation["success"]
        and action.read_file is not None
    ):
        path = action.read_file.path

        if path not in updated["files_inspected"]:
            updated["files_inspected"].append(path)

    if (
        action.action == "finish"
        and observation["success"]
    ):
        assert action.finish is not None

        updated["final_diagnosis"] = (
            action.finish.diagnosis
        )
        updated["completion_status"] = "diagnosed"

    return updated


def _extract_arguments(
    action: AgentAction,
) -> dict:
    selected_args = getattr(
        action,
        action.action,
    )

    if selected_args is None:
        return {}

    return selected_args.model_dump()