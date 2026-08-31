from pathlib import Path

from debugger_agent.repository.workspace import RepositoryWorkspace
from debugger_agent.tools.filesystem import list_directory, read_file
from debugger_agent.tools.search import search_code


FIXTURE_REPO = (
    Path(__file__).parent
    / "fixtures"
    / "sample_repo"
)


def test_repository_inspection_workflow():
    workspace = RepositoryWorkspace(FIXTURE_REPO)

    listing = list_directory(workspace, "app")

    entry_names = {entry.name for entry in listing.entries}

    assert "auth.py" in entry_names
    assert "tokens.py" in entry_names

    search_result = search_code(
        workspace,
        "refresh_access_token",
    )

    assert search_result.matches

    matching_paths = {
        match.path
        for match in search_result.matches
    }

    assert "app/auth.py" in matching_paths

    file_result = read_file(
        workspace,
        "app/auth.py",
    )

    assert "def refresh_access_token" in file_result.content
    assert file_result.truncated is False