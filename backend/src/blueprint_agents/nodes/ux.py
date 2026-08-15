from blueprint_agents.llm import LLMFactory
from blueprint_agents.prompts.ux import SYSTEM_PROMPT, build_user_message
from blueprint_agents.schemas.events import NodeEvent
from blueprint_agents.schemas.ux import UXOutput
from blueprint_agents.state import GraphState


def make_ux_node(llm_factory: LLMFactory):
    def ux_node(state: GraphState) -> dict:
        llm = llm_factory("ux")
        structured_llm = llm.with_structured_output(UXOutput)

        brief = state["brief"]
        product_output = state["product_output"]
        prior = state.get("ux_output")
        review = state.get("review")
        issues = review.issues if review else None

        user_message = build_user_message(brief, product_output, prior=prior, issues=issues)
        output: UXOutput = structured_llm.invoke(
            [("system", SYSTEM_PROMPT), ("human", user_message)]
        )

        round_ = state.get("revision_round", 0)
        return {
            "ux_output": output,
            "trace": [f"ux_agent ran (revision_round={round_})"],
            "events": [NodeEvent(node="ux", revision_round=round_)],
        }

    return ux_node
