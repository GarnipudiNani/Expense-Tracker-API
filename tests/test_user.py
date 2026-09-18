"""Tests for /user: update username and delete account."""


def test_update_username(client, auth_headers):
    response = client.put("/user", json={"username": "newname"}, headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["username"] == "newname"


def test_update_username_conflict(client):
    client.post("/signup", json={"username": "alice", "password": "alicepass123"})
    login = client.post("/login", data={"username": "alice", "password": "alicepass123"})
    alice_headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

    client.post("/signup", json={"username": "bob", "password": "bobpassword123"})

    response = client.put("/user", json={"username": "bob"}, headers=alice_headers)
    assert response.status_code == 409


def test_delete_account(client, auth_headers):
    response = client.delete("/user", headers=auth_headers)
    assert response.status_code == 204

    # the token should no longer work for anything, since the user is gone
    follow_up = client.get("/expenses", headers=auth_headers)
    assert follow_up.status_code == 401


def test_delete_account_removes_expenses(client, auth_headers):
    client.post(
        "/expenses",
        json={
            "description": "Groceries",
            "amount": 20,
            "category": "Food",
            "date": "2026-09-01",
        },
        headers=auth_headers,
    )

    response = client.delete("/user", headers=auth_headers)
    assert response.status_code == 204
