from pathlib import Path

import pytest

from debugger_agent.repository.workspace import (
    RepositoryWorkspace,
)
from debugger_agent.tools.testing import (
    TestExecutionError,
    run_tests,
)


def create_repo(tmp_path: Path) -> RepositoryWorkspace:
    repo = tmp_path / "repo"
    repo.mkdir()

    (repo / "test_example.py").write_text(
        "def test_example():\n"
        "    assert 1 + 1 == 2\n",
        encoding="utf-8",
    )

    return RepositoryWorkspace(repo)


def test_run_tests_executes_pytest(
    tmp_path: Path,
):
    workspace = create_repo(tmp_path)

    result = run_tests(workspace)

    assert result.exit_code == 0
    assert result.timed_out is False
    assert "passed" in result.stdout.lower()


def test_run_tests_captures_failure(
    tmp_path: Path,
):
    repo = tmp_path / "repo"
    repo.mkdir()

    (repo / "test_failure.py").write_text(
        "def test_failure():\n"
        "    assert False\n",
        encoding="utf-8",
    )

    workspace = RepositoryWorkspace(repo)

    result = run_tests(workspace)

    assert result.exit_code != 0
    assert result.timed_out is False
    assert "failed" in result.stdout.lower()


def test_run_tests_rejects_unapproved_command(
    tmp_path: Path,
):
    workspace = create_repo(tmp_path)

    with pytest.raises(TestExecutionError):
        run_tests(
            workspace,
            command=["python", "something.py"],
        )


def test_run_tests_rejects_invalid_timeout(
    tmp_path: Path,
):
    workspace = create_repo(tmp_path)

    with pytest.raises(ValueError):
        run_tests(
            workspace,
            timeout_seconds=0,
        )