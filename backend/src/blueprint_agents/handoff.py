from blueprint_agents.llm import LLMFactory
from blueprint_agents.prompts.handoff import SYSTEM_PROMPT, build_user_message
from blueprint_agents.schemas.brief import Brief
from blueprint_agents.schemas.common import Spec
from blueprint_agents.schemas.handoff import HandoffOutput

# Not wired into `graph.py`'s StateGraph: this runs on demand, once, after `spec` already
# exists, so it needs none of the routing/revision-loop machinery the pipeline nodes share.


def build_agent_prompt(spec: Spec, handoff: HandoffOutput) -> str:
    """Deterministic, non-LLM assembly of the handoff agent's structured output into the
    final prompt text handed to a coding agent — mirrors `nodes/assemble.build_spec`."""

    lines = [f"# Build brief: {spec.title}", "", spec.summary, "", handoff.context, "", "## Tasks"]
    for i, task in enumerate(handoff.tasks, start=1):
        lines += ["", f"### {i}. {task.title}", "", task.description]
    return "\n".join(lines) + "\n"


def generate_handoff(brief: Brief, spec: Spec, llm_factory: LLMFactory) -> HandoffOutput:
    llm = llm_factory("handoff")
    structured_llm = llm.with_structured_output(HandoffOutput)
    user_message = build_user_message(brief, spec)
    return structured_llm.invoke([("system", SYSTEM_PROMPT), ("human", user_message)])
