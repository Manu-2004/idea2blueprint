from pydantic import BaseModel, Field


class Brief(BaseModel):
    """The 6-question brief collected by the frontend. Field-for-field identical to
    `FormFields` in frontend/lib/types.ts — all free text, no enums, since the form lets
    users override any suggested chip with custom text."""

    idea: str = Field(description="The idea in the user's own words, one or two sentences.")
    who: str = Field(description="Who the product is for.")
    problem: str = Field(description="What problem the product solves, in one line.")
    platform: str = Field(description="Where the product has to work on day one (e.g. Web, Mobile).")
    features: str = Field(description="What the product must do on day one.")
    budget: str = Field(description="Timeline and budget constraints.")
    comfort: str = Field(description="How technical the user is, which drives the stack recommendation.")
