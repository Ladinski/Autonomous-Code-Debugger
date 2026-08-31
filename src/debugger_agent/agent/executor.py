import json

from debugger_agent.agent.actions import AgentAction
from debugger_agent.repository.workspace import RepositoryWorkspace
from debugger_agent.tools.filesystem import list_directory, read_file
from debugger_agent.tools.search import search_code
from debugger_agent.tools.testing import run_tests

class ToolExecutionError(RuntimeError):
    """Raised when an agent action cannot be executed."""


class ToolExecutor:
    def __init__(self, workspace: RepositoryWorkspace):
        self.workspace = workspace

    def execute(self, action: AgentAction) -> dict:
        try:
            if action.action == "list_directory":
                assert action.list_directory is not None

                result = list_directory(
                    self.workspace,
                    action.list_directory.path,
                )

            elif action.action == "search_code":
                assert action.search_code is not None

                result = search_code(
                    self.workspace,
                    query=action.search_code.query,
                    max_results=action.search_code.max_results,
                )

            elif action.action == "read_file":
                assert action.read_file is not None

                result = read_file(
                    self.workspace,
                    path=action.read_file.path,
                    max_lines=action.read_file.max_lines,
                )

            elif action.action == "run_tests":
                assert action.run_tests is not None

                result = run_tests(
                    self.workspace,
                    command=action.run_tests.command,
                    timeout_seconds=action.run_tests.timeout_seconds,
                )

            elif action.action == "finish":
                assert action.finish is not None

                return {
                    "tool": "finish",
                    "success": True,
                    "result": action.finish.model_dump(),
                    "summary": action.finish.diagnosis,
                }

            else:
                raise ToolExecutionError(
                    f"Unsupported action: {action.action}"
                )

        except Exception as exc:
            return {
                "tool": action.action,
                "success": False,
                "result": None,
                "summary": str(exc),
                "error_type": type(exc).__name__,
            }

        result_data = result.model_dump()

        return {
            "tool": action.action,
            "success": True,
            "result": result_data,
            "summary": self._summarize_result(
                action.action,
                result_data,
            ),
        }

    def _summarize_result(
        self,
        tool: str,
        result: dict,
    ) -> str:
        if tool == "list_directory":
            entries = result["entries"]

            location = (
                "repository root"
                if result["path"] == "."
                else result["path"]
            )

            return (
                f"Listed {len(entries)} entries in "
                f"{location}."
            )

        if tool == "search_code":
            matches = result["matches"]

            return (
                f"Found {len(matches)} matches for "
                f"{json.dumps(result['query'])}."
            )

        if tool == "read_file":
            return (
                f"Read {result['returned_lines']} of "
                f"{result['total_lines']} lines from "
                f"{result['path']}."
            )

        if tool == "run_tests":
            if result["timed_out"]:
                return "Test execution timed out."

            return (
                f"Tests finished with exit code "
                f"{result['exit_code']}."
            )
        return "Tool completed."