from blueprint_agents.constants import MAX_TITLE_ATTEMPTS
from blueprint_agents.llm import LLMFactory
from blueprint_agents.prompts.product import SYSTEM_PROMPT, build_user_message
from blueprint_agents.schemas.events import NodeEvent
from blueprint_agents.schemas.product import ProductOutput
from blueprint_agents.state import GraphState


def _collides(title: str, used_titles: list[str]) -> bool:
    normalized = title.strip().casefold()
    return any(normalized == used.strip().casefold() for used in used_titles)


def make_product_node(llm_factory: LLMFactory):
    def product_node(state: GraphState) -> dict:
        brief = state["brief"]
        prior = state.get("product_output")
        review = state.get("review")
        issues = review.issues if review else None
        used_titles = list(state.get("used_titles") or [])

        # The prompt already tells the LLM to avoid `used_titles`, but that's best-effort —
        # this loop is the deterministic backstop. Each retry adds the just-rejected title to
        # the avoid-list too, so a stubborn LLM can't loop on the same collision. Re-fetching
        # the LLM per attempt (cheap, stateless — see llm.py) rather than reusing one client
        # matters for the fake test double, which sequences distinct responses per factory
        # call, mirroring distinct real-world completions.
        output: ProductOutput
        for attempt in range(MAX_TITLE_ATTEMPTS):
            structured_llm = llm_factory("product").with_structured_output(ProductOutput)
            user_message = build_user_message(brief, prior=prior, issues=issues, used_titles=used_titles)
            output = structured_llm.invoke([("system", SYSTEM_PROMPT), ("human", user_message)])
            if not _collides(output.title, used_titles):
                break
            used_titles = used_titles + [output.title]

        round_ = state.get("revision_round", 0)
        return {
            "product_output": output,
            "trace": [f"product_agent ran (revision_round={round_})"],
            "events": [NodeEvent(node="product", revision_round=round_)],
        }

    return product_node
