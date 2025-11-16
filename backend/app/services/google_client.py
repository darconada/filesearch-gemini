"""Cliente para Google Gen AI SDK (nuevo)"""
from google import genai
from google.genai import types
from typing import Optional
from app.config import settings
import logging

logger = logging.getLogger(__name__)


class GoogleClient:
    """Cliente singleton para interactuar con Google Gen AI"""

    _instance: Optional["GoogleClient"] = None
    _client: Optional[genai.Client] = None
    _configured: bool = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def configure(self, api_key: Optional[str] = None) -> None:
        """Configurar el cliente con la API key"""
        key = api_key or settings.api_key

        if not key:
            raise ValueError("API key no configurada")

        try:
            self._client = genai.Client(api_key=key)
            self._configured = True
            logger.info("Google Gen AI client configured successfully")
        except Exception as e:
            self._configured = False
            logger.error(f"Error configuring Google client: {e}")
            raise

    def is_configured(self) -> bool:
        """Verificar si el cliente está configurado"""
        return self._configured and self._client is not None

    def get_client(self) -> genai.Client:
        """Obtener el cliente configurado"""
        if not self._configured or self._client is None:
            self.configure()
        return self._client

    def test_connection(self) -> tuple[bool, Optional[str]]:
        """Probar la conexión listando stores"""
        try:
            if not self._configured:
                self.configure()

            # Intentar listar stores como prueba con sintaxis correcta
            client = self.get_client()
            pager = client.file_search_stores.list(config={"pageSize": 1})

            # Forzar la ejecución accediendo a la primera página
            _ = list(pager.page)

            return True, None
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False, str(e)


# Instancia global del cliente
google_client = GoogleClient()
