from pydantic import BaseModel

from debugger_agent.repository.workspace import RepositoryWorkspace


class PatchResult(BaseModel):
    path: str
    replacements: int
    changed: bool


class PatchError(ValueError):
    """Raised when a requested patch cannot be safely applied."""


def replace_text(
    workspace: RepositoryWorkspace,
    path: str,
    old_text: str,
    new_text: str,
) -> PatchResult:
    if not old_text:
        raise PatchError("old_text cannot be empty.")

    resolved_path = workspace.resolve_path(path)

    if not resolved_path.exists():
        raise FileNotFoundError(
            f"File does not exist: {path}"
        )

    if not resolved_path.is_file():
        raise PatchError(
            f"Path is not a file: {path}"
        )

    try:
        content = resolved_path.read_text(
            encoding="utf-8"
        )
    except UnicodeDecodeError as exc:
        raise PatchError(
            f"File is not valid UTF-8 text: {path}"
        ) from exc

    occurrences = content.count(old_text)

    if occurrences == 0:
        raise PatchError(
            "Expected text was not found in the file."
        )

    if occurrences > 1:
        raise PatchError(
            "Expected text appears multiple times; "
            "patch must be unambiguous."
        )

    updated_content = content.replace(
        old_text,
        new_text,
        1,
    )

    resolved_path.write_text(
        updated_content,
        encoding="utf-8",
    )

    return PatchResult(
        path=resolved_path.relative_to(
            workspace.root
        ).as_posix(),
        replacements=1,
        changed=True,
    )