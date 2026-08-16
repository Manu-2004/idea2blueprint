from pydantic import BaseModel, Field


class AgentTask(BaseModel):
    """One sequential step in the coding-agent kickoff prompt."""

    title: str = Field(description="Short imperative task title, e.g. 'Set up auth and user model'.")
    description: str = Field(
        description="What to build in this task: concrete deliverables, key files/endpoints/"
        "components, and a definition of done. 3-6 sentences."
    )


class HandoffOutput(BaseModel):
    """Coding-agent handoff kit derived from a finished `Spec`: a kickoff prompt broken into
    sequential tasks, plus an AGENTS.md for the repo. Generated on demand after `spec`
    already exists — not part of the main product/ux/technical/reviewer pipeline."""

    context: str = Field(
        description="2-4 sentence framing paragraph for a coding agent picking up this MVP "
        "cold: what it is, who it's for, and how to approach the build (e.g. what to get "
        "working end-to-end first)."
    )
    tasks: list[AgentTask] = Field(
        description="Ordered, sequential implementation tasks sized to the MVP's actual "
        "complexity — a small MVP might need 3-4 tasks, a larger one 8-10. Each task must be "
        "independently completable and leave the app in a working, runnable state before the "
        "next task starts."
    )
    agents_md: str = Field(
        description="Full contents of an AGENTS.md file for this repo: project overview, tech "
        "stack, conventions, and the commands to install/run/test/build. Valid Markdown."
    )
