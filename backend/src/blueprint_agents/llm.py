from typing import Callable

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_openai import ChatOpenAI

from blueprint_agents.config import AgentName, get_settings

# Nodes call this lazily (at invoke time, not at graph-build time) so `build_graph()` never
# needs a working OpenAI client — constructing `ChatOpenAI()` without an API key raises
# immediately, so eagerly building clients at graph-compile time would break structural
# tests that run with no key.
LLMFactory = Callable[[AgentName], BaseChatModel]


def default_llm_factory(agent: AgentName) -> BaseChatModel:
    settings = get_settings()
    return ChatOpenAI(
        model=settings.model_for(agent),
        temperature=settings.temperature_for(agent),
        api_key=settings.openai_api_key,
    )
