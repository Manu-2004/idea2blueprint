from blueprint_agents.llm import LLMFactory
from blueprint_agents.prompts.intake import SYSTEM_PROMPT, build_user_message
from blueprint_agents.schemas.events import NodeEvent
from blueprint_agents.schemas.intake import IntakeVerdict
from blueprint_agents.state import GraphState


def make_intake_node(llm_factory: LLMFactory):
    def intake_node(state: GraphState) -> dict:
        llm = llm_factory("intake")
        structured_llm = llm.with_structured_output(IntakeVerdict)

        brief = state["brief"]
        user_message = build_user_message(brief)
        verdict: IntakeVerdict = structured_llm.invoke(
            [("system", SYSTEM_PROMPT), ("human", user_message)]
        )

        return {
            "intake": verdict,
            "trace": [f"intake ran is_relevant={verdict.is_relevant}"],
            "events": [NodeEvent(node="intake", revision_round=0)],
        }

    return intake_node
