from pydantic import BaseModel, Field

from blueprint_agents.schemas.common import RiskItem, SpecGroupDraft


class TechnicalOutput(BaseModel):
    """Technical agent's output: stack choice sized to the brief's budget/comfort, and
    technical risks. Feeds section 05 (stack) and half of section 06 (risks)."""

    stack_lead: str = Field(description="1-2 sentence prose introduction framing the stack choice.")
    stack_groups: list[SpecGroupDraft] = Field(
        description="Expected groups: 'Build' (the chosen stack, one item per layer/service "
        "with a short reason) and 'Deliberately deferred' (infrastructure explicitly not "
        "needed yet)."
    )

    technical_risks: list[RiskItem] = Field(description="Technical/delivery risks: scaling, integrations, feasibility.")
    technical_assumptions: list[str] = Field(
        default_factory=list, description="Technical assumptions that need validating, if any."
    )
