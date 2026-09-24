from datetime import datetime
from pydantic import BaseModel, ConfigDict


class DepartmentCreate(BaseModel):
    name: str
    is_active: bool = True


class DepartmentUpdate(BaseModel):
    name: str | None = None
    is_active: bool | None = None


class DepartmentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    department_id: int
    name: str
    is_active: bool
    created_at: datetime

class DepartmentQRToken(BaseModel):
    department_id: int
    qr_code_token: str
    scan_url_path: str