"""Modelos para el navegador de archivos del servidor"""
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class FileSystemItem(BaseModel):
    """Elemento del sistema de archivos (archivo o directorio)"""
    name: str
    path: str
    is_directory: bool
    size: Optional[int] = None  # Solo para archivos
    modified_time: Optional[datetime] = None
    mime_type: Optional[str] = None  # Solo para archivos
    is_readable: bool = True


class DirectoryListing(BaseModel):
    """Listado de un directorio"""
    current_path: str
    parent_path: Optional[str] = None
    items: List[FileSystemItem]
