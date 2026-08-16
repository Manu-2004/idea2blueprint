from pydantic import BaseModel, Field


class ClarifyingQuestion(BaseModel):
    """One question the intake agent wants answered before the pipeline drafts a spec.
    `choices` is a short list of suggested answers; the frontend always also lets the user
    type their own answer instead, so an empty `choices` list just means a fully open
    question."""

    key: str = Field(description="Stable snake_case identifier for this question, e.g. 'target_audience'.")
    question: str = Field(max_length=300)
    choices: list[str] = Field(
        default_factory=list,
        max_length=5,
        description="0-5 short suggested answers. Empty means a free-text-only question.",
    )


class IntakeVerdict(BaseModel):
    """The intake agent's output. Gates the brief before the Product/UX/Technical agents
    spend effort on it — never contains spec prose."""

    is_relevant: bool = Field(description="True if the brief describes a genuine, buildable product idea.")
    reason: str = Field(
        description="One or two plain sentences. If rejecting, say what's wrong and what to "
        "do instead. If accepting, a short confirmation is enough."
    )
    needs_clarification: bool = Field(
        default=False,
        description="True if the idea is relevant but ambiguous in a way that would materially "
        "change the spec, and is worth pausing to ask the user about before drafting.",
    )
    questions: list[ClarifyingQuestion] = Field(
        default_factory=list,
        max_length=3,
        description="Up to 3 targeted questions. Only populated when needs_clarification is True.",
    )
