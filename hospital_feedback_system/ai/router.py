from ai_ml.exceptions import (
    AINotConfiguredError,
    AIProviderError,
    AIResponseFormatError,
    AITimeoutError,
)
from ai_ml.generator import generate_survey_draft
from ai_ml.schemas import SurveyDraft, SurveyGenerateRequest
from fastapi import APIRouter, Depends, HTTPException, status

from hospital_feedback_system.config import settings
from hospital_feedback_system.core.deps import get_current_admin
from hospital_feedback_system.core.rate_limit import ai_generate_limiter
from hospital_feedback_system.models.admin import Admin

router = APIRouter(prefix="/ai", tags=["ai"])


@router.post("/generate-survey", response_model=SurveyDraft)
def generate_survey(
    data: SurveyGenerateRequest,
    admin: Admin = Depends(get_current_admin),
    _rate_limited: None = Depends(ai_generate_limiter),
):
    """Returns a draft only — nothing is saved. The admin reviews it and
    creates whatever they want via POST /feedback-categories and
    POST /questions."""
    try:
        return generate_survey_draft(
            data.focus,
            data.num_categories,
            data.questions_per_category,
            api_key=settings.GEMINI_API_KEY,
            model=settings.GEMINI_MODEL,
        )
    except AINotConfiguredError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI survey generation isn't configured (GEMINI_API_KEY is unset).",
        )
    except AITimeoutError:
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="AI generation timed out. Please try again.",
        )
    except (AIProviderError, AIResponseFormatError) as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc))