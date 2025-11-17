"""Endpoints para configuración MCP y CLI"""
from fastapi import APIRouter, HTTPException
from app.models.mcp_config import (
    MCPConfig, CLIConfig, MCPConfigUpdate, CLIConfigUpdate,
    MCPStatus, CLIStatus, IntegrationGuide
)
from app.services.mcp_config_service import mcp_config_service
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/integration", tags=["integration"])


# ============================================================================
# MCP SERVER ENDPOINTS
# ============================================================================

@router.get("/mcp/config", response_model=MCPConfig)
async def get_mcp_config():
    """Obtener configuración actual del servidor MCP"""
    try:
        return mcp_config_service.get_mcp_config()
    except Exception as e:
        logger.error(f"Error getting MCP config: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/mcp/config", response_model=MCPConfig)
async def update_mcp_config(update: MCPConfigUpdate):
    """Actualizar configuración del servidor MCP"""
    try:
        return mcp_config_service.update_mcp_config(update)
    except Exception as e:
        logger.error(f"Error updating MCP config: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/mcp/status", response_model=MCPStatus)
async def get_mcp_status():
    """Obtener estado y ejemplos de configuración del servidor MCP"""
    try:
        return mcp_config_service.get_mcp_status()
    except Exception as e:
        logger.error(f"Error getting MCP status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# CLI ENDPOINTS
# ============================================================================

@router.get("/cli/config", response_model=CLIConfig)
async def get_cli_config():
    """Obtener configuración actual del CLI local"""
    try:
        return mcp_config_service.get_cli_config()
    except Exception as e:
        logger.error(f"Error getting CLI config: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/cli/config", response_model=CLIConfig)
async def update_cli_config(update: CLIConfigUpdate):
    """Actualizar configuración del CLI local"""
    try:
        return mcp_config_service.update_cli_config(update)
    except Exception as e:
        logger.error(f"Error updating CLI config: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/cli/status", response_model=CLIStatus)
async def get_cli_status():
    """Obtener estado y ejemplos de uso del CLI local"""
    try:
        return mcp_config_service.get_cli_status()
    except Exception as e:
        logger.error(f"Error getting CLI status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# INTEGRATION GUIDE
# ============================================================================

@router.get("/guide", response_model=IntegrationGuide)
async def get_integration_guide():
    """
    Obtener guía completa de integración con ejemplos para todos los agents
    (Gemini CLI, Claude Code, Codex CLI, y CLI local)
    """
    try:
        return mcp_config_service.get_integration_guide()
    except Exception as e:
        logger.error(f"Error getting integration guide: {e}")
        raise HTTPException(status_code=500, detail=str(e))
