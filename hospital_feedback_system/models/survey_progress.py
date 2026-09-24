from datetime import datetime
from hospital_feedback_system.database import Base
from sqlalchemy import Column, Integer, Boolean, ForeignKey, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship


class Survey_progress(Base):
    __tablename__ = "survey_progress"

    survey_progress_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    patient_id = Column(
        Integer,
        ForeignKey("patients.patient_id"),         
        nullable=False,
        unique=True,
    )
    current_feedback_category_order = Column(Integer, nullable=False, default=1)
    is_completed = Column(Boolean, nullable=False, default=False)
    total_questions_answered = Column(Integer, nullable=False, default=0)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    last_activity_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    Patients = relationship("Patients", back_populates="survey_progress")