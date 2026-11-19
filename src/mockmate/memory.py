from datetime import datetime
from pathlib import Path
import re

from .config import SESSIONS_DIR, WEAK_TOPICS_FILE, ensure_workspace
from .security import safe_workspace_path


def load_weak_topics() -> list[str]:
    ensure_workspace()
    if not WEAK_TOPICS_FILE.exists():
        return []
    text = WEAK_TOPICS_FILE.read_text(encoding="utf-8")
    topics = []
    for line in text.splitlines():
        match = re.match(r"^\s*-\s+(.+?)\s+\|\s+score:\s*(\d+)", line)
        if match:
            topics.append(match.group(1).strip())
    return list(dict.fromkeys(topics))


def render_weak_topics(entries: list[dict]) -> str:
    lines = [
        "# MockMate Weak Topics",
        "",
        "Topics are prioritised from lower-scoring answers. This file is local user data.",
        "",
    ]
    if not entries:
        lines.append("_No weak topics recorded yet._")
    else:
        for item in entries:
            lines.append(
                f"- {item['topic']} | score: {item['score']}/10 | "
                f"updated: {item['date']} | note: {item.get('note', 'Needs revision')}"
            )
    return "\n".join(lines) + "\n"


def update_weak_topic_entries(new_entry: dict) -> list[dict]:
    ensure_workspace()
    entries = []
    if WEAK_TOPICS_FILE.exists():
        for line in WEAK_TOPICS_FILE.read_text(encoding="utf-8").splitlines():
            match = re.match(
                r"^\s*-\s+(.+?)\s+\|\s+score:\s*(\d+)/10\s+\|\s+updated:\s*(.+?)\s+\|\s+note:\s*(.*)$",
                line,
            )
            if match:
                entries.append({
                    "topic": match.group(1), "score": int(match.group(2)),
                    "date": match.group(3), "note": match.group(4)
                })
    topic = new_entry["topic"]
    entries = [e for e in entries if e["topic"].lower() != topic.lower()]
    entries.append(new_entry)
    entries.sort(key=lambda e: e["score"])
    return entries[:20]


def save_session(thread_id: str, state: dict) -> Path:
    ensure_workspace()
    safe_id = re.sub(r"[^A-Za-z0-9_.-]", "_", thread_id)[:80]
    relative = Path("sessions") / f"{safe_id}.md"
    target = safe_workspace_path(relative)
    history = state.get("history", [])
    lines = [
        f"# MockMate Session: {thread_id}",
        "",
        f"- Role: {state.get('role', 'Unknown')}",
        f"- Round: {state.get('round_name', 'Unknown')}",
        f"- Difficulty: {state.get('difficulty', 'Unknown')}",
        f"- Questions: {state.get('question_number', 0)}/{state.get('total_questions', 5)}",
        f"- Updated: {datetime.now().astimezone().isoformat(timespec='seconds')}",
        "",
        "## Interview transcript",
        "",
    ]
    for index, item in enumerate(history, 1):
        lines += [
            f"### Question {index}: {item.get('question', '')}",
            "",
            f"**Candidate answer:** {item.get('answer', '')}",
            "",
            f"**Score:** {item.get('score', 0)}/10",
            "",
            "**Strengths:**",
        ]
        lines += [f"- {x}" for x in item.get("strengths", [])]
        lines += ["", "**Gaps:**"]
        lines += [f"- {x}" for x in item.get("gaps", [])]
        lines += ["", f"**Hint:** {item.get('hint', '')}", ""]
    if state.get("current_question"):
        lines += ["## Current question", "", state["current_question"], ""]
    if state.get("summary"):
        lines += ["## Running summary", "", state["summary"], ""]
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("\n".join(lines), encoding="utf-8")
    return target
