from urllib.parse import quote_plus

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

_ALLOWED_JWT_ALGORITHMS = {"RS256", "RS384", "RS512", "ES256", "ES384", "ES512"}


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True, extra="ignore")

    DATABASE_URL: str | None = None
    DB_USER: str | None = None
    DB_PASSWORD: str | None = None
    DB_HOST: str | None = None
    DB_PORT: str | None = None
    DB_NAME: str | None = None
    AUTO_CREATE_TABLES: bool = False

    ENVIRONMENT: str = "development"

    ALGORITHM: str = "RS256"
    PRIVATE_KEY: str | None = None
    PUBLIC_KEY: str | None = None
    PRIVATE_KEY_PATH: str = "keys/private.pem"
    PUBLIC_KEY_PATH: str = "keys/public.pem"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    BCRYPT_ROUNDS: int = Field(default=12, ge=4, le=16)

    ALLOWED_ORIGINS: str = "http://localhost:5173"

    PATIENT_SESSION_HOURS: int = 24
    LOGIN_RATE_LIMIT: int = 10
    QR_SCAN_RATE_LIMIT: int = 30
    RATE_LIMIT_WINDOW_SECONDS: int = 60

    @field_validator("ALGORITHM")
    @classmethod
    def _asymmetric_algorithms_only(cls, value: str) -> str:
        if value not in _ALLOWED_JWT_ALGORITHMS:
            raise ValueError(
                f"ALGORITHM must be one of {sorted(_ALLOWED_JWT_ALGORITHMS)}; "
                "symmetric (HS*) and 'none' are not accepted."
            )
        return value

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT.strip().lower() in {"production", "prod"}

    @property
    def allowed_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",") if origin.strip()]

    @property
    def sqlalchemy_url(self) -> str:
        url = self.DATABASE_URL
        if not url:
            parts = ("DB_USER", "DB_PASSWORD", "DB_HOST", "DB_PORT", "DB_NAME")
            missing = [name for name in parts if not getattr(self, name)]
            if missing:
                raise RuntimeError(
                    "Database is not configured: set DATABASE_URL or " + ", ".join(missing)
                )
            url = (
                f"postgresql://{quote_plus(self.DB_USER)}:{quote_plus(self.DB_PASSWORD)}"
                f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
            )
        if url.startswith("postgres://"):
            url = "postgresql://" + url[len("postgres://"):]
        return url


settings = Settings()