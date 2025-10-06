from pathlib import Path
import shutil
from typing import Iterable, List

from fastapi import HTTPException, UploadFile, status


class StorageService:
    def __init__(self, base_dir: Path, allowed_extensions: Iterable[str]) -> None:
        self.base_dir = base_dir.resolve()
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.allowed_extensions = {ext.lower() for ext in allowed_extensions}

    def _resolve_folder(self, folder_name: str) -> Path:
        target_dir = (self.base_dir / folder_name).resolve()
        if not target_dir.is_relative_to(self.base_dir) or not target_dir.is_dir():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Folder '{folder_name}' not found.",
            )
        return target_dir

    def create_folder(self, folder_name: str) -> Path:
        destination = (self.base_dir / folder_name).resolve()
        if not destination.is_relative_to(self.base_dir):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid folder path.",
            )
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

    def list_files(self, folder_name: str) -> List[Path]:
        target_dir = self._resolve_folder(folder_name)
        return sorted(
            [item for item in target_dir.iterdir() if item.is_file()],
            key=lambda path: path.name,
        )

    def delete_folder(self, folder_name: str) -> None:
        target_dir = self._resolve_folder(folder_name)
        shutil.rmtree(target_dir)

    async def save_file(self, folder_name: str, upload: UploadFile, dest_filename: str) -> Path:
        target_dir = (self.base_dir / folder_name).resolve()
        if not target_dir.is_relative_to(self.base_dir):
            await upload.close()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid folder path.",
            )
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

    def delete_file(self, folder_name: str, base_filename: str) -> Path:
        target_dir = self._resolve_folder(folder_name)
        matches = [item for item in target_dir.iterdir() if item.is_file() and item.stem == base_filename]
        if not matches:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"File '{base_filename}' not found in folder '{folder_name}'.",
            )
        if len(matches) > 1:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    "Multiple files share that name. Remove duplicates manually or include the extension."
                ),
            )
        file_path = matches[0]
        file_path.unlink()
        return file_path
