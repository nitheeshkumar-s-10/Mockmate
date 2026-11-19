from typing import TypedDict, Any

from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import StateGraph, START, END

from .evaluator import evaluate_answer
from .prompts import INTERVIEWER_RULES, QUESTION_RULES



class InterviewState(TypedDict, total=False):
    role: str
    round_name: str
    difficulty: str
    total_questions: int
    question_number: int
    current_question: str
    current_topic: str
    user_answer: str
    history: list[dict[str, Any]]
    weak_topics: list[str]
    weak_topic_update: dict[str, Any] | None
    summary: str
    output: str
    finished: bool
    context_notice: str



def _clean_question(text: str) -> str:
    text = text.strip()
    text = "\n".join(line.strip() for line in text.splitlines() if line.strip())
    text = text.split("\n")[0].strip()
    if "?" in text:
        text = text[: text.index("?") + 1]
    elif text:
        text = text.rstrip(".!") + "?"
    return text


def _generate_question(model, state: InterviewState, topic: str) -> str:
    prompt = (
        f"Role: {state['role']}\nRound: {state['round_name']}\n"
        f"Difficulty: {state['difficulty']}\n"
        f"Topic to assess: {topic}\n"
        f"Previously covered topics: "
        f"{', '.join(x.get('topic', '') for x in state.get('history', [])) or 'None'}\n"
        f"Interview summary: {state.get('summary', '') or 'None'}\n"
        "Ask one new, relevant, assessable question."
    )
    result = model.invoke([
        SystemMessage(content=INTERVIEWER_RULES + "\n" + QUESTION_RULES),
        HumanMessage(content=prompt),
    ])
    content = result.content
    if isinstance(content, list):
        content = " ".join(str(x.get("text", "")) for x in content if isinstance(x, dict))
    question = _clean_question(str(content))
    if not question:
        raise RuntimeError("The model returned an empty interview question.")
    return question


def _summarize_old_history(model, history: list[dict], old_summary: str) -> str:
    old_items = history[:-3]
    transcript = "\n".join(
        f"Q: {x['question']}\nA: {x['answer']}\nScore: {x['score']}/10; topic: {x['topic']}"
        for x in old_items
    )
    result = model.invoke(
        "Compress this earlier interview history into a concise factual summary. "
        "Preserve role-relevant strengths, misconceptions, and weak topics. Do not invent facts.\n\n"
        f"Previous summary:\n{old_summary}\n\nEarlier turns:\n{transcript}"
    )
    return str(result.content).strip()


def build_interview_graph(model):
    def interview_turn(state: InterviewState) -> dict:
        history = list(state.get("history", []))
        question_number = int(state.get("question_number", 0))
        total = int(state.get("total_questions", 5))
        answer = str(state.get("user_answer", "")).strip()
        summary = state.get("summary", "")
        output_parts = []
        updates: dict = {"weak_topic_update": None}

        # Evaluate the answer to the currently displayed question.
        if state.get("current_question") and answer:
            scorecard = evaluate_answer(
                model,
                role=state["role"],
                round_name=state["round_name"],
                difficulty=state["difficulty"],
                question=state["current_question"],
                answer=answer,
                summary=summary,
            )
            topic = str(state.get("current_topic", state["round_name"])).strip()
            history.append({
                "question": state["current_question"],
                "answer": answer,
                "score": scorecard.score,
                "strengths": scorecard.strengths,
                "gaps": scorecard.gaps,
                "hint": scorecard.hint,
                "topic": topic,
                "suggested_next_topic": scorecard.next_topic.strip(),
            })
            output_parts += [
                f"\nScore: {scorecard.score}/10",
                "Strengths:",
                *[f"  + {x}" for x in scorecard.strengths],
                "Gaps:",
                *[f"  - {x}" for x in scorecard.gaps],
                f"Hint: {scorecard.hint}",
            ]
            updates["history"] = history
            updates["user_answer"] = ""

            if scorecard.score <= 6:
                weak = list(state.get("weak_topics", []))
                if topic not in weak:
                    weak.append(topic)
                updates["weak_topics"] = weak
                updates["weak_topic_update"] = {
                    "topic": topic,
                "suggested_next_topic": scorecard.next_topic.strip(),
                    "score": scorecard.score,
                    "date": __import__("datetime").date.today().isoformat(),
                    "note": "; ".join(scorecard.gaps),
                }

            # Keep the prompt bounded while preserving a running summary.
            if len(history) > 3:
                summary = _summarize_old_history(model, history, summary)
                updates["summary"] = summary
                updates["context_notice"] = (
                    f"[Context management active: summarized {len(history) - 3} earlier turns; "
                    "the latest three remain in detailed context.]"
                )

            if len(history) >= total:
                updates["finished"] = True
                updates["current_question"] = ""
                output_parts.append("\nInterview complete. Your session has been saved.")
                updates["output"] = "\n".join(output_parts)
                return updates

            target_topic = scorecard.next_topic.strip()
            weak_topics = updates.get("weak_topics", state.get("weak_topics", []))
            if weak_topics:
                target_topic = weak_topics[0]
            next_question = _generate_question(model, state, target_topic)
            question_number += 1
            updates.update({
                "question_number": question_number,
                "current_question": next_question,
                "current_topic": target_topic,
                "finished": False,
            })
            output_parts.append(
                f"\nQuestion {question_number} of {total}:\n{next_question}"
            )
            updates["output"] = "\n".join(output_parts)
            return updates

        # Initial question for a new thread.
        weak_topics = state.get("weak_topics", [])
        topic = weak_topics[0] if weak_topics else f"{state['round_name']} fundamentals"
        question = _generate_question(model, state, topic)
        updates.update({
            "question_number": 1,
            "current_question": question,
            "current_topic": topic,
            "history": history,
            "finished": False,
            "user_answer": "",
            "output": f"Question 1 of {total}:\n{question}",
        })
        return updates

    builder = StateGraph(InterviewState)
    builder.add_node("interview_turn", interview_turn)
    builder.add_edge(START, "interview_turn")
    builder.add_edge("interview_turn", END)
    return builder
