def test_signup_then_me(client):
    res = client.post(
        "/api/auth/signup", json={"name": "Ada", "email": "ada@example.com", "password": "hunter22"}
    )
    assert res.status_code == 201
    body = res.json()
    assert body["user"]["email"] == "ada@example.com"

    me = client.get("/api/auth/me", headers={"Authorization": f"Bearer {body['token']}"})
    assert me.status_code == 200
    assert me.json()["email"] == "ada@example.com"


def test_signup_duplicate_email_conflicts(client):
    payload = {"name": "Ada", "email": "ada@example.com", "password": "hunter22"}
    client.post("/api/auth/signup", json=payload)
    res = client.post("/api/auth/signup", json={**payload, "name": "Ada Two", "password": "hunter23"})
    assert res.status_code == 409


def test_signup_rejects_short_password(client):
    res = client.post(
        "/api/auth/signup", json={"name": "Ada", "email": "ada@example.com", "password": "short"}
    )
    assert res.status_code == 422


def test_login_success(client):
    client.post(
        "/api/auth/signup", json={"name": "Ada", "email": "ada@example.com", "password": "hunter22"}
    )
    res = client.post("/api/auth/login", json={"email": "ada@example.com", "password": "hunter22"})
    assert res.status_code == 200
    assert "token" in res.json()


def test_login_wrong_password(client):
    client.post(
        "/api/auth/signup", json={"name": "Ada", "email": "ada@example.com", "password": "hunter22"}
    )
    res = client.post("/api/auth/login", json={"email": "ada@example.com", "password": "nope"})
    assert res.status_code == 401


def test_login_unknown_email(client):
    res = client.post("/api/auth/login", json={"email": "nobody@example.com", "password": "whatever"})
    assert res.status_code == 401


def test_me_without_token_is_unauthorized(client):
    assert client.get("/api/auth/me").status_code == 401


def test_me_with_bad_token_is_unauthorized(client):
    res = client.get("/api/auth/me", headers={"Authorization": "Bearer not-a-real-token"})
    assert res.status_code == 401


def test_logout_invalidates_token(client):
    signup = client.post(
        "/api/auth/signup", json={"name": "Ada", "email": "ada@example.com", "password": "hunter22"}
    )
    headers = {"Authorization": f"Bearer {signup.json()['token']}"}

    assert client.post("/api/auth/logout", headers=headers).status_code == 204
    assert client.get("/api/auth/me", headers=headers).status_code == 401
