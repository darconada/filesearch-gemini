"""Modelos para sincronización con Google Drive (base futura)"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum


class SyncMode(str, Enum):
    """Modo de sincronización"""
    MANUAL = "manual"
    AUTO = "auto"


class DriveLinkCreate(BaseModel):
    """Request para crear un vínculo Drive -> File Search"""
    drive_file_id: str = Field(..., description="ID del archivo en Google Drive")
    store_id: str = Field(..., description="ID del store de destino")
    sync_mode: SyncMode = Field(SyncMode.MANUAL, description="Modo de sincronización")
    sync_interval_minutes: Optional[int] = Field(None, ge=5, description="Intervalo de sincronización automática (minutos)")


class DriveLinkResponse(BaseModel):
    """Response de un vínculo Drive"""
    id: str = Field(..., description="ID del vínculo")
    drive_file_id: str
    drive_file_name: Optional[str] = Field(None, description="Nombre del archivo en Drive")
    store_id: str
    document_id: Optional[str] = Field(None, description="ID del documento en File Search (si ya está sincronizado)")
    sync_mode: SyncMode
    sync_interval_minutes: Optional[int] = None
    last_synced_at: Optional[datetime] = None
    drive_last_modified_at: Optional[datetime] = None
    status: str = Field("not_synced", description="Estado: not_synced, synced, syncing, error")
    error_message: Optional[str] = None

    # Versioning fields
    version: int = Field(1, description="Versión del archivo")
    original_file_id: Optional[str] = Field(None, description="ID original del archivo")


class DriveLinkList(BaseModel):
    """Lista de vínculos Drive"""
    links: list[DriveLinkResponse]


class DriveSyncRequest(BaseModel):
    """Request para sincronizar manualmente"""
    force: bool = Field(False, description="Forzar sincronización aunque no haya cambios")
