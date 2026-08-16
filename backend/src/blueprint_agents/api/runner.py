import logging
import time

from openai import APITimeoutError, BadRequestError, RateLimitError

from blueprint_agents.api.jobs import JobStore
from blueprint_agents.api.schemas import JobError
from blueprint_agents.config import get_settings
from blueprint_agents.graph import build_graph

logger = logging.getLogger(__name__)


def _classify_error(exc: Exception) -> JobError:
    if isinstance(exc, RateLimitError):
        return JobError(type="openai_rate_limit", message="OpenAI rate limit hit — try again shortly.")
    if isinstance(exc, APITimeoutError):
        return JobError(type="openai_timeout", message="The request to OpenAI timed out — try again.")
    if isinstance(exc, BadRequestError):
        # OpenAI doesn't consistently distinguish content-policy refusals from other bad
        # requests at the exception-type level — this is a best-effort heuristic, not exact.
        if "content" in str(exc).lower() or "policy" in str(exc).lower():
            return JobError(
                type="openai_content_policy",
                message="The idea couldn't be processed as written — try rephrasing it.",
            )
        return JobError(type="openai_error", message="OpenAI rejected the request — try again.")
    return JobError(type="internal_error", message="Something went wrong generating the spec.")


def run_job(job_id: str, store: JobStore) -> None:
    """Runs synchronously in a background thread (dispatched by FastAPI's BackgroundTasks),
    not the event loop — the graph's node calls are blocking OpenAI calls, and a run can
    take minutes on the long tail, so this must never run inline on an async request path."""

    job = store.get(job_id)
    if job is None:
        return

    store.update(job_id, status="running")
    settings = get_settings()
    graph = build_graph()
    started = time.monotonic()

    initial_state = {
        "brief": job.brief,
        "used_titles": store.list_titles_for_user(job.user_id),
        "revision_round": 0,
        "max_revision_rounds": job.max_revision_rounds,
        "trace": [],
        "events": [],
    }

    try:
        result_state = initial_state
        for chunk in graph.stream(initial_state, stream_mode="values"):
            result_state = chunk
            store.update(
                job_id,
                events=result_state.get("events", []),
                revision_round=result_state.get("revision_round", 0),
            )

        intake = result_state.get("intake")
        if intake is not None and not intake.is_relevant:
            store.update(
                job_id,
                status="failed",
                error=JobError(type="irrelevant_input", message=intake.reason),
            )
            logger.info("spec job %s rejected at intake: %s", job_id, intake.reason)
            return

        if intake is not None and intake.needs_clarification and not job.brief.clarifications:
            store.update(job_id, status="needs_input", clarifying_questions=intake.questions)
            logger.info("spec job %s paused for clarification (%d questions)", job_id, len(intake.questions))
            return

        spec = result_state["spec"]
        store.update(job_id, status="done", spec=spec)
        logger.info(
            "spec job %s done in %.1fs, revision_round=%d, models={product:%s, ux:%s, technical:%s, reviewer:%s}",
            job_id,
            time.monotonic() - started,
            result_state.get("revision_round", 0),
            settings.model_for("product"),
            settings.model_for("ux"),
            settings.model_for("technical"),
            settings.model_for("reviewer"),
        )
    except Exception as exc:  # noqa: BLE001 - classify broadly; full detail logged, never returned to the client
        error = _classify_error(exc)
        store.update(job_id, status="failed", error=error)
        logger.warning(
            "spec job %s failed after %.1fs (%s): %s",
            job_id,
            time.monotonic() - started,
            error.type,
            exc,
            exc_info=True,
        )
