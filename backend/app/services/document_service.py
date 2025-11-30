"""Servicio para gestión de documentos en File Search"""
from typing import Optional, BinaryIO, Dict, Any
from app.models.document import DocumentResponse, DocumentList, ChunkingConfig
from app.services.google_client import google_client
from app.models.db_models import DocumentDB
from app.database import SessionLocal
import logging
import tempfile
from pathlib import Path
import hashlib
import uuid
import os

logger = logging.getLogger(__name__)


class DuplicateFileException(Exception):
    """Exception raised when a duplicate file is detected"""
    def __init__(self, message: str, existing_document: DocumentDB):
        self.message = message
        self.existing_document = existing_document
        super().__init__(self.message)


class DocumentService:
    """Servicio para operaciones con documentos"""

    def __init__(self):
        self.google_client = google_client

    def _calculate_file_hash(self, file_content: BinaryIO) -> str:
        """
        Calcular SHA256 hash del contenido del archivo

        Args:
            file_content: Binary file object

        Returns:
            SHA256 hash como string hexadecimal
        """
        sha256_hash = hashlib.sha256()

        # Guardar posición actual
        original_position = file_content.tell() if hasattr(file_content, 'tell') else 0

        # Resetear al inicio
        if hasattr(file_content, 'seek'):
            file_content.seek(0)

        # Leer en chunks para archivos grandes
        if hasattr(file_content, 'read'):
            for byte_block in iter(lambda: file_content.read(4096), b""):
                sha256_hash.update(byte_block)
        else:
            # Si es bytes directamente
            sha256_hash.update(file_content)

        # Restaurar posición original
        if hasattr(file_content, 'seek'):
            file_content.seek(original_position)

        return sha256_hash.hexdigest()

    def _check_duplicate(self, file_hash: str, store_id: str, db: SessionLocal) -> Optional[DocumentDB]:
        """
        Verificar si existe un documento duplicado en el store

        Args:
            file_hash: SHA256 hash del archivo
            store_id: ID del store donde buscar
            db: Sesión de base de datos

        Returns:
            DocumentDB si existe duplicado, None si no existe
        """
        existing = db.query(DocumentDB).filter(
            DocumentDB.file_hash == file_hash,
            DocumentDB.store_id == store_id
        ).first()

        return existing

    def _convert_metadata_to_google_format(self, metadata: Dict[str, Any]) -> list:
        """
        Convertir metadata de formato simple a formato Google
        
        Google File Search espera metadata como lista de objetos:
        [
            {'key': 'campo', 'string_value': 'valor'},
            {'key': 'numero', 'numeric_value': 123.0}
        ]
        
        Restricciones de las keys:
        - Solo minúsculas, números, guiones bajos y guiones
        - Deben empezar con letra minúscula
        - Máximo 63 caracteres
        """
        google_metadata = []
        
        for key, value in metadata.items():
            # Sanitizar la key: convertir a minúsculas, reemplazar espacios por guiones bajos
            # y eliminar caracteres no permitidos
            sanitized_key = key.lower().replace(' ', '_').replace('-', '_')
            # Mantener solo letras, números y guiones bajos
            sanitized_key = ''.join(c for c in sanitized_key if c.isalnum() or c == '_')
            
            # Verificar que empiece con letra
            if not sanitized_key or not sanitized_key[0].isalpha():
                logger.warning(f"Skipping metadata key '{key}': must start with a letter")
                continue
            
            # Limitar longitud
            sanitized_key = sanitized_key[:63]
            
            # Crear el objeto de metadata
            if isinstance(value, (int, float)):
                google_metadata.append({
                    'key': sanitized_key,
                    'numeric_value': float(value)
                })
            else:
                # Limitar valor a 63 caracteres
                string_value = str(value)[:63]
                google_metadata.append({
                    'key': sanitized_key,
                    'string_value': string_value
                })
        
        return google_metadata

    def _convert_metadata_from_google_format(self, google_metadata) -> Dict[str, Any]:
        """
        Convertir metadata de formato Google a formato simple
        
        Maneja tanto el formato antiguo (dict) como el nuevo (list)
        """
        metadata = {}

        if not google_metadata:
            return metadata
        
        # Si es una lista (formato correcto de Google)
        if isinstance(google_metadata, list):
            for item in google_metadata:
                # Manejar tanto dicts como objetos Pydantic
                key = None
                numeric_value = None
                string_value = None
                
                if isinstance(item, dict):
                    key = item.get('key')
                    if 'numeric_value' in item:
                        numeric_value = item['numeric_value']
                    elif 'string_value' in item:
                        string_value = item['string_value']
                else:
                    # Asumir que es un objeto (CustomMetadata)
                    key = getattr(item, 'key', None)
                    numeric_value = getattr(item, 'numeric_value', None)
                    string_value = getattr(item, 'string_value', None)
                
                if not key:
                    continue
                
                if numeric_value is not None:
                    metadata[key] = numeric_value
                elif string_value is not None:
                    metadata[key] = string_value
        
        # Si es un dict (formato antiguo, para retrocompatibilidad)
        elif isinstance(google_metadata, dict):
            for key, value_obj in google_metadata.items():
                if isinstance(value_obj, dict):
                    if "numeric_value" in value_obj:
                        metadata[key] = value_obj["numeric_value"]
                    elif "string_value" in value_obj:
                        metadata[key] = value_obj["string_value"]
                else:
                    metadata[key] = value_obj

        return metadata

    def upload_document(
        self,
        store_id: str,
        file_content: BinaryIO,
        filename: str,
        display_name: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        chunking_config: Optional[ChunkingConfig] = None,
        force: bool = False,
        project_id: Optional[int] = None,
        uploaded_by: Optional[str] = None
    ) -> DocumentResponse:
        """
        Subir un documento al store con detección de duplicados

        Args:
            store_id: ID del store donde subir el documento
            file_content: Contenido del archivo
            filename: Nombre del archivo
            display_name: Nombre para mostrar (opcional)
            metadata: Metadata personalizada (opcional)
            chunking_config: Configuración de chunking (opcional)
            force: Si True, sube el archivo aunque sea duplicado (default: False)
            project_id: ID del proyecto asociado (opcional)
            uploaded_by: Identificador del usuario/IP que sube el archivo (opcional)

        Returns:
            DocumentResponse con la información del documento subido

        Raises:
            DuplicateFileException: Si el archivo es duplicado y force=False
        """
        db = SessionLocal()

        try:
            # 1. Calcular hash del archivo para detección de duplicados
            logger.info(f"Calculating hash for {filename}")
            file_hash = self._calculate_file_hash(file_content)
            logger.info(f"File hash: {file_hash}")

            # 2. Verificar duplicados si force=False
            if not force:
                existing = self._check_duplicate(file_hash, store_id, db)
                if existing:
                    logger.warning(
                        f"Duplicate file detected: {filename} "
                        f"matches existing document '{existing.display_name or existing.filename}' "
                        f"(uploaded {existing.uploaded_at})"
                    )
                    raise DuplicateFileException(
                        f"This file already exists in the store as '{existing.display_name or existing.filename}' "
                        f"(uploaded on {existing.uploaded_at.strftime('%Y-%m-%d %H:%M:%S')})",
                        existing
                    )

            logger.info(f"No duplicate found, proceeding with upload of {filename}")

            client = self.google_client.get_client()

            # 3. Guardar el archivo temporalmente con el nombre original
            # Esto es importante porque Google File Search usa el nombre del archivo físico
            # Añadimos un UUID para evitar colisiones si múltiples usuarios suben archivos con el mismo nombre
            tmp_dir = tempfile.gettempdir()
            unique_dir = os.path.join(tmp_dir, f"filesearch_{uuid.uuid4().hex[:8]}")
            os.makedirs(unique_dir, exist_ok=True)
            tmp_path = os.path.join(unique_dir, filename)

            with open(tmp_path, 'wb') as tmp_file:
                if hasattr(file_content, 'read'):
                    tmp_file.write(file_content.read())
                else:
                    # Assume it's bytes
                    tmp_file.write(file_content)

            try:
                # Subir usando upload_to_file_search_store
                # Ahora con soporte completo para metadata personalizada
                logger.info(f"Starting upload of {filename} to store {store_id}")
                
                # Construir configuración de upload
                upload_config = {}
                google_metadata = None
                
                # Añadir metadata personalizada si se proporciona
                if metadata:
                    google_metadata = self._convert_metadata_to_google_format(metadata)
                    if google_metadata:
                        logger.info(f"Uploading with {len(google_metadata)} metadata fields")
                        logger.debug(f"Original metadata: {metadata}")
                        logger.debug(f"Google metadata format: {google_metadata}")
                
                # Intentar pasar metadata directamente como parámetro
                # Según la documentación, custom_metadata puede ser un parámetro directo
                try:
                    if google_metadata:
                        logger.info("Attempting upload with custom_metadata parameter...")
                        operation = client.file_search_stores.upload_to_file_search_store(
                            file=tmp_path,
                            file_search_store_name=store_id,
                            custom_metadata=google_metadata
                        )
                    else:
                        logger.info("Uploading without metadata...")
                        operation = client.file_search_stores.upload_to_file_search_store(
                            file=tmp_path,
                            file_search_store_name=store_id
                        )
                except TypeError as te:
                    # Si falla, intentar con config usando snake_case (estándar en Python SDK)
                    logger.warning(f"custom_metadata parameter failed: {te}, trying config approach...")
                    
                    # INTENTO 1: custom_metadata (snake_case)
                    upload_config['custom_metadata'] = google_metadata
                    logger.debug(f"Upload config (snake_case): {upload_config}")
                    
                    try:
                        operation = client.file_search_stores.upload_to_file_search_store(
                            file=tmp_path,
                            file_search_store_name=store_id,
                            config=upload_config
                        )
                    except Exception as e_config:
                        logger.warning(f"Config with custom_metadata failed: {e_config}")
                        # INTENTO 2: metadata (algunas versiones usan este nombre)
                        upload_config = {'metadata': google_metadata}
                        logger.debug(f"Retrying with config 'metadata': {upload_config}")
                        operation = client.file_search_stores.upload_to_file_search_store(
                            file=tmp_path,
                            file_search_store_name=store_id,
                            config=upload_config
                        )

                # Esperar a que se complete la operación (es asíncrona)
                import time
                max_wait = 120  # Máximo 2 minutos
                waited = 0
                while not operation.done and waited < max_wait:
                    time.sleep(3)
                    waited += 3
                    operation = client.operations.get(operation)
                    logger.info(f"Upload operation status: done={operation.done}, waited={waited}s")

                if not operation.done:
                    raise TimeoutError(f"Upload operation timed out after {max_wait} seconds")

                logger.info(f"Upload operation completed. Fetching document from store...")

                # Después del upload, el documento está indexado en el store
                # El File temporal se elimina automáticamente después de 48h
                # Necesitamos listar documentos para obtener información del recién subido
                pager = client.file_search_stores.documents.list(
                    parent=store_id,
                    config={"pageSize": 20}
                )

                # Buscar el documento recién subido (el más reciente)
                file_obj = None
                for doc in pager.page:
                    # El documento más reciente debería ser el nuestro
                    if not file_obj:
                        file_obj = doc
                    elif hasattr(doc, 'create_time') and hasattr(file_obj, 'create_time'):
                        if doc.create_time > file_obj.create_time:
                            file_obj = doc

                if not file_obj:
                    # Si no encontramos ningún documento, crear respuesta básica
                    logger.warning("Could not find uploaded document in list, creating basic response")
                    return DocumentResponse(
                        name=f"{store_id}/documents/unknown",
                        display_name=display_name or filename,
                        custom_metadata=metadata or {},
                        state="PENDING"
                    )

                logger.info(f"Document uploaded successfully: {file_obj.name}")

                # 4. Guardar en base de datos local para tracking de duplicados
                try:
                    # Obtener tamaño del archivo temporal
                    file_size = Path(tmp_path).stat().st_size if Path(tmp_path).exists() else None

                    doc_db = DocumentDB(
                        id=str(uuid.uuid4()),
                        document_id=file_obj.name,
                        store_id=store_id,
                        project_id=project_id,
                        filename=filename,
                        display_name=display_name or filename,
                        file_hash=file_hash,
                        file_size=file_size,
                        mime_type=getattr(file_obj, 'mime_type', None),
                        custom_metadata=metadata,
                        max_tokens_per_chunk=chunking_config.max_tokens_per_chunk if chunking_config else None,
                        max_overlap_tokens=chunking_config.max_overlap_tokens if chunking_config else None,
                        uploaded_by=uploaded_by
                    )

                    db.add(doc_db)
                    db.commit()
                    logger.info(f"Document tracked in database: {doc_db.id}")

                except Exception as db_error:
                    logger.error(f"Error saving document to database: {db_error}")
                    # No fallar el upload por error de BD, pero loguear
                    db.rollback()

                # 5. Convertir respuesta
                return DocumentResponse(
                    name=file_obj.name,
                    display_name=file_obj.display_name or filename,
                    custom_metadata=self._convert_metadata_from_google_format(
                        getattr(file_obj, 'custom_metadata', {})
                    ),
                    create_time=getattr(file_obj, 'create_time', None),
                    update_time=getattr(file_obj, 'update_time', None),
                    state=getattr(file_obj, 'state', 'INDEXED')
                )

            finally:
                # Limpiar archivo temporal y directorio
                Path(tmp_path).unlink(missing_ok=True)
                try:
                    os.rmdir(unique_dir)
                except:
                    pass  # Ignorar si el directorio no está vacío o no existe

        except DuplicateFileException:
            # Re-raise duplicate exceptions sin modificar
            raise
        except Exception as e:
            logger.error(f"Error uploading document: {e}")
            raise
        finally:
            # Cerrar sesión de base de datos
            db.close()

    def list_documents(
        self,
        store_id: str,
        page_size: int = 20,
        page_token: Optional[str] = None
    ) -> DocumentList:
        """Listar documentos en un store"""
        try:
            client = self.google_client.get_client()

            # Sintaxis correcta: client.file_search_stores.documents.list()
            config_dict = {"pageSize": page_size}
            if page_token:
                config_dict["pageToken"] = page_token

            pager = client.file_search_stores.documents.list(
                parent=store_id,
                config=config_dict
            )

            documents = []
            next_token = None

            # Iterar sobre el pager
            for doc in pager.page:
                # Debug logging para investigar problema de metadata
                if hasattr(doc, 'custom_metadata') and doc.custom_metadata:
                    logger.info(f"Document {doc.display_name} has metadata: {doc.custom_metadata}")
                else:
                    logger.debug(f"Document {doc.display_name} has NO metadata in SDK object")
                    # Intentar ver si está en otro atributo o diccionario interno
                    logger.debug(f"Doc dir: {dir(doc)}")
                
                documents.append(DocumentResponse(
                    name=doc.name,
                    display_name=doc.display_name or "Untitled",
                    custom_metadata=self._convert_metadata_from_google_format(
                        getattr(doc, 'custom_metadata', {})
                    ),
                    create_time=getattr(doc, 'create_time', None),
                    update_time=getattr(doc, 'update_time', None),
                    state=getattr(doc, 'state', 'INDEXED')
                ))

            if hasattr(pager, 'next_page_token') and pager.next_page_token:
                next_token = pager.next_page_token

            logger.info(f"Listed {len(documents)} documents from store {store_id}")

            return DocumentList(documents=documents, next_page_token=next_token)

        except Exception as e:
            logger.error(f"Error listing documents: {e}")
            raise

    def delete_document(self, store_id: str, document_id: str) -> dict:
        """Eliminar un documento"""
        try:
            client = self.google_client.get_client()

            # Sintaxis correcta: client.file_search_stores.documents.delete()
            # force=True es necesario para eliminar documentos con contenido indexado
            client.file_search_stores.documents.delete(
                name=document_id,  # El ID completo ya incluye el store
                config={"force": True}
            )

            logger.info(f"Document deleted: {document_id}")

            return {"success": True, "message": f"Document {document_id} deleted successfully"}

        except Exception as e:
            logger.error(f"Error deleting document: {e}")
            raise

    def update_document(
        self,
        store_id: str,
        document_id: str,
        file_content: BinaryIO,
        filename: str,
        display_name: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> DocumentResponse:
        """Actualizar un documento (eliminar y recrear)"""
        try:
            # Primero eliminar el documento existente
            self.delete_document(store_id, document_id)

            # Luego subir el nuevo
            return self.upload_document(
                store_id=store_id,
                file_content=file_content,
                filename=filename,
                display_name=display_name,
                metadata=metadata
            )

        except Exception as e:
            logger.error(f"Error updating document: {e}")
            raise


# Instancia global del servicio
document_service = DocumentService()
