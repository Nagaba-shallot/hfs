from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware

from hospital_feedback_system import models  
from hospital_feedback_system.config import settings
from hospital_feedback_system.database import Base, engine
from hospital_feedback_system.routers import all_routers

if settings.AUTO_CREATE_TABLES:
    Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Hospital Feedback System API",
    description="QR-code-driven patient feedback collection API",
    version="1.0.0",
    docs_url=None if settings.is_production else "/docs",
    redoc_url=None if settings.is_production else "/redoc",
)

if settings.is_production:
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=["*"])

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "DELETE"],
    allow_headers=["Authorization", "Content-Type", "X-Session-Token"],
)

for router in all_routers:
    app.include_router(router)


@app.get("/")
async def root():
    return {
        "message": "Hospital Feedback System API",
        "docs": "/docs" if not settings.is_production else None,
        "version": "1.0.0",
    }


@app.get("/health")
async def health():
    return {"status": "ok"}