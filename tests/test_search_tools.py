from pathlib import Path

import pytest

from debugger_agent.repository.workspace import RepositoryWorkspace
from debugger_agent.tools.search import search_code


def test_search_code_finds_matching_lines(tmp_path: Path):
    repo = tmp_path / "repo"
    repo.mkdir()

    auth_file = repo / "auth.py"
    auth_file.write_text(
        "def login():\n"
        "    pass\n\n"
        "def refresh_token():\n"
        "    pass\n",
        encoding="utf-8",
    )

    workspace = RepositoryWorkspace(repo)

    result = search_code(workspace, "refresh_token")

    assert result.query == "refresh_token"
    assert result.truncated is False
    assert len(result.matches) == 1

    match = result.matches[0]

    assert match.path == "auth.py"
    assert match.line_number == 4
    assert match.line == "def refresh_token():"


def test_search_code_is_case_insensitive(tmp_path: Path):
    repo = tmp_path / "repo"
    repo.mkdir()

    file_path = repo / "tokens.py"
    file_path.write_text(
        "REFRESH_TOKEN_EXPIRY = 3600",
        encoding="utf-8",
    )

    workspace = RepositoryWorkspace(repo)

    result = search_code(workspace, "refresh_token")

    assert len(result.matches) == 1


def test_search_code_searches_multiple_files(tmp_path: Path):
    repo = tmp_path / "repo"
    repo.mkdir()

    (repo / "auth.py").write_text(
        "refresh_token = 'abc'",
        encoding="utf-8",
    )

    (repo / "service.py").write_text(
        "def validate_refresh_token():\n"
        "    pass",
        encoding="utf-8",
    )

    workspace = RepositoryWorkspace(repo)

    result = search_code(workspace, "refresh_token")

    assert len(result.matches) == 2


def test_search_code_returns_empty_result(tmp_path: Path):
    repo = tmp_path / "repo"
    repo.mkdir()

    (repo / "main.py").write_text(
        "print('hello')",
        encoding="utf-8",
    )

    workspace = RepositoryWorkspace(repo)

    result = search_code(workspace, "does_not_exist")

    assert result.matches == []
    assert result.truncated is False


def test_search_code_respects_max_results(tmp_path: Path):
    repo = tmp_path / "repo"
    repo.mkdir()

    (repo / "example.py").write_text(
        "\n".join(["refresh_token"] * 10),
        encoding="utf-8",
    )

    workspace = RepositoryWorkspace(repo)

    result = search_code(
        workspace,
        "refresh_token",
        max_results=3,
    )

    assert len(result.matches) == 3
    assert result.truncated is True


def test_search_code_rejects_empty_query(tmp_path: Path):
    repo = tmp_path / "repo"
    repo.mkdir()

    workspace = RepositoryWorkspace(repo)

    with pytest.raises(ValueError):
        search_code(workspace, "")


def test_search_code_rejects_invalid_max_results(tmp_path: Path):
    repo = tmp_path / "repo"
    repo.mkdir()

    workspace = RepositoryWorkspace(repo)

    with pytest.raises(ValueError):
        search_code(workspace, "token", max_results=0)


def test_search_code_ignores_virtual_environment(tmp_path: Path):
    repo = tmp_path / "repo"
    repo.mkdir()

    venv = repo / ".venv"
    venv.mkdir()

    (venv / "secret.py").write_text(
        "refresh_token",
        encoding="utf-8",
    )

    workspace = RepositoryWorkspace(repo)

    result = search_code(workspace, "refresh_token")

    assert result.matches == []