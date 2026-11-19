"""Deep Agents integration for workspace review and behavioural-round guidance."""

from deepagents import create_deep_agent
from deepagents.backends import FilesystemBackend

from .config import WORKSPACE_DIR


def build_workspace_agent(model):
    # The backend's virtual root is workspace/, so Deep Agent filesystem paths
    # are confined to the application workspace rather than the repository root.
    backend = FilesystemBackend(root_dir=WORKSPACE_DIR, virtual_mode=True)
    return create_deep_agent(
        model=model,
        backend=backend,
        system_prompt=(
            "You are MockMate's workspace assistant. You may inspect and summarize "
            "interview files inside the workspace only. Never request or reveal secrets. "
            "Do not delete or overwrite files. For behavioural interviews, follow the "
            "STAR rubric supplied in the skill file."
        ),
        skills=["/skills/behavioural/"],
    )
