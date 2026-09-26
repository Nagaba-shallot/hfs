from unittest.mock import patch

from ai_ml.exceptions import (
    AINotConfiguredError,
    AIProviderError,
    AIResponseFormatError,
    AITimeoutError,
)
from ai_ml.schemas import DraftCategory, DraftQuestion, SurveyDraft

from tests.helpers import bootstrap_super_admin

_SAMPLE_DRAFT = SurveyDraft(
    categories=[
        DraftCategory(
            name="Wait Times",
            display_order=1,
            questions=[
                DraftQuestion(
                    question_text="How would you rate your wait time?",
                    question_type="rating",
                    is_required=True,
                    min_rating_label="Poor",
                    max_rating_label="Excellent",
                )
            ],
        )
    ]
)


def test_generate_survey_requires_admin_token(client):
    resp = client.post("/ai/generate-survey", json={"focus": "Emergency Room"})
    assert resp.status_code == 401


def test_generate_survey_happy_path_returns_draft(client):
    headers = bootstrap_super_admin(client)
    with patch(
        "hospital_feedback_system.ai.router.generate_survey_draft", return_value=_SAMPLE_DRAFT
    ):
        resp = client.post(
            "/ai/generate-survey", json={"focus": "Emergency Room"}, headers=headers
        )
    assert resp.status_code == 200, resp.text
    assert resp.json()["categories"][0]["name"] == "Wait Times"


def test_not_configured_maps_to_503(client):
    headers = bootstrap_super_admin(client)
    with patch(
        "hospital_feedback_system.ai.router.generate_survey_draft",
        side_effect=AINotConfiguredError("no key"),
    ):
        resp = client.post(
            "/ai/generate-survey", json={"focus": "Emergency Room"}, headers=headers
        )
    assert resp.status_code == 503


def test_timeout_maps_to_504(client):
    headers = bootstrap_super_admin(client)
    with patch(
        "hospital_feedback_system.ai.router.generate_survey_draft",
        side_effect=AITimeoutError("slow"),
    ):
        resp = client.post(
            "/ai/generate-survey", json={"focus": "Emergency Room"}, headers=headers
        )
    assert resp.status_code == 504


def test_provider_error_maps_to_502(client):
    headers = bootstrap_super_admin(client)
    with patch(
        "hospital_feedback_system.ai.router.generate_survey_draft",
        side_effect=AIProviderError("bad gateway", status_code=500),
    ):
        resp = client.post(
            "/ai/generate-survey", json={"focus": "Emergency Room"}, headers=headers
        )
    assert resp.status_code == 502


def test_malformed_response_maps_to_502(client):
    headers = bootstrap_super_admin(client)
    with patch(
        "hospital_feedback_system.ai.router.generate_survey_draft",
        side_effect=AIResponseFormatError("bad shape"),
    ):
        resp = client.post(
            "/ai/generate-survey", json={"focus": "Emergency Room"}, headers=headers
        )
    assert resp.status_code == 502


def test_generate_survey_is_rate_limited(client, monkeypatch):
    headers = bootstrap_super_admin(client)
    from hospital_feedback_system.core.rate_limit import ai_generate_limiter

    monkeypatch.setattr(ai_generate_limiter, "max_calls", 1)

    with patch(
        "hospital_feedback_system.ai.router.generate_survey_draft",
        return_value=_SAMPLE_DRAFT,
    ):
        client.post("/ai/generate-survey", json={"focus": "Emergency Room"}, headers=headers)
        resp = client.post(
            "/ai/generate-survey", json={"focus": "Emergency Room"}, headers=headers
        )
    assert resp.status_code == 429


def test_generate_survey_rejects_out_of_range_counts(client):
    headers = bootstrap_super_admin(client)
    resp = client.post(
        "/ai/generate-survey",
        json={"focus": "Emergency Room", "num_categories": 99},
        headers=headers,
    )
    assert resp.status_code == 422