from pathlib import Path
import shutil

from debugger_agent.repository.workspace import (
    RepositoryWorkspace,
)


def test_fixture_copy_can_be_modified_without_changing_original(
    tmp_path: Path,
):
    original = tmp_path / "original"
    original.mkdir()

    source_file = original / "app.py"

    source_file.write_text(
        "value = False\n",
        encoding="utf-8",
    )

    copied = tmp_path / "copied"

    shutil.copytree(
        original,
        copied,
    )

    workspace = RepositoryWorkspace(
        copied
    )

    copied_file = workspace.resolve_path(
        "app.py"
    )

    copied_file.write_text(
        "value = True\n",
        encoding="utf-8",
    )

    assert (
        source_file.read_text(
            encoding="utf-8"
        )
        == "value = False\n"
    )

    assert (
        copied_file.read_text(
            encoding="utf-8"
        )
        == "value = True\n"
    )