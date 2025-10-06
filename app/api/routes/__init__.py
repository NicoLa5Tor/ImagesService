from fastapi import APIRouter

from .folders import router as folders_router
from .uploads import router as uploads_router

api_router = APIRouter()
api_router.include_router(folders_router)
api_router.include_router(uploads_router)

__all__ = ["api_router"]
