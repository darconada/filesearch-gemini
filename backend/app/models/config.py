"""Modelos para configuración"""
from pydantic import BaseModel, Field
from typing import Optional


class ConfigApiKey(BaseModel):
    """Request para configurar API key"""
    api_key: str = Field(..., min_length=1, description="API key de Google Generative Language")


class ConfigStatus(BaseModel):
    """Estado de la configuración"""
    configured: bool = Field(..., description="Si la API key está configurada")
    api_key_valid: bool = Field(False, description="Si la API key es válida")
    error_message: Optional[str] = Field(None, description="Mensaje de error si hay problemas")
    model_available: Optional[str] = Field(None, description="Modelo disponible para usar")
