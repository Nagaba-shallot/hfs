from datetime import datetime
from hospital_feedback_system.database import Base
from sqlalchemy import Column, String, Integer, Boolean, DateTime
from sqlalchemy.sql import func


class Department(Base):
    __tablename__ = "department"

    department_id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    qr_code_token = Column(String, nullable=False, unique=True)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())