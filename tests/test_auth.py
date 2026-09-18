"""Tests for /signup and /login."""


def test_signup_success(client):
    response = client.post("/signup", json={"username": "alice", "password": "alicepass123"})
    assert response.status_code == 201
    body = response.json()
    assert body["username"] == "alice"
    assert "id" in body
    assert "password" not in body
    assert "hashed_password" not in body


def test_signup_duplicate_username(client):
    client.post("/signup", json={"username": "alice", "password": "alicepass123"})
    response = client.post("/signup", json={"username": "alice", "password": "anotherpass123"})
    assert response.status_code == 409


def test_signup_short_password_rejected(client):
    response = client.post("/signup", json={"username": "alice", "password": "short"})
    assert response.status_code == 422


def test_login_success(client):
    client.post("/signup", json={"username": "alice", "password": "alicepass123"})
    response = client.post("/login", data={"username": "alice", "password": "alicepass123"})
    assert response.status_code == 200
    body = response.json()
    assert "access_token" in body
    assert body["token_type"] == "bearer"


def test_login_invalid_password(client):
    client.post("/signup", json={"username": "alice", "password": "alicepass123"})
    response = client.post("/login", data={"username": "alice", "password": "wrongpassword"})
    assert response.status_code == 401


def test_login_nonexistent_user(client):
    response = client.post("/login", data={"username": "ghost", "password": "whatever123"})
    assert response.status_code == 401


def test_missing_authentication_rejected(client):
    response = client.get("/expenses")
    assert response.status_code == 401


def test_invalid_jwt_rejected(client):
    response = client.get("/expenses", headers={"Authorization": "Bearer not-a-real-token"})
    assert response.status_code == 401
