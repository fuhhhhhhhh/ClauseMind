from functools import cached_property
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "ClauseMind Contract Review System"
    app_env: str = "dev"
    app_host: str = "0.0.0.0"
    app_port: int = 8000

    database_url: str = "sqlite:///./contract_review.db"

    jwt_secret_key: str = "change-this-secret"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 1440

    storage_root: Path = Path("../storage")
    upload_dir: Path = Path("../storage/uploads")
    mineru_output_dir: Path = Path("../storage/mineru_output")
    report_dir: Path = Path("../storage/reports")
    temp_dir: Path = Path("../storage/temp")

    llm_api_base: str = "http://localhost:11434/v1"
    llm_api_key: str = "EMPTY"
    llm_model: str = "qwen2.5"
    llm_timeout: int = 120

    mineru_command: str = "mineru"
    mineru_backend: str = "pipeline"
    mineru_timeout: int = 600

    cors_origins: str = Field(default="http://localhost:5173")

    @cached_property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    def ensure_storage_dirs(self) -> None:
        for path in [
            self.storage_root,
            self.upload_dir,
            self.mineru_output_dir,
            self.report_dir,
            self.temp_dir,
        ]:
            path.mkdir(parents=True, exist_ok=True)

    def public_config(self) -> dict:
        return {
            "app_name": self.app_name,
            "app_env": self.app_env,
            "database": "sqlite" if self.database_url.startswith("sqlite") else "external",
            "llm_model": self.llm_model,
            "llm_api_base_configured": bool(self.llm_api_base),
            "mineru_backend": self.mineru_backend,
            "cors_origins": self.cors_origins_list,
        }


settings = Settings()
