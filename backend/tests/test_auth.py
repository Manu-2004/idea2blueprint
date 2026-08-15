from datetime import timedelta

import pytest

import blueprint_agents.auth as auth_module
from blueprint_agents.auth import AuthStore, EmailAlreadyRegistered
from blueprint_agents.db import Database


@pytest.fixture
def auth_store():
    db = Database(":memory:")
    db.init_schema()
    return AuthStore(db)


def test_create_user_then_authenticate(auth_store):
    user = auth_store.create_user("Ada", "ada@example.com", "hunter22")
    authenticated = auth_store.authenticate("ada@example.com", "hunter22")
    assert authenticated is not None
    assert authenticated.id == user.id


def test_authenticate_wrong_password_returns_none(auth_store):
    auth_store.create_user("Ada", "ada@example.com", "hunter22")
    assert auth_store.authenticate("ada@example.com", "wrong") is None


def test_authenticate_unknown_email_returns_none(auth_store):
    assert auth_store.authenticate("nobody@example.com", "whatever") is None


def test_email_is_normalized_on_create_and_lookup(auth_store):
    auth_store.create_user("Ada", "  Ada@Example.com  ", "hunter22")
    assert auth_store.authenticate("ada@example.com", "hunter22") is not None


def test_duplicate_email_raises(auth_store):
    auth_store.create_user("Ada", "ada@example.com", "hunter22")
    with pytest.raises(EmailAlreadyRegistered):
        auth_store.create_user("Ada Two", "ada@example.com", "otherpass")


def test_session_round_trip(auth_store):
    user = auth_store.create_user("Ada", "ada@example.com", "hunter22")
    token = auth_store.create_session(user.id)
    fetched = auth_store.get_user_by_token(token)
    assert fetched is not None
    assert fetched.id == user.id


def test_unknown_token_returns_none(auth_store):
    assert auth_store.get_user_by_token("not-a-real-token") is None


def test_delete_session_invalidates_token(auth_store):
    user = auth_store.create_user("Ada", "ada@example.com", "hunter22")
    token = auth_store.create_session(user.id)
    auth_store.delete_session(token)
    assert auth_store.get_user_by_token(token) is None


def test_expired_session_returns_none(auth_store, monkeypatch):
    monkeypatch.setattr(auth_module, "SESSION_TTL", timedelta(seconds=-1))
    user = auth_store.create_user("Ada", "ada@example.com", "hunter22")
    token = auth_store.create_session(user.id)
    assert auth_store.get_user_by_token(token) is None
