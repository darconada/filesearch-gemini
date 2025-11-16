"""Modelos de base de datos SQLAlchemy"""
from sqlalchemy import Column, String, Integer, DateTime, Boolean, Enum as SQLEnum
from sqlalchemy.sql import func
from app.database import Base
from app.models.drive import SyncMode
import enum


class DriveLinkDB(Base):
    """Modelo de base de datos para vínculos Drive"""
    __tablename__ = "drive_links"

    id = Column(String, primary_key=True, index=True)
    drive_file_id = Column(String, nullable=False, index=True)
    store_id = Column(String, nullable=False)
    document_id = Column(String, nullable=True)
    sync_mode = Column(SQLEnum(SyncMode), nullable=False)
    sync_interval_minutes = Column(Integer, nullable=True)
    last_synced_at = Column(DateTime(timezone=True), nullable=True)
    drive_last_modified_at = Column(DateTime(timezone=True), nullable=True)
    status = Column(String, default="not_synced")
    error_message = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
