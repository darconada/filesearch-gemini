"""Modelos para configuración MCP y CLI"""
from pydantic import BaseModel, Field, HttpUrl
from typing import Optional
from datetime import datetime


class MCPConfig(BaseModel):
    """Configuración del servidor MCP"""
    backend_url: str = Field(default="http://localhost:8000", description="URL del backend FastAPI")
    enabled: bool = Field(default=False, description="Si el servidor MCP está habilitado")
    last_updated: Optional[datetime] = None


class CLIConfig(BaseModel):
    """Configuración del CLI local"""
    backend_url: str = Field(default="http://localhost:8000", description="URL del backend FastAPI")
    default_store_id: Optional[str] = Field(None, description="Store ID por defecto")
    last_updated: Optional[datetime] = None


class MCPConfigUpdate(BaseModel):
    """Request para actualizar configuración MCP"""
    backend_url: Optional[str] = None
    enabled: Optional[bool] = None


class CLIConfigUpdate(BaseModel):
    """Request para actualizar configuración CLI"""
    backend_url: Optional[str] = None
    default_store_id: Optional[str] = None


class MCPStatus(BaseModel):
    """Estado del servidor MCP"""
    configured: bool = Field(..., description="Si está configurado")
    backend_url: str = Field(..., description="URL del backend configurada")
    enabled: bool = Field(..., description="Si está habilitado")
    example_commands: dict = Field(..., description="Ejemplos de configuración para diferentes agents")


class CLIStatus(BaseModel):
    """Estado del CLI"""
    configured: bool = Field(..., description="Si está configurado")
    backend_url: str = Field(..., description="URL del backend configurada")
    default_store_id: Optional[str] = Field(None, description="Store por defecto")
    executable_path: str = Field(..., description="Ruta al ejecutable CLI")
    example_commands: list[str] = Field(..., description="Ejemplos de comandos CLI")


class IntegrationGuide(BaseModel):
    """Guía de integración para agents"""
    gemini_cli: dict = Field(..., description="Configuración para Gemini CLI")
    claude_code: dict = Field(..., description="Configuración para Claude Code")
    codex_cli: dict = Field(..., description="Configuración para Codex CLI")
    cli_local: dict = Field(..., description="Uso del CLI local")
