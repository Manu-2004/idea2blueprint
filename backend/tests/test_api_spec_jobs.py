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


def test_save_and_edit_draft(client):
    token = _signup(client)
    create = client.post("/api/spec-jobs/drafts", json=SAMPLE_BRIEF, headers=_auth(token))
    assert create.status_code == 201
    job_id = create.json()["job_id"]
    assert create.json()["status"] == "draft"

    get = client.get(f"/api/spec-jobs/{job_id}", headers=_auth(token))
    assert get.status_code == 200
    assert get.json()["status"] == "draft"
    assert get.json()["brief"]["idea"] == SAMPLE_BRIEF["idea"]

    edited_brief = {**SAMPLE_BRIEF, "idea": "A different idea entirely."}
    update = client.put(f"/api/spec-jobs/{job_id}/draft", json=edited_brief, headers=_auth(token))
    assert update.status_code == 200

    get_after_edit = client.get(f"/api/spec-jobs/{job_id}", headers=_auth(token))
    assert get_after_edit.json()["brief"]["idea"] == "A different idea entirely."


def test_cannot_edit_a_non_draft_job(client):
    token = _signup(client)
    job_id = client.post("/api/spec-jobs", json=SAMPLE_BRIEF, headers=_auth(token)).json()["job_id"]

    update = client.put(f"/api/spec-jobs/{job_id}/draft", json=SAMPLE_BRIEF, headers=_auth(token))
    assert update.status_code == 409


def test_generate_from_draft_schedules_the_job(client, monkeypatch):
    calls = []
    monkeypatch.setattr(
        "blueprint_agents.api.app.run_job", lambda job_id, store: calls.append(job_id)
    )
    token = _signup(client)
    job_id = client.post(
        "/api/spec-jobs/drafts", json=SAMPLE_BRIEF, headers=_auth(token)
    ).json()["job_id"]

    generate = client.post(f"/api/spec-jobs/{job_id}/generate", headers=_auth(token))
    assert generate.status_code == 202
    assert generate.json()["status"] == "pending"
    assert calls == [job_id]


def test_cannot_generate_a_job_that_is_not_a_draft(client):
    token = _signup(client)
    job_id = client.post("/api/spec-jobs", json=SAMPLE_BRIEF, headers=_auth(token)).json()["job_id"]

    generate = client.post(f"/api/spec-jobs/{job_id}/generate", headers=_auth(token))
    assert generate.status_code == 409


def test_delete_spec_job(client):
    token = _signup(client)
    job_id = client.post("/api/spec-jobs", json=SAMPLE_BRIEF, headers=_auth(token)).json()["job_id"]

    delete = client.delete(f"/api/spec-jobs/{job_id}", headers=_auth(token))
    assert delete.status_code == 204

    get = client.get(f"/api/spec-jobs/{job_id}", headers=_auth(token))
    assert get.status_code == 404
    assert client.get("/api/spec-jobs", headers=_auth(token)).json() == []


def test_cannot_delete_another_users_job(client):
    token_a = _signup(client, "a@example.com")
    token_b = _signup(client, "b@example.com")
    job_id = client.post(
        "/api/spec-jobs", json=SAMPLE_BRIEF, headers=_auth(token_a)
    ).json()["job_id"]

    delete = client.delete(f"/api/spec-jobs/{job_id}", headers=_auth(token_b))
    assert delete.status_code == 404
    assert client.get(f"/api/spec-jobs/{job_id}", headers=_auth(token_a)).status_code == 200


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
