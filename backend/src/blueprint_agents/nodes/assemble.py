from blueprint_agents.constants import SECTION_META, SECTION_ORDER
from blueprint_agents.schemas.common import RiskItem, Section, SectionGroup, SectionItem, Spec, SpecGroupDraft
from blueprint_agents.schemas.events import NodeEvent
from blueprint_agents.schemas.product import ProductOutput
from blueprint_agents.schemas.technical import TechnicalOutput
from blueprint_agents.schemas.ux import UXOutput
from blueprint_agents.state import GraphState


def _group(draft: SpecGroupDraft) -> SectionGroup:
    return SectionGroup(label=draft.label, items=[SectionItem(text=t) for t in draft.items])


def _render_risk(item: RiskItem) -> str:
    mitigation = item.mitigation.rstrip(".")
    return f"{item.risk} Mitigation — {mitigation}."


def _section(section_id: str, lead: str, groups: list[SectionGroup]) -> Section:
    meta = SECTION_META[section_id]
    return Section(id=meta.id, num=meta.num, title=meta.title, lead=lead, groups=groups)


def build_spec(product: ProductOutput, ux: UXOutput, technical: TechnicalOutput) -> Spec:
    """Deterministic, non-LLM assembly of the three agents' outputs into the 6-section
    `Spec`. Section id/num/title/order are fixed via `SECTION_META` — never LLM-generated."""

    risk_items = [
        SectionItem(text=_render_risk(risk))
        for risk in [*product.product_risks, *technical.technical_risks]
    ]
    assumption_items = [
        SectionItem(text=text)
        for text in [*product.product_assumptions, *technical.technical_assumptions]
    ]

    sections = [
        _section("problem", product.problem_lead, [_group(g) for g in product.problem_groups]),
        _section("features", product.features_lead, [_group(g) for g in product.feature_groups]),
        _section("stories", ux.stories_lead, [_group(g) for g in ux.story_groups]),
        _section("flows", ux.flows_lead, [_group(g) for g in ux.flow_groups]),
        _section("stack", technical.stack_lead, [_group(g) for g in technical.stack_groups]),
        _section(
            "risks",
            product.risks_lead,
            [
                SectionGroup(label="Risks", items=risk_items),
                SectionGroup(label="Assumptions to validate", items=assumption_items),
            ],
        ),
    ]
    assert [section.id for section in sections] == SECTION_ORDER
    return Spec(title=product.title, summary=product.summary, sections=sections)


def assemble_node(state: GraphState) -> dict:
    spec = build_spec(state["product_output"], state["ux_output"], state["technical_output"])
    round_ = state.get("revision_round", 0)
    return {
        "spec": spec,
        "trace": ["assemble ran"],
        "events": [NodeEvent(node="assemble", revision_round=round_)],
    }
