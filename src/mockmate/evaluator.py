from langchain_core.messages import HumanMessage, SystemMessage

from .prompts import EVALUATION_RULES
from .schemas import Scorecard


def evaluate_answer(model, *, role: str, round_name: str, difficulty: str,
                    question: str, answer: str, summary: str = "") -> Scorecard:
    structured_model = model.with_structured_output(Scorecard)
    prompt = (
        f"Role: {role}\nRound: {round_name}\nDifficulty: {difficulty}\n"
        f"Question: {question}\nCandidate answer: {answer}\n"
        f"Earlier interview summary: {summary or 'None'}\n"
        "Return the required scorecard."
    )
    last_error = None
    for attempt in range(2):
        try:
            result = structured_model.invoke([
                SystemMessage(content=EVALUATION_RULES),
                HumanMessage(content=prompt if attempt == 0 else
                             prompt + "\nYour previous response failed schema validation. "
                             "Return a corrected object matching every field and constraint."),
            ])
            if isinstance(result, Scorecard):
                return result
            return Scorecard.model_validate(result)
        except Exception as exc:
            last_error = exc
    raise RuntimeError(
        "The model failed to produce a valid scorecard after two attempts. "
        "No unvalidated output was shown."
    ) from last_error
