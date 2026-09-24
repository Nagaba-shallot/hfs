from hospital_feedback_system.core.security import generate_qr_token
from hospital_feedback_system.database import Base, SessionLocal, engine
from hospital_feedback_system.models.department import Department
from hospital_feedback_system.models.feedback_category import Feedback_category
from hospital_feedback_system.models.question import Questions

DEPARTMENTS = ["Cardiology", "Emergency", "Outpatient Clinic", "Maternity"]

CATEGORIES_WITH_QUESTIONS = [
    {
        "name": "Waiting Experience",
        "display_order": 1,
        "questions": [
            ("How long did you wait to be seen?", "rating", "Very long", "Very short"),
            ("Was the waiting area comfortable?", "yes_no", None, None),
        ],
    },
    {
        "name": "Staff & Care",
        "display_order": 2,
        "questions": [
            ("How would you rate the staff's care and attentiveness?", "rating", "Poor", "Excellent"),
            ("Anything you'd like staff to know?", "text", None, None),
        ],
    },
    {
        "name": "Cleanliness",
        "display_order": 3,
        "questions": [
            ("How clean was the facility?", "rating", "Poor", "Excellent"),
        ],
    },
]


def main() -> None:
    Base.metadata.create_all(bind=engine)  
    db = SessionLocal()
    try:
        for name in DEPARTMENTS:
            if db.query(Department).filter_by(name=name).first():
                continue
            db.add(Department(name=name, qr_code_token=generate_qr_token(), is_active=True))
        db.commit()

        for cat_data in CATEGORIES_WITH_QUESTIONS:
            category = db.query(Feedback_category).filter_by(name=cat_data["name"]).first()
            if category is None:
                category = Feedback_category(
                    name=cat_data["name"], display_order=cat_data["display_order"]
                )
                db.add(category)
                db.commit()
                db.refresh(category)

            for order, (text, qtype, min_label, max_label) in enumerate(
                cat_data["questions"], start=1
            ):
                exists = (
                    db.query(Questions)
                    .filter_by(feedback_category_id=category.feedback_category_id, question_text=text)
                    .first()
                )
                if exists:
                    continue
                db.add(
                    Questions(
                        feedback_category_id=category.feedback_category_id,
                        question_text=text,
                        question_type=qtype,
                        order_in_feedback_category=order,
                        is_required=True,
                        min_rating_label=min_label,
                        max_rating_label=max_label,
                    )
                )
        db.commit()

        print(f"Seeded {len(DEPARTMENTS)} departments and "
              f"{len(CATEGORIES_WITH_QUESTIONS)} feedback categories.")
        print("Note: no admin account is seeded — POST /auth/register to create one.")
    finally:
        db.close()


if __name__ == "__main__":
    main()