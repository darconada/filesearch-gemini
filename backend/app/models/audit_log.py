"""Modelos Pydantic para Audit Logs"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Dict, Any, List
from app.models.db_models import AuditAction


class AuditLogCreate(BaseModel):
    """Datos para crear un audit log"""
    action: AuditAction
    user_identifier: Optional[str] = None
    resource_type: Optional[str] = None
    resource_id: Optional[str] = None
    details: Optional[Dict[str, Any]] = None
    success: bool = True
    error_message: Optional[str] = None


class AuditLogResponse(BaseModel):
    """Respuesta de audit log"""
    id: int
    timestamp: datetime
    action: str  # Convertido a string para el frontend
    user_identifier: Optional[str]
    resource_type: Optional[str]
    resource_id: Optional[str]
    details: Optional[Dict[str, Any]]
    success: bool
    error_message: Optional[str]

    class Config:
        from_attributes = True


class AuditLogList(BaseModel):
    """Lista de audit logs con paginación"""
    logs: List[AuditLogResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class AuditLogFilter(BaseModel):
    """Filtros para buscar audit logs"""
    action: Optional[str] = None
    resource_type: Optional[str] = None
    resource_id: Optional[str] = None
    user_identifier: Optional[str] = None
    success: Optional[bool] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=50, ge=1, le=200)
