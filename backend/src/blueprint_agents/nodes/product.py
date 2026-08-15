from blueprint_agents.llm import LLMFactory
from blueprint_agents.prompts.product import SYSTEM_PROMPT, build_user_message
from blueprint_agents.schemas.events import NodeEvent
from blueprint_agents.schemas.product import ProductOutput
from blueprint_agents.state import GraphState


def make_product_node(llm_factory: LLMFactory):
    def product_node(state: GraphState) -> dict:
        llm = llm_factory("product")
        structured_llm = llm.with_structured_output(ProductOutput)

        brief = state["brief"]
        prior = state.get("product_output")
        review = state.get("review")
        issues = review.issues if review else None

        user_message = build_user_message(brief, prior=prior, issues=issues)
        output: ProductOutput = structured_llm.invoke(
            [("system", SYSTEM_PROMPT), ("human", user_message)]
        )

        round_ = state.get("revision_round", 0)
        return {
            "product_output": output,
            "trace": [f"product_agent ran (revision_round={round_})"],
            "events": [NodeEvent(node="product", revision_round=round_)],
        }

    return product_node
