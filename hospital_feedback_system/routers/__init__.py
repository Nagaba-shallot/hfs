from hospital_feedback_system.routers.admin import router as admin_router
from hospital_feedback_system.routers.admin_reply import router as admin_reply_router
from hospital_feedback_system.routers.auth import router as auth_router
from hospital_feedback_system.routers.department import router as department_router
from hospital_feedback_system.routers.feedback_category import router as feedback_category_router
from hospital_feedback_system.routers.feedback_response import router as feedback_response_router
from hospital_feedback_system.routers.patients import router as patients_router
from hospital_feedback_system.routers.qr_scan import router as qr_scan_router
from hospital_feedback_system.routers.question import router as question_router
from hospital_feedback_system.routers.survey_progress import router as survey_progress_router

all_routers = [
    auth_router,
    admin_router,
    admin_reply_router,
    department_router,
    feedback_category_router,
    feedback_response_router,
    patients_router,
    qr_scan_router,
    question_router,
    survey_progress_router,
]

__all__ = [
    "all_routers",
    "auth_router",
    "admin_router",
    "admin_reply_router",
    "department_router",
    "feedback_category_router",
    "feedback_response_router",
    "patients_router",
    "qr_scan_router",
    "question_router",
    "survey_progress_router",
]