"""Servicio para gestionar audit logs"""
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from app.models.db_models import AuditLogDB, AuditAction
from app.models.audit_log import (
    AuditLogCreate,
    AuditLogResponse,
    AuditLogList,
    AuditLogFilter
)
from fastapi import Request
import logging
import math

logger = logging.getLogger(__name__)


class AuditService:
    """Servicio para registrar y consultar audit logs"""

    def _get_client_identifier(self, request: Optional[Request] = None) -> Optional[str]:
        """Obtener identificador del cliente (IP address)"""
        if not request:
            return None

        # Intentar obtener la IP real si está detrás de un proxy
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()

        # Obtener IP del cliente directamente
        if request.client:
            return request.client.host

        return None

    def log(
        self,
        db: Session,
        action: AuditAction,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        details: Optional[dict] = None,
        success: bool = True,
        error_message: Optional[str] = None,
        request: Optional[Request] = None
    ) -> AuditLogResponse:
        """
        Registrar una acción en el audit log

        Args:
            db: Sesión de base de datos
            action: Tipo de acción realizada
            resource_type: Tipo de recurso afectado (ej: "project", "store")
            resource_id: ID del recurso afectado
            details: Detalles adicionales de la acción
            success: Si la acción fue exitosa
            error_message: Mensaje de error si la acción falló
            request: Request de FastAPI para obtener IP del cliente

        Returns:
            AuditLogResponse con el log creado
        """
        try:
            user_identifier = self._get_client_identifier(request)

            # Crear el log
            audit_log = AuditLogDB(
                action=action,
                user_identifier=user_identifier,
                resource_type=resource_type,
                resource_id=resource_id,
                details=details,
                success=success,
                error_message=error_message
            )

            db.add(audit_log)
            db.commit()
            db.refresh(audit_log)

            logger.info(
                f"Audit log created: {action.value} on {resource_type}:{resource_id} "
                f"by {user_identifier} - {'SUCCESS' if success else 'FAILED'}"
            )

            return self._db_to_response(audit_log)

        except Exception as e:
            logger.error(f"Error creating audit log: {e}")
            db.rollback()
            # No propagamos el error para no afectar la operación principal
            return None

    def get_logs(
        self,
        db: Session,
        filters: Optional[AuditLogFilter] = None
    ) -> AuditLogList:
        """
        Obtener audit logs con filtros y paginación

        Args:
            db: Sesión de base de datos
            filters: Filtros opcionales para buscar logs

        Returns:
            AuditLogList con los logs encontrados
        """
        if not filters:
            filters = AuditLogFilter()

        # Construir query base
        query = db.query(AuditLogDB)

        # Aplicar filtros
        conditions = []

        if filters.action:
            try:
                action_enum = AuditAction(filters.action)
                conditions.append(AuditLogDB.action == action_enum)
            except ValueError:
                logger.warning(f"Invalid action filter: {filters.action}")

        if filters.resource_type:
            conditions.append(AuditLogDB.resource_type == filters.resource_type)

        if filters.resource_id:
            conditions.append(AuditLogDB.resource_id == filters.resource_id)

        if filters.user_identifier:
            conditions.append(AuditLogDB.user_identifier.like(f"%{filters.user_identifier}%"))

        if filters.success is not None:
            conditions.append(AuditLogDB.success == filters.success)

        if filters.start_date:
            conditions.append(AuditLogDB.timestamp >= filters.start_date)

        if filters.end_date:
            conditions.append(AuditLogDB.timestamp <= filters.end_date)

        if conditions:
            query = query.filter(and_(*conditions))

        # Contar total de resultados
        total = query.count()

        # Aplicar paginación y ordenar por timestamp descendente (más recientes primero)
        query = query.order_by(AuditLogDB.timestamp.desc())

        offset = (filters.page - 1) * filters.page_size
        logs = query.offset(offset).limit(filters.page_size).all()

        total_pages = math.ceil(total / filters.page_size) if total > 0 else 0

        return AuditLogList(
            logs=[self._db_to_response(log) for log in logs],
            total=total,
            page=filters.page,
            page_size=filters.page_size,
            total_pages=total_pages
        )

    def get_log(self, db: Session, log_id: int) -> Optional[AuditLogResponse]:
        """Obtener un audit log específico por ID"""
        log = db.query(AuditLogDB).filter(AuditLogDB.id == log_id).first()
        if log:
            return self._db_to_response(log)
        return None

    def delete_old_logs(self, db: Session, days: int = 90) -> int:
        """
        Eliminar logs antiguos (limpieza)

        Args:
            db: Sesión de base de datos
            days: Eliminar logs más antiguos que X días

        Returns:
            Número de logs eliminados
        """
        from datetime import datetime, timedelta, timezone

        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)

        deleted = db.query(AuditLogDB).filter(
            AuditLogDB.timestamp < cutoff_date
        ).delete()

        db.commit()

        logger.info(f"Deleted {deleted} audit logs older than {days} days")

        return deleted

    def get_statistics(self, db: Session, days: int = 30) -> dict:
        """
        Obtener estadísticas de audit logs

        Args:
            db: Sesión de base de datos
            days: Últimos X días para las estadísticas

        Returns:
            Diccionario con estadísticas
        """
        from datetime import datetime, timedelta, timezone

        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)

        # Total de acciones
        total_actions = db.query(func.count(AuditLogDB.id)).filter(
            AuditLogDB.timestamp >= cutoff_date
        ).scalar()

        # Acciones exitosas vs fallidas
        successful = db.query(func.count(AuditLogDB.id)).filter(
            and_(
                AuditLogDB.timestamp >= cutoff_date,
                AuditLogDB.success == True
            )
        ).scalar()

        failed = total_actions - successful

        # Top acciones
        top_actions = db.query(
            AuditLogDB.action,
            func.count(AuditLogDB.id).label('count')
        ).filter(
            AuditLogDB.timestamp >= cutoff_date
        ).group_by(AuditLogDB.action).order_by(func.count(AuditLogDB.id).desc()).limit(10).all()

        # Top usuarios/IPs
        top_users = db.query(
            AuditLogDB.user_identifier,
            func.count(AuditLogDB.id).label('count')
        ).filter(
            and_(
                AuditLogDB.timestamp >= cutoff_date,
                AuditLogDB.user_identifier.isnot(None)
            )
        ).group_by(AuditLogDB.user_identifier).order_by(func.count(AuditLogDB.id).desc()).limit(10).all()

        return {
            "period_days": days,
            "total_actions": total_actions,
            "successful_actions": successful,
            "failed_actions": failed,
            "success_rate": (successful / total_actions * 100) if total_actions > 0 else 0,
            "top_actions": [{"action": action.value, "count": count} for action, count in top_actions],
            "top_users": [{"user": user, "count": count} for user, count in top_users]
        }

    def _db_to_response(self, db_log: AuditLogDB) -> AuditLogResponse:
        """Convertir AuditLogDB a AuditLogResponse"""
        return AuditLogResponse(
            id=db_log.id,
            timestamp=db_log.timestamp,
            action=db_log.action.value,  # Convertir enum a string
            user_identifier=db_log.user_identifier,
            resource_type=db_log.resource_type,
            resource_id=db_log.resource_id,
            details=db_log.details,
            success=db_log.success,
            error_message=db_log.error_message
        )


# Instancia global del servicio
audit_service = AuditService()
