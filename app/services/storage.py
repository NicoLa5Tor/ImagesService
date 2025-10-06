from pathlib import Path
from typing import Iterable

from fastapi import HTTPException, UploadFile, status


class StorageService:
    def __init__(self, base_dir: Path, allowed_extensions: Iterable[str]) -> None:
        self.base_dir = base_dir
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.allowed_extensions = {ext.lower() for ext in allowed_extensions}

    def create_folder(self, folder_name: str) -> Path:
        destination = self.base_dir / folder_name
        if destination.exists():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Folder '{folder_name}' already exists.",
            )
        destination.mkdir(parents=True, exist_ok=False)
        return destination

    def list_folders(self) -> Iterable[str]:
        yield from sorted(
            folder.name
            for folder in self.base_dir.iterdir()
            if folder.is_dir()
        )

    async def save_file(self, folder_name: str, upload: UploadFile, dest_filename: str) -> Path:
        target_dir = self.base_dir / folder_name
        target_dir.mkdir(parents=True, exist_ok=True)

        original_name = upload.filename or ""
        extension = Path(original_name).suffix.lower()
        if not extension:
            await upload.close()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Uploaded file must include an extension.",
            )

        if self.allowed_extensions and extension not in self.allowed_extensions:
            await upload.close()
            allowed = ", ".join(sorted(ext.lstrip('.') for ext in self.allowed_extensions))
            raise HTTPException(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail=f"Extension '{extension.lstrip('.').upper()}' is not allowed. Allowed: {allowed}.",
            )

        base_name = Path(dest_filename).stem
        if not base_name:
            await upload.close()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Filename is required.",
            )

        safe_name = f"{base_name}{extension}"
        destination = target_dir / safe_name

        await upload.seek(0)
        with destination.open("wb") as buffer:
            while chunk := await upload.read(1024 * 1024):
                buffer.write(chunk)
        await upload.close()
        return destination
