from typing import Annotated

from pydantic import BaseModel, Field

FolderName = Annotated[
    str,
    Field(
        min_length=1,
        max_length=50,
        pattern=r"^[\w-]+$",
        strip_whitespace=True,
        description="Nombre de carpeta permitido (letras, números, guiones y guiones bajos)",
    ),
]

FileName = Annotated[
    str,
    Field(
        min_length=1,
        max_length=120,
        pattern=r"^[\w-]+$",
        strip_whitespace=True,
        description="Nombre base del archivo sin extensión (letras, números, guiones y guiones bajos)",
    ),
]


class FolderCreate(BaseModel):
    name: FolderName


class FolderCreated(BaseModel):
    message: str
    folder: str
    path: str


class FileUploaded(BaseModel):
    message: str
    folder: str
    filename: str
    url: str


class FolderDeleted(BaseModel):
    message: str
    folder: str


class FileDeleted(BaseModel):
    message: str
    folder: str
    filename: str


class FileInfo(BaseModel):
    folder: str
    filename: str
    url: str
