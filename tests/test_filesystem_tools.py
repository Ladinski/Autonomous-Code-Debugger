from pathlib import Path

import pytest

from debugger_agent.repository.workspace import (
    RepositoryWorkspace,
    WorkspaceSecurityError,
)
from debugger_agent.tools.filesystem import (
    FileReadError,
    read_file,
)

from debugger_agent.tools.filesystem import (
    FileReadError,
    list_directory,
    read_file,
)

def test_read_file_returns_content(tmp_path: Path):
    repo = tmp_path / "repo"
    repo.mkdir()

    file_path = repo / "example.py"
    file_path.write_text("line 1\nline 2\nline 3", encoding="utf-8")

    workspace = RepositoryWorkspace(repo)

    result = read_file(workspace, "example.py")

    assert result.path == "example.py"
    assert result.content == "line 1\nline 2\nline 3"
    assert result.truncated is False
    assert result.total_lines == 3
    assert result.returned_lines == 3


def test_read_file_truncates_large_file(tmp_path: Path):
    repo = tmp_path / "repo"
    repo.mkdir()

    file_path = repo / "large.py"
    file_path.write_text(
        "\n".join(f"line {i}" for i in range(10)),
        encoding="utf-8",
    )

    workspace = RepositoryWorkspace(repo)

    result = read_file(
        workspace,
        "large.py",
        max_lines=3,
    )

    assert result.content == "line 0\nline 1\nline 2"
    assert result.truncated is True
    assert result.total_lines == 10
    assert result.returned_lines == 3


def test_read_file_rejects_directory(tmp_path: Path):
    repo = tmp_path / "repo"
    repo.mkdir()

    directory = repo / "src"
    directory.mkdir()

    workspace = RepositoryWorkspace(repo)

    with pytest.raises(FileReadError):
        read_file(workspace, "src")


def test_read_file_rejects_missing_file(tmp_path: Path):
    repo = tmp_path / "repo"
    repo.mkdir()

    workspace = RepositoryWorkspace(repo)

    with pytest.raises(FileNotFoundError):
        read_file(workspace, "missing.py")


def test_read_file_cannot_escape_workspace(tmp_path: Path):
    repo = tmp_path / "repo"
    repo.mkdir()

    secret = tmp_path / "secret.txt"
    secret.write_text("private", encoding="utf-8")

    workspace = RepositoryWorkspace(repo)

    with pytest.raises(WorkspaceSecurityError):
        read_file(workspace, "../secret.txt")


def test_read_file_rejects_invalid_max_lines(tmp_path: Path):
    repo = tmp_path / "repo"
    repo.mkdir()

    file_path = repo / "example.py"
    file_path.write_text("hello", encoding="utf-8")

    workspace = RepositoryWorkspace(repo)

    with pytest.raises(ValueError):
        read_file(workspace, "example.py", max_lines=0)

def test_read_file_rejects_invalid_utf8(tmp_path: Path):
    repo = tmp_path / "repo"
    repo.mkdir()

    binary_file = repo / "binary.bin"
    binary_file.write_bytes(b"\xff\xfe\x00\x01")

    workspace = RepositoryWorkspace(repo)

    with pytest.raises(FileReadError):
        read_file(workspace, "binary.bin")


def test_list_directory_returns_structured_entries(tmp_path: Path):
    repo = tmp_path / "repo"
    repo.mkdir()

    (repo / "src").mkdir()
    (repo / "README.md").write_text("hello", encoding="utf-8")

    workspace = RepositoryWorkspace(repo)

    result = list_directory(workspace)

    assert result.path == "."
    assert len(result.entries) == 2

    assert result.entries[0].name == "README.md"
    assert result.entries[0].type == "file"

    assert result.entries[1].name == "src"
    assert result.entries[1].type == "directory"


def test_list_directory_rejects_file_path(tmp_path: Path):
    repo = tmp_path / "repo"
    repo.mkdir()

    file_path = repo / "example.py"
    file_path.write_text("hello", encoding="utf-8")

    workspace = RepositoryWorkspace(repo)

    with pytest.raises(NotADirectoryError):
        list_directory(workspace, "example.py")


def test_list_directory_cannot_escape_workspace(tmp_path: Path):
    repo = tmp_path / "repo"
    repo.mkdir()

    workspace = RepositoryWorkspace(repo)

    with pytest.raises(WorkspaceSecurityError):
        list_directory(workspace, "..")