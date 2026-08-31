from pathlib import Path

from debugger_agent.repository.models import (
    DirectoryEntry,
    DirectoryListing,
    FileContent,
)
from debugger_agent.repository.workspace import RepositoryWorkspace


class FileReadError(ValueError):
    """Raised when a file cannot be safely read."""


def read_file(
    workspace: RepositoryWorkspace,
    path: str,
    max_lines: int = 500,
    max_bytes: int = 1_000_000,
) -> FileContent:
    resolved_path = workspace.resolve_path(path)

    if not resolved_path.exists():
        raise FileNotFoundError(f"File does not exist: {path}")

    if not resolved_path.is_file():
        raise FileReadError(f"Path is not a file: {path}")

    if max_lines <= 0:
        raise ValueError("max_lines must be greater than 0.")

    if max_bytes <= 0:
        raise ValueError("max_bytes must be greater than 0.")

    file_size = resolved_path.stat().st_size

    if file_size > max_bytes:
        raise FileReadError(
            f"File exceeds maximum allowed size: {path} "
            f"({file_size} bytes > {max_bytes} bytes)"
        )

    try:
        text = resolved_path.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        raise FileReadError(
            f"File is not valid UTF-8 text: {path}"
        ) from exc

    lines = text.splitlines()
    returned = lines[:max_lines]

    return FileContent(
        path=resolved_path.relative_to(workspace.root).as_posix(),
        content="\n".join(returned),
        truncated=len(lines) > max_lines,
        total_lines=len(lines),
        returned_lines=len(returned),
    )
def list_directory(
    workspace: RepositoryWorkspace,
    path: str = ".",
) -> DirectoryListing:
    resolved_path = workspace.resolve_path(path)

    if not resolved_path.exists():
        raise FileNotFoundError(f"Directory does not exist: {path}")

    if not resolved_path.is_dir():
        raise NotADirectoryError(f"Path is not a directory: {path}")

    entries: list[DirectoryEntry] = []

    for entry in sorted(
        resolved_path.iterdir(),
        key=lambda item: item.name.lower(),
    ):
        if entry.is_symlink():
            entry_type = "symlink"
        elif entry.is_dir():
            entry_type = "directory"
        elif entry.is_file():
            entry_type = "file"
        else:
            entry_type = "other"

        entries.append(
            DirectoryEntry(
                name=entry.name,
                path=entry.relative_to(workspace.root).as_posix(),
                type=entry_type,
            )
        )

    relative_path = resolved_path.relative_to(workspace.root)

    return DirectoryListing(
        path="." if relative_path == Path(".") else relative_path.as_posix(),
        entries=entries,
    )