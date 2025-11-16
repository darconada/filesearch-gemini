"""Cliente para Google Generative AI y File Search"""
import google.generativeai as genai
from typing import Optional
from app.config import settings
import logging

logger = logging.getLogger(__name__)


class GoogleClient:
    """Cliente singleton para interactuar con Google Generative AI"""

    _instance: Optional["GoogleClient"] = None
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
            genai.configure(api_key=key)
            self._configured = True
            logger.info("Google Generative AI client configured successfully")
        except Exception as e:
            self._configured = False
            logger.error(f"Error configuring Google client: {e}")
            raise

    def is_configured(self) -> bool:
        """Verificar si el cliente está configurado"""
        return self._configured

    def get_model(self, model_name: Optional[str] = None):
        """Obtener una instancia del modelo generativo"""
        if not self._configured:
            self.configure()

        model = model_name or settings.model_name
        return genai.GenerativeModel(model)

    def test_connection(self) -> tuple[bool, Optional[str]]:
        """Probar la conexión listando stores"""
        try:
            if not self._configured:
                self.configure()

            # Intentar listar stores como prueba
            stores = genai.list_file_search_stores(page_size=1)
            # Convertir a lista para forzar la ejecución
            _ = list(stores)

            return True, None
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False, str(e)


# Instancia global del cliente
google_client = GoogleClient()
