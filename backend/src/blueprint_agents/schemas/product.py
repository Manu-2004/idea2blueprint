from pydantic import BaseModel, Field

from blueprint_agents.schemas.common import RiskItem, SpecGroupDraft


class ProductOutput(BaseModel):
    """Product agent's output: problem/user framing, feature scoping, and product-level
    risks. Feeds section 01 (problem), 02 (features), and half of section 06 (risks)."""

    problem_lead: str = Field(description="2-4 sentence prose introduction to the problem and target user.")
    problem_groups: list[SpecGroupDraft] = Field(
        description="Expected groups: 'Primary user' and 'Explicitly not the user'."
    )

    features_lead: str = Field(description="2-4 sentence prose introduction framing the MVP feature cut.")
    feature_groups: list[SpecGroupDraft] = Field(
        description="Expected groups: 'Must have', 'Should have, post-launch', 'Will not have in the MVP'."
    )

    risks_lead: str = Field(description="2-3 sentence prose introduction to the risks and assumptions section.")
    product_risks: list[RiskItem] = Field(description="Product/market risks: adoption, trust, positioning.")
    product_assumptions: list[str] = Field(description="Assumptions about users/market that need validating.")
