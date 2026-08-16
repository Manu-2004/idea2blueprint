from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict

from blueprint_agents.constants import DEFAULT_MAX_REVISION_ROUNDS

AgentName = Literal["intake", "product", "ux", "technical", "reviewer", "handoff"]

# The reviewer writes shorter, more mechanical output (a verdict, not prose), so a lower
# temperature suits it; technical benefits from consistency over creativity too. Product/UX
# are the sections doing the most freeform prose writing. Intake is a binary classification
# call, so it gets the lowest temperature of all. Handoff sits with technical/reviewer — it's
# translating an already-fixed spec into tasks and an AGENTS.md, not inventing new scope.
DEFAULT_TEMPERATURES: dict[AgentName, float] = {
    "intake": 0.0,
    "product": 0.5,
    "ux": 0.5,
    "technical": 0.2,
    "reviewer": 0.2,
    "handoff": 0.2,
}


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    openai_api_key: str | None = None

    openai_model_default: str = "gpt-4.1-mini"
    openai_model_intake: str | None = None
    openai_model_product: str | None = None
    openai_model_ux: str | None = None
    openai_model_technical: str | None = None
    # The reviewer is the one node doing genuine cross-checking between the other three
    # agents' output, and it only runs 1-3 times per pipeline run — the cheapest place to
    # spend extra model quality.
    openai_model_reviewer: str | None = "gpt-4.1"
    openai_model_handoff: str | None = None

    max_revision_rounds: int = DEFAULT_MAX_REVISION_ROUNDS

    # Comma-separated list of origins allowed to call the API directly (browser CORS).
    cors_origins: str = "http://localhost:3000"

    # sqlite file path holding users/sessions/spec_jobs. Relative paths resolve against the
    # process's working directory (typically `backend/`).
    database_path: str = "blueprint_agents.db"

    def model_for(self, agent: AgentName) -> str:
        override = getattr(self, f"openai_model_{agent}")
        return override or self.openai_model_default

    def temperature_for(self, agent: AgentName) -> float:
        return DEFAULT_TEMPERATURES[agent]


@lru_cache
def get_settings() -> Settings:
    return Settings()
