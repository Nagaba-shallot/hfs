import jwt
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from hospital_feedback_system.core.constants import ROLE_SUPER_ADMIN
from hospital_feedback_system.core.deps import get_current_admin
from hospital_feedback_system.core.rate_limit import login_limiter
from hospital_feedback_system.core.security import (
    burn_password_check,
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)
from hospital_feedback_system.config import settings
from hospital_feedback_system.database import get_db
from hospital_feedback_system.models.admin import Admin
from hospital_feedback_system.repositories.admin import admin_repository
from hospital_feedback_system.schemas.admin import AdminCreate, AdminRead, Token

router = APIRouter(prefix="/auth", tags=["auth"])


def _require_super_admin_if_any_admin_exists(request: Request, db: Session) -> None:
    if db.query(Admin).count() == 0:
        return

    header = request.headers.get("Authorization", "")
    if not header.lower().startswith("bearer "):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Registration is closed. A super_admin must create your account "
            "via POST /admin.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = header[len("bearer "):].strip()
    try:
        payload = decode_access_token(token)
        admin = db.get(Admin, int(payload["sub"]))
    except (jwt.PyJWTError, ValueError, KeyError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token"
        )
    if admin is None or not admin.is_active or admin.role != ROLE_SUPER_ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only a super_admin can register new admins once accounts exist. "
            "Use POST /admin instead.",
        )


@router.post("/register", response_model=AdminRead, status_code=status.HTTP_201_CREATED)
def register(data: AdminCreate, request: Request, db: Session = Depends(get_db)):
    _require_super_admin_if_any_admin_exists(request, db)

    existing = db.query(Admin).filter_by(email=data.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered"
        )

    is_first_admin = db.query(Admin).count() == 0
    values = data.model_dump()
    values["password"] = hash_password(values.pop("password"))
    values["role"] = ROLE_SUPER_ADMIN if is_first_admin else "admin"
    values["is_active"] = True
    return admin_repository.create(db, values)


@router.post("/login", response_model=Token)
def login(
    form: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
    _rate_limited: None = Depends(login_limiter),
):
    admin = db.query(Admin).filter_by(email=form.username).first()
    if admin is None:
        burn_password_check(form.password)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not verify_password(form.password, admin.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not admin.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Inactive admin")

    from sqlalchemy.sql import func

    admin.last_login = func.now()
    db.commit()

    token = create_access_token(
        subject=admin.admin_id,
        extra={"role": admin.role, "tv": admin.token_version},
    )
    return Token(access_token=token, expires_in_minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)


@router.get("/me", response_model=AdminRead)
def read_me(admin: Admin = Depends(get_current_admin)):
    return admin