from blueprint_agents.constants import DEFAULT_MAX_REVISION_ROUNDS
from blueprint_agents.llm import LLMFactory
from blueprint_agents.prompts.reviewer import SYSTEM_PROMPT, build_user_message
from blueprint_agents.schemas.review import ReviewVerdict
from blueprint_agents.state import GraphState


def make_reviewer_node(llm_factory: LLMFactory):
    def reviewer_node(state: GraphState) -> dict:
        llm = llm_factory("reviewer")
        structured_llm = llm.with_structured_output(ReviewVerdict)

        brief = state["brief"]
        product_output = state["product_output"]
        ux_output = state["ux_output"]
        technical_output = state["technical_output"]
        prior_round = state.get("revision_round", 0)
        max_rounds = state.get("max_revision_rounds", DEFAULT_MAX_REVISION_ROUNDS)

        user_message = build_user_message(
            brief, product_output, ux_output, technical_output, prior_round, max_rounds
        )
        verdict: ReviewVerdict = structured_llm.invoke(
            [("system", SYSTEM_PROMPT), ("human", user_message)]
        )

        new_round = prior_round + 1
        blockers = [issue for issue in verdict.issues if issue.severity == "blocker"]
        return {
            "review": verdict,
            "revision_round": new_round,
            "trace": [
                f"reviewer ran round={new_round} approved={verdict.approved} blockers={len(blockers)}"
            ],
        }

    return reviewer_node
