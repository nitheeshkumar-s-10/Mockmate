from pathlib import Path
import pytest

from mockmate.security import write_workspace_file, ApprovalRequired


def test_existing_file_requires_approval(tmp_path, monkeypatch):
    import mockmate.security as security
    monkeypatch.setattr(security, "WORKSPACE_DIR", tmp_path)
    (tmp_path / "weak-topics.md").write_text("old", encoding="utf-8")
    with pytest.raises(ApprovalRequired):
        write_workspace_file("weak-topics.md", "new")
    assert (tmp_path / "weak-topics.md").read_text(encoding="utf-8") == "old"


def test_approved_write_replaces_file(tmp_path, monkeypatch):
    import mockmate.security as security
    monkeypatch.setattr(security, "WORKSPACE_DIR", tmp_path)
    (tmp_path / "weak-topics.md").write_text("old", encoding="utf-8")
    write_workspace_file("weak-topics.md", "new", approved=True)
    assert (tmp_path / "weak-topics.md").read_text(encoding="utf-8") == "new"
