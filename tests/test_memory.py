
from mockmate.schemas import Scorecard
from mockmate.agent import _filter_weak_topics


def test_scorecard_shape_is_stable():
    score = Scorecard(
        score=2,
        strengths=["Named the concept", "Attempted an explanation"],
        gaps=["Definition is inaccurate", "No example or reasoning"],
        hint="Start by defining the concept precisely.",
        next_topic="Core definitions",
    )
    assert score.model_dump()["score"] == 2


def test_dsa_ignores_ml_weak_topics():
    topics = ["ml fundamentals", "dsa fundamentals"]

    result = _filter_weak_topics(topics, "dsa")

    assert result == ["dsa fundamentals"]


def test_ml_keeps_ml_weak_topics():
    topics = ["ml fundamentals", "dsa fundamentals"]

    result = _filter_weak_topics(topics, "ML Fundamentals")

    assert result == ["ml fundamentals"]


def test_behavioural_keeps_behavioural_topics():
    topics = [
        "ml fundamentals",
        "dsa fundamentals",
        "teamwork",
        "communication",
    ]

    result = _filter_weak_topics(topics, "Behavioural")

    assert result == ["teamwork", "communication"]
