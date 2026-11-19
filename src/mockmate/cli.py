import re
import uuid

from langgraph.checkpoint.sqlite import SqliteSaver

from .agent import build_interview_graph
from .approval import approve_weak_topic_update, delete_session_with_approval
from .config import CHECKPOINT_DB, ensure_workspace
from .deep_workspace import build_workspace_agent
from .memory import load_weak_topics, save_session, update_weak_topic_entries
from .model import build_model


def _ask_setup():
    print("\nWhat role are you preparing for?")
    role = input("> ").strip()
    if role.lower() == "just start" or not role:
        role, round_name, difficulty = "Software Engineer", "DSA", "Intermediate"
        print("Defaults selected: Software Engineer / DSA / Intermediate.")
        return role, round_name, difficulty

    print("\nWhich interview round? (ML Fundamentals / DSA / Behavioural)")
    round_name = input("> ").strip() or "DSA"
    print("\nDifficulty? (Beginner / Intermediate / Advanced)")
    difficulty = input("> ").strip() or "Intermediate"
    return role, round_name, difficulty


def _print_output(state: dict):
    notice = state.get("context_notice")
    if notice:
        print(f"\n{notice}")
    print(f"\nMockMate:\n{state.get('output', '')}")


def main():
    print("=" * 52)
    print("                 MOCKMATE")
    print("       AI-POWERED MOCK TECHNICAL INTERVIEW")
    print("=" * 52)
    ensure_workspace()

    try:
        model = build_model()
    except Exception as exc:
        print(f"\nConfiguration error: {exc}")
        return

    weak_topics = load_weak_topics()
    if weak_topics:
        print("\nI loaded your saved weak topics:")
        for topic in weak_topics[:5]:
            print(f" - {topic}")
    else:
        print("\nNo saved weak topics found. This will be a fresh interview.")

    print("\nEnter an existing thread ID to resume, or press Enter for a new session.")
    thread_id = input("Thread ID: ").strip() or str(uuid.uuid4())
    print(f"Session thread_id: {thread_id}")

    with SqliteSaver.from_conn_string(str(CHECKPOINT_DB)) as checkpointer:
        graph = build_interview_graph(model).compile(checkpointer=checkpointer)
        config = {"configurable": {"thread_id": thread_id}}
        saved = graph.get_state(config)
        existing = bool(saved and saved.values and saved.values.get("current_question")
                        and not saved.values.get("finished"))

        if existing:
            state = saved.values
            role = state["role"]
            round_name = state["round_name"]
            difficulty = state["difficulty"]
            total_questions = state["total_questions"]
            print(
                f"\nResuming: {role} / {round_name} / {difficulty} "
                f"({state.get('question_number')} of {total_questions})"
            )
            print(f"\nMockMate:\n{state.get('current_question')}")
        else:
            role, round_name, difficulty = _ask_setup()
            try:
                total_questions = int(input("\nHow many questions? (default 5): ").strip() or "5")
                total_questions = max(1, min(total_questions, 20))
            except ValueError:
                total_questions = 5

            initial = {
                "role": role,
                "round_name": round_name,
                "difficulty": difficulty,
                "total_questions": total_questions,
                "question_number": 0,
                "current_question": "",
                "current_topic": "",
                "user_answer": "",
                "history": [],
                "weak_topics": weak_topics,
                "summary": "",
                "finished": False,
            }
            state = graph.invoke(initial, config)
            _print_output(state)
            save_session(thread_id, state)

        # Deep Agents assistant is optional during an interview, but is genuinely
        # callable and its filesystem backend is rooted only at workspace/.
        deep_agent = None

        while not state.get("finished", False):
            answer = input(
                "\nYou (/quit, /workspace-summary, /delete-session): "
            ).strip()

            if answer.lower() == "/quit":
                print("Interview paused. Run again with the same thread ID to resume.")
                break

            if answer.lower() == "/delete-session":
                delete_session_with_approval(thread_id)
                continue

            if answer.lower() == "/workspace-summary":
                if deep_agent is None:
                    try:
                        deep_agent = build_workspace_agent(model)
                    except Exception as exc:
                        print(f"Deep Agents could not start: {exc}")
                        continue
                safe_id = re.sub(r"[^A-Za-z0-9_.-]", "_", thread_id)[:80]
                request = (
                    f"Read sessions/{safe_id}.md from your workspace and summarize "
                    "the candidate's performance, strongest areas, and topics to revise. "
                    "Do not modify or delete any files."
                )
                try:
                    result = deep_agent.invoke({"messages": [{"role": "user", "content": request}]})
                    messages = result.get("messages", [])
                    print("\nDeep Agents workspace summary:")
                    print(messages[-1].content if messages else result)
                except Exception as exc:
                    print(f"Workspace summary failed: {exc}")
                continue

            if not answer:
                print("Please enter an answer, or type /quit.")
                continue

            try:
                state = graph.invoke({"user_answer": answer}, config)
            except Exception as exc:
                print(f"\nCould not complete this turn: {exc}")
                print("Your previous checkpoint remains available. Try again.")
                continue

            _print_output(state)
            save_session(thread_id, state)

            weak_update = state.get("weak_topic_update")
            if weak_update:
                entries = update_weak_topic_entries(weak_update)
                approve_weak_topic_update(entries)

        if state.get("finished"):
            print("\nInterview finished. Summary:")
            scores = [item["score"] for item in state.get("history", [])]
            if scores:
                print(f"Average score: {sum(scores) / len(scores):.1f}/10")
            print(f"Session saved under workspace/sessions/.")
            print(f"Resume thread ID: {thread_id}")
