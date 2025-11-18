"""Endpoints para configuración"""
from fastapi import APIRouter, HTTPException
from app.models.config import (
    ConfigApiKey,
    ConfigStatus,
    DriveCredentialsJSON,
    DriveCredentialsManual,
    DriveCredentialsStatus
)
from app.config import settings
from app.services.google_client import google_client
from app.services.drive_client import drive_client
from app.constants import AVAILABLE_MODELS, DEFAULT_MODEL
import logging
import os

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


# Google Drive Credentials Endpoints

@router.post("/drive-credentials/json", status_code=200)
async def set_drive_credentials_json(config: DriveCredentialsJSON) -> dict:
    """Configurar credenciales de Google Drive desde JSON completo"""
    try:
        settings.save_drive_credentials_json(config.credentials_json)
        logger.info("Drive credentials saved from JSON")

        return {
            "success": True,
            "message": "Credenciales de Drive guardadas correctamente. Ahora puedes iniciar el flujo de autenticación OAuth."
        }

    except ValueError as e:
        logger.error(f"Invalid credentials JSON: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error saving Drive credentials: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/drive-credentials/manual", status_code=200)
async def set_drive_credentials_manual(config: DriveCredentialsManual) -> dict:
    """Configurar credenciales de Google Drive desde client_id y client_secret"""
    try:
        settings.save_drive_credentials_manual(
            config.client_id,
            config.client_secret,
            config.project_id
        )
        logger.info("Drive credentials saved from manual input")

        return {
            "success": True,
            "message": "Credenciales de Drive guardadas correctamente. Ahora puedes iniciar el flujo de autenticación OAuth."
        }

    except ValueError as e:
        logger.error(f"Invalid credentials: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error saving Drive credentials: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/drive-credentials/status", response_model=DriveCredentialsStatus)
async def get_drive_credentials_status() -> DriveCredentialsStatus:
    """Obtener estado de las credenciales de Google Drive"""
    try:
        credentials_configured = False
        token_exists = False
        drive_connected = False
        error_message = None

        # Verificar si credentials.json existe
        if settings.drive_credentials_file and os.path.exists(settings.drive_credentials_file):
            credentials_configured = True

        # Verificar si token.json existe
        if os.path.exists(settings.drive_token_file):
            token_exists = True

        # Si ambos existen, probar la conexión
        if credentials_configured and token_exists:
            success, error = drive_client.test_connection()
            drive_connected = success
            if not success:
                error_message = error

        return DriveCredentialsStatus(
            credentials_configured=credentials_configured,
            token_exists=token_exists,
            drive_connected=drive_connected,
            error_message=error_message
        )

    except Exception as e:
        logger.error(f"Error getting Drive credentials status: {e}")
        return DriveCredentialsStatus(
            credentials_configured=False,
            token_exists=False,
            drive_connected=False,
            error_message=str(e)
        )


@router.post("/drive-credentials/test", status_code=200)
async def test_drive_connection() -> dict:
    """Probar la conexión a Google Drive (fuerza autenticación OAuth si es necesario)"""
    try:
        # Verificar que las credenciales estén configuradas
        if not settings.drive_credentials_file or not os.path.exists(settings.drive_credentials_file):
            raise HTTPException(
                status_code=400,
                detail="Credentials file not configured. Please upload credentials first."
            )

        # Intentar configurar el cliente (esto iniciará el flujo OAuth si es necesario)
        success = drive_client.configure()

        if not success:
            raise HTTPException(
                status_code=400,
                detail="Failed to configure Drive client. Please check your credentials."
            )

        # Probar la conexión
        test_success, error = drive_client.test_connection()

        if not test_success:
            raise HTTPException(
                status_code=400,
                detail=f"Drive connection test failed: {error}"
            )

        logger.info("Drive connection test successful")

        return {
            "success": True,
            "message": "Conexión a Google Drive exitosa. El sistema está listo para sincronizar archivos."
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error testing Drive connection: {e}")
        raise HTTPException(status_code=500, detail=str(e))
