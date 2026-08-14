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
    """Thin envelope so `spec.sections` can be dropped straight into the frontend's
    `SECTIONS: Section[]` later. No title/idea echo — those live elsewhere in the
    frontend's data model (`SpecItem`, `Template`), out of scope for this pass."""

    sections: list[Section]
