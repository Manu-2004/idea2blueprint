from pydantic import BaseModel, Field

from blueprint_agents.schemas.common import SpecGroupDraft


class UXOutput(BaseModel):
    """UX agent's output: user stories and user flows, grounded in the Product agent's
    scoped features. Feeds section 03 (stories) and 04 (flows)."""

    stories_lead: str = Field(description="1-2 sentence prose introduction to the user stories.")
    story_groups: list[SpecGroupDraft] = Field(
        description="Expected groups: 'Setup' and 'Day to day'. Each item is a testable "
        "'As a <user>, I <action>' story."
    )

    flows_lead: str = Field(description="1-2 sentence prose introduction to the user flows.")
    flow_groups: list[SpecGroupDraft] = Field(
        description="One group per named flow (e.g. 'First run — signup to first invoice'). "
        "Each group's items are the main path step-by-step, plus an optional fallback item."
    )
