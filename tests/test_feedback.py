from tests.helpers import (
    bootstrap_super_admin,
    create_category,
    create_department,
    create_question,
    get_qr_token,
    patient_headers,
    scan_qr,
)


def _seed_department_with_one_question(client, headers):
    department = create_department(client, headers)
    token = get_qr_token(client, headers, department["department_id"])
    category = create_category(client, headers)
    question = create_question(client, headers, category["feedback_category_id"])
    return department, token, question


def test_scanning_a_valid_qr_code_issues_a_session(client):
    headers = bootstrap_super_admin(client)
    department = create_department(client, headers)
    token = get_qr_token(client, headers, department["department_id"])

    session = scan_qr(client, token)
    assert "session_token" in session
    assert session["department_visited"] == department["name"]


def test_scanning_an_unknown_qr_code_is_rejected(client):
    resp = client.post("/qr-scan/not-a-real-token")
    assert resp.status_code == 404


def test_scanning_an_inactive_departments_qr_code_is_rejected(client):
    headers = bootstrap_super_admin(client)
    department = create_department(client, headers)
    token = get_qr_token(client, headers, department["department_id"])
    client.patch(
        f"/departments/{department['department_id']}", json={"is_active": False}, headers=headers
    )
    resp = client.post(f"/qr-scan/{token}")
    assert resp.status_code == 404


def test_patient_can_submit_a_rating_answer(client):
    headers = bootstrap_super_admin(client)
    _, qr_token, question = _seed_department_with_one_question(client, headers)
    session = scan_qr(client, qr_token)

    resp = client.post(
        "/feedback-responses",
        json={"question_id": question["question_id"], "rating_value": 5},
        headers=patient_headers(session["session_token"]),
    )
    assert resp.status_code == 201, resp.text
    assert resp.json()["patient_id"] == session["patient_id"]


def test_patient_id_in_request_body_is_ignored_in_favor_of_the_session(client):
    """A patient must never be able to submit feedback as someone else."""
    headers = bootstrap_super_admin(client)
    _, qr_token, question = _seed_department_with_one_question(client, headers)
    session = scan_qr(client, qr_token)

    resp = client.post(
        "/feedback-responses",
        json={"question_id": question["question_id"], "rating_value": 5, "patient_id": 999999},
        headers=patient_headers(session["session_token"]),
    )
    assert resp.status_code == 201
    assert resp.json()["patient_id"] == session["patient_id"]
    assert resp.json()["patient_id"] != 999999


def test_feedback_endpoints_require_a_session_token(client):
    resp = client.post("/feedback-responses", json={"question_id": 1, "rating_value": 5})
    assert resp.status_code == 401


def test_rating_out_of_range_is_rejected(client):
    headers = bootstrap_super_admin(client)
    _, qr_token, question = _seed_department_with_one_question(client, headers)
    session = scan_qr(client, qr_token)

    resp = client.post(
        "/feedback-responses",
        json={"question_id": question["question_id"], "rating_value": 99},
        headers=patient_headers(session["session_token"]),
    )
    assert resp.status_code == 422


def test_wrong_answer_field_for_question_type_is_rejected(client):
    headers = bootstrap_super_admin(client)
    _, qr_token, question = _seed_department_with_one_question(client, headers)  # rating question
    session = scan_qr(client, qr_token)

    resp = client.post(
        "/feedback-responses",
        json={"question_id": question["question_id"], "text_response": "great!"},
        headers=patient_headers(session["session_token"]),
    )
    assert resp.status_code == 422


def test_answering_twice_updates_rather_than_duplicates(client):
    headers = bootstrap_super_admin(client)
    _, qr_token, question = _seed_department_with_one_question(client, headers)
    session = scan_qr(client, qr_token)
    ph = patient_headers(session["session_token"])

    client.post(
        "/feedback-responses",
        json={"question_id": question["question_id"], "rating_value": 2},
        headers=ph,
    )
    client.post(
        "/feedback-responses",
        json={"question_id": question["question_id"], "rating_value": 4},
        headers=ph,
    )

    resp = client.get("/feedback-responses/me", headers=ph)
    answers = resp.json()
    assert len(answers) == 1
    assert answers[0]["rating_value"] == 4


def test_survey_progress_completes_after_all_required_questions_answered(client):
    headers = bootstrap_super_admin(client)
    _, qr_token, question = _seed_department_with_one_question(client, headers)
    session = scan_qr(client, qr_token)
    ph = patient_headers(session["session_token"])

    progress = client.get("/survey-progress/me", headers=ph).json()
    assert progress["is_completed"] is False

    client.post(
        "/feedback-responses",
        json={"question_id": question["question_id"], "rating_value": 5},
        headers=ph,
    )

    progress = client.get("/survey-progress/me", headers=ph).json()
    assert progress["is_completed"] is True
    assert progress["total_questions_answered"] == 1


def test_a_patient_cannot_read_another_patients_progress_or_answers(client):
    """There is no ``/survey-progress/{id}`` or ``/feedback-responses?patient_id=``
    reachable with a patient session — those require an admin token."""
    headers = bootstrap_super_admin(client)
    department = create_department(client, headers)
    token = get_qr_token(client, headers, department["department_id"])
    victim_session = scan_qr(client, token)

    resp = client.get(f"/survey-progress/{victim_session['patient_id']}")
    assert resp.status_code == 401

    resp = client.get(f"/feedback-responses?patient_id={victim_session['patient_id']}")
    assert resp.status_code == 401


def test_admin_can_reply_to_feedback_and_reply_records_the_authenticated_admin(client):
    headers = bootstrap_super_admin(client)
    _, qr_token, question = _seed_department_with_one_question(client, headers)
    session = scan_qr(client, qr_token)
    response = client.post(
        "/feedback-responses",
        json={"question_id": question["question_id"], "rating_value": 1},
        headers=patient_headers(session["session_token"]),
    ).json()

    resp = client.post(
        "/admin-replies",
        json={
            "feedback_response_id": response["feedback_response_id"],
            "reply_text": "Sorry to hear that — we'll follow up.",
        },
        headers=headers,
    )
    assert resp.status_code == 201, resp.text
    me = client.get("/admins/me", headers=headers).json()
    assert resp.json()["admin_id"] == me["admin_id"]


def test_qr_scan_is_rate_limited(client, monkeypatch):
    from hospital_feedback_system.core.rate_limit import qr_scan_limiter

    monkeypatch.setattr(qr_scan_limiter, "max_calls", 2)

    for _ in range(2):
        client.post("/qr-scan/nonexistent")  
    resp = client.post("/qr-scan/nonexistent")
    assert resp.status_code == 429