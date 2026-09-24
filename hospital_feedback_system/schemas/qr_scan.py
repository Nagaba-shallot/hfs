from datetime import datetime
from pydantic import BaseModel, ConfigDict

class QRScanRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    qr_scan_id: int
    department: str
    patient_id: int | None = None
    ip_address: str | None = None
    user_agent: str | None = None
    scanned_at: datetime