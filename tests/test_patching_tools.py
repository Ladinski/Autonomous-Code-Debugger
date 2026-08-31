from pathlib import Path

import pytest

from debugger_agent.repository.workspace import (
    RepositoryWorkspace,
)
from debugger_agent.tools.patching import (
    PatchError,
    replace_text,
)


def create_repo(
    tmp_path: Path,
) -> RepositoryWorkspace:
    repo = tmp_path / "repo"
    repo.mkdir()

    (repo / "auth.py").write_text(
        "def check():\n"
        "    return False\n",
        encoding="utf-8",
    )

    return RepositoryWorkspace(repo)


def test_replace_text_changes_file(
    tmp_path: Path,
):
    workspace = create_repo(tmp_path)

    result = replace_text(
        workspace,
        path="auth.py",
        old_text="return False",
        new_text="return True",
    )

    content = (
        workspace.root / "auth.py"
    ).read_text(encoding="utf-8")

    assert result.changed is True
    assert result.replacements == 1
    assert "return True" in content


def test_replace_text_rejects_missing_text(
    tmp_path: Path,
):
    workspace = create_repo(tmp_path)

    with pytest.raises(PatchError):
        replace_text(
            workspace,
            path="auth.py",
            old_text="does not exist",
            new_text="replacement",
        )


def test_replace_text_rejects_ambiguous_match(
    tmp_path: Path,
):
    repo = tmp_path / "repo"
    repo.mkdir()

    (repo / "example.py").write_text(
        "value = 1\n"
        "value = 1\n",
        encoding="utf-8",
    )

    workspace = RepositoryWorkspace(repo)

    with pytest.raises(PatchError):
        replace_text(
            workspace,
            path="example.py",
            old_text="value = 1",
            new_text="value = 2",
        )


def test_replace_text_cannot_escape_workspace(
    tmp_path: Path,
):
    workspace = create_repo(tmp_path)

    with pytest.raises(ValueError):
        replace_text(
            workspace,
            path="../outside.py",
            old_text="a",
            new_text="b",
        )


def test_replace_text_rejects_empty_old_text(
    tmp_path: Path,
):
    workspace = create_repo(tmp_path)

    with pytest.raises(PatchError):
        replace_text(
            workspace,
            path="auth.py",
            old_text="",
            new_text="anything",
        )