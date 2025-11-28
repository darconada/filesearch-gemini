"""Modelos para sincronización de archivos locales"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime


class LocalFileLinkCreate(BaseModel):
    """Request para crear un vínculo de archivo local -> File Search"""
    local_file_path: str = Field(..., description="Ruta absoluta al archivo local")
    store_id: str = Field(..., description="ID del store de destino")
    project_id: Optional[int] = Field(None, description="ID del proyecto (None = proyecto activo actual)")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Metadata personalizada (hasta 20 key-value pairs)")


class LocalFileLinkResponse(BaseModel):
    """Response de un vínculo de archivo local"""
    id: str = Field(..., description="ID del vínculo")
    local_file_path: str
    file_name: str
    store_id: str
    document_id: Optional[str] = Field(None, description="ID del documento en File Search")

    # Project association
    project_id: Optional[int] = Field(None, description="ID del proyecto asociado")

    # Custom metadata
    custom_metadata: Optional[Dict[str, Any]] = Field(None, description="Metadata personalizada del usuario")

    # File metadata
    file_size: Optional[int] = None
    file_hash: Optional[str] = None
    last_modified_at: Optional[datetime] = None
    mime_type: Optional[str] = None

    # Sync tracking
    last_synced_at: Optional[datetime] = None
    status: str = Field("not_synced", description="Estado: not_synced, synced, syncing, error")
    error_message: Optional[str] = None

    # Versioning
    version: int = Field(1, description="Versión del archivo")

    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class LocalFileLinkList(BaseModel):
    """Lista de vínculos de archivos locales"""
    links: list[LocalFileLinkResponse]


class LocalFileSyncRequest(BaseModel):
    """Request para sincronizar manualmente un archivo local"""
    force: bool = Field(False, description="Forzar sincronización aunque no haya cambios")
