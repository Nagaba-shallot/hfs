from datetime import datetime
from hospital_feedback_system.database import Base
from sqlalchemy import Column, String, Integer, ForeignKey, Text, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship


class QR_scan(Base):
    __tablename__ = "qr_scan"

    qr_scan_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    qr_code_token = Column(String, nullable=False)
    department = Column(String, nullable=False)
    patient_id = Column(
        Integer,
        ForeignKey("patients.patient_id"),          
        nullable=True,
        default=None,
    )
    ip_address = Column(String(45), nullable=True, default=None)  
    user_agent = Column(Text, nullable=True, default=None)
    scanned_at = Column(DateTime(timezone=True), server_default=func.now())

    Patients = relationship("Patients", back_populates="qr_scan")