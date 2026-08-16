from blueprint_agents.graph import route_after_intake, route_after_review
from blueprint_agents.schemas.brief import Brief, ClarificationAnswer
from blueprint_agents.schemas.intake import ClarifyingQuestion, IntakeVerdict
from blueprint_agents.schemas.review import Issue, ReviewVerdict
from langgraph.graph import END


def _brief(clarifications=None):
    return Brief(
        idea="An idea", who="Someone", problem="A problem",
        platform="Web", features="A feature", budget="8 weeks",
        comfort="Some code", clarifications=clarifications or [],
    )


def test_relevant_brief_routes_to_product_agent():
    state = {
        "intake": IntakeVerdict(is_relevant=True, reason="Looks like a real product idea."),
        "brief": _brief(),
    }
    assert route_after_intake(state) == "product_agent"


def test_irrelevant_brief_routes_to_end():
    state = {
        "intake": IntakeVerdict(is_relevant=False, reason="This isn't a product idea."),
        "brief": _brief(),
    }
    assert route_after_intake(state) == END


def test_needs_clarification_without_answers_routes_to_end():
    verdict = IntakeVerdict(
        is_relevant=True,
        reason="Relevant but ambiguous.",
        needs_clarification=True,
        questions=[ClarifyingQuestion(key="audience", question="Who is this for?", choices=["Teams", "Individuals"])],
    )
    state = {"intake": verdict, "brief": _brief()}
    assert route_after_intake(state) == END


def test_needs_clarification_with_answers_routes_to_product_agent():
    verdict = IntakeVerdict(
        is_relevant=True,
        reason="Relevant but ambiguous.",
        needs_clarification=True,
        questions=[ClarifyingQuestion(key="audience", question="Who is this for?", choices=["Teams", "Individuals"])],
    )
    answers = [ClarificationAnswer(key="audience", question="Who is this for?", answer="Teams")]
    state = {"intake": verdict, "brief": _brief(clarifications=answers)}
    assert route_after_intake(state) == "product_agent"


def _verdict(issues):
    approved = not any(issue.severity == "blocker" for issue in issues)
    return ReviewVerdict(approved=approved, issues=issues, summary="test")


def test_no_blockers_routes_to_assemble():
    verdict = _verdict([Issue(agent="product", section="problem", description="nit", severity="minor")])
    state = {"review": verdict, "revision_round": 0, "max_revision_rounds": 2}
    assert route_after_review(state) == "assemble"


def test_blocker_on_product_routes_to_product_agent():
    verdict = _verdict(
        [Issue(agent="product", section="features", description="scope mismatch", severity="blocker")]
    )
    state = {"review": verdict, "revision_round": 0, "max_revision_rounds": 2}
    assert route_after_review(state) == "product_agent"


def test_blocker_on_ux_routes_to_both_siblings():
    verdict = _verdict(
        [Issue(agent="ux", section="flows", description="references missing feature", severity="blocker")]
    )
    state = {"review": verdict, "revision_round": 0, "max_revision_rounds": 2}
    assert route_after_review(state) == ["ux_agent", "technical_agent"]


def test_blocker_on_technical_routes_to_both_siblings():
    verdict = _verdict(
        [Issue(agent="technical", section="stack", description="too complex for comfort level", severity="blocker")]
    )
    state = {"review": verdict, "revision_round": 0, "max_revision_rounds": 2}
    assert route_after_review(state) == ["ux_agent", "technical_agent"]


def test_product_blocker_takes_priority_over_sibling_blockers():
    verdict = _verdict(
        [
            Issue(agent="ux", section="flows", description="x", severity="blocker"),
            Issue(agent="product", section="problem", description="y", severity="blocker"),
        ]
    )
    state = {"review": verdict, "revision_round": 0, "max_revision_rounds": 2}
    assert route_after_review(state) == "product_agent"


def test_cap_reached_forces_assemble_despite_blockers():
    verdict = _verdict([Issue(agent="product", section="problem", description="still wrong", severity="blocker")])
    state = {"review": verdict, "revision_round": 3, "max_revision_rounds": 2}
    assert route_after_review(state) == "assemble"
