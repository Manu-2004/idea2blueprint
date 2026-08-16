from blueprint_agents.graph import build_graph
from blueprint_agents.schemas.brief import Brief
from blueprint_agents.schemas.common import RiskItem, SpecGroupDraft
from blueprint_agents.schemas.intake import ClarifyingQuestion, IntakeVerdict
from blueprint_agents.schemas.product import ProductOutput
from blueprint_agents.schemas.review import Issue, ReviewVerdict
from blueprint_agents.schemas.technical import TechnicalOutput
from blueprint_agents.schemas.ux import UXOutput
from fakes import make_llm_factory


def _relevant_intake():
    return IntakeVerdict(is_relevant=True, reason="Describes a real product idea.")


def _brief(clarifications=None):
    return Brief(
        idea="An idea", who="Someone", problem="A problem",
        platform="Web", features="A feature", budget="8 weeks",
        comfort="Some code", clarifications=clarifications or [],
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


def _invoke(factory, brief=None, used_titles=None):
    graph = build_graph(llm_factory=factory)
    return graph.invoke(
        {
            "brief": brief or _brief(),
            "used_titles": used_titles or [],
            "revision_round": 0,
            "max_revision_rounds": 2,
            "trace": [],
            "events": [],
        }
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


def test_product_agent_retries_when_title_collides_with_a_used_title():
    approved = ReviewVerdict(approved=True, issues=[], summary="looks good")
    colliding = _product_output()  # title="Invoice Chaser"
    fresh = ProductOutput(**{**colliding.model_dump(), "title": "Tabsy"})

    factory = make_llm_factory(
        {
            "intake": _relevant_intake(),
            "product": [colliding, fresh],
            "ux": _ux_output(),
            "technical": _technical_output(),
            "reviewer": [approved],
        }
    )
    result = _invoke(factory, used_titles=["Invoice Chaser"])

    assert result["spec"].title == "Tabsy"
    # Still one node-level pass — the retries happen inside the single product_agent call.
    assert len(_calls(result["trace"], "product_agent ran")) == 1


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


def test_ambiguous_brief_ends_at_intake_pending_clarification():
    needs_clarification = IntakeVerdict(
        is_relevant=True,
        reason="Real idea, but ambiguous.",
        needs_clarification=True,
        questions=[ClarifyingQuestion(key="audience", question="Who is this for?", choices=["Teams", "Individuals"])],
    )
    factory = make_llm_factory({"intake": needs_clarification})
    result = _invoke(factory)

    assert result.get("spec") is None
    assert result["intake"].needs_clarification is True
    assert _calls(result["trace"], "product_agent ran") == []
    assert _calls(result["trace"], "ux_agent ran") == []
    assert _calls(result["trace"], "technical_agent ran") == []
    assert _calls(result["trace"], "reviewer ran") == []


def test_answered_clarification_proceeds_through_the_full_pipeline():
    approved = ReviewVerdict(approved=True, issues=[], summary="looks good")
    still_ambiguous = IntakeVerdict(
        is_relevant=True,
        reason="Answered now.",
        needs_clarification=True,  # even if the LLM still flags this, code enforces one round
        questions=[ClarifyingQuestion(key="audience", question="Who is this for?", choices=["Teams"])],
    )
    factory = make_llm_factory(
        {
            "intake": still_ambiguous,
            "product": _product_output(),
            "ux": _ux_output(),
            "technical": _technical_output(),
            "reviewer": [approved],
        }
    )
    answered_brief = _brief(clarifications=[
        {"key": "audience", "question": "Who is this for?", "answer": "Teams"}
    ])
    result = _invoke(factory, brief=answered_brief)

    assert result["spec"] is not None
    assert len(result["spec"].sections) == 6
