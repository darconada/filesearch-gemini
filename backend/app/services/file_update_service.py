"""Servicio para actualización/reemplazo de archivos en File Search"""
from typing import Union, Optional
from sqlalchemy.orm import Session
from app.models.db_models import DriveLinkDB, LocalFileLinkDB
from app.models.file_update import FileReplaceResponse, FileVersionHistory
from app.services.document_service import document_service
import logging
from datetime import datetime, timezone
import json

logger = logging.getLogger(__name__)


class FileUpdateService:
    """
    Servicio para actualizar/reemplazar archivos existentes en File Search

    Dado que la API de Gemini no permite actualizar archivos directamente,
    este servicio implementa la estrategia "delete + re-create" mientras
    mantiene el versionado y tracking en nuestra BD.
    """

    def __init__(self):
        self.document_service = document_service

    def _get_link(self, link_id: str, db: Session) -> Union[DriveLinkDB, LocalFileLinkDB]:
        """Obtener un link (Drive o Local) por ID"""
        # Intentar primero con Drive
        link = db.query(DriveLinkDB).filter(DriveLinkDB.id == link_id).first()
        if link:
            return link

        # Si no es Drive, intentar con Local
        link = db.query(LocalFileLinkDB).filter(LocalFileLinkDB.id == link_id).first()
        if link:
            return link

        raise ValueError(f"Link {link_id} not found")

    def replace_file(
        self,
        link_id: str,
        new_file_content: bytes,
        db: Session,
        filename: Optional[str] = None
    ) -> FileReplaceResponse:
        """
        Reemplazar un archivo existente en File Search

        Args:
            link_id: ID del link (Drive o Local)
            new_file_content: Contenido del nuevo archivo
            db: Sesión de BD
            filename: Nombre del archivo (opcional, se usa el existente si no se provee)

        Returns:
            FileReplaceResponse con información de la actualización

        Proceso:
        1. Obtener el link actual
        2. Validar que tiene document_id (debe estar sincronizado)
        3. Guardar el document_id viejo en historial
        4. Borrar archivo viejo de File Search
        5. Subir nueva versión
        6. Actualizar BD con nueva info y versión
        """
        link = self._get_link(link_id, db)

        if not link.document_id:
            raise ValueError(f"Link {link_id} is not synced yet. Cannot replace non-existent document.")

        old_document_id = link.document_id

        try:
            logger.info(f"Replacing file for link {link_id}, old document: {old_document_id}")

            # 1. Guardar el document_id viejo en historial
            history = []
            if link.previous_document_ids:
                try:
                    history = json.loads(link.previous_document_ids)
                except json.JSONDecodeError:
                    logger.warning(f"Could not parse previous_document_ids for link {link_id}")
                    history = []

            # Agregar el documento actual al historial con timestamp
            history.append({
                "document_id": old_document_id,
                "version": link.version,
                "replaced_at": datetime.now(timezone.utc).isoformat()
            })

            # 2. Borrar archivo viejo de File Search
            try:
                logger.info(f"Deleting old document {old_document_id} from store {link.store_id}")
                self.document_service.delete_document(link.store_id, old_document_id)
            except Exception as e:
                logger.warning(f"Could not delete old document: {e}")
                # Continuar de todas formas, el nuevo archivo se subirá

            # 3. Subir nueva versión
            display_name = filename or link.file_name if hasattr(link, 'file_name') else \
                          (link.drive_file_name if hasattr(link, 'drive_file_name') else 'updated_file')

            logger.info(f"Uploading new version to store {link.store_id}")

            # Metadata incluye información de versión
            metadata = {
                "previous_document_id": old_document_id,
                "version": link.version + 1,
                "updated_at": datetime.now(timezone.utc).isoformat()
            }

            # Agregar metadata específica según el tipo de link
            if isinstance(link, DriveLinkDB):
                metadata["drive_file_id"] = link.drive_file_id
                metadata["synced_from"] = "google_drive"
            elif isinstance(link, LocalFileLinkDB):
                metadata["local_file_path"] = link.local_file_path
                metadata["synced_from"] = "local_filesystem"

            document = self.document_service.upload_document(
                store_id=link.store_id,
                file_content=new_file_content,
                filename=display_name,
                display_name=display_name,
                metadata=metadata
            )

            # 4. Actualizar BD con nueva versión
            new_version = link.version + 1
            link.document_id = document.name
            link.version = new_version
            link.previous_document_ids = json.dumps(history)
            link.last_synced_at = datetime.now(timezone.utc)

            # Actualizar campos específicos según tipo
            if isinstance(link, DriveLinkDB):
                link.drive_last_modified_at = datetime.now(timezone.utc)
                # Si se provee filename, actualizar drive_file_name
                if filename:
                    link.drive_file_name = filename
            elif isinstance(link, LocalFileLinkDB):
                link.last_modified_at = datetime.now(timezone.utc)
                # Si se provee filename, actualizar file_name
                if filename:
                    link.file_name = filename
                # Podríamos recalcular hash aquí si quisiéramos
                link.file_size = len(new_file_content)

            # Guardar original_file_id en la primera actualización
            if not link.original_file_id:
                if isinstance(link, DriveLinkDB):
                    link.original_file_id = link.drive_file_id
                else:
                    link.original_file_id = link.id

            link.status = "synced"
            link.error_message = None

            db.commit()

            logger.info(f"Successfully replaced file for link {link_id}. New document: {document.name}, version: {new_version}")

            return FileReplaceResponse(
                success=True,
                link_id=link_id,
                new_version=new_version,
                new_document_id=document.name,
                old_document_id=old_document_id,
                message=f"File replaced successfully. Version {link.version - 1} → {new_version}"
            )

        except Exception as e:
            logger.error(f"Error replacing file for link {link_id}: {e}")
            db.rollback()
            raise

    def get_version_history(self, link_id: str, db: Session) -> FileVersionHistory:
        """
        Obtener el historial de versiones de un archivo

        Args:
            link_id: ID del link

        Returns:
            FileVersionHistory con el historial completo
        """
        link = self._get_link(link_id, db)

        # Parse historial
        previous_versions = []
        if link.previous_document_ids:
            try:
                previous_versions = json.loads(link.previous_document_ids)
            except json.JSONDecodeError:
                logger.warning(f"Could not parse previous_document_ids for link {link_id}")

        # Determinar file_name según tipo
        file_name = "unknown"
        if isinstance(link, DriveLinkDB):
            file_name = link.drive_file_name or link.drive_file_id
        elif isinstance(link, LocalFileLinkDB):
            file_name = link.file_name

        return FileVersionHistory(
            link_id=link_id,
            file_name=file_name,
            current_version=link.version,
            current_document_id=link.document_id or "not_synced",
            previous_versions=previous_versions,
            created_at=link.created_at,
            updated_at=link.updated_at
        )


# Instancia global del servicio
file_update_service = FileUpdateService()
