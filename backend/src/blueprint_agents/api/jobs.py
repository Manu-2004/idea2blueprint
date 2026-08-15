import threading
import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional

from blueprint_agents.api.schemas import JobError, JobStatus
from blueprint_agents.schemas.brief import Brief
from blueprint_agents.schemas.common import Spec
from blueprint_agents.schemas.events import NodeEvent

# No DB in this pass: jobs live only in process memory and are lost on restart. This TTL
# just keeps a long-running dev/demo process from leaking memory indefinitely — it is not a
# substitute for real persistence.
JOB_TTL = timedelta(minutes=30)


class Job:
    def __init__(self, job_id: str, brief: Brief, max_revision_rounds: int):
        now = datetime.now(timezone.utc)
        self.id = job_id
        self.brief = brief
        self.status: JobStatus = "pending"
        self.events: list[NodeEvent] = []
        self.revision_round = 0
        self.max_revision_rounds = max_revision_rounds
        self.spec: Optional[Spec] = None
        self.error: Optional[JobError] = None
        self.created_at = now
        self.updated_at = now


class JobStore:
    """In-memory job store, guarded by a real lock (not just relying on the GIL) since
    updates are read-modify-write from a background thread while GET handlers read
    concurrently on the event loop thread."""

    def __init__(self) -> None:
        self._jobs: dict[str, Job] = {}
        self._lock = threading.Lock()

    def create(self, brief: Brief, max_revision_rounds: int) -> Job:
        with self._lock:
            self._evict_expired_locked()
            job_id = uuid.uuid4().hex
            job = Job(job_id, brief, max_revision_rounds)
            self._jobs[job_id] = job
            return job

    def get(self, job_id: str) -> Optional[Job]:
        with self._lock:
            return self._jobs.get(job_id)

    def update(self, job_id: str, **fields) -> None:
        with self._lock:
            job = self._jobs.get(job_id)
            if job is None:
                return
            for key, value in fields.items():
                setattr(job, key, value)
            job.updated_at = datetime.now(timezone.utc)

    def _evict_expired_locked(self) -> None:
        cutoff = datetime.now(timezone.utc) - JOB_TTL
        expired = [
            job_id
            for job_id, job in self._jobs.items()
            if job.status in ("done", "failed") and job.updated_at < cutoff
        ]
        for job_id in expired:
            del self._jobs[job_id]
