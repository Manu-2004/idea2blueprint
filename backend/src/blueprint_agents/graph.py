from langgraph.graph import END, START, StateGraph

from blueprint_agents.constants import DEFAULT_MAX_REVISION_ROUNDS
from blueprint_agents.llm import LLMFactory, default_llm_factory
from blueprint_agents.nodes.assemble import assemble_node
from blueprint_agents.nodes.intake import make_intake_node
from blueprint_agents.nodes.product import make_product_node
from blueprint_agents.nodes.reviewer import make_reviewer_node
from blueprint_agents.nodes.technical import make_technical_node
from blueprint_agents.nodes.ux import make_ux_node
from blueprint_agents.schemas.intake import IntakeVerdict
from blueprint_agents.schemas.review import ReviewVerdict
from blueprint_agents.state import GraphState


def route_after_intake(state: GraphState):
    """Gate the brief before the Product/UX/Technical agents run at all.

    - Relevant brief -> proceed into the normal pipeline.
    - Irrelevant/gibberish/off-topic brief -> end the graph immediately with no `spec`,
      so `api/runner.py` can classify it as a rejection rather than burn 3 more LLM calls
      drafting a spec for input that was never a real idea.
    """
    verdict: IntakeVerdict = state["intake"]
    return "product_agent" if verdict.is_relevant else END


def route_after_review(state: GraphState):
    """Decide where to go after the reviewer runs.

    - No blocker issues -> assemble.
    - Blockers, but the revision budget is used up -> assemble anyway (best effort).
    - Blocker targeting `product` -> back to product_agent (this naturally recascades
      through ux_agent/technical_agent too, via their existing static edges).
    - Blocker targeting ux and/or technical -> regenerate BOTH siblings together, even if
      only one was flagged, so reviewer_agent's fan-in join stays synchronized on every
      loop iteration instead of firing on a stale/partial state.
    """
    verdict: ReviewVerdict = state["review"]
    blockers = [issue for issue in verdict.issues if issue.severity == "blocker"]
    if not blockers:
        return "assemble"

    revision_round = state.get("revision_round", 0)
    max_revision_rounds = state.get("max_revision_rounds", DEFAULT_MAX_REVISION_ROUNDS)
    if revision_round > max_revision_rounds:
        return "assemble"

    agents_flagged = {issue.agent for issue in blockers}
    if "product" in agents_flagged:
        return "product_agent"
    return ["ux_agent", "technical_agent"]


def build_graph(llm_factory: LLMFactory = default_llm_factory):
    """Build and compile the agentic pipeline.

    `llm_factory` is only invoked lazily, inside each node, at invoke time — never here at
    build time — so this function compiles successfully with no OpenAI API key present
    (constructing a real `ChatOpenAI` client without a key raises immediately, so it must
    never happen just from building the graph).
    """
    graph = StateGraph(GraphState)

    graph.add_node("intake_agent", make_intake_node(llm_factory))
    graph.add_node("product_agent", make_product_node(llm_factory))
    graph.add_node("ux_agent", make_ux_node(llm_factory))
    graph.add_node("technical_agent", make_technical_node(llm_factory))
    graph.add_node("reviewer_agent", make_reviewer_node(llm_factory))
    graph.add_node("assemble", assemble_node)

    graph.add_edge(START, "intake_agent")
    graph.add_conditional_edges("intake_agent", route_after_intake, ["product_agent", END])
    graph.add_edge("product_agent", "ux_agent")
    graph.add_edge("product_agent", "technical_agent")
    graph.add_edge("ux_agent", "reviewer_agent")
    graph.add_edge("technical_agent", "reviewer_agent")

    graph.add_conditional_edges(
        "reviewer_agent",
        route_after_review,
        ["assemble", "product_agent", "ux_agent", "technical_agent"],
    )
    graph.add_edge("assemble", END)

    return graph.compile()
