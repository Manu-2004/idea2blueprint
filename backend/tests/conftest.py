import importlib

import pytest
from fastapi.testclient import TestClient

from blueprint_agents.config import get_settings


@pytest.fixture
def client(tmp_path, monkeypatch):
    """A TestClient wired to a throwaway sqlite file per test, via a full reload of
    `api.app` (its `db`/`store`/`auth_store` singletons are built at import time from
    `get_settings()`, so a stale cached module would leak state between tests)."""
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setenv("DATABASE_PATH", str(tmp_path / "test.db"))
    get_settings.cache_clear()

    import blueprint_agents.api.app as app_module

    importlib.reload(app_module)
    # Creating a spec job schedules a real OpenAI-backed graph run via BackgroundTasks.
    # These tests only exercise the HTTP/storage layer, so stub the run out.
    monkeypatch.setattr(app_module, "run_job", lambda job_id, store: None)

    with TestClient(app_module.app) as test_client:
        yield test_client

    get_settings.cache_clear()
