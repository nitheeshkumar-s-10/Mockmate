from .config import WEAK_TOPICS_FILE, WORKSPACE_DIR
from .memory import render_weak_topics
from .security import safe_workspace_path, write_workspace_file, delete_workspace_file



def approve_weak_topic_update(entries: list[dict]) -> bool:
    new_content = render_weak_topics(entries)

    if WEAK_TOPICS_FILE.exists():
        print("\nMockMate wants to update workspace/weak-topics.md.")
    else:
        print("\nMockMate wants to create workspace/weak-topics.md.")

    print("\nProposed weak-topic information:")
    print(new_content)

    choice = input(
        "[A]pprove / [E]dit replacement / [R]eject: "
    ).strip().lower()

    if choice in {"a", "approve"}:
        write_workspace_file("weak-topics.md", new_content, approved=True)
        print("Weak-topic file saved successfully.")
        return True

    if choice in {"e", "edit"}:
        print("Enter replacement content. Finish with a line containing .SAVE")
        lines = []

        while True:
            line = input()
            if line == ".SAVE":
                break
            lines.append(line)

        edited = "\n".join(lines).strip() + "\n"
        write_workspace_file("weak-topics.md", edited, approved=True)
        print("Your edited weak-topic file was saved.")
        return True

    print("Rejected. The weak-topic file was not changed.")
    return False



def delete_session_with_approval(thread_id: str) -> None:
    import re
    safe_id = re.sub(r"[^A-Za-z0-9_.-]", "_", thread_id)[:80]
    relative = f"sessions/{safe_id}.md"
    target = safe_workspace_path(relative)
    if not target.exists():
        print("No saved session file found.")
        return
    print(f"\nSession file: {relative}")
    print(target.read_text(encoding="utf-8")[:2500])
    choice = input("[A]pprove delete / [E]dit file / [R]eject: ").strip().lower()
    if choice in {"a", "approve"}:
        delete_workspace_file(relative, approved=True)
        print("Session file deleted.")
    elif choice in {"e", "edit"}:
        print("Enter replacement content. Finish with a line containing .SAVE")
        lines = []
        while True:
            line = input()
            if line == ".SAVE":
                break
            lines.append(line)
        target.write_text("\n".join(lines) + "\n", encoding="utf-8")
        print("Session file edited; it was not deleted.")
    else:
        print("Rejected. The session file was left untouched.")
