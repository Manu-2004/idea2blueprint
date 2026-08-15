from pydantic import BaseModel, Field


class SpecGroupDraft(BaseModel):
    """A labeled group of bullet points, as emitted by a domain agent — one step short of a
    `SectionGroup` (items are plain strings here; `assemble` wraps them as `SectionItem`)."""

    label: str = Field(description="Group heading, e.g. 'Must have' or 'Primary user'.")
    items: list[str] = Field(description="Bullet points in this group, one sentence each.")


class RiskItem(BaseModel):
    """A single risk with its mitigation, rendered at assemble time as one bullet:
    '{risk} Mitigation — {mitigation}.'"""

    risk: str = Field(description="The risk, stated plainly.")
    mitigation: str = Field(description="The concrete mitigation for this risk.")


# --- final output contract, field-for-field identical to frontend/lib/types.ts ---


class SectionItem(BaseModel):
    text: str


class SectionGroup(BaseModel):
    label: str
    items: list[SectionItem]


class Section(BaseModel):
    id: str
    num: str
    title: str
    lead: str
    groups: list[SectionGroup]


class Spec(BaseModel):
    """Field-for-field compatible with the frontend's spec display: a short product title,
    a one-line byline, and the 6 sections."""

    title: str
    summary: str
    sections: list[Section]
