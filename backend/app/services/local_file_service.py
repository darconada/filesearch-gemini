"""Servicio para sincronización de archivos locales"""
from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.local_file import (
    LocalFileLinkCreate,
    LocalFileLinkResponse,
    LocalFileLinkList
)
from app.models.db_models import LocalFileLinkDB
from app.services.document_service import document_service
import logging
from datetime import datetime, timezone
import uuid
import os
import hashlib
import mimetypes
from pathlib import Path

logger = logging.getLogger(__name__)


class LocalFileService:
    """Servicio para gestión de archivos locales sincronizados con File Search"""

    def __init__(self):
        self.document_service = document_service

    def _calculate_file_hash(self, file_path: str) -> str:
        """Calcular SHA256 hash del archivo"""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            # Leer en chunks para archivos grandes
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()

    def _get_file_metadata(self, file_path: str) -> dict:
        """Obtener metadata del archivo local"""
        stat = os.stat(file_path)
        mime_type, _ = mimetypes.guess_type(file_path)

        return {
            "size": stat.st_size,
            "modified_time": datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc),
            "mime_type": mime_type or "application/octet-stream"
        }

    def _validate_file_path(self, file_path: str) -> Path:
        """Validar que la ruta del archivo existe y es accesible"""
        path = Path(file_path).resolve()

        if not path.exists():
            raise ValueError(f"File does not exist: {file_path}")

        if not path.is_file():
            raise ValueError(f"Path is not a file: {file_path}")

        if not os.access(path, os.R_OK):
            raise ValueError(f"File is not readable: {file_path}")

        return path

    def _db_to_response(self, db_link: LocalFileLinkDB) -> LocalFileLinkResponse:
        """Convertir modelo de BD a response"""
        return LocalFileLinkResponse(
            id=db_link.id,
            local_file_path=db_link.local_file_path,
            file_name=db_link.file_name,
            store_id=db_link.store_id,
            document_id=db_link.document_id,
            file_size=db_link.file_size,
            file_hash=db_link.file_hash,
            last_modified_at=db_link.last_modified_at,
            mime_type=db_link.mime_type,
            last_synced_at=db_link.last_synced_at,
            status=db_link.status,
            error_message=db_link.error_message,
            version=db_link.version,
            created_at=db_link.created_at,
            updated_at=db_link.updated_at
        )

    def create_link(self, link_data: LocalFileLinkCreate, db: Session) -> LocalFileLinkResponse:
        """Crear un vínculo para archivo local -> File Search"""
        try:
            # Validar que el archivo existe
            file_path = self._validate_file_path(link_data.local_file_path)

            # Verificar si ya existe un link para este archivo
            existing_link = db.query(LocalFileLinkDB).filter(
                LocalFileLinkDB.local_file_path == str(file_path)
            ).first()

            if existing_link:
                raise ValueError(f"A link for this file already exists: {existing_link.id}")

            # Obtener metadata del archivo
            metadata = self._get_file_metadata(str(file_path))

            # Generar ID único
            link_id = str(uuid.uuid4())

            # Crear el vínculo en BD
            db_link = LocalFileLinkDB(
                id=link_id,
                local_file_path=str(file_path),
                file_name=file_path.name,
                store_id=link_data.store_id,
                document_id=None,
                file_size=metadata["size"],
                file_hash=None,  # Se calculará en el primer sync
                last_modified_at=metadata["modified_time"],
                mime_type=metadata["mime_type"],
                last_synced_at=None,
                status="not_synced",
                error_message=None,
                version=1
            )

            db.add(db_link)
            db.commit()
            db.refresh(db_link)

            logger.info(f"Local file link created: {link_id} for {file_path}")

            return self._db_to_response(db_link)

        except Exception as e:
            db.rollback()
            logger.error(f"Error creating local file link: {e}")
            raise

    def list_links(self, db: Session, store_id: Optional[str] = None) -> LocalFileLinkList:
        """Listar todos los vínculos de archivos locales"""
        query = db.query(LocalFileLinkDB)
        if store_id:
            query = query.filter(LocalFileLinkDB.store_id == store_id)
        links = query.all()
        return LocalFileLinkList(links=[self._db_to_response(link) for link in links])

    def get_link(self, link_id: str, db: Session) -> Optional[LocalFileLinkResponse]:
        """Obtener un vínculo por ID"""
        link = db.query(LocalFileLinkDB).filter(LocalFileLinkDB.id == link_id).first()
        if link:
            return self._db_to_response(link)
        return None

    def delete_link(self, link_id: str, db: Session, delete_from_store: bool = False) -> dict:
        """
        Eliminar un vínculo de archivo local

        Args:
            link_id: ID del link
            db: Sesión de BD
            delete_from_store: Si True, también elimina el documento del File Search store
        """
        link = db.query(LocalFileLinkDB).filter(LocalFileLinkDB.id == link_id).first()
        if not link:
            raise ValueError(f"Link {link_id} not found")

        # Opcionalmente eliminar del store
        if delete_from_store and link.document_id:
            try:
                self.document_service.delete_document(link.store_id, link.document_id)
                logger.info(f"Deleted document {link.document_id} from store")
            except Exception as e:
                logger.warning(f"Could not delete document from store: {e}")

        db.delete(link)
        db.commit()
        logger.info(f"Local file link deleted: {link_id}")
        return {"success": True, "message": f"Link {link_id} deleted"}

    def sync_file(self, link_id: str, force: bool, db: Session) -> LocalFileLinkResponse:
        """
        Sincronizar un archivo local con File Search

        Proceso:
        1. Verificar que el archivo aún existe y es accesible
        2. Obtener metadata actual del archivo (size, modified_time)
        3. Calcular hash del contenido
        4. Comparar con última sincronización
        5. Si cambió o force=True:
           a. Leer el contenido del archivo
           b. Si existe document_id, eliminarlo del store (replace)
           c. Subir nuevo documento al store
           d. Actualizar metadata en BD
        """
        link = db.query(LocalFileLinkDB).filter(LocalFileLinkDB.id == link_id).first()
        if not link:
            raise ValueError(f"Link {link_id} not found")

        try:
            link.status = "syncing"
            link.error_message = None
            db.commit()

            # 1. Validar que el archivo existe
            file_path = self._validate_file_path(link.local_file_path)

            # 2. Obtener metadata actual
            current_metadata = self._get_file_metadata(str(file_path))

            # 3. Calcular hash para detectar cambios de contenido
            logger.info(f"Calculating hash for {file_path}")
            current_hash = self._calculate_file_hash(str(file_path))

            # 4. Verificar si necesitamos sincronizar
            # Asegurar timezone en last_modified_at
            last_modified = link.last_modified_at
            if last_modified and last_modified.tzinfo is None:
                last_modified = last_modified.replace(tzinfo=timezone.utc)

            needs_sync = force or \
                        link.file_hash is None or \
                        current_hash != link.file_hash or \
                        last_modified is None or \
                        current_metadata["modified_time"] > last_modified

            if not needs_sync:
                logger.info(f"File {file_path} not modified, skipping sync")
                link.status = "synced"
                link.last_synced_at = datetime.now(timezone.utc)
                db.commit()
                return self._db_to_response(link)

            logger.info(f"File {file_path} modified or force sync, uploading...")

            # 5. Si existe document_id previo, eliminarlo (replace)
            if link.document_id:
                try:
                    logger.info(f"Deleting old document {link.document_id}")
                    self.document_service.delete_document(link.store_id, link.document_id)
                except Exception as e:
                    logger.warning(f"Could not delete old document: {e}")

            # 6. Subir nuevo documento al store
            # Abrir el archivo y pasar el file object (BinaryIO) directamente
            logger.info(f"Uploading document to store {link.store_id}")
            with open(file_path, "rb") as file_obj:
                document = self.document_service.upload_document(
                    store_id=link.store_id,
                    file_content=file_obj,
                    filename=link.file_name,
                    display_name=link.file_name,
                    metadata={
                        "local_file_path": str(file_path),
                        "synced_from": "local_filesystem",
                        "file_hash": current_hash,
                        "last_modified": current_metadata["modified_time"].isoformat()
                    }
                )

            # 8. Actualizar el vínculo
            link.document_id = document.name
            link.file_size = current_metadata["size"]
            link.file_hash = current_hash
            link.last_modified_at = current_metadata["modified_time"]
            link.mime_type = current_metadata["mime_type"]
            link.last_synced_at = datetime.now(timezone.utc)
            link.status = "synced"
            link.error_message = None

            db.commit()

            logger.info(f"Successfully synced local file {file_path} to document {document.name}")

            return self._db_to_response(link)

        except Exception as e:
            logger.error(f"Error syncing link {link_id}: {e}")
            link.status = "error"
            link.error_message = str(e)
            db.commit()
            raise

    def sync_all(self, db: Session, store_id: Optional[str] = None) -> List[LocalFileLinkResponse]:
        """
        Sincronizar todos los archivos locales (opcionalmente filtrados por store)
        """
        query = db.query(LocalFileLinkDB)
        if store_id:
            query = query.filter(LocalFileLinkDB.store_id == store_id)

        links = query.all()
        results = []

        for link in links:
            try:
                synced = self.sync_file(link.id, force=False, db=db)
                results.append(synced)
            except Exception as e:
                logger.error(f"Error syncing link {link.id}: {e}")
                # Continuar con el siguiente archivo
                continue

        logger.info(f"Synced {len(results)} local files")
        return results


# Instancia global del servicio
local_file_service = LocalFileService()
