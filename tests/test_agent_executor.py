from pathlib import Path

from debugger_agent.agent.actions import (
    AgentAction,
    FinishArgs,
    ListDirectoryArgs,
    ReadFileArgs,
    SearchCodeArgs,
)
from debugger_agent.agent.executor import ToolExecutor
from debugger_agent.repository.workspace import RepositoryWorkspace


def create_repo(tmp_path: Path) -> RepositoryWorkspace:
    repo = tmp_path / "repo"
    repo.mkdir()

    app = repo / "app"
    app.mkdir()

    (app / "auth.py").write_text(
        "def refresh_token():\n"
        "    return 'token'\n",
        encoding="utf-8",
    )

    return RepositoryWorkspace(repo)


def test_executor_lists_directory(tmp_path: Path):
    workspace = create_repo(tmp_path)
    executor = ToolExecutor(workspace)

    action = AgentAction(
        action="list_directory",
        reasoning_summary="Inspect repository.",
        list_directory=ListDirectoryArgs(
            path=".",
        ),
    )

    observation = executor.execute(action)

    assert observation["success"] is True
    assert observation["tool"] == "list_directory"
    assert observation["result"] is not None


def test_executor_searches_code(tmp_path: Path):
    workspace = create_repo(tmp_path)
    executor = ToolExecutor(workspace)

    action = AgentAction(
        action="search_code",
        reasoning_summary="Locate refresh code.",
        search_code=SearchCodeArgs(
            query="refresh_token",
        ),
    )

    observation = executor.execute(action)

    assert observation["success"] is True
    assert len(observation["result"]["matches"]) == 1


def test_executor_reads_file(tmp_path: Path):
    workspace = create_repo(tmp_path)
    executor = ToolExecutor(workspace)

    action = AgentAction(
        action="read_file",
        reasoning_summary="Inspect auth implementation.",
        read_file=ReadFileArgs(
            path="app/auth.py",
        ),
    )

    observation = executor.execute(action)

    assert observation["success"] is True
    assert "refresh_token" in observation["result"]["content"]


def test_executor_returns_structured_failure(tmp_path: Path):
    workspace = create_repo(tmp_path)
    executor = ToolExecutor(workspace)

    action = AgentAction(
        action="read_file",
        reasoning_summary="Inspect likely file.",
        read_file=ReadFileArgs(
            path="app/missing.py",
        ),
    )

    observation = executor.execute(action)

    assert observation["success"] is False
    assert observation["tool"] == "read_file"
    assert observation["error_type"] == "FileNotFoundError"


def test_executor_handles_finish(tmp_path: Path):
    workspace = create_repo(tmp_path)
    executor = ToolExecutor(workspace)

    action = AgentAction(
        action="finish",
        reasoning_summary="Evidence supports diagnosis.",
        finish=FinishArgs(
            diagnosis="Refresh token validation is incorrect.",
            confidence=0.9,
        ),
    )

    observation = executor.execute(action)

    assert observation["success"] is True
    assert observation["tool"] == "finish"
    assert observation["result"]["confidence"] == 0.9