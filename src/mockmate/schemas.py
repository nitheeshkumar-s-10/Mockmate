from pydantic import BaseModel, Field, ConfigDict


class Scorecard(BaseModel):
    """Validated evaluation returned for every submitted answer."""

    model_config = ConfigDict(extra="forbid")

    score: int = Field(ge=0, le=10, description="Answer score from 0 to 10")
    strengths: list[str] = Field(min_length=2, max_length=2)
    gaps: list[str] = Field(min_length=2, max_length=2)
    hint: str = Field(min_length=5)
    next_topic: str = Field(min_length=2)
