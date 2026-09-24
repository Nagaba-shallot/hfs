from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, field_validator, model_validator

from hospital_feedback_system.core.constants import MAX_PASSWORD_BYTES, MIN_PASSWORD_LENGTH


def _validate_password(value: str) -> str:
    if len(value) < MIN_PASSWORD_LENGTH:
        raise ValueError(f"password must be at least {MIN_PASSWORD_LENGTH} characters")
    if len(value.encode("utf-8")) > MAX_PASSWORD_BYTES:
        raise ValueError(f"password must be at most {MAX_PASSWORD_BYTES} bytes")
    return value


class AdminCreate(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    password: str
    hospital_name: str

    _validate = field_validator("password")(_validate_password)


class AdminSelfUpdate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    hospital_name: str | None = None
    password: str | None = None

    @model_validator(mode="after")
    def _validate_password_if_set(self):
        if self.password is not None:
            _validate_password(self.password)
        return self


class AdminUpdate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    hospital_name: str | None = None
    role: str | None = None
    is_active: bool | None = None


class AdminRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    admin_id: int
    first_name: str
    last_name: str
    email: str
    hospital_name: str
    role: str
    is_active: bool
    created_at: datetime
    last_login: datetime | None = None


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in_minutes: int

class AdminPasswordChange(BaseModel):
    current_password: str
    new_password: str

    @field_validator("new_password")
    @classmethod
    def check_new_password(cls, v: str) -> str:
        if len(v) < 12:
            raise ValueError("Password must be at least 12 characters")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        if not any(not c.isalnum() for c in v):
            raise ValueError("Password must contain at least one symbol")
        return v