import pytest
from pydantic import ValidationError

from mockmate.schemas import Scorecard


def test_valid_scorecard():
    item = Scorecard(
        score=5,
        strengths=["Correct definition", "Relevant example"],
        gaps=["Missing trade-off", "No complexity analysis"],
        hint="Consider the runtime and memory implications.",
        next_topic="Time complexity",
    )
    assert item.score == 5
    assert len(item.strengths) == 2
    assert len(item.gaps) == 2


def test_invalid_score_is_rejected():
    with pytest.raises(ValidationError):
        Scorecard(
            score=11,
            strengths=["a", "b"],
            gaps=["c", "d"],
            hint="A useful hint.",
            next_topic="Topic",
        )


def test_missing_gap_is_rejected():
    with pytest.raises(ValidationError):
        Scorecard(
            score=5,
            strengths=["a", "b"],
            gaps=["only one"],
            hint="A useful hint.",
            next_topic="Topic",
        )
