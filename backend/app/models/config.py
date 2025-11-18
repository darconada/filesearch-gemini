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


class DriveCredentialsJSON(BaseModel):
    """Request para configurar credenciales Drive desde JSON completo"""
    credentials_json: str = Field(..., min_length=1, description="JSON completo de credentials.json de Google Cloud Console")


class DriveCredentialsManual(BaseModel):
    """Request para configurar credenciales Drive manualmente"""
    client_id: str = Field(..., min_length=1, description="Client ID de OAuth 2.0")
    client_secret: str = Field(..., min_length=1, description="Client Secret de OAuth 2.0")
    project_id: Optional[str] = Field(None, description="Project ID de Google Cloud (opcional)")


class DriveCredentialsStatus(BaseModel):
    """Estado de las credenciales de Drive"""
    credentials_configured: bool = Field(..., description="Si credentials.json existe")
    token_exists: bool = Field(..., description="Si token.json existe (usuario ya autenticado)")
    drive_connected: bool = Field(False, description="Si la conexión a Drive funciona")
    error_message: Optional[str] = Field(None, description="Mensaje de error si hay problemas")
