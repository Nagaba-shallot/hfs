import os

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

_private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
_private_pem = _private_key.private_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PrivateFormat.PKCS8,
    encryption_algorithm=serialization.NoEncryption(),
).decode()
_public_pem = (
    _private_key.public_key()
    .public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    .decode()
)

os.environ["ENVIRONMENT"] = "test"
os.environ["DATABASE_URL"] = "sqlite:///./test_hfs.db"
os.environ["PRIVATE_KEY"] = _private_pem
os.environ["PUBLIC_KEY"] = _public_pem
os.environ["ALGORITHM"] = "RS256"
os.environ["ACCESS_TOKEN_EXPIRE_MINUTES"] = "30"
os.environ["BCRYPT_ROUNDS"] = "4"  
os.environ["LOGIN_RATE_LIMIT"] = "1000"
os.environ["QR_SCAN_RATE_LIMIT"] = "1000"
os.environ["ALLOWED_ORIGINS"] = "http://localhost:5173"

import pytest  
from fastapi.testclient import TestClient  
from sqlalchemy import create_engine  
from sqlalchemy.orm import sessionmaker  

from hospital_feedback_system import models  
from hospital_feedback_system.core.rate_limit import reset_all_limiters
from hospital_feedback_system.database import Base, get_db  
from hospital_feedback_system.main import app 

TEST_DB_PATH = "./test_hfs.db"
engine = create_engine(f"sqlite:///{TEST_DB_PATH}", connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def _override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = _override_get_db


@pytest.fixture(autouse=True)
def _fresh_database():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    reset_all_limiters()
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c