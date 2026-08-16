import json
import uuid
from datetime import datetime, timezone
from typing import Optional

from blueprint_agents.api.schemas import JobError, JobStatus
from blueprint_agents.db import Database
from blueprint_agents.schemas.brief import Brief
from blueprint_agents.schemas.common import Spec
from blueprint_agents.schemas.events import NodeEvent
from blueprint_agents.schemas.intake import ClarifyingQuestion


class Job:
    def __init__(
        self,
        job_id: str,
        user_id: str,
        brief: Brief,
        max_revision_rounds: int,
        *,
        title: Optional[str] = None,
        status: JobStatus = "pending",
        events: Optional[list[NodeEvent]] = None,
        revision_round: int = 0,
        spec: Optional[Spec] = None,
        error: Optional[JobError] = None,
        clarifying_questions: Optional[list[ClarifyingQuestion]] = None,
        agent_prompt: Optional[str] = None,
        agents_md: Optional[str] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        now = datetime.now(timezone.utc)
        self.id = job_id
        self.user_id = user_id
        self.brief = brief
        self.title = title
        self.status = status
        self.events = events if events is not None else []
        self.revision_round = revision_round
        self.max_revision_rounds = max_revision_rounds
        self.spec = spec
        self.error = error
        self.clarifying_questions = clarifying_questions
        self.agent_prompt = agent_prompt
        self.agents_md = agents_md
        self.created_at = created_at or now
        self.updated_at = updated_at or now


def _row_to_job(row) -> Job:
    return Job(
        job_id=row["id"],
        user_id=row["user_id"],
        brief=Brief.model_validate_json(row["brief_json"]),
        max_revision_rounds=row["max_revision_rounds"],
        title=row["title"],
        status=row["status"],
        events=[NodeEvent(**e) for e in json.loads(row["events_json"])],
        revision_round=row["revision_round"],
        spec=Spec.model_validate_json(row["spec_json"]) if row["spec_json"] else None,
        error=JobError.model_validate_json(row["error_json"]) if row["error_json"] else None,
        clarifying_questions=(
            [ClarifyingQuestion(**q) for q in json.loads(row["clarifying_questions_json"])]
            if row["clarifying_questions_json"]
            else None
        ),
        agent_prompt=row["agent_prompt_md"],
        agents_md=row["agents_md"],
        created_at=datetime.fromisoformat(row["created_at"]),
        updated_at=datetime.fromisoformat(row["updated_at"]),
    )


class JobStore:
    """Spec-job storage backed by sqlite (`Database`) instead of an in-memory dict, so
    generated specs survive a server restart and can be listed per-user for the dashboard.
    `get`/`update` keep the exact signatures the in-memory version had — `api/runner.py`
    calls them without knowing storage moved under it."""

    def __init__(self, db: Database):
        self._db = db

    def create(
        self,
        user_id: str,
        brief: Brief,
        max_revision_rounds: int,
        *,
        status: JobStatus = "pending",
    ) -> Job:
        job = Job(uuid.uuid4().hex, user_id, brief, max_revision_rounds, status=status)
        with self._db.lock, self._db.conn:
            self._db.conn.execute(
                """
                INSERT INTO spec_jobs
                    (id, user_id, title, brief_json, status, spec_json, error_json,
                     revision_round, max_revision_rounds, events_json, agent_prompt_md,
                     agents_md, clarifying_questions_json, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    job.id,
                    job.user_id,
                    job.title,
                    job.brief.model_dump_json(),
                    job.status,
                    None,
                    None,
                    job.revision_round,
                    job.max_revision_rounds,
                    "[]",
                    None,
                    None,
                    None,
                    job.created_at.isoformat(),
                    job.updated_at.isoformat(),
                ),
            )
        return job

    def get(self, job_id: str) -> Optional[Job]:
        with self._db.lock:
            row = self._db.conn.execute(
                "SELECT * FROM spec_jobs WHERE id = ? AND deleted_at IS NULL", (job_id,)
            ).fetchone()
        return _row_to_job(row) if row is not None else None

    def list_for_user(self, user_id: str) -> list[Job]:
        with self._db.lock:
            rows = self._db.conn.execute(
                "SELECT * FROM spec_jobs WHERE user_id = ? AND deleted_at IS NULL ORDER BY updated_at DESC",
                (user_id,),
            ).fetchall()
        return [_row_to_job(row) for row in rows]

    def delete(self, job_id: str) -> None:
        # Soft delete: a deleted spec still counts toward the month it was generated in,
        # it just drops out of listings. A hard DELETE would let deleting specs lower the
        # "specs used this month" quota display, which is wrong.
        with self._db.lock, self._db.conn:
            self._db.conn.execute(
                "UPDATE spec_jobs SET deleted_at = ? WHERE id = ?",
                (datetime.now(timezone.utc).isoformat(), job_id),
            )

    def list_titles_for_user(self, user_id: str) -> list[str]:
        """Product names from every spec this user has ever generated, including soft-deleted
        ones (deleting a spec doesn't free up its name for reuse, mirroring
        `count_created_since`'s soft-delete handling) — used to steer the Product agent away
        from repeating a name (see `nodes/product.py`)."""
        with self._db.lock:
            rows = self._db.conn.execute(
                "SELECT DISTINCT title FROM spec_jobs WHERE user_id = ? AND title IS NOT NULL",
                (user_id,),
            ).fetchall()
        return [row["title"] for row in rows]

    def count_created_since(self, user_id: str, since: datetime) -> int:
        """Counts every job created on/after `since` for quota purposes, including ones
        since soft-deleted — deleting a spec must not free up quota for the month."""
        with self._db.lock:
            row = self._db.conn.execute(
                "SELECT COUNT(*) AS n FROM spec_jobs WHERE user_id = ? AND created_at >= ?",
                (user_id, since.isoformat()),
            ).fetchone()
        return row["n"]

    def update(self, job_id: str, **fields) -> None:
        if not fields:
            return
        encoders = {
            "status": lambda v: v,
            "title": lambda v: v,
            "brief": lambda v: v.model_dump_json(),
            "events": lambda v: json.dumps([e.model_dump() for e in v]),
            "revision_round": lambda v: v,
            "spec": lambda v: v.model_dump_json() if v is not None else None,
            "error": lambda v: v.model_dump_json() if v is not None else None,
            "clarifying_questions": lambda v: json.dumps([q.model_dump() for q in v]) if v is not None else None,
            "agent_prompt": lambda v: v,
            "agents_md": lambda v: v,
        }
        columns = {
            "status": "status",
            "title": "title",
            "brief": "brief_json",
            "events": "events_json",
            "revision_round": "revision_round",
            "spec": "spec_json",
            "error": "error_json",
            "clarifying_questions": "clarifying_questions_json",
            "agent_prompt": "agent_prompt_md",
            "agents_md": "agents_md",
        }
        set_clauses = []
        values: list = []
        for field, value in fields.items():
            set_clauses.append(f"{columns[field]} = ?")
            values.append(encoders[field](value))

        # The spec carries its own title; derive the job's title from it once generation
        # finishes, unless the caller set one explicitly.
        if "spec" in fields and "title" not in fields and fields["spec"] is not None:
            set_clauses.append("title = ?")
            values.append(fields["spec"].title)

        set_clauses.append("updated_at = ?")
        values.append(datetime.now(timezone.utc).isoformat())
        values.append(job_id)

        with self._db.lock, self._db.conn:
            self._db.conn.execute(
                f"UPDATE spec_jobs SET {', '.join(set_clauses)} WHERE id = ?",
                values,
            )
