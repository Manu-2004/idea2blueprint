import logging
from contextlib import asynccontextmanager

from fastapi import BackgroundTasks, FastAPI, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware

from blueprint_agents.api.jobs import JobStore
from blueprint_agents.api.progress import compute_step
from blueprint_agents.api.runner import run_job
from blueprint_agents.api.schemas import JobCreateResponse, JobStatusResponse, ProgressInfo
from blueprint_agents.config import get_settings
from blueprint_agents.schemas.brief import Brief

logging.basicConfig(level=logging.INFO)

store = JobStore()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Fail loudly at boot rather than let every job fail individually minutes into a run.
    if not get_settings().openai_api_key:
        raise RuntimeError(
            "OPENAI_API_KEY is not set. Copy backend/.env.example to backend/.env and fill it in."
        )
    yield


app = FastAPI(title="Idea2Blueprint agentic API", lifespan=lifespan)

_cors_origins = [origin.strip() for origin in get_settings().cors_origins.split(",") if origin.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/api/spec-jobs", status_code=202, response_model=JobCreateResponse)
def create_spec_job(brief: Brief, background_tasks: BackgroundTasks, response: Response) -> JobCreateResponse:
    settings = get_settings()
    job = store.create(brief, settings.max_revision_rounds)
    background_tasks.add_task(run_job, job.id, store)
    response.headers["Location"] = f"/api/spec-jobs/{job.id}"
    return JobCreateResponse(job_id=job.id, status=job.status)


@app.get("/api/spec-jobs/{job_id}", response_model=JobStatusResponse)
def get_spec_job(job_id: str) -> JobStatusResponse:
    job = store.get(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Unknown job id (never existed, or expired).")

    return JobStatusResponse(
        status=job.status,
        progress=ProgressInfo(
            step=compute_step(job.events),
            revision_round=job.revision_round,
            max_revision_rounds=job.max_revision_rounds,
        ),
        spec=job.spec,
        error=job.error,
        created_at=job.created_at,
        updated_at=job.updated_at,
    )
