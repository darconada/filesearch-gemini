"""Modelos de base de datos SQLAlchemy"""
from sqlalchemy import Column, String, Integer, DateTime, Boolean, Enum as SQLEnum, Text, JSON
from sqlalchemy.sql import func
from app.database import Base
from app.models.drive import SyncMode
import enum


class AuditAction(enum.Enum):
    """Tipos de acciones auditables"""
    # Proyectos
    PROJECT_CREATE = "project_create"
    PROJECT_UPDATE = "project_update"
    PROJECT_DELETE = "project_delete"
    PROJECT_ACTIVATE = "project_activate"

    # Stores
    STORE_CREATE = "store_create"
    STORE_UPDATE = "store_update"
    STORE_DELETE = "store_delete"

    # Documentos
    DOCUMENT_UPLOAD = "document_upload"
    DOCUMENT_DELETE = "document_delete"
    DOCUMENT_UPDATE = "document_update"

    # Drive links
    DRIVE_LINK_CREATE = "drive_link_create"
    DRIVE_LINK_SYNC = "drive_link_sync"
    DRIVE_LINK_DELETE = "drive_link_delete"

    # Local files
    LOCAL_FILE_LINK_CREATE = "local_file_link_create"
    LOCAL_FILE_SYNC = "local_file_sync"
    LOCAL_FILE_DELETE = "local_file_delete"

    # Queries
    QUERY_EXECUTE = "query_execute"

    # Backups
    BACKUP_CREATE = "backup_create"
    BACKUP_RESTORE = "backup_restore"
    BACKUP_DELETE = "backup_delete"

    # Config
    CONFIG_UPDATE = "config_update"


class ProjectDB(Base):
    """Modelo de base de datos para proyectos de Google AI Studio"""
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, nullable=False, unique=True)
    api_key = Column(String, nullable=False)  # TODO: Encrypt in production
    description = Column(String, nullable=True)
    model_name = Column(String, nullable=True)  # Modelo Gemini a usar (null = usar default global)
    is_active = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class DriveLinkDB(Base):
    """Modelo de base de datos para vínculos Drive"""
    __tablename__ = "drive_links"

    id = Column(String, primary_key=True, index=True)
    drive_file_id = Column(String, nullable=False, index=True)
    drive_file_name = Column(String, nullable=True)  # Nombre del archivo en Drive
    store_id = Column(String, nullable=False)
    document_id = Column(String, nullable=True)
    sync_mode = Column(SQLEnum(SyncMode), nullable=False)
    sync_interval_minutes = Column(Integer, nullable=True)
    last_synced_at = Column(DateTime(timezone=True), nullable=True)
    drive_last_modified_at = Column(DateTime(timezone=True), nullable=True)
    status = Column(String, default="not_synced")
    error_message = Column(String, nullable=True)

    # Versioning fields para file updates
    version = Column(Integer, default=1, nullable=False)  # Versión del archivo
    original_file_id = Column(String, nullable=True)  # ID original (nunca cambia)
    previous_document_ids = Column(Text, nullable=True)  # JSON array con historial

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class LocalFileLinkDB(Base):
    """Modelo de base de datos para archivos locales sincronizados"""
    __tablename__ = "local_file_links"

    id = Column(String, primary_key=True, index=True)
    local_file_path = Column(String, nullable=False, index=True)  # Ruta absoluta al archivo
    file_name = Column(String, nullable=False)  # Nombre del archivo
    store_id = Column(String, nullable=False)  # Vector store asociado
    document_id = Column(String, nullable=True)  # ID en File Search

    # Project association
    project_id = Column(Integer, nullable=True, index=True)  # Proyecto asociado

    # Custom metadata (user-defined key-value pairs)
    custom_metadata = Column(JSON, nullable=True)  # Metadata personalizada del usuario

    # File metadata para detectar cambios
    file_size = Column(Integer, nullable=True)  # Tamaño en bytes
    file_hash = Column(String, nullable=True)  # SHA256 del contenido
    last_modified_at = Column(DateTime(timezone=True), nullable=True)  # Última modificación del archivo
    mime_type = Column(String, nullable=True)  # Tipo MIME

    # Sync tracking
    last_synced_at = Column(DateTime(timezone=True), nullable=True)
    status = Column(String, default="not_synced")  # "not_synced", "syncing", "synced", "error"
    error_message = Column(String, nullable=True)

    # Versioning fields para file updates
    version = Column(Integer, default=1, nullable=False)  # Versión del archivo
    original_file_id = Column(String, nullable=True)  # ID original (nunca cambia)
    previous_document_ids = Column(Text, nullable=True)  # JSON array con historial

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class DocumentDB(Base):
    """Modelo de base de datos para documentos subidos directamente a File Search"""
    __tablename__ = "documents"

    id = Column(String, primary_key=True, index=True)  # UUID generado localmente
    document_id = Column(String, unique=True, nullable=False, index=True)  # ID de Google File Search (fileSearchDocuments/xxx)
    store_id = Column(String, nullable=False, index=True)  # Store donde está el documento
    project_id = Column(Integer, nullable=True, index=True)  # Proyecto asociado

    # File information
    filename = Column(String, nullable=False)  # Nombre original del archivo
    display_name = Column(String, nullable=True)  # Nombre para mostrar (opcional)
    file_hash = Column(String, nullable=False, index=True)  # SHA256 para detección de duplicados
    file_size = Column(Integer, nullable=True)  # Tamaño en bytes
    mime_type = Column(String, nullable=True)  # Tipo MIME

    # Metadata
    custom_metadata = Column(JSON, nullable=True)  # Metadata personalizada del usuario

    # Chunking configuration (guardado para referencia)
    max_tokens_per_chunk = Column(Integer, nullable=True)
    max_overlap_tokens = Column(Integer, nullable=True)

    # Tracking
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    uploaded_by = Column(String, nullable=True)  # IP o user_id (para cuando implementes auth)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class AuditLogDB(Base):
    """Modelo de base de datos para audit logs"""
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    action = Column(SQLEnum(AuditAction), nullable=False, index=True)
    user_identifier = Column(String, nullable=True)  # IP, user_id, session_id, etc.
    resource_type = Column(String, nullable=True, index=True)  # "project", "store", "document", etc.
    resource_id = Column(String, nullable=True, index=True)  # ID del recurso afectado
    details = Column(JSON, nullable=True)  # Detalles adicionales en JSON
    success = Column(Boolean, default=True, nullable=False)  # Si la operación fue exitosa
    error_message = Column(String, nullable=True)  # Mensaje de error si falló
