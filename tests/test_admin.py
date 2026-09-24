from tests.helpers import (
    auth_headers,
    bootstrap_super_admin,
    create_department,
    login,
    register_first_admin,
)


def test_first_admin_can_register_without_a_token(client):
    admin = register_first_admin(client)
    assert admin["role"] == "super_admin"
    assert "password" not in admin  


def test_login_returns_a_bearer_jwt(client):
    register_first_admin(client)
    token = login(client)
    assert isinstance(token, str) and token.count(".") == 2  


def test_login_rejects_wrong_password(client):
    register_first_admin(client)
    resp = client.post(
        "/auth/login", data={"username": "owner@hospital.example.dev", "password": "wrong-password"}
    )
    assert resp.status_code == 401


def test_login_rejects_unknown_email_with_same_status_as_wrong_password(client):
    register_first_admin(client)
    resp = client.post(
        "/auth/login", data={"username": "nobody@hospital.example.dev", "password": "whatever12345"}
    )
    assert resp.status_code == 401
    assert resp.json()["detail"] == "Incorrect email or password"


def test_registration_is_closed_once_an_admin_exists(client):
    register_first_admin(client)
    resp = client.post(
        "/auth/register",
        json={
            "first_name": "Second",
            "last_name": "Admin",
            "email": "second@hospital.example.dev",
            "password": "another-strong-pw",
            "hospital_name": "Test Hospital",
        },
    )
    assert resp.status_code == 403


def test_super_admin_can_create_further_admins_via_admins_endpoint(client):
    headers = bootstrap_super_admin(client)
    resp = client.post(
        "/admin",
        json={
            "first_name": "Second",
            "last_name": "Admin",
            "email": "second@hospital.example.dev",
            "password": "another-strong-pw",
            "hospital_name": "Test Hospital",
        },
        headers=headers,
    )
    assert resp.status_code == 201, resp.text
    assert resp.json()["role"] == "admin"  


def test_plain_admin_cannot_create_further_admins(client):
    headers = bootstrap_super_admin(client)
    client.post(
        "/admin",
        json={
            "first_name": "Plain",
            "last_name": "Admin",
            "email": "plain@hospital.example.dev",
            "password": "another-strong-pw",
            "hospital_name": "Test Hospital",
        },
        headers=headers,
    )
    plain_token = login(client, "plain@hospital.example.dev", "another-strong-pw")
    resp = client.post(
        "/admin",
        json={
            "first_name": "X",
            "last_name": "Y",
            "email": "third@hospital.example.dev",
            "password": "another-strong-pw",
            "hospital_name": "Test Hospital",
        },
        headers=auth_headers(plain_token),
    )
    assert resp.status_code == 403


def test_admin_endpoints_reject_missing_token(client):
    resp = client.get("/admin")
    assert resp.status_code == 401


def test_admin_endpoints_reject_garbage_token(client):
    resp = client.get("/admin", headers=auth_headers("not-a-real-token"))
    assert resp.status_code == 401


def test_write_endpoints_reject_patients_and_public_callers(client):
    """Every mutating admin endpoint must require a valid admin token."""
    resp = client.post("/departments", json={"name": "Radiology"})
    assert resp.status_code == 401

    resp = client.post(
        "/feedback-categories", json={"name": "Cleanliness", "display_order": 1}
    )
    assert resp.status_code == 401

    resp = client.post(
        "/questions",
        json={
            "feedback_category_id": 1,
            "question_text": "?",
            "question_type": "rating",
            "order_in_feedback_category": 1,
        },
    )
    assert resp.status_code == 401


def test_admin_cannot_delete_their_own_account(client):
    headers = bootstrap_super_admin(client)
    me = client.get("/admin/me", headers=headers).json()
    resp = client.delete(f"/admin/{me['admin_id']}", headers=headers)
    assert resp.status_code == 400


def test_qr_token_is_never_exposed_on_public_department_listing(client):
    headers = bootstrap_super_admin(client)
    create_department(client, headers, "Cardiology")
    resp = client.get("/departments")
    assert resp.status_code == 200
    assert "qr_code_token" not in resp.json()[0]