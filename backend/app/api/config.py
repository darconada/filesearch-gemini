"""Endpoints para configuración"""
from fastapi import APIRouter, HTTPException
from app.models.config import ConfigApiKey, ConfigStatus
from app.config import settings
from app.services.google_client import google_client
from app.constants import AVAILABLE_MODELS, DEFAULT_MODEL
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/config", tags=["config"])


@router.post("/api-key", status_code=200)
async def set_api_key(config: ConfigApiKey) -> dict:
    """Configurar la API key de Google"""
    try:
        # Guardar la API key
        settings.set_api_key(config.api_key)

        # Configurar el cliente
        google_client.configure(config.api_key)

        # Probar la conexión
        success, error = google_client.test_connection()

        if not success:
            raise HTTPException(
                status_code=400,
                detail=f"API key inválida o sin permisos: {error}"
            )

        logger.info("API key configured successfully")

        return {
            "success": True,
            "message": "API key configurada correctamente"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error setting API key: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status", response_model=ConfigStatus)
async def get_config_status() -> ConfigStatus:
    """Obtener el estado de la configuración"""
    try:
        configured = settings.has_api_key()
        api_key_valid = False
        error_message = None
        model_available = None

        if configured:
            # Probar la conexión
            success, error = google_client.test_connection()
            api_key_valid = success

            if success:
                model_available = settings.model_name
            else:
                error_message = error

        return ConfigStatus(
            configured=configured,
            api_key_valid=api_key_valid,
            error_message=error_message,
            model_available=model_available
        )

    except Exception as e:
        logger.error(f"Error getting config status: {e}")
        return ConfigStatus(
            configured=False,
            api_key_valid=False,
            error_message=str(e)
        )


@router.get("/models")
async def get_available_models() -> dict:
    """Obtener lista de modelos Gemini disponibles"""
    return {
        "models": AVAILABLE_MODELS,
        "default_model": DEFAULT_MODEL
    }
