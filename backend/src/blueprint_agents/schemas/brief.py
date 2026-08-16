from pydantic import BaseModel, Field


class ClarificationAnswer(BaseModel):
    """One answered clarifying question, echoed back from `IntakeVerdict.questions` with
    the user's answer attached — carries the question text along so downstream agents don't
    need to look it up separately."""

    key: str
    question: str = Field(max_length=300)
    answer: str = Field(max_length=1000)


class Brief(BaseModel):
    """The 6-question brief collected by the frontend. Field-for-field identical to
    `FormFields` in frontend/lib/types.ts — all free text, no enums, since the form lets
    users override any suggested chip with custom text."""

    idea: str = Field(max_length=2000, description="The idea in the user's own words, one or two sentences.")
    who: str = Field(max_length=500, description="Who the product is for.")
    problem: str = Field(max_length=2000, description="What problem the product solves, in one line.")
    platform: str = Field(max_length=500, description="Where the product has to work on day one (e.g. Web, Mobile).")
    features: str = Field(max_length=2000, description="What the product must do on day one.")
    budget: str = Field(max_length=500, description="Timeline and budget constraints.")
    comfort: str = Field(
        max_length=500, description="How technical the user is, which drives the stack recommendation."
    )
    # Answers to a prior round of intake clarifying questions, if any were asked. Empty on
    # the initial submission; populated once via POST /api/spec-jobs/{id}/clarify, after
    # which the intake agent is instructed not to ask again (see graph.py::route_after_intake).
    clarifications: list[ClarificationAnswer] = Field(default_factory=list)
