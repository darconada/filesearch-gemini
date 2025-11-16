"""Modelos para documentos en File Search"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime


class MetadataValue(BaseModel):
    """Valor de metadata (puede ser string o numérico)"""
    string_value: Optional[str] = None
    numeric_value: Optional[float] = None


class DocumentMetadata(BaseModel):
    """Metadata personalizada de un documento (hasta 20 pares clave/valor)"""
    metadata: Dict[str, MetadataValue] = Field(default_factory=dict)


class ChunkingConfig(BaseModel):
    """Configuración avanzada de chunking"""
    max_tokens_per_chunk: Optional[int] = Field(None, ge=100, le=2048, description="Tokens máximos por chunk")
    max_overlap_tokens: Optional[int] = Field(None, ge=0, le=512, description="Tokens de solapamiento entre chunks")


class DocumentUpload(BaseModel):
    """Request para subir un documento (metadata desde form)"""
    display_name: Optional[str] = Field(None, description="Nombre legible del documento")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Metadatos personalizados")
    chunking_config: Optional[ChunkingConfig] = None


class DocumentResponse(BaseModel):
    """Response de un documento"""
    name: str = Field(..., description="ID interno del documento")
    display_name: str = Field(..., description="Nombre legible")
    custom_metadata: Dict[str, Any] = Field(default_factory=dict, description="Metadatos personalizados")
    create_time: Optional[datetime] = None
    update_time: Optional[datetime] = None
    state: Optional[str] = Field(None, description="Estado: PROCESSING, INDEXED, ERROR")


class DocumentList(BaseModel):
    """Lista de documentos"""
    documents: list[DocumentResponse]
    next_page_token: Optional[str] = None


class DocumentUpdate(BaseModel):
    """Request para actualizar un documento"""
    display_name: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
