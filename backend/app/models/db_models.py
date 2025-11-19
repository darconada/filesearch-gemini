"""Modelos de base de datos SQLAlchemy"""
from sqlalchemy import Column, String, Integer, DateTime, Boolean, Enum as SQLEnum, Text
from sqlalchemy.sql import func
from app.database import Base
from app.models.drive import SyncMode
import enum


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
