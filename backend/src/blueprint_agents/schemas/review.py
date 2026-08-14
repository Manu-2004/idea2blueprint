from typing import Literal

from pydantic import BaseModel, Field


class Issue(BaseModel):
    """A single problem found in one agent's output. Only `blocker` severity triggers the
    revision loop; `minor` issues are logged but don't block assembly."""

    agent: Literal["product", "ux", "technical"] = Field(description="Which agent's output this issue is about.")
    section: str = Field(description="Which section the issue is in, e.g. 'stack' or 'flows'.")
    description: str = Field(description="What's wrong, specifically enough that the agent can fix it.")
    severity: Literal["blocker", "minor"]


class ReviewVerdict(BaseModel):
    """The reviewer's output. Never contains spec prose — only a verdict and issues; the
    `assemble` node does the actual composition of the final spec."""

    approved: bool = Field(description="True if there are no blocker-severity issues.")
    issues: list[Issue] = Field(default_factory=list)
    summary: str = Field(description="One or two sentence overall assessment, for logs/trace only.")
