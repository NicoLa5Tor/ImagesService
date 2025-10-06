from typing import List

from fastapi import APIRouter, Depends

from app.core.dependencies import get_storage_service
from app.schemas.folders import FolderCreate, FolderCreated
from app.services.storage import StorageService

router = APIRouter(prefix="/folders", tags=["folders"])


@router.post("", response_model=FolderCreated, status_code=201)
async def create_folder(
    payload: FolderCreate,
    storage: StorageService = Depends(get_storage_service),
) -> FolderCreated:
    storage.create_folder(payload.name)
    public_path = f"/static/images/{payload.name}"
    return FolderCreated(
        message="Folder created",
        folder=payload.name,
        path=public_path,
    )


@router.get("", response_model=List[str])
async def list_folders(
    storage: StorageService = Depends(get_storage_service),
) -> List[str]:
    return list(storage.list_folders())
