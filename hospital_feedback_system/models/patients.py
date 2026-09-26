from datetime import datetime
from hospital_feedback_system.database import Base
from sqlalchemy import Column, String, Boolean, Date, Integer, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship


class Patients(Base):
    __tablename__ = "patients"

    patient_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    session_token = Column(String, nullable=False, unique=True)
    phone_number = Column(String, nullable=True, default=None)
    department_visited = Column(String, nullable=False)
    department_id = Column(Integer, ForeignKey("department.department_id"), nullable=True)
    visit_date = Column(Date, nullable=True, default=None)       
    is_anonymous = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    qr_scan = relationship("QR_scan", back_populates="Patients")
    survey_progress = relationship("Survey_progress", back_populates="Patients")