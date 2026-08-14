from blueprint_agents.llm import LLMFactory
from blueprint_agents.prompts.technical import SYSTEM_PROMPT, build_user_message
from blueprint_agents.schemas.technical import TechnicalOutput
from blueprint_agents.state import GraphState


def make_technical_node(llm_factory: LLMFactory):
    def technical_node(state: GraphState) -> dict:
        llm = llm_factory("technical")
        structured_llm = llm.with_structured_output(TechnicalOutput)

        brief = state["brief"]
        product_output = state["product_output"]
        prior = state.get("technical_output")
        review = state.get("review")
        issues = review.issues if review else None

        user_message = build_user_message(brief, product_output, prior=prior, issues=issues)
        output: TechnicalOutput = structured_llm.invoke(
            [("system", SYSTEM_PROMPT), ("human", user_message)]
        )

        round_ = state.get("revision_round", 0)
        return {"technical_output": output, "trace": [f"technical_agent ran (revision_round={round_})"]}

    return technical_node
