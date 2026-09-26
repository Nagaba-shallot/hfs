import json

import httpx

from ai_ml.exceptions import (
    AINotConfiguredError,
    AIProviderError,
    AIResponseFormatError,
    AITimeoutError,
)
from ai_ml.schemas import (
    QUESTION_TYPE_RATING,
    QUESTION_TYPE_TEXT,
    QUESTION_TYPE_YES_NO,
    SurveyDraft,
)

_GEMINI_URL_TEMPLATE = (
    "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
)

_SYSTEM_PROMPT = """You write patient-experience survey questions for a hospital \
feedback system. You are given a focus area and must produce categories of \
questions about the SERVICE experience only.

Allowed topics: wait times, staff courtesy and communication, cleanliness, \
facility comfort, ease of check-in/scheduling, clarity of information given, \
and similar service-quality topics.

STRICTLY FORBIDDEN, even if the focus area seems to invite it: questions about \
symptoms, diagnoses, medications, treatment decisions, test results, mental \
health status, or any other clinical/medical content. Do not ask for names, \
contact details, or any other personally identifying information.

If the requested focus area is clinical in nature (e.g. "pain levels" or \
"medication side effects"), reinterpret it as the closest legitimate service \
topic (e.g. how clearly staff explained the treatment plan) rather than \
refusing outright.

Respond with JSON only, matching the provided schema exactly."""

_RESPONSE_SCHEMA = {
    "type": "OBJECT",
    "properties": {
        "categories": {
            "type": "ARRAY",
            "items": {
                "type": "OBJECT",
                "properties": {
                    "name": {"type": "STRING"},
                    "display_order": {"type": "INTEGER"},
                    "icon": {"type": "STRING", "nullable": True},
                    "questions": {
                        "type": "ARRAY",
                        "items": {
                            "type": "OBJECT",
                            "properties": {
                                "question_text": {"type": "STRING"},
                                "question_type": {
                                    "type": "STRING",
                                    "enum": [
                                        QUESTION_TYPE_RATING,
                                        QUESTION_TYPE_TEXT,
                                        QUESTION_TYPE_YES_NO,
                                    ],
                                },
                                "is_required": {"type": "BOOLEAN"},
                                "min_rating_label": {"type": "STRING", "nullable": True},
                                "max_rating_label": {"type": "STRING", "nullable": True},
                            },
                            "required": ["question_text", "question_type", "is_required"],
                        },
                    },
                },
                "required": ["name", "display_order", "questions"],
            },
        }
    },
    "required": ["categories"],
}

DEFAULT_MODEL = "gemini-2-5-flash-lite"


def generate_survey_draft(
    focus: str,
    num_categories: int,
    questions_per_category: int,
    api_key: str | None,
    model: str = DEFAULT_MODEL,
) -> SurveyDraft:
    if not api_key:
        raise AINotConfiguredError("No Gemini API key was provided.")

    user_prompt = (
        f"Focus area: {focus}\n"
        f"Produce exactly {num_categories} categories, each with exactly "
        f"{questions_per_category} questions. Use display_order starting at 1. "
        f"Prefer question_type 'rating' for most questions; use 'yes_no' for a "
        f"simple factual check and 'text' for at most one open-ended question "
        f"per category. For 'rating' questions, set min_rating_label and "
        f"max_rating_label (e.g. 'Poor' / 'Excellent')."
    )

    url = _GEMINI_URL_TEMPLATE.format(model=model)
    body = {
        "system_instruction": {"parts": [{"text": _SYSTEM_PROMPT}]},
        "contents": [{"parts": [{"text": user_prompt}]}],
        "generationConfig": {
            "responseMimeType": "application/json",
            "responseSchema": _RESPONSE_SCHEMA,
            "temperature": 0.6,
        },
    }

    try:
        response = httpx.post(
            url,
            headers={"x-goog-api-key": api_key},
            json=body,
            timeout=120.0,
        )
        response.raise_for_status()
    except httpx.TimeoutException:
        raise AITimeoutError("Gemini didn't respond in time.")
    except httpx.HTTPStatusError as exc:
        raise AIProviderError(
            f"Gemini returned an error ({exc.response.status_code}).",
            status_code=exc.response.status_code,
        )
    except httpx.RequestError as exc:
        raise AIProviderError(f"Couldn't reach Gemini: {exc}")

    try:
        payload = response.json()
        raw_text = payload["candidates"][0]["content"]["parts"][0]["text"]
        parsed = json.loads(raw_text)
        return SurveyDraft.model_validate(parsed)
    except (KeyError, IndexError, json.JSONDecodeError, ValueError) as exc:
        raise AIResponseFormatError(f"Gemini's response wasn't in the expected shape: {exc}")