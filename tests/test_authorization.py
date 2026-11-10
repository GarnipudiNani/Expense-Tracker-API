"""Authorization tests: a user must never be able to access, modify, or
delete another user's expenses."""

from tests.conftest import signup_and_login


def _headers_for(client, username):
    token = signup_and_login(client, username=username, password="somepassword123")
    return {"Authorization": f"Bearer {token}"}


def _create_expense_for(client, headers):
    payload = {
        "description": "Alice's private expense",
        "amount": 100.00,
        "category": "Food",
        "date": "2026-09-01",
    }
    return client.post("/expenses", json=payload, headers=headers).json()


def test_user_cannot_view_other_users_expenses(client):
    alice_headers = _headers_for(client, "alice")
    bob_headers = _headers_for(client, "bob")
    _create_expense_for(client, alice_headers)

    response = client.get("/expenses", headers=bob_headers)
    assert response.status_code == 200
    assert response.json() == []


def test_user_cannot_update_other_users_expense(client):
    alice_headers = _headers_for(client, "alice")
    bob_headers = _headers_for(client, "bob")
    alice_expense = _create_expense_for(client, alice_headers)

    response = client.put(
        f"/expenses/{alice_expense['id']}",
        json={"amount": 999999},
        headers=bob_headers,
    )
    assert response.status_code == 404

    # confirm Alice's expense was not modified
    unchanged = client.get("/expenses", headers=alice_headers).json()
    assert unchanged[0]["amount"] == "100.00"


def test_user_cannot_delete_other_users_expense(client):
    alice_headers = _headers_for(client, "alice")
    bob_headers = _headers_for(client, "bob")
    alice_expense = _create_expense_for(client, alice_headers)

    response = client.delete(f"/expenses/{alice_expense['id']}", headers=bob_headers)
    assert response.status_code == 404

    # confirm Alice's expense still exists
    still_there = client.get("/expenses", headers=alice_headers).json()
    assert len(still_there) == 1
