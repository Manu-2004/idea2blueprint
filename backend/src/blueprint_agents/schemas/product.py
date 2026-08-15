from pydantic import BaseModel, Field

from blueprint_agents.schemas.common import RiskItem, SpecGroupDraft


class ProductOutput(BaseModel):
    """Product agent's output: problem/user framing, feature scoping, and product-level
    risks. Feeds section 01 (problem), 02 (features), and half of section 06 (risks)."""

    title: str = Field(description="A short, punchy product name, 2-6 words, e.g. 'Invoice chaser for freelancers'.")
    summary: str = Field(
        description="One-line byline for the spec header: who it's for and its scope, e.g. "
        "'Web app for solo designers and developers invoicing 3-10 clients a month. Scoped "
        "to 8 weeks and a low-code build.'"
    )

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
