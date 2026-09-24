from sqlalchemy.orm import Session

from hospital_feedback_system.models.feedback_category import Feedback_category
from hospital_feedback_system.models.feedback_response import Feedback_response
from hospital_feedback_system.models.question import Questions
from hospital_feedback_system.models.survey_progress import Survey_progress
from hospital_feedback_system.core.survey_rules import survey_position


def get_or_create(db: Session, patient_id: int) -> Survey_progress:
    progress = db.query(Survey_progress).filter_by(patient_id=patient_id).first()
    if progress is None:
        progress = Survey_progress(patient_id=patient_id)
        db.add(progress)
        db.commit()
        db.refresh(progress)
    return progress


def recompute(db: Session, patient_id: int) -> Survey_progress:
    progress = get_or_create(db, patient_id)

    categories = db.query(Feedback_category.feedback_category_id, Feedback_category.display_order).all()
    questions = db.query(
        Questions.question_id, Questions.feedback_category_id, Questions.is_required
    ).all()
    answered_ids = [
        row[0]
        for row in db.query(Feedback_response.question_id).filter_by(patient_id=patient_id).all()
    ]

    current_order, missing_required = survey_position(categories, questions, answered_ids)

    progress.current_feedback_category_order = current_order
    progress.total_questions_answered = len(set(answered_ids))
    was_completed = progress.is_completed
    progress.is_completed = len(questions) > 0 and not missing_required
    if progress.is_completed and not was_completed:
        from sqlalchemy.sql import func

        progress.completed_at = func.now()

    db.commit()
    db.refresh(progress)
    return progress