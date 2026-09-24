from hospital_feedback_system.database import Base
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    Text,
    UniqueConstraint,
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship


class Feedback_response(Base):
    __tablename__ = "feedback_response"
    __table_args__ = (
        UniqueConstraint(
            "patient_id", "question_id", name="uq_feedback_response_patient_question"
        ),
    )

    feedback_response_id = Column(
        Integer, primary_key=True, index=True, autoincrement=True
    )
    patient_id = Column(Integer, ForeignKey("patients.patient_id"), nullable=False)
    question_id = Column(Integer, ForeignKey("questions.question_id"), nullable=False)
    rating_value = Column(Integer, nullable=True)
    text_response = Column(Text, nullable=True)
    yes_no_value = Column(Boolean, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    admin_reply = relationship("Admin_reply", back_populates="feedback_response")