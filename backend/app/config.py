"""Configuración de la aplicación"""
import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv, set_key
from app.constants import DEFAULT_MODEL

# Cargar variables de entorno
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)


class Settings:
    """Configuración global de la aplicación"""

    def __init__(self):
        self.env_path = env_path
        self.api_key: Optional[str] = os.getenv("GOOGLE_API_KEY")
        self.model_name: str = os.getenv("GEMINI_MODEL", DEFAULT_MODEL)
        self.host: str = os.getenv("HOST", "0.0.0.0")
        self.port: int = int(os.getenv("PORT", "8000"))
        self.cors_origins: list[str] = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://localhost:3000").split(",")

        # Google Drive OAuth configuration
        self.drive_credentials_file: Optional[str] = os.getenv("GOOGLE_DRIVE_CREDENTIALS")
        self.drive_token_file: str = os.getenv("GOOGLE_DRIVE_TOKEN", str(Path(__file__).parent.parent / "token.json"))
        self.drive_scopes: list[str] = ["https://www.googleapis.com/auth/drive.readonly"]

        # Database configuration
        self.database_url: str = os.getenv("DATABASE_URL", f"sqlite:///{Path(__file__).parent.parent / 'app.db'}")

    def set_api_key(self, api_key: str) -> None:
        """Guardar API key en el archivo .env"""
        self.api_key = api_key

        # Crear el archivo .env si no existe
        if not self.env_path.exists():
            self.env_path.touch()

        # Guardar la API key
        set_key(self.env_path, "GOOGLE_API_KEY", api_key)

        # Actualizar variable de entorno en el proceso actual
        os.environ["GOOGLE_API_KEY"] = api_key

    def has_api_key(self) -> bool:
        """Verificar si la API key está configurada"""
        return self.api_key is not None and len(self.api_key) > 0


# Instancia global de configuración
settings = Settings()
