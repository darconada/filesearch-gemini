"""Cliente para Google Drive API con OAuth 2.0"""
import os
import logging
from typing import Optional, BinaryIO
from pathlib import Path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from app.config import settings
import io

logger = logging.getLogger(__name__)


class DriveClient:
    """Cliente singleton para interactuar con Google Drive"""

    _instance: Optional["DriveClient"] = None
    _service = None
    _credentials: Optional[Credentials] = None
    _configured: bool = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def _get_credentials(self) -> Optional[Credentials]:
        """Obtener credenciales OAuth, autenticando si es necesario"""
        creds = None
        token_path = settings.drive_token_file

        # Cargar token existente si existe
        if os.path.exists(token_path):
            try:
                creds = Credentials.from_authorized_user_file(token_path, settings.drive_scopes)
                logger.info("Loaded existing Drive credentials from token file")
            except Exception as e:
                logger.warning(f"Error loading token file: {e}")

        # Si no hay credenciales válidas, autenticar
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                    logger.info("Refreshed Drive credentials")
                except Exception as e:
                    logger.error(f"Error refreshing credentials: {e}")
                    creds = None

            # Si aún no hay credenciales, hacer flujo OAuth
            if not creds:
                if not settings.drive_credentials_file or not os.path.exists(settings.drive_credentials_file):
                    logger.error("Drive credentials file not found. Please configure GOOGLE_DRIVE_CREDENTIALS")
                    return None

                try:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        settings.drive_credentials_file,
                        settings.drive_scopes
                    )
                    creds = flow.run_local_server(port=0)
                    logger.info("Completed OAuth flow for Drive")
                except Exception as e:
                    logger.error(f"Error in OAuth flow: {e}")
                    return None

            # Guardar credenciales para la próxima vez
            try:
                with open(token_path, 'w') as token:
                    token.write(creds.to_json())
                logger.info("Saved Drive credentials to token file")
            except Exception as e:
                logger.warning(f"Could not save token file: {e}")

        return creds

    def configure(self) -> bool:
        """Configurar el cliente de Drive"""
        try:
            self._credentials = self._get_credentials()
            if not self._credentials:
                logger.error("Failed to obtain Drive credentials")
                return False

            self._service = build('drive', 'v3', credentials=self._credentials)
            self._configured = True
            logger.info("Drive client configured successfully")
            return True
        except Exception as e:
            logger.error(f"Error configuring Drive client: {e}")
            self._configured = False
            return False

    def is_configured(self) -> bool:
        """Verificar si el cliente está configurado"""
        return self._configured and self._service is not None

    def get_service(self):
        """Obtener el servicio de Drive"""
        if not self._configured or self._service is None:
            if not self.configure():
                raise ValueError("Drive client not configured. Please set up OAuth credentials.")
        return self._service

    def get_file_metadata(self, file_id: str) -> Optional[dict]:
        """
        Obtener metadatos de un archivo de Drive

        Returns:
            Dict con: name, mimeType, modifiedTime, size, etc.
        """
        try:
            service = self.get_service()
            file = service.files().get(
                fileId=file_id,
                fields='id, name, mimeType, modifiedTime, size, webViewLink'
            ).execute()
            logger.info(f"Retrieved metadata for file {file_id}: {file.get('name')}")
            return file
        except Exception as e:
            logger.error(f"Error getting file metadata for {file_id}: {e}")
            return None

    def download_file(self, file_id: str) -> Optional[BinaryIO]:
        """
        Descargar contenido de un archivo de Drive

        Returns:
            BytesIO con el contenido del archivo
        """
        try:
            service = self.get_service()
            request = service.files().get_media(fileId=file_id)

            file_io = io.BytesIO()
            downloader = MediaIoBaseDownload(file_io, request)

            done = False
            while not done:
                status, done = downloader.next_chunk()
                if status:
                    logger.info(f"Download progress: {int(status.progress() * 100)}%")

            file_io.seek(0)
            logger.info(f"Successfully downloaded file {file_id}")
            return file_io
        except Exception as e:
            logger.error(f"Error downloading file {file_id}: {e}")
            return None

    def list_files(self, page_size: int = 10, page_token: Optional[str] = None) -> Optional[dict]:
        """
        Listar archivos en Drive (para futuras extensiones)

        Returns:
            Dict con: files (lista), nextPageToken
        """
        try:
            service = self.get_service()
            results = service.files().list(
                pageSize=page_size,
                pageToken=page_token,
                fields="nextPageToken, files(id, name, mimeType, modifiedTime)"
            ).execute()
            logger.info(f"Listed {len(results.get('files', []))} files from Drive")
            return results
        except Exception as e:
            logger.error(f"Error listing files: {e}")
            return None

    def test_connection(self) -> tuple[bool, Optional[str]]:
        """Probar la conexión listando archivos"""
        try:
            if not self.is_configured():
                if not self.configure():
                    return False, "Failed to configure Drive client"

            # Intentar listar archivos como prueba
            result = self.list_files(page_size=1)
            if result is None:
                return False, "Failed to list files"

            return True, None
        except Exception as e:
            logger.error(f"Drive connection test failed: {e}")
            return False, str(e)

    def get_access_token(self) -> Optional[str]:
        """
        Obtener el access token actual para usar en Google Picker API

        Returns:
            Access token string o None si no está configurado
        """
        try:
            if not self.is_configured():
                if not self.configure():
                    logger.error("Cannot get access token: Drive client not configured")
                    return None

            if not self._credentials:
                logger.error("No credentials available")
                return None

            # Refrescar el token si está expirado
            if self._credentials.expired and self._credentials.refresh_token:
                try:
                    self._credentials.refresh(Request())
                    logger.info("Refreshed credentials for access token")
                except Exception as e:
                    logger.error(f"Error refreshing credentials: {e}")
                    return None

            return self._credentials.token
        except Exception as e:
            logger.error(f"Error getting access token: {e}")
            return None


# Instancia global del cliente
drive_client = DriveClient()
