from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel

from blueprint_agents.schemas.common import Spec

JobStatus = Literal["pending", "running", "done", "failed"]

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
    spec: Optional[Spec] = None
    error: Optional[JobError] = None
    created_at: datetime
    updated_at: datetime
