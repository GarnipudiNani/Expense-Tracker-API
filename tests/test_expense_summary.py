"""Tests for category-based expense summaries."""


def _create_expense(client, headers, category, amount, date):
    return client.post(
        "/expenses",
        json={
            "description": f"{category} expense",
            "amount": amount,
            "category": category,
            "date": date,
        },
        headers=headers,
    )


def test_summary_returns_category_totals_counts_and_order(client, auth_headers):
    _create_expense(client, auth_headers, "Food", "10.10", "2026-09-01")
    _create_expense(client, auth_headers, "Food", "2.25", "2026-09-02")
    _create_expense(client, auth_headers, "Travel", "12.35", "2026-09-03")
    _create_expense(client, auth_headers, "Books", "13.00", "2026-09-04")

    response = client.get("/expenses/summary", headers=auth_headers)

    assert response.status_code == 200
    assert response.json() == [
        {"category": "Books", "total": "13.00", "count": 1},
        {"category": "Food", "total": "12.35", "count": 2},
        {"category": "Travel", "total": "12.35", "count": 1},
    ]


def test_summary_date_bounds_are_inclusive(client, auth_headers):
    _create_expense(client, auth_headers, "Food", "1.10", "2026-09-01")
    _create_expense(client, auth_headers, "Food", "2.20", "2026-09-02")
    _create_expense(client, auth_headers, "Food", "3.30", "2026-09-03")

    response = client.get(
        "/expenses/summary?start_date=2026-09-01&end_date=2026-09-02",
        headers=auth_headers,
    )

    assert response.status_code == 200
    assert response.json() == [{"category": "Food", "total": "3.30", "count": 2}]


def test_summary_for_user_without_expenses_is_empty(client, auth_headers):
    response = client.get("/expenses/summary", headers=auth_headers)

    assert response.status_code == 200
    assert response.json() == []


def test_summary_is_scoped_to_current_user(client, auth_headers):
    client.post("/signup", json={"username": "other", "password": "otherpassword123"})
    other_login = client.post(
        "/login", data={"username": "other", "password": "otherpassword123"}
    )
    other_headers = {
        "Authorization": f"Bearer {other_login.json()['access_token']}"
    }

    _create_expense(client, auth_headers, "Food", "9.99", "2026-09-01")
    _create_expense(client, other_headers, "Travel", "99.99", "2026-09-01")

    response = client.get("/expenses/summary", headers=auth_headers)

    assert response.status_code == 200
    assert response.json() == [{"category": "Food", "total": "9.99", "count": 1}]


def test_summary_rejects_invalid_date_range(client, auth_headers):
    response = client.get(
        "/expenses/summary?start_date=2026-09-02&end_date=2026-09-01",
        headers=auth_headers,
    )

    assert response.status_code == 400
    assert response.json() == {"detail": "start_date cannot be after end_date"}


def test_summary_requires_authentication(client):
    response = client.get("/expenses/summary")

    assert response.status_code == 401


def test_summary_preserves_two_decimal_places(client, auth_headers):
    _create_expense(client, auth_headers, "Food", "1.20", "2026-09-01")
    _create_expense(client, auth_headers, "Food", "2.00", "2026-09-02")

    response = client.get("/expenses/summary", headers=auth_headers)

    assert response.status_code == 200
    assert response.json()[0]["total"] == "3.20"
