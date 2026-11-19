from pathlib import Path

from .config import WORKSPACE_DIR


class WorkspaceSecurityError(ValueError):
    """Raised when an operation attempts to escape workspace/."""


class ApprovalRequired(PermissionError):
    """Raised when a destructive write needs explicit user approval."""


def safe_workspace_path(relative_path: str | Path) -> Path:
    raw = str(relative_path).strip()
    if not raw:
        raise WorkspaceSecurityError("Empty workspace path is not allowed.")

    candidate = Path(raw)
    # Absolute paths are rejected even if they happen to resolve under workspace.
    if candidate.is_absolute():
        raise WorkspaceSecurityError("Absolute paths are not allowed.")

    resolved_root = WORKSPACE_DIR.resolve()
    resolved_target = (resolved_root / candidate).resolve()
    try:
        resolved_target.relative_to(resolved_root)
    except ValueError as exc:
        raise WorkspaceSecurityError(
            f"Blocked path outside workspace/: {relative_path}"
        ) from exc
    return resolved_target


def write_workspace_file(relative_path: str, content: str, *, approved: bool = False) -> Path:
    target = safe_workspace_path(relative_path)
    if target.exists() and not approved:
        raise ApprovalRequired(f"Overwriting {relative_path} requires approval.")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")
    return target


def delete_workspace_file(relative_path: str, *, approved: bool = False) -> None:
    target = safe_workspace_path(relative_path)
    if not target.exists():
        raise FileNotFoundError(relative_path)
    if not approved:
        raise ApprovalRequired(f"Deleting {relative_path} requires approval.")
    if not target.is_file():
        raise WorkspaceSecurityError("Only individual files may be deleted.")
    target.unlink()
