from hospital_feedback_system.models.admin_reply import Admin_reply
from hospital_feedback_system.models.admin import Admin
from hospital_feedback_system.models.department import Department
from hospital_feedback_system.models.feedback_category import Feedback_category
from hospital_feedback_system.models.feedback_response import Feedback_response
from hospital_feedback_system.models.patients import Patients
from hospital_feedback_system.models.qr_scan import QR_scan
from hospital_feedback_system.models.question import Questions
from hospital_feedback_system.models.survey_progress import Survey_progress




__all__ = [
    "Patients",
    "Feedback_category",
    "Questions",
    "Feedback_response",
    "Survey_progress",
    "Admin",
    "Admin_reply",
    "QR_scan",
    "Department",
]