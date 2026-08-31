from pathlib import Path


class WorkspaceSecurityError(ValueError):
    """Raised when a requested path escapes the repository workspace."""


class RepositoryWorkspace:
    def __init__(self, root: str | Path):
        self.root = Path(root).resolve()

        if not self.root.exists():
            raise FileNotFoundError(f"Workspace root does not exist: {self.root}")

        if not self.root.is_dir():
            raise NotADirectoryError(f"Workspace root is not a directory: {self.root}")

    def resolve_path(self, relative_path: str | Path) -> Path:
        requested_path = Path(relative_path)

        if requested_path.is_absolute():
            raise WorkspaceSecurityError("Absolute paths are not allowed.")

        resolved_path = (self.root / requested_path).resolve()

        try:
            resolved_path.relative_to(self.root)
        except ValueError as exc:
            raise WorkspaceSecurityError(
                f"Path escapes workspace: {relative_path}"
            ) from exc

        return resolved_path