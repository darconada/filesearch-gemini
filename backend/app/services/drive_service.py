"""Servicio para sincronización completa con Google Drive"""
from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.drive import (
    DriveLinkCreate,
    DriveLinkResponse,
    DriveLinkList,
    SyncMode
)
from app.models.db_models import DriveLinkDB
from app.services.drive_client import drive_client
from app.services.document_service import document_service
import logging
from datetime import datetime, timezone
import uuid

logger = logging.getLogger(__name__)


class DriveService:
    """Servicio para gestión de vínculos Drive -> File Search con sincronización real"""

    def __init__(self):
        self.drive_client = drive_client
        self.document_service = document_service

    def _db_to_response(self, db_link: DriveLinkDB) -> DriveLinkResponse:
        """Convertir modelo de BD a response"""
        return DriveLinkResponse(
            id=db_link.id,
            drive_file_id=db_link.drive_file_id,
            drive_file_name=db_link.drive_file_name,
            store_id=db_link.store_id,
            document_id=db_link.document_id,
            sync_mode=db_link.sync_mode,
            sync_interval_minutes=db_link.sync_interval_minutes,
            last_synced_at=db_link.last_synced_at,
            drive_last_modified_at=db_link.drive_last_modified_at,
            status=db_link.status,
            error_message=db_link.error_message
        )

    def create_link(self, link_data: DriveLinkCreate, db: Session) -> DriveLinkResponse:
        """Crear un vínculo Drive -> File Search"""
        try:
            # Generar ID único
            link_id = str(uuid.uuid4())

            # Crear el vínculo en BD
            db_link = DriveLinkDB(
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

            db.add(db_link)
            db.commit()
            db.refresh(db_link)

            logger.info(f"Drive link created: {link_id}")

            return self._db_to_response(db_link)

        except Exception as e:
            db.rollback()
            logger.error(f"Error creating drive link: {e}")
            raise

    def list_links(self, db: Session) -> DriveLinkList:
        """Listar todos los vínculos"""
        links = db.query(DriveLinkDB).all()
        return DriveLinkList(links=[self._db_to_response(link) for link in links])

    def get_link(self, link_id: str, db: Session) -> Optional[DriveLinkResponse]:
        """Obtener un vínculo por ID"""
        link = db.query(DriveLinkDB).filter(DriveLinkDB.id == link_id).first()
        if link:
            return self._db_to_response(link)
        return None

    def delete_link(self, link_id: str, db: Session) -> dict:
        """Eliminar un vínculo"""
        link = db.query(DriveLinkDB).filter(DriveLinkDB.id == link_id).first()
        if not link:
            raise ValueError(f"Link {link_id} not found")

        db.delete(link)
        db.commit()
        logger.info(f"Drive link deleted: {link_id}")
        return {"success": True, "message": f"Link {link_id} deleted"}

    def sync_link(self, link_id: str, force: bool, db: Session) -> DriveLinkResponse:
        """
        Sincronizar un vínculo con Google Drive (IMPLEMENTACIÓN COMPLETA)

        Proceso:
        1. Obtener metadatos del archivo de Drive
        2. Comparar modifiedTime con drive_last_modified_at
        3. Si ha cambiado o force=True:
           a. Descargar el archivo
           b. Si existe document_id, eliminarlo del store
           c. Subir nuevo documento al store
           d. Actualizar document_id, last_synced_at, drive_last_modified_at
        """
        link = db.query(DriveLinkDB).filter(DriveLinkDB.id == link_id).first()
        if not link:
            raise ValueError(f"Link {link_id} not found")

        try:
            link.status = "syncing"
            link.error_message = None
            db.commit()

            # 1. Obtener metadatos del archivo de Drive
            logger.info(f"Fetching metadata for Drive file {link.drive_file_id}")
            file_metadata = self.drive_client.get_file_metadata(link.drive_file_id)

            if not file_metadata:
                raise Exception("Could not retrieve file metadata from Drive")

            drive_modified_time = datetime.fromisoformat(file_metadata['modifiedTime'].replace('Z', '+00:00'))
            file_name = file_metadata.get('name', 'untitled')

            # 2. Verificar si necesitamos sincronizar
            needs_sync = force or \
                        link.drive_last_modified_at is None or \
                        drive_modified_time > link.drive_last_modified_at

            if not needs_sync:
                logger.info(f"File {link.drive_file_id} not modified, skipping sync")
                link.status = "synced"
                link.last_synced_at = datetime.now(timezone.utc)
                db.commit()
                return self._db_to_response(link)

            logger.info(f"File {link.drive_file_id} modified or force sync, downloading...")

            # 3. Descargar el archivo
            file_content = self.drive_client.download_file(link.drive_file_id)
            if not file_content:
                raise Exception("Could not download file from Drive")

            # 4. Si existe document_id previo, eliminarlo
            if link.document_id:
                try:
                    logger.info(f"Deleting old document {link.document_id}")
                    self.document_service.delete_document(link.store_id, link.document_id)
                except Exception as e:
                    logger.warning(f"Could not delete old document: {e}")

            # 5. Subir nuevo documento al store
            logger.info(f"Uploading new document to store {link.store_id}")
            document = self.document_service.upload_document(
                store_id=link.store_id,
                file_content=file_content,
                filename=file_name,
                display_name=file_name,
                metadata={
                    "drive_file_id": link.drive_file_id,
                    "synced_from": "google_drive",
                    "last_modified": drive_modified_time.isoformat()
                }
            )

            # 6. Actualizar el vínculo
            link.document_id = document.name
            link.drive_file_name = file_name
            link.last_synced_at = datetime.now(timezone.utc)
            link.drive_last_modified_at = drive_modified_time
            link.status = "synced"
            link.error_message = None

            db.commit()

            logger.info(f"Successfully synced Drive file {link.drive_file_id} to document {document.name}")

            return self._db_to_response(link)

        except Exception as e:
            logger.error(f"Error syncing link {link_id}: {e}")
            link.status = "error"
            link.error_message = str(e)
            db.commit()
            raise

    def sync_all_auto_links(self, db: Session) -> List[DriveLinkResponse]:
        """
        Sincronizar todos los vínculos en modo automático

        Esta función es llamada por el scheduler periódicamente
        """
        auto_links = db.query(DriveLinkDB).filter(DriveLinkDB.sync_mode == SyncMode.AUTO).all()

        results = []
        for link in auto_links:
            try:
                synced = self.sync_link(link.id, force=False, db=db)
                results.append(synced)
            except Exception as e:
                logger.error(f"Error auto-syncing link {link.id}: {e}")
                # Continuar con el siguiente link incluso si uno falla
                continue

        logger.info(f"Auto-synced {len(results)} links")
        return results


# Instancia global del servicio
drive_service = DriveService()
