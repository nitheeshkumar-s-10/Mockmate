import pytest

from mockmate.security import safe_workspace_path, WorkspaceSecurityError


def test_workspace_relative_path_is_allowed():
    path = safe_workspace_path("sessions/demo.md")
    assert path.name == "demo.md"


@pytest.mark.parametrize("bad_path", ["../secrets.txt", "/tmp/outside.txt"])
def test_workspace_escape_is_refused(bad_path):
    with pytest.raises(WorkspaceSecurityError):
        safe_workspace_path(bad_path)


def test_symlink_escape_is_refused(tmp_path, monkeypatch):
    import mockmate.security as security

    workspace = tmp_path / "workspace"
    outside = tmp_path / "outside"
    workspace.mkdir()
    outside.mkdir()

    monkeypatch.setattr(security, "WORKSPACE_DIR", workspace)

    secret = outside / "secret.txt"
    secret.write_text("private", encoding="utf-8")

    link = workspace / "external"
    try:
        link.symlink_to(outside, target_is_directory=True)
    except OSError:
        pytest.skip("Symlink creation is not permitted on this system.")

    with pytest.raises(WorkspaceSecurityError):
        safe_workspace_path("external/secret.txt")

