from tests.helpers import (
    auth_headers,
    bootstrap_super_admin,
    create_category,
    create_department,
    create_question,
    login,
    patient_headers,
    scan_qr,
)


def _create_plain_admin(client, super_admin_headers, email="plain@hospital.example.dev"):
    resp = client.post(
        "/admin",
        json={
            "first_name": "Plain",
            "last_name": "Admin",
            "email": email,
            "password": "another-strong-pw",
            "hospital_name": "Test Hospital",
        },
        headers=super_admin_headers,
    )
    assert resp.status_code == 201, resp.text
    token = login(client, email, "another-strong-pw")
    return auth_headers(token)


def test_replace_survey_requires_super_admin(client):
    headers = bootstrap_super_admin(client)
    plain_headers = _create_plain_admin(client, headers)

    resp = client.post(
        "/feedback-categories/admin/survey/replace",
        json={"categories": []},
        headers=plain_headers,
    )
    assert resp.status_code == 403


def test_replace_survey_works_for_super_admin(client):
    headers = bootstrap_super_admin(client)
    resp = client.post(
        "/feedback-categories/admin/survey/replace",
        json={
            "categories": [
                {
                    "name": "Wait Times",
                    "display_order": 1,
                    "questions": [
                        {"question_text": "How was your wait?", "question_type": "rating"}
                    ],
                }
            ]
        },
        headers=headers,
    )
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["categories_created"] == 1
    assert body["questions_created"] == 1
    assert body["categories_preserved"] == []


def test_replace_survey_never_deletes_a_category_with_real_responses(client):
    headers = bootstrap_super_admin(client)
    department = create_department(client, headers)
    category = create_category(client, headers, name="Staff Courtesy")
    question = create_question(client, headers, category["feedback_category_id"])

    from tests.helpers import get_qr_token

    qr_token = get_qr_token(client, headers, department["department_id"])
    session = scan_qr(client, qr_token)
    resp = client.post(
        "/feedback-responses",
        json={"question_id": question["question_id"], "rating_value": 5},
        headers=patient_headers(session["session_token"]),
    )
    assert resp.status_code == 201, resp.text

    resp = client.post(
        "/feedback-categories/admin/survey/replace",
        json={
            "categories": [
                {
                    "name": "Totally Different Category",
                    "display_order": 1,
                    "questions": [
                        {"question_text": "New question?", "question_type": "rating"}
                    ],
                }
            ]
        },
        headers=headers,
    )
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert "Staff Courtesy" in body["categories_preserved"]

    resp = client.get("/feedback-categories", headers=headers)
    names = [c["name"] for c in resp.json()]
    assert "Staff Courtesy" in names
    assert "Totally Different Category" in names

    resp = client.get(
        f"/feedback-responses?question_id={question['question_id']}", headers=headers
    )
    assert resp.status_code == 200
    assert len(resp.json()) == 1
    assert resp.json()[0]["rating_value"] == 5


def test_deleting_a_category_with_responses_returns_409_not_a_crash(client):
    headers = bootstrap_super_admin(client)
    department = create_department(client, headers)
    category = create_category(client, headers)
    question = create_question(client, headers, category["feedback_category_id"])

    from tests.helpers import get_qr_token

    qr_token = get_qr_token(client, headers, department["department_id"])
    session = scan_qr(client, qr_token)
    client.post(
        "/feedback-responses",
        json={"question_id": question["question_id"], "rating_value": 3},
        headers=patient_headers(session["session_token"]),
    )

    resp = client.delete(
        f"/feedback-categories/{category['feedback_category_id']}", headers=headers
    )
    assert resp.status_code == 409


def test_creating_a_category_with_bogus_department_id_returns_404(client):
    headers = bootstrap_super_admin(client)
    resp = client.post(
        "/feedback-categories",
        json={"name": "Orphan Category", "display_order": 1, "department_id": 999999},
        headers=headers,
    )
    assert resp.status_code == 404


def test_category_name_can_repeat_across_departments(client):
    headers = bootstrap_super_admin(client)
    dept_a = create_department(client, headers, name="Cardiology")
    dept_b = create_department(client, headers, name="Neurology")

    resp_a = client.post(
        "/feedback-categories",
        json={
            "name": "Check-In and Wait Times",
            "display_order": 1,
            "department_id": dept_a["department_id"],
        },
        headers=headers,
    )
    resp_b = client.post(
        "/feedback-categories",
        json={
            "name": "Check-In and Wait Times",
            "display_order": 1,
            "department_id": dept_b["department_id"],
        },
        headers=headers,
    )
    assert resp_a.status_code == 201, resp_a.text
    assert resp_b.status_code == 201, resp_b.text