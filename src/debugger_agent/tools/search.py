from pathlib import Path

from debugger_agent.repository.models import SearchMatch, SearchResult
from debugger_agent.repository.workspace import RepositoryWorkspace


DEFAULT_IGNORED_DIRECTORIES = {
    ".git",
    ".venv",
    "venv",
    "__pycache__",
    ".pytest_cache",
    "node_modules",
    "dist",
    "build",
}


def search_code(
    workspace: RepositoryWorkspace,
    query: str,
    max_results: int = 50,
) -> SearchResult:
    if not query.strip():
        raise ValueError("Search query cannot be empty.")

    if max_results <= 0:
        raise ValueError("max_results must be greater than 0.")

    matches: list[SearchMatch] = []
    truncated = False

    for file_path in _iter_searchable_files(workspace.root):
        try:
            text = file_path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue

        for line_number, line in enumerate(text.splitlines(), start=1):
            if query.lower() not in line.lower():
                continue

            if len(matches) >= max_results:
                truncated = True
                return SearchResult(
                    query=query,
                    matches=matches,
                    truncated=truncated,
                )

            matches.append(
                SearchMatch(
                    path=file_path.relative_to(workspace.root).as_posix(),
                    line_number=line_number,
                    line=line.strip(),
                )
            )

    return SearchResult(
        query=query,
        matches=matches,
        truncated=truncated,
    )


def _iter_searchable_files(root: Path):
    for path in root.rglob("*"):
        if not path.is_file():
            continue

        relative_path = path.relative_to(root)

        if any(
            part in DEFAULT_IGNORED_DIRECTORIES
            for part in relative_path.parts
        ):
            continue

        yield path