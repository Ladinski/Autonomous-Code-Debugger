from pathlib import Path

import pytest

from debugger_agent.repository.workspace import (
    RepositoryWorkspace,
    WorkspaceSecurityError,
)


def test_workspace_accepts_valid_relative_path(tmp_path: Path):
    repo = tmp_path / "repo"
    repo.mkdir()

    src = repo / "src"
    src.mkdir()

    file_path = src / "main.py"
    file_path.write_text("print('hello')")

    workspace = RepositoryWorkspace(repo)

    resolved = workspace.resolve_path("src/main.py")

    assert resolved == file_path.resolve()


def test_workspace_normalizes_relative_path(tmp_path: Path):
    repo = tmp_path / "repo"
    repo.mkdir()

    src = repo / "src"
    src.mkdir()

    workspace = RepositoryWorkspace(repo)

    resolved = workspace.resolve_path("src/../src")

    assert resolved == src.resolve()


def test_workspace_rejects_parent_traversal(tmp_path: Path):
    repo = tmp_path / "repo"
    repo.mkdir()

    workspace = RepositoryWorkspace(repo)

    with pytest.raises(WorkspaceSecurityError):
        workspace.resolve_path("../secret.txt")


def test_workspace_rejects_absolute_path(tmp_path: Path):
    repo = tmp_path / "repo"
    repo.mkdir()

    workspace = RepositoryWorkspace(repo)

    absolute_path = tmp_path / "secret.txt"

    with pytest.raises(WorkspaceSecurityError):
        workspace.resolve_path(absolute_path)


def test_workspace_requires_existing_root(tmp_path: Path):
    missing_repo = tmp_path / "missing"

    with pytest.raises(FileNotFoundError):
        RepositoryWorkspace(missing_repo)   