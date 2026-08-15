import importlib
import json
from pathlib import Path

from fastapi.testclient import TestClient

from blueprint_agents.config import get_settings

EXAMPLES_PATH = Path(__file__).resolve().parents[1] / "examples" / "sample_briefs.json"
SAMPLE_BRIEF = json.loads(EXAMPLES_PATH.read_text(encoding="utf-8"))["saas"]


def _signup(client, email="ada@example.com"):
    res = client.post(
        "/api/auth/signup", json={"name": "Ada", "email": email, "password": "hunter22"}
    )
    return res.json()["token"]


def _auth(token):
    return {"Authorization": f"Bearer {token}"}


def test_create_spec_job_requires_auth(client):
    res = client.post("/api/spec-jobs", json=SAMPLE_BRIEF)
    assert res.status_code == 401


def test_create_and_get_own_job(client):
    token = _signup(client)
    create = client.post("/api/spec-jobs", json=SAMPLE_BRIEF, headers=_auth(token))
    assert create.status_code == 202
    job_id = create.json()["job_id"]

    get = client.get(f"/api/spec-jobs/{job_id}", headers=_auth(token))
    assert get.status_code == 200
    assert get.json()["status"] == "pending"


def test_list_scoped_to_current_user(client):
    token_a = _signup(client, "a@example.com")
    token_b = _signup(client, "b@example.com")
    client.post("/api/spec-jobs", json=SAMPLE_BRIEF, headers=_auth(token_a))

    listing_a = client.get("/api/spec-jobs", headers=_auth(token_a))
    listing_b = client.get("/api/spec-jobs", headers=_auth(token_b))
    assert len(listing_a.json()) == 1
    assert listing_a.json()[0]["title"].startswith(SAMPLE_BRIEF["idea"][:20])
    assert listing_b.json() == []


def test_get_other_users_job_is_404(client):
    token_a = _signup(client, "a@example.com")
    token_b = _signup(client, "b@example.com")
    job_id = client.post(
        "/api/spec-jobs", json=SAMPLE_BRIEF, headers=_auth(token_a)
    ).json()["job_id"]

    res = client.get(f"/api/spec-jobs/{job_id}", headers=_auth(token_b))
    assert res.status_code == 404


def test_get_unknown_job_is_404(client):
    token = _signup(client)
    res = client.get("/api/spec-jobs/does-not-exist", headers=_auth(token))
    assert res.status_code == 404


def test_jobs_persist_across_a_fresh_store_on_the_same_db_file(tmp_path, monkeypatch):
    db_path = str(tmp_path / "persist.db")
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setenv("DATABASE_PATH", db_path)
    get_settings.cache_clear()

    import blueprint_agents.api.app as app_module

    importlib.reload(app_module)
    monkeypatch.setattr(app_module, "run_job", lambda job_id, store: None)

    with TestClient(app_module.app) as test_client:
        token = _signup(test_client)
        job_id = test_client.post(
            "/api/spec-jobs", json=SAMPLE_BRIEF, headers=_auth(token)
        ).json()["job_id"]

    # Simulate a server restart: a fresh Database/JobStore pointed at the same file must
    # see the job that the previous process created.
    from blueprint_agents.api.jobs import JobStore
    from blueprint_agents.db import Database

    fresh_store = JobStore(Database(db_path))
    job = fresh_store.get(job_id)
    assert job is not None
    assert job.brief.idea == SAMPLE_BRIEF["idea"]

    get_settings.cache_clear()
