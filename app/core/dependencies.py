from functools import lru_cache

from .config import get_settings
from app.services.storage import StorageService


@lru_cache(maxsize=1)
def get_storage_service() -> StorageService:
    settings = get_settings()
    return StorageService(settings.images_dir, settings.allowed_extensions_list)
