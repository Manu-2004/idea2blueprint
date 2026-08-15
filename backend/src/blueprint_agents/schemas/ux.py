from pydantic import BaseModel, Field

from blueprint_agents.schemas.common import SpecGroupDraft


class UXOutput(BaseModel):
    """UX agent's output: user stories and user flows, grounded in the Product agent's
    scoped features. Feeds section 03 (stories) and 04 (flows)."""

    stories_lead: str = Field(description="1-2 sentence prose introduction to the user stories.")
    story_groups: list[SpecGroupDraft] = Field(
        description="Expected groups: 'Setup' and 'Day to day'. Each item is a testable, "
        "concrete action tied to the actual named persona from the brief/problem framing "
        "(e.g. 'freelancer'), never the literal word 'user'. Vary the opening across the "
        "group — do not start every item with the identical 'As a <persona>, I ...' clause."
    )

    flows_lead: str = Field(description="1-2 sentence prose introduction to the user flows.")
    flow_groups: list[SpecGroupDraft] = Field(
        description="One group per named flow (e.g. 'First run — signup to first invoice'). "
        "The first item is the main path as ONE string with steps joined by ' -> ' (plain "
        "ASCII arrow, e.g. 'Sign up -> connect Stripe -> confirm invoices -> land on the "
        "board'; never the unicode '→' character). An optional second item starting with "
        "'Fallback:' covers the most likely way the path breaks."
    )
