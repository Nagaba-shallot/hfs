from hospital_feedback_system.models.qr_scan import QR_scan
from sqlalchemy.orm import Session

class QRScanRepository:
    def __init__(self):
        self.model = QR_scan

    def get(self, db:Session, admin_id:int):
        return db.get(QR_scan, admin_id)

    def get_all(self, db:Session):
        return db.query(QR_scan).all()

    def create(self, db:Session, data:dict):
        qr_scan=QR_scan(**data)
        db.add(qr_scan)
        db.commit()
        db.refresh(qr_scan)
        return qr_scan

    def update(self, db:Session, db_obj:QR_scan, data:dict):
        for field, value in data.items():
            setattr(db_obj, field, value)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def delete(self, db:Session, db_obj:QR_scan):
        db.delete(db_obj)
        db.commit()

qr_scan_repository=QRScanRepository()