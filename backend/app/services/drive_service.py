"""Servicio para sincronización con Google Drive (base futura)"""
from typing import List, Optional
from app.models.drive import (
    DriveLinkCreate,
    DriveLinkResponse,
    DriveLinkList,
    SyncMode
)
import logging
from datetime import datetime
import uuid

logger = logging.getLogger(__name__)


class DriveService:
    """Servicio para gestión de vínculos Drive -> File Search"""

    def __init__(self):
        # En memoria por ahora (base para futura persistencia en DB)
        self._links: dict[str, DriveLinkResponse] = {}

    def create_link(self, link_data: DriveLinkCreate) -> DriveLinkResponse:
        """Crear un vínculo Drive -> File Search"""
        try:
            # Generar ID único
            link_id = str(uuid.uuid4())

            # Crear el vínculo
            link = DriveLinkResponse(
                id=link_id,
                drive_file_id=link_data.drive_file_id,
                store_id=link_data.store_id,
                document_id=None,
                sync_mode=link_data.sync_mode,
                sync_interval_minutes=link_data.sync_interval_minutes,
                last_synced_at=None,
                drive_last_modified_at=None,
                status="not_synced",
                error_message=None
            )

            # Almacenar en memoria
            self._links[link_id] = link

            logger.info(f"Drive link created: {link_id}")

            return link

        except Exception as e:
            logger.error(f"Error creating drive link: {e}")
            raise

    def list_links(self) -> DriveLinkList:
        """Listar todos los vínculos"""
        return DriveLinkList(links=list(self._links.values()))

    def get_link(self, link_id: str) -> Optional[DriveLinkResponse]:
        """Obtener un vínculo por ID"""
        return self._links.get(link_id)

    def delete_link(self, link_id: str) -> dict:
        """Eliminar un vínculo"""
        if link_id in self._links:
            del self._links[link_id]
            logger.info(f"Drive link deleted: {link_id}")
            return {"success": True, "message": f"Link {link_id} deleted"}
        else:
            raise ValueError(f"Link {link_id} not found")

    def sync_link(self, link_id: str, force: bool = False) -> DriveLinkResponse:
        """
        Sincronizar un vínculo manualmente (STUB - base para implementación futura)

        En una implementación completa:
        1. Obtener el archivo de Google Drive usando Drive API
        2. Verificar modifiedTime vs drive_last_modified_at
        3. Si ha cambiado o force=True:
           - Descargar el contenido
           - Si document_id existe, eliminarlo del store
           - Subir nuevo documento al store
           - Actualizar document_id, last_synced_at, drive_last_modified_at
        """
        link = self._links.get(link_id)
        if not link:
            raise ValueError(f"Link {link_id} not found")

        try:
            # STUB: Simular sincronización exitosa
            logger.warning(f"STUB: Sync requested for link {link_id}. Drive API integration pending.")

            # Actualizar estado del vínculo
            link.status = "synced"
            link.last_synced_at = datetime.utcnow()
            link.error_message = None

            # TODO: Implementar lógica real de sincronización con Drive API
            # - Autenticación OAuth 2.0
            # - Obtener metadatos del archivo (modifiedTime)
            # - Descargar contenido si ha cambiado
            # - Actualizar documento en File Search

            self._links[link_id] = link

            return link

        except Exception as e:
            logger.error(f"Error syncing link {link_id}: {e}")
            link.status = "error"
            link.error_message = str(e)
            self._links[link_id] = link
            raise


# Instancia global del servicio
drive_service = DriveService()
