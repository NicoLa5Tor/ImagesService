from functools import lru_cache
from pathlib import Path
from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings


def _split_csv(value: str) -> List[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


class Settings(BaseSettings):
    project_name: str = Field(..., env="PROJECT_NAME")
    api_version: str = Field(..., env="API_VERSION")
    static_dir: str = Field(..., env="STATIC_DIR")
    images_subdir: str = Field(..., env="IMAGES_SUBDIR")
    allow_origins: str = Field(..., env="ALLOW_ORIGINS")
    allow_methods: str = Field(..., env="ALLOW_METHODS")
    allow_headers: str = Field(..., env="ALLOW_HEADERS")
    allowed_extensions: str = Field('jpg,jpeg,png', env="ALLOWED_EXTENSIONS")
    public_base_url: str = Field("", env="PUBLIC_BASE_URL")
    uvicorn_host: str = Field(..., env="UVICORN_HOST")
    uvicorn_port: int = Field(..., env="UVICORN_PORT")
    uvicorn_reload: bool = Field(..., env="UVICORN_RELOAD")

    @property
    def cors_allow_origins(self) -> List[str]:
        return _split_csv(self.allow_origins)

    @property
    def cors_allow_methods(self) -> List[str]:
        return _split_csv(self.allow_methods)

    @property
    def cors_allow_headers(self) -> List[str]:
        return _split_csv(self.allow_headers)

    @property
    def allowed_extensions_list(self) -> List[str]:
        normalized: List[str] = []
        for item in _split_csv(self.allowed_extensions):
            lower = item.lower()
            candidate = lower if lower.startswith('.') else f'.{lower}'
            if candidate not in normalized:
                normalized.append(candidate)
        return normalized

    @property
    def public_base_url_value(self) -> str:
        return self.public_base_url.strip()

    @property
    def base_dir(self) -> Path:
        return Path(__file__).resolve().parents[2]

    @property
    def static_path(self) -> Path:
        return self.base_dir / self.static_dir

    @property
    def images_dir(self) -> Path:
        return self.static_path / self.images_subdir

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    settings = Settings()
    settings.images_dir.mkdir(parents=True, exist_ok=True)
    return settings
