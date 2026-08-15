from pydantic import BaseModel, Field


class IntakeVerdict(BaseModel):
    """The intake agent's output. Gates the brief before the Product/UX/Technical agents
    spend effort on it — never contains spec prose."""

    is_relevant: bool = Field(description="True if the brief describes a genuine, buildable product idea.")
    reason: str = Field(
        description="One or two plain sentences. If rejecting, say what's wrong and what to "
        "do instead. If accepting, a short confirmation is enough."
    )
