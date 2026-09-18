"""Tests for expense CRUD and filtering."""


def _create_expense(client, headers, **overrides):
    payload = {
        "description": "Groceries",
        "amount": 45.50,
        "category": "Food",
        "date": "2026-09-01",
    }
    payload.update(overrides)
    return client.post("/expenses", json=payload, headers=headers)


def test_create_expense(client, auth_headers):
    response = _create_expense(client, auth_headers)
    assert response.status_code == 201
    body = response.json()
    assert body["description"] == "Groceries"
    assert body["category"] == "Food"
    assert "id" in body
    assert "owner_id" in body


def test_create_expense_negative_amount_rejected(client, auth_headers):
    response = _create_expense(client, auth_headers, amount=-10)
    assert response.status_code == 422


def test_create_expense_future_date_rejected(client, auth_headers):
    response = _create_expense(client, auth_headers, date="2099-01-01")
    assert response.status_code == 422


def test_create_expense_missing_field_rejected(client, auth_headers):
    response = client.post(
        "/expenses", json={"description": "bad", "amount": 5}, headers=auth_headers
    )
    assert response.status_code == 422


def test_get_expenses(client, auth_headers):
    _create_expense(client, auth_headers, description="Groceries")
    _create_expense(client, auth_headers, description="Bus fare", category="Transport", amount=2.5)

    response = client.get("/expenses", headers=auth_headers)
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_update_expense(client, auth_headers):
    created = _create_expense(client, auth_headers).json()

    response = client.put(
        f"/expenses/{created['id']}", json={"amount": 99.99}, headers=auth_headers
    )
    assert response.status_code == 200
    assert response.json()["amount"] == "99.99"


def test_update_nonexistent_expense_returns_404(client, auth_headers):
    response = client.put("/expenses/99999", json={"amount": 5}, headers=auth_headers)
    assert response.status_code == 404


def test_delete_expense(client, auth_headers):
    created = _create_expense(client, auth_headers).json()

    response = client.delete(f"/expenses/{created['id']}", headers=auth_headers)
    assert response.status_code == 204

    listing = client.get("/expenses", headers=auth_headers)
    assert listing.json() == []


def test_filter_by_category(client, auth_headers):
    _create_expense(client, auth_headers, category="Food")
    _create_expense(client, auth_headers, category="Transport", amount=2.5)

    response = client.get("/expenses?category=Food", headers=auth_headers)
    assert response.status_code == 200
    results = response.json()
    assert len(results) == 1
    assert results[0]["category"] == "Food"


def test_filter_by_date_range(client, auth_headers):
    _create_expense(client, auth_headers, date="2026-09-01")
    _create_expense(client, auth_headers, date="2026-09-15")

    response = client.get(
        "/expenses?start_date=2026-09-01&end_date=2026-09-05", headers=auth_headers
    )
    assert response.status_code == 200
    results = response.json()
    assert len(results) == 1
    assert results[0]["date"] == "2026-09-01"


def test_filter_invalid_date_range_rejected(client, auth_headers):
    response = client.get(
        "/expenses?start_date=2026-09-15&end_date=2026-09-01", headers=auth_headers
    )
    assert response.status_code == 400
