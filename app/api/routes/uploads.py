from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, UploadFile, Request

from app.core.dependencies import get_storage_service
from app.schemas.folders import FileUploaded, FolderName, FileName
from app.services.storage import StorageService

router = APIRouter(prefix='/upload', tags=['uploads'])

FolderForm = Annotated[FolderName, Form(..., description='Nombre de la carpeta destino')]
FilenameForm = Annotated[
    FileName,
    Form(
        ...,
        description='Nombre base (sin extensión); se usará la extensión original del archivo',
    ),
]


@router.post("", response_model=FileUploaded, status_code=201)
async def upload_image(
    request: Request,
    folder: FolderForm,
    filename: FilenameForm,
    file: UploadFile = File(...),
    storage: StorageService = Depends(get_storage_service),
) -> FileUploaded:
    saved_path = await storage.save_file(folder, file, filename)
    public_url = str(request.url_for("static", path=f"images/{folder}/{saved_path.name}"))
    return FileUploaded(
        message='File uploaded',
        folder=folder,
        filename=saved_path.name,
        url=public_url,
    )
