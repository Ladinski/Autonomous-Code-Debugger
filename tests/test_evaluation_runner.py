from pathlib import Path
import shutil

from debugger_agent.evaluation.models import EvaluationCase
from debugger_agent.evaluation.runner import run_evaluation_case
from debugger_agent.repository.workspace import (
    RepositoryWorkspace,
)


def test_evaluation_saves_trace(
    tmp_path,
):
    fixture = tmp_path / "fixture"
    app_dir = fixture / "app"
    tests_dir = fixture / "tests"

    app_dir.mkdir(parents=True)
    tests_dir.mkdir(parents=True)

    (app_dir / "__init__.py").write_text(
        "",
        encoding="utf-8",
    )

    (tests_dir / "__init__.py").write_text(
        "",
        encoding="utf-8",
    )

    (app_dir / "example.py").write_text(
        "value = 1\n",
        encoding="utf-8",
    )

    case = EvaluationCase(
        name="trace_test",
        fixture_path=fixture,
        bug_report="Inspect the repository.",
        expected_file="app/example.py",
        expected_text="value = 1",
    )

    trace_directory = tmp_path / "traces"

    result = run_evaluation_case(
        case,
        max_iterations=3,
        max_patch_attempts=1,
        trace_directory=trace_directory,
    )

    assert result.trace_path is not None

    trace_path = Path(
        result.trace_path
    )

    assert trace_path.exists()
    assert trace_path.suffix == ".json"
    assert trace_path.parent == (
        trace_directory
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