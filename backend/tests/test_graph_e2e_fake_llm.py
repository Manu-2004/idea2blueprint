from blueprint_agents.graph import build_graph
from blueprint_agents.schemas.brief import Brief
from blueprint_agents.schemas.common import RiskItem, SpecGroupDraft
from blueprint_agents.schemas.intake import IntakeVerdict
from blueprint_agents.schemas.product import ProductOutput
from blueprint_agents.schemas.review import Issue, ReviewVerdict
from blueprint_agents.schemas.technical import TechnicalOutput
from blueprint_agents.schemas.ux import UXOutput
from fakes import make_llm_factory


def _relevant_intake():
    return IntakeVerdict(is_relevant=True, reason="Describes a real product idea.")


def _brief():
    return Brief(
        idea="An idea", who="Someone", problem="A problem",
        platform="Web", features="A feature", budget="8 weeks",
        comfort="Some code",
    )


def _product_output():
    return ProductOutput(
        title="Invoice Chaser",
        summary="Web app for solo freelancers. Scoped to 8 weeks.",
        problem_lead="problem lead",
        problem_groups=[SpecGroupDraft(label="Primary user", items=["a user"])],
        features_lead="features lead",
        feature_groups=[SpecGroupDraft(label="Must have", items=["a feature"])],
        risks_lead="risks lead",
        product_risks=[RiskItem(risk="a product risk", mitigation="a mitigation")],
        product_assumptions=["an assumption"],
    )


def _ux_output():
    return UXOutput(
        stories_lead="stories lead",
        story_groups=[SpecGroupDraft(label="Setup", items=["a story"])],
        flows_lead="flows lead",
        flow_groups=[SpecGroupDraft(label="First run", items=["a flow step"])],
    )


def _technical_output(stack_label="Build"):
    return TechnicalOutput(
        stack_lead="stack lead",
        stack_groups=[SpecGroupDraft(label=stack_label, items=["a stack choice"])],
        technical_risks=[RiskItem(risk="a technical risk", mitigation="a mitigation")],
        technical_assumptions=[],
    )


def _invoke(factory):
    graph = build_graph(llm_factory=factory)
    return graph.invoke(
        {"brief": _brief(), "revision_round": 0, "max_revision_rounds": 2, "trace": [], "events": []}
    )


def _calls(trace, prefix):
    return [line for line in trace if line.startswith(prefix)]


def test_happy_path_approves_on_first_pass():
    approved = ReviewVerdict(approved=True, issues=[], summary="looks good")
    factory = make_llm_factory(
        {
            "intake": _relevant_intake(),
            "product": _product_output(),
            "ux": _ux_output(),
            "technical": _technical_output(),
            "reviewer": [approved],
        }
    )
    result = _invoke(factory)

    assert result["spec"] is not None
    assert len(result["spec"].sections) == 6
    assert result["revision_round"] == 1
    assert len(_calls(result["trace"], "product_agent ran")) == 1
    assert len(_calls(result["trace"], "ux_agent ran")) == 1
    assert len(_calls(result["trace"], "technical_agent ran")) == 1
    assert len(_calls(result["trace"], "reviewer ran")) == 1

    # events plumbing feeds the API layer's progress computation (api/progress.py) —
    # confirm it lands in the graph result end-to-end, not just per-node in isolation.
    from blueprint_agents.api.progress import compute_step

    assert compute_step(result["events"]) == 6


def test_blocker_on_technical_regenerates_both_siblings_then_approves():
    blocker = ReviewVerdict(
        approved=False,
        issues=[Issue(agent="technical", section="stack", description="too complex", severity="blocker")],
        summary="stack too complex",
    )
    approved = ReviewVerdict(approved=True, issues=[], summary="fixed now")

    factory = make_llm_factory(
        {
            "intake": _relevant_intake(),
            "product": _product_output(),
            "ux": _ux_output(),
            "technical": [_technical_output("Build (v1)"), _technical_output("Build (v2, simplified)")],
            "reviewer": [blocker, approved],
        }
    )
    result = _invoke(factory)

    assert result["spec"] is not None
    assert result["revision_round"] == 2
    # product_agent is never re-invoked since the blocker didn't target it.
    assert len(_calls(result["trace"], "product_agent ran")) == 1
    # ux_agent regenerates too, even though it wasn't flagged, to keep reviewer_agent's
    # fan-in join synchronized on the second pass.
    assert len(_calls(result["trace"], "ux_agent ran")) == 2
    assert len(_calls(result["trace"], "technical_agent ran")) == 2
    assert len(_calls(result["trace"], "reviewer ran")) == 2

    stack_section = next(section for section in result["spec"].sections if section.id == "stack")
    assert stack_section.groups[0].label == "Build (v2, simplified)"


def test_blocker_on_product_recascades_through_ux_and_technical():
    blocker = ReviewVerdict(
        approved=False,
        issues=[Issue(agent="product", section="problem", description="wrong user", severity="blocker")],
        summary="wrong target user",
    )
    approved = ReviewVerdict(approved=True, issues=[], summary="fixed now")

    factory = make_llm_factory(
        {
            "intake": _relevant_intake(),
            "product": _product_output(),
            "ux": _ux_output(),
            "technical": _technical_output(),
            "reviewer": [blocker, approved],
        }
    )
    result = _invoke(factory)

    assert result["revision_round"] == 2
    assert len(_calls(result["trace"], "product_agent ran")) == 2
    assert len(_calls(result["trace"], "ux_agent ran")) == 2
    assert len(_calls(result["trace"], "technical_agent ran")) == 2
    assert len(_calls(result["trace"], "reviewer ran")) == 2


def test_cap_reached_forces_assemble_even_with_persistent_blockers():
    blocker = ReviewVerdict(
        approved=False,
        issues=[Issue(agent="product", section="problem", description="still wrong", severity="blocker")],
        summary="still not right",
    )
    factory = make_llm_factory(
        {
            "intake": _relevant_intake(),
            "product": _product_output(),
            "ux": _ux_output(),
            "technical": _technical_output(),
            "reviewer": [blocker, blocker, blocker],
        }
    )
    result = _invoke(factory)

    assert result["spec"] is not None
    assert result["revision_round"] == 3
    assert len(_calls(result["trace"], "reviewer ran")) == 3


def test_irrelevant_brief_ends_at_intake_without_running_other_agents():
    rejected = IntakeVerdict(is_relevant=False, reason="This is song lyrics, not a product idea.")
    factory = make_llm_factory({"intake": rejected})
    result = _invoke(factory)

    assert result.get("spec") is None
    assert result["intake"].is_relevant is False
    assert _calls(result["trace"], "product_agent ran") == []
    assert _calls(result["trace"], "ux_agent ran") == []
    assert _calls(result["trace"], "technical_agent ran") == []
    assert _calls(result["trace"], "reviewer ran") == []
