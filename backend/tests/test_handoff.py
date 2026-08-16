import json
from pathlib import Path

from blueprint_agents.handoff import build_agent_prompt
from blueprint_agents.schemas.common import Section, SectionGroup, SectionItem, Spec
from blueprint_agents.schemas.handoff import AgentTask, HandoffOutput

from fakes import make_llm_factory

EXAMPLES_PATH = Path(__file__).resolve().parents[1] / "examples" / "sample_briefs.json"
SAMPLE_BRIEF = json.loads(EXAMPLES_PATH.read_text(encoding="utf-8"))["saas"]


def _spec() -> Spec:
    return Spec(
        title="Invoice Chaser",
        summary="Web app for solo freelancers. Scoped to 8 weeks.",
        sections=[
            Section(
                id="problem",
                num="01",
                title="Problem and target user",
                lead="lead",
                groups=[SectionGroup(label="Primary user", items=[SectionItem(text="a user")])],
            )
        ],
    )


def _handoff() -> HandoffOutput:
    return HandoffOutput(
        context="Build a scoped invoice-chasing MVP for solo freelancers.",
        tasks=[
            AgentTask(title="Set up auth and data model", description="Stand up user auth and the invoice model."),
            AgentTask(title="Build the reminder flow", description="Send automated reminders for overdue invoices."),
        ],
        agents_md="# AGENTS.md\n\nOverview...\n",
    )


def test_build_agent_prompt_includes_title_context_and_all_tasks_in_order():
    prompt = build_agent_prompt(_spec(), _handoff())

    assert "# Build brief: Invoice Chaser" in prompt
    assert "Build a scoped invoice-chasing MVP" in prompt
    assert "### 1. Set up auth and data model" in prompt
    assert "### 2. Build the reminder flow" in prompt
    assert prompt.index("### 1.") < prompt.index("### 2.")
    assert "Stand up user auth" in prompt
    assert "Send automated reminders" in prompt


def _signup(client, email="ada@example.com"):
    res = client.post("/api/auth/signup", json={"name": "Ada", "email": email, "password": "hunter22"})
    return res.json()["token"]


def _auth(token):
    return {"Authorization": f"Bearer {token}"}


def _make_done_job(client, token):
    """Creates a job and forces it straight to 'done' with a spec, bypassing run_job (which
    the `client` fixture already stubs out) so handoff tests don't need a real graph run."""
    job_id = client.post("/api/spec-jobs", json=SAMPLE_BRIEF, headers=_auth(token)).json()["job_id"]

    import blueprint_agents.api.app as app_module

    app_module.store.update(job_id, status="done", spec=_spec())
    return job_id


def test_handoff_requires_a_done_job_with_a_spec(client):
    token = _signup(client)
    job_id = client.post("/api/spec-jobs", json=SAMPLE_BRIEF, headers=_auth(token)).json()["job_id"]

    res = client.post(f"/api/spec-jobs/{job_id}/handoff", headers=_auth(token))
    assert res.status_code == 409


def test_handoff_generates_and_persists_prompt_and_agents_md(client, monkeypatch):
    token = _signup(client)
    job_id = _make_done_job(client, token)

    monkeypatch.setattr(
        "blueprint_agents.api.app.default_llm_factory",
        make_llm_factory({"handoff": _handoff()}),
    )

    res = client.post(f"/api/spec-jobs/{job_id}/handoff", headers=_auth(token))
    assert res.status_code == 200
    body = res.json()
    assert "### 1. Set up auth and data model" in body["agent_prompt"]
    assert body["agents_md"] == "# AGENTS.md\n\nOverview...\n"

    get = client.get(f"/api/spec-jobs/{job_id}", headers=_auth(token))
    assert get.json()["agent_prompt"] == body["agent_prompt"]
    assert get.json()["agents_md"] == "# AGENTS.md\n\nOverview...\n"


def test_handoff_is_null_until_generated(client):
    token = _signup(client)
    job_id = _make_done_job(client, token)

    get = client.get(f"/api/spec-jobs/{job_id}", headers=_auth(token))
    assert get.json()["agent_prompt"] is None
    assert get.json()["agents_md"] is None


def test_cannot_generate_handoff_for_another_users_job(client):
    token_a = _signup(client, "a@example.com")
    token_b = _signup(client, "b@example.com")
    job_id = _make_done_job(client, token_a)

    res = client.post(f"/api/spec-jobs/{job_id}/handoff", headers=_auth(token_b))
    assert res.status_code == 404
