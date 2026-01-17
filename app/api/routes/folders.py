from typing import List

from fastapi import APIRouter, Depends, HTTPException, Path, Request
from fastapi.responses import FileResponse

from app.core.dependencies import get_storage_service
from app.schemas.folders import (
    FileDeleted,
    FileInfo,
    FileName,
    FileFullName,
    FolderCreate,
    FolderCreated,
    FolderDeleted,
    FolderName,
)
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


@router.get(
    "/{folder_name}/files",
    response_model=List[FileInfo],
    status_code=200,
)
async def list_folder_files(
    request: Request,
    folder_name: FolderName = Path(..., description="Nombre de la carpeta"),
    storage: StorageService = Depends(get_storage_service),
) -> List[FileInfo]:
    files = storage.list_files(folder_name)
    return [
        FileInfo(
            folder=folder_name,
            filename=file_path.name,
            url=str(request.url_for("static", path=f"images/{folder_name}/{file_path.name}")),
            download_url=(
                str(
                    request.url_for(
                        "download_file",
                        folder_name=folder_name,
                        filename=file_path.name,
                    )
                )
                if file_path.suffix.lower() == ".apk"
                else None
            ),
        )
        for file_path in files
    ]


@router.delete(
    "/{folder_name}/files/{filename}",
    response_model=FileDeleted,
    status_code=200,
)
async def delete_file(
    folder_name: FolderName = Path(..., description="Nombre de la carpeta"),
    filename: FileName = Path(..., description="Nombre base del archivo sin extensión"),
    storage: StorageService = Depends(get_storage_service),
) -> FileDeleted:
    deleted_path = storage.delete_file(folder_name, filename)
    return FileDeleted(
        message="File deleted",
        folder=folder_name,
        filename=deleted_path.name,
    )


@router.get(
    "/{folder_name}/files/{filename}/download",
    response_class=FileResponse,
    status_code=200,
    name="download_file",
)
async def download_file(
    folder_name: FolderName = Path(..., description="Nombre de la carpeta"),
    filename: FileFullName = Path(..., description="Nombre del archivo con extensión"),
    storage: StorageService = Depends(get_storage_service),
) -> FileResponse:
    if not filename.lower().endswith(".apk"):
        raise HTTPException(
            status_code=400,
            detail="Only APK files support direct download.",
        )
    file_path = storage.get_file(folder_name, filename)
    return FileResponse(
        path=file_path,
        media_type="application/vnd.android.package-archive",
        filename=file_path.name,
    )


@router.delete(
    "/{folder_name}",
    response_model=FolderDeleted,
    status_code=200,
)
async def delete_folder(
    folder_name: FolderName = Path(..., description="Nombre de la carpeta a eliminar"),
    storage: StorageService = Depends(get_storage_service),
) -> FolderDeleted:
    storage.delete_folder(folder_name)
    return FolderDeleted(message="Folder deleted", folder=folder_name)
