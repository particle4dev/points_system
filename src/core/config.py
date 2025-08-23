# python-training/lessons/points_system/src/core/config.py
from typing import Any
from pydantic_settings import BaseSettings

from pydantic import (
    PostgresDsn,
    ValidationInfo,
    field_validator,
)

class Settings(BaseSettings):
    ENVIRONMENT_NAME: str

    @property
    def is_production(self):
        return self.ENVIRONMENT_NAME == "Production"

    # Postgres
    POSTGRES_SERVER: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    SQLALCHEMY_DATABASE_URI: PostgresDsn | None = None

    @field_validator("SQLALCHEMY_DATABASE_URI", mode="before")
    def assemble_db_connection(cls, v: str | None, info: ValidationInfo) -> Any:
        if isinstance(v, str):
            return v
        return PostgresDsn.build(
            scheme="postgresql+psycopg",
            username=info.data.get("POSTGRES_USER"),
            password=info.data.get("POSTGRES_PASSWORD"),
            host=info.data.get("POSTGRES_SERVER"),
            path=f"{info.data.get('POSTGRES_DB') or ''}",
        )

    class Config:
        case_sensitive = True
        env_file = "../.env"
        extra = "allow"

settings = Settings()
