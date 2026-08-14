"""Fixed identity of the 6 spec sections.

Section id/num/title are never LLM-generated — the `assemble` node looks them up here so
section identity and order stay stable across runs. Order matches `frontend/lib/data.ts`'s
`SECTIONS`.
"""

from typing import NamedTuple


class SectionMeta(NamedTuple):
    id: str
    num: str
    title: str


SECTION_ORDER: list[str] = ["problem", "features", "stories", "flows", "stack", "risks"]

SECTION_META: dict[str, SectionMeta] = {
    "problem": SectionMeta(id="problem", num="01", title="Problem and target user"),
    "features": SectionMeta(id="features", num="02", title="Core features"),
    "stories": SectionMeta(id="stories", num="03", title="User stories"),
    "flows": SectionMeta(id="flows", num="04", title="User flows"),
    "stack": SectionMeta(id="stack", num="05", title="Tech stack"),
    "risks": SectionMeta(id="risks", num="06", title="Risks and assumptions"),
}

DEFAULT_MAX_REVISION_ROUNDS = 2
