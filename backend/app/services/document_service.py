"""Servicio para gestión de documentos en File Search"""
from typing import Optional, BinaryIO, Dict, Any
from app.models.document import DocumentResponse, DocumentList, ChunkingConfig
from app.services.google_client import google_client
import logging
import tempfile
from pathlib import Path

logger = logging.getLogger(__name__)


class DocumentService:
    """Servicio para operaciones con documentos"""

    def __init__(self):
        self.google_client = google_client

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
        chunking_config: Optional[ChunkingConfig] = None
    ) -> DocumentResponse:
        """Subir un documento al store"""
        try:
            client = self.google_client.get_client()

            # Guardar el archivo temporalmente con el nombre original
            # Esto es importante porque Google File Search usa el nombre del archivo físico
            # Añadimos un UUID para evitar colisiones si múltiples usuarios suben archivos con el mismo nombre
            import os
            import uuid
            tmp_dir = tempfile.gettempdir()
            unique_dir = os.path.join(tmp_dir, f"filesearch_{uuid.uuid4().hex[:8]}")
            os.makedirs(unique_dir, exist_ok=True)
            tmp_path = os.path.join(unique_dir, filename)

            with open(tmp_path, 'wb') as tmp_file:
                tmp_file.write(file_content.read())

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

                # Convertir respuesta
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

        except Exception as e:
            logger.error(f"Error uploading document: {e}")
            raise

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
