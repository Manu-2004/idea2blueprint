from blueprint_agents.constants import SECTION_ORDER
from blueprint_agents.nodes.assemble import build_spec
from blueprint_agents.schemas.common import RiskItem, SpecGroupDraft
from blueprint_agents.schemas.product import ProductOutput
from blueprint_agents.schemas.technical import TechnicalOutput
from blueprint_agents.schemas.ux import UXOutput


def _product():
    return ProductOutput(
        problem_lead="problem lead",
        problem_groups=[SpecGroupDraft(label="Primary user", items=["a user"])],
        features_lead="features lead",
        feature_groups=[SpecGroupDraft(label="Must have", items=["a feature"])],
        risks_lead="risks lead",
        product_risks=[RiskItem(risk="a product risk", mitigation="a product mitigation")],
        product_assumptions=["a product assumption"],
    )


def _ux():
    return UXOutput(
        stories_lead="stories lead",
        story_groups=[SpecGroupDraft(label="Setup", items=["a story"])],
        flows_lead="flows lead",
        flow_groups=[SpecGroupDraft(label="First run", items=["a flow step"])],
    )


def _technical():
    return TechnicalOutput(
        stack_lead="stack lead",
        stack_groups=[SpecGroupDraft(label="Build", items=["a stack choice"])],
        technical_risks=[RiskItem(risk="a technical risk", mitigation="a technical mitigation")],
        technical_assumptions=["a technical assumption"],
    )


def test_build_spec_has_six_sections_in_fixed_order():
    spec = build_spec(_product(), _ux(), _technical())
    assert [section.id for section in spec.sections] == SECTION_ORDER
    assert [section.num for section in spec.sections] == ["01", "02", "03", "04", "05", "06"]


def test_section_content_traces_back_to_the_right_agent():
    spec = build_spec(_product(), _ux(), _technical())
    by_id = {section.id: section for section in spec.sections}

    assert by_id["problem"].groups[0].items[0].text == "a user"
    assert by_id["features"].groups[0].items[0].text == "a feature"
    assert by_id["stories"].groups[0].items[0].text == "a story"
    assert by_id["flows"].groups[0].items[0].text == "a flow step"
    assert by_id["stack"].groups[0].items[0].text == "a stack choice"


def test_risks_section_merges_product_and_technical():
    spec = build_spec(_product(), _ux(), _technical())
    risks_section = next(section for section in spec.sections if section.id == "risks")
    risk_group = next(group for group in risks_section.groups if group.label == "Risks")
    assumption_group = next(group for group in risks_section.groups if group.label == "Assumptions to validate")

    assert len(risk_group.items) == 2
    assert "a product risk" in risk_group.items[0].text
    assert "a product mitigation" in risk_group.items[0].text
    assert "a technical risk" in risk_group.items[1].text

    assert len(assumption_group.items) == 2
    assert assumption_group.items[0].text == "a product assumption"
    assert assumption_group.items[1].text == "a technical assumption"
