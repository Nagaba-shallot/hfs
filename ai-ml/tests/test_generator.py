import json
from unittest.mock import patch

import httpx
import pytest

from ai_ml.exceptions import (
    AINotConfiguredError,
    AIProviderError,
    AIResponseFormatError,
    AITimeoutError,
)
from ai_ml.generator import generate_survey_draft


def _fake_gemini_response(categories, status_code=200):
    text = json.dumps({"categories": categories})
    payload = {"candidates": [{"content": {"parts": [{"text": text}]}}]}
    return httpx.Response(
        status_code, json=payload, request=httpx.Request("POST", "https://example.test")
    )


_SAMPLE_CATEGORIES = [
    {
        "name": "Wait Times",
        "display_order": 1,
        "icon": None,
        "questions": [
            {
                "question_text": "How would you rate your wait time?",
                "question_type": "rating",
                "is_required": True,
                "min_rating_label": "Poor",
                "max_rating_label": "Excellent",
            }
        ],
    }
]


def test_missing_api_key_raises_not_configured():
    with pytest.raises(AINotConfiguredError):
        generate_survey_draft("Emergency Room", 3, 3, api_key=None)


def test_successful_generation_returns_parsed_draft():
    with patch("ai_ml.generator.httpx.post") as mock_post:
        mock_post.return_value = _fake_gemini_response(_SAMPLE_CATEGORIES)
        draft = generate_survey_draft("Emergency Room", 1, 1, api_key="fake-key")

    assert draft.categories[0].name == "Wait Times"
    assert draft.categories[0].questions[0].question_type == "rating"


def test_timeout_raises_ai_timeout_error():
    with patch("ai_ml.generator.httpx.post", side_effect=httpx.TimeoutException("slow")):
        with pytest.raises(AITimeoutError):
            generate_survey_draft("Emergency Room", 1, 1, api_key="fake-key")


def test_provider_error_status_propagates():
    request = httpx.Request("POST", "https://example.test")
    error_response = httpx.Response(429, json={"error": "rate limited"}, request=request)
    with patch("ai_ml.generator.httpx.post") as mock_post:
        mock_post.return_value = error_response
        with pytest.raises(AIProviderError) as exc_info:
            generate_survey_draft("Emergency Room", 1, 1, api_key="fake-key")
    assert exc_info.value.status_code == 429


def test_malformed_response_raises_format_error():
    request = httpx.Request("POST", "https://example.test")
    bad_response = httpx.Response(200, json={"unexpected": "shape"}, request=request)
    with patch("ai_ml.generator.httpx.post") as mock_post:
        mock_post.return_value = bad_response
        with pytest.raises(AIResponseFormatError):
            generate_survey_draft("Emergency Room", 1, 1, api_key="fake-key")


def test_custom_model_name_is_used_in_url():
    with patch("ai_ml.generator.httpx.post") as mock_post:
        mock_post.return_value = _fake_gemini_response(_SAMPLE_CATEGORIES)
        generate_survey_draft(
            "Emergency Room", 1, 1, api_key="fake-key", model="gemini-custom-test"
        )
    called_url = mock_post.call_args[0][0]
    assert "gemini-custom-test" in called_url