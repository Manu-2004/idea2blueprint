import logging
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import Optional

from fastapi import BackgroundTasks, Depends, FastAPI, Header, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware

from blueprint_agents.api.deps import extract_bearer_token, make_get_current_user
from blueprint_agents.api.jobs import JobStore
from blueprint_agents.api.progress import compute_step
from blueprint_agents.api.runner import run_job
from blueprint_agents.api.schemas import (
    AuthResponse,
    HandoffResponse,
    JobCreateResponse,
    JobStatusResponse,
    LoginRequest,
    ProgressInfo,
    SignupRequest,
    SpecJobSummary,
    UsageResponse,
    UserResponse,
)
from blueprint_agents.auth import AuthStore, EmailAlreadyRegistered, User
from blueprint_agents.config import get_settings
from blueprint_agents.db import Database
from blueprint_agents.handoff import build_agent_prompt, generate_handoff
from blueprint_agents.llm import default_llm_factory
from blueprint_agents.schemas.brief import Brief

logging.basicConfig(level=logging.INFO)

db = Database(get_settings().database_path)
auth_store = AuthStore(db)
store = JobStore(db)
get_current_user = make_get_current_user(auth_store)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Fail loudly at boot rather than let every job fail individually minutes into a run.
    if not get_settings().openai_api_key:
        raise RuntimeError(
            "OPENAI_API_KEY is not set. Copy backend/.env.example to backend/.env and fill it in."
        )
    db.init_schema()
    yield


app = FastAPI(title="Idea2Blueprint agentic API", lifespan=lifespan)

_cors_origins = [origin.strip() for origin in get_settings().cors_origins.split(",") if origin.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok"}


def _user_response(user: User) -> UserResponse:
    return UserResponse(id=user.id, name=user.name, email=user.email)


def _get_owned_job_or_404(job_id: str, current_user: User):
    job = store.get(job_id)
    if job is None or job.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Unknown job id.")
    return job


@app.post("/api/auth/signup", status_code=201, response_model=AuthResponse)
def signup(body: SignupRequest) -> AuthResponse:
    try:
        user = auth_store.create_user(body.name, body.email, body.password)
    except EmailAlreadyRegistered as exc:
        raise HTTPException(status_code=409, detail="An account with that email already exists.") from exc
    token = auth_store.create_session(user.id)
    return AuthResponse(token=token, user=_user_response(user))


@app.post("/api/auth/login", response_model=AuthResponse)
def login(body: LoginRequest) -> AuthResponse:
    user = auth_store.authenticate(body.email, body.password)
    if user is None:
        raise HTTPException(status_code=401, detail="Incorrect email or password.")
    token = auth_store.create_session(user.id)
    return AuthResponse(token=token, user=_user_response(user))


@app.get("/api/auth/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)) -> UserResponse:
    return _user_response(current_user)


@app.post("/api/auth/logout", status_code=204)
def logout(authorization: Optional[str] = Header(default=None)) -> Response:
    token = extract_bearer_token(authorization)
    if token is not None:
        auth_store.delete_session(token)
    return Response(status_code=204)


@app.post("/api/spec-jobs", status_code=202, response_model=JobCreateResponse)
def create_spec_job(
    brief: Brief,
    background_tasks: BackgroundTasks,
    response: Response,
    current_user: User = Depends(get_current_user),
) -> JobCreateResponse:
    settings = get_settings()
    job = store.create(current_user.id, brief, settings.max_revision_rounds)
    background_tasks.add_task(run_job, job.id, store)
    response.headers["Location"] = f"/api/spec-jobs/{job.id}"
    return JobCreateResponse(job_id=job.id, status=job.status)


@app.post("/api/spec-jobs/drafts", status_code=201, response_model=JobCreateResponse)
def save_draft(
    brief: Brief,
    response: Response,
    current_user: User = Depends(get_current_user),
) -> JobCreateResponse:
    settings = get_settings()
    job = store.create(current_user.id, brief, settings.max_revision_rounds, status="draft")
    response.headers["Location"] = f"/api/spec-jobs/{job.id}"
    return JobCreateResponse(job_id=job.id, status=job.status)


@app.put("/api/spec-jobs/{job_id}/draft", response_model=JobCreateResponse)
def update_draft(
    job_id: str,
    brief: Brief,
    current_user: User = Depends(get_current_user),
) -> JobCreateResponse:
    job = _get_owned_job_or_404(job_id, current_user)
    if job.status != "draft":
        raise HTTPException(status_code=409, detail="Only draft specs can be edited.")
    store.update(job_id, brief=brief)
    return JobCreateResponse(job_id=job.id, status=job.status)


@app.post("/api/spec-jobs/{job_id}/generate", status_code=202, response_model=JobCreateResponse)
def generate_from_draft(
    job_id: str,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
) -> JobCreateResponse:
    job = _get_owned_job_or_404(job_id, current_user)
    if job.status != "draft":
        raise HTTPException(status_code=409, detail="Only draft specs can be generated.")
    store.update(job_id, status="pending")
    background_tasks.add_task(run_job, job.id, store)
    return JobCreateResponse(job_id=job.id, status="pending")


@app.post("/api/spec-jobs/{job_id}/handoff", response_model=HandoffResponse)
def create_handoff(job_id: str, current_user: User = Depends(get_current_user)) -> HandoffResponse:
    """Generates (or regenerates) the coding-agent kickoff kit for a finished spec: a
    task-broken-down prompt plus an AGENTS.md. Runs inline rather than via BackgroundTasks —
    unlike a full spec run, this is a single LLM call, and FastAPI already dispatches sync
    `def` path operations like this one to a worker thread, so it doesn't block the event loop."""

    job = _get_owned_job_or_404(job_id, current_user)
    if job.status != "done" or job.spec is None:
        raise HTTPException(status_code=409, detail="Generate the spec before creating a coding-agent handoff.")

    handoff = generate_handoff(job.brief, job.spec, default_llm_factory)
    agent_prompt = build_agent_prompt(job.spec, handoff)
    store.update(job_id, agent_prompt=agent_prompt, agents_md=handoff.agents_md)
    return HandoffResponse(agent_prompt=agent_prompt, agents_md=handoff.agents_md)


@app.delete("/api/spec-jobs/{job_id}", status_code=204)
def delete_spec_job(job_id: str, current_user: User = Depends(get_current_user)) -> Response:
    _get_owned_job_or_404(job_id, current_user)
    store.delete(job_id)
    return Response(status_code=204)


@app.get("/api/spec-jobs", response_model=list[SpecJobSummary])
def list_spec_jobs(current_user: User = Depends(get_current_user)) -> list[SpecJobSummary]:
    jobs = store.list_for_user(current_user.id)
    return [
        SpecJobSummary(
            id=job.id,
            title=job.title or (job.brief.idea[:60] + ("…" if len(job.brief.idea) > 60 else "")),
            status=job.status,
            created_at=job.created_at,
            updated_at=job.updated_at,
        )
        for job in jobs
    ]


@app.get("/api/spec-jobs/usage", response_model=UsageResponse)
def get_spec_usage(current_user: User = Depends(get_current_user)) -> UsageResponse:
    since = datetime.now(timezone.utc).replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    count = store.count_created_since(current_user.id, since)
    return UsageResponse(specs_used_this_month=count)


@app.get("/api/spec-jobs/{job_id}", response_model=JobStatusResponse)
def get_spec_job(job_id: str, current_user: User = Depends(get_current_user)) -> JobStatusResponse:
    job = _get_owned_job_or_404(job_id, current_user)

    return JobStatusResponse(
        status=job.status,
        progress=ProgressInfo(
            step=compute_step(job.events),
            revision_round=job.revision_round,
            max_revision_rounds=job.max_revision_rounds,
        ),
        brief=job.brief,
        spec=job.spec,
        error=job.error,
        agent_prompt=job.agent_prompt,
        agents_md=job.agents_md,
        created_at=job.created_at,
        updated_at=job.updated_at,
    )
