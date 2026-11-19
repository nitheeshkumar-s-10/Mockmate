from mockmate.schemas import Scorecard


def test_scorecard_shape_is_stable():
    score = Scorecard(
        score=2,
        strengths=["Named the concept", "Attempted an explanation"],
        gaps=["Definition is inaccurate", "No example or reasoning"],
        hint="Start by defining the concept precisely.",
        next_topic="Core definitions",
    )
    assert score.model_dump()["score"] == 2
