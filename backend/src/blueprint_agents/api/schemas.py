from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field

from blueprint_agents.schemas.brief import Brief, ClarificationAnswer
from blueprint_agents.schemas.common import Spec
from blueprint_agents.schemas.intake import ClarifyingQuestion

JobStatus = Literal["draft", "pending", "running", "done", "failed", "needs_input"]

# Best-effort classification of what went wrong, so the frontend can distinguish "try
# again" (rate limit/timeout) from "rephrase your idea" (content policy) from a bug on our
# side. OpenAI doesn't always distinguish these cleanly at the exception-type level, so
# `openai_error` is a catch-all for OpenAI-side failures that don't fit a more specific type.
JobErrorType = Literal[
    "openai_rate_limit",
    "openai_timeout",
    "openai_content_policy",
    "openai_error",
    "internal_error",
    "irrelevant_input",
]


class ProgressInfo(BaseModel):
    step: int
    revision_round: int
    max_revision_rounds: int


class JobError(BaseModel):
    type: JobErrorType
    message: str


class JobCreateResponse(BaseModel):
    job_id: str
    status: JobStatus


class JobStatusResponse(BaseModel):
    status: JobStatus
    progress: ProgressInfo
    brief: Brief
    spec: Optional[Spec] = None
    error: Optional[JobError] = None
    clarifying_questions: Optional[list[ClarifyingQuestion]] = None
    agent_prompt: Optional[str] = None
    agents_md: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class ClarifyAnswersRequest(BaseModel):
    answers: list[ClarificationAnswer]


class HandoffResponse(BaseModel):
    """A coding-agent kickoff kit derived from a finished spec: a task-broken-down prompt
    ready to hand a coding agent, and an AGENTS.md for the repo it'll be building in."""

    agent_prompt: str
    agents_md: str


class SpecJobSummary(BaseModel):
    """One row of `GET /api/spec-jobs` — enough for the dashboard list without shipping the
    full spec/brief/event history for every job."""

    id: str
    title: str
    status: JobStatus
    created_at: datetime
    updated_at: datetime


class UsageResponse(BaseModel):
    """Monthly spec-generation quota usage — counts every spec created this calendar
    month, including ones the user has since deleted."""

    specs_used_this_month: int


class UserResponse(BaseModel):
    id: str
    name: str
    email: str


class SignupRequest(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    email: str = Field(min_length=3, max_length=320)
    password: str = Field(min_length=8, max_length=200)


class LoginRequest(BaseModel):
    email: str
    password: str


class AuthResponse(BaseModel):
    token: str
    user: UserResponse
