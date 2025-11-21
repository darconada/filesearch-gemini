"""Modelos para actualización/reemplazo de archivos"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class FileReplaceResponse(BaseModel):
    """Response al reemplazar un archivo"""
    success: bool
    link_id: str
    new_version: int
    new_document_id: str
    old_document_id: Optional[str] = None
    message: str = "File replaced successfully"


class FileVersionHistory(BaseModel):
    """Historial de versiones de un archivo"""
    link_id: str
    file_name: str
    current_version: int
    current_document_id: str
    previous_versions: List[dict] = Field(default_factory=list, description="Historial de document_ids anteriores")
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class FileUpdateStats(BaseModel):
    """Estadísticas de actualizaciones de archivos"""
    total_files: int
    files_with_updates: int
    total_versions: int
    most_updated_file: Optional[dict] = None
