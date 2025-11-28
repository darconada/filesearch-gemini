"""API endpoints para audit logs"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.audit_log import (
    AuditLogResponse,
    AuditLogList,
    AuditLogFilter
)
from app.services.audit_service import audit_service
from typing import Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/audit-logs",
    tags=["audit-logs"]
)


@router.get("/", response_model=AuditLogList)
async def get_audit_logs(
    action: Optional[str] = Query(None, description="Filtrar por tipo de acción"),
    resource_type: Optional[str] = Query(None, description="Filtrar por tipo de recurso"),
    resource_id: Optional[str] = Query(None, description="Filtrar por ID de recurso"),
    user_identifier: Optional[str] = Query(None, description="Filtrar por usuario/IP"),
    success: Optional[bool] = Query(None, description="Filtrar por éxito/fallo"),
    start_date: Optional[datetime] = Query(None, description="Fecha inicio (ISO format)"),
    end_date: Optional[datetime] = Query(None, description="Fecha fin (ISO format)"),
    page: int = Query(1, ge=1, description="Número de página"),
    page_size: int = Query(50, ge=1, le=200, description="Tamaño de página"),
    db: Session = Depends(get_db)
):
    """
    Obtener audit logs con filtros y paginación

    Permite filtrar por:
    - Tipo de acción (action)
    - Tipo de recurso (resource_type)
    - ID de recurso (resource_id)
    - Usuario/IP (user_identifier)
    - Éxito/Fallo (success)
    - Rango de fechas (start_date, end_date)

    Los resultados están paginados y ordenados por fecha descendente (más recientes primero)
    """
    try:
        filters = AuditLogFilter(
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            user_identifier=user_identifier,
            success=success,
            start_date=start_date,
            end_date=end_date,
            page=page,
            page_size=page_size
        )

        return audit_service.get_logs(db, filters)

    except Exception as e:
        logger.error(f"Error getting audit logs: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{log_id}", response_model=AuditLogResponse)
async def get_audit_log(
    log_id: int,
    db: Session = Depends(get_db)
):
    """Obtener un audit log específico por ID"""
    log = audit_service.get_log(db, log_id)
    if not log:
        raise HTTPException(status_code=404, detail=f"Audit log {log_id} not found")
    return log


@router.get("/stats/summary")
async def get_audit_stats(
    days: int = Query(30, ge=1, le=365, description="Últimos X días para las estadísticas"),
    db: Session = Depends(get_db)
):
    """
    Obtener estadísticas de audit logs

    Retorna:
    - Total de acciones en el período
    - Acciones exitosas vs fallidas
    - Tasa de éxito
    - Top 10 acciones más comunes
    - Top 10 usuarios/IPs más activos
    """
    try:
        return audit_service.get_statistics(db, days)
    except Exception as e:
        logger.error(f"Error getting audit statistics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/cleanup")
async def cleanup_old_logs(
    days: int = Query(90, ge=1, description="Eliminar logs más antiguos que X días"),
    db: Session = Depends(get_db)
):
    """
    Eliminar audit logs antiguos (limpieza)

    Por defecto elimina logs de más de 90 días.
    Útil para mantener la base de datos optimizada.
    """
    try:
        deleted = audit_service.delete_old_logs(db, days)
        return {
            "message": f"Deleted {deleted} audit logs older than {days} days",
            "deleted_count": deleted
        }
    except Exception as e:
        logger.error(f"Error cleaning up old logs: {e}")
        raise HTTPException(status_code=500, detail=str(e))
