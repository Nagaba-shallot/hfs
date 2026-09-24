def register_first_admin(client, email="owner@hospital.example.dev", password="a-very-strong-pw"):
    resp = client.post(
        "/auth/register",
        json={
            "first_name": "Owner",
            "last_name": "Admin",
            "email": email,
            "password": password,
            "hospital_name": "Test Hospital",
        },
    )
    assert resp.status_code == 201, resp.text
    return resp.json()


def login(client, email="owner@hospital.example.dev", password="a-very-strong-pw"):
    resp = client.post("/auth/login", data={"username": email, "password": password})
    assert resp.status_code == 200, resp.text
    return resp.json()["access_token"]


def auth_headers(token):
    return {"Authorization": f"Bearer {token}"}


def bootstrap_super_admin(client):
    register_first_admin(client)
    token = login(client)
    return auth_headers(token)


def create_department(client, admin_headers, name="Cardiology"):
    resp = client.post("/departments", json={"name": name}, headers=admin_headers)
    assert resp.status_code == 201, resp.text
    return resp.json()


def get_qr_token(client, admin_headers, department_id):
    resp = client.get(f"/departments/{department_id}/qr-token", headers=admin_headers)
    assert resp.status_code == 200, resp.text
    return resp.json()["qr_code_token"]


def scan_qr(client, qr_code_token):
    resp = client.post(f"/qr-scan/{qr_code_token}")
    assert resp.status_code == 200, resp.text
    return resp.json()


def patient_headers(session_token):
    return {"X-Session-Token": session_token}


def create_category(client, admin_headers, name="Care Quality", display_order=1):
    resp = client.post(
        "/feedback-categories",
        json={"name": name, "display_order": display_order},
        headers=admin_headers,
    )
    assert resp.status_code == 201, resp.text
    return resp.json()


def create_question(
    client,
    admin_headers,
    feedback_category_id,
    question_text="How was your visit?",
    question_type="rating",
    order_in_feedback_category=1,
):
    resp = client.post(
        "/questions",
        json={
            "feedback_category_id": feedback_category_id,
            "question_text": question_text,
            "question_type": question_type,
            "order_in_feedback_category": order_in_feedback_category,
        },
        headers=admin_headers,
    )
    assert resp.status_code == 201, resp.text
    return resp.json()