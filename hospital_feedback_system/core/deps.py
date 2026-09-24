from collections.abc import Callable, Generator

import jwt
from fastapi import Depends, Header, HTTPException, Request, status
from sqlalchemy.orm import Session

from hospital_feedback_system.core.constants import Role, SESSION_HEADER_NAME
from hospital_feedback_system.core.security import decode_access_token, hash_session_token
from hospital_feedback_system.database import get_db
from hospital_feedback_system.models.admin import Admin
from hospital_feedback_system.models.patients import Patients
from hospital_feedback_system.repositories.admin import admin_repository

_bearer_error = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Invalid or expired token",
    headers={"WWW-Authenticate": "Bearer"},
)


def _extract_bearer_token(request: Request) -> str:
    header = request.headers.get("Authorization")
    if not header or not header.lower().startswith("bearer "):
        raise _bearer_error
    return header[len("bearer "):].strip()


def get_current_admin(
    request: Request,
    db: Session = Depends(get_db),
) -> Admin:
    token = _extract_bearer_token(request)
    try:
        payload = decode_access_token(token)
    except jwt.PyJWTError:
        raise _bearer_error

    sub = payload.get("sub")
    if not sub:
        raise _bearer_error
    try:
        admin_id = int(sub)
    except (TypeError, ValueError):
        raise _bearer_error

    admin = admin_repository.get(db, admin_id)
    if admin is None:
        raise _bearer_error
    if not admin.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Inactive admin")
    return admin


def require_role(*allowed_roles: Role) -> Callable[[Admin], Admin]:
    def _checker(admin: Admin = Depends(get_current_admin)) -> Admin:
        if admin.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to perform this action",
            )
        return admin

    return _checker


def get_current_patient(
    db: Session = Depends(get_db),
    x_session_token: str | None = Header(default=None, alias=SESSION_HEADER_NAME),
) -> Patients:
    unauthorized = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Missing or invalid session token",
        headers={"WWW-Authenticate": f'Bearer realm="patient", header="{SESSION_HEADER_NAME}"'},
    )
    if not x_session_token:
        raise unauthorized

    token_hash = hash_session_token(x_session_token)
    patient = db.query(Patients).filter_by(session_token=token_hash).first()
    if patient is None:
        raise unauthorized
    return patient