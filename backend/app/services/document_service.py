"""Servicio para gestión de documentos en File Search"""
import google.generativeai as genai
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
        self.client = google_client

    def _convert_metadata_to_google_format(self, metadata: Dict[str, Any]) -> list:
        """Convertir metadata de formato simple a formato Google"""
        google_metadata = []

        for key, value in metadata.items():
            if isinstance(value, (int, float)):
                google_metadata.append({
                    "key": key,
                    "value": {"numeric_value": float(value)}
                })
            else:
                google_metadata.append({
                    "key": key,
                    "value": {"string_value": str(value)}
                })

        return google_metadata

    def _convert_metadata_from_google_format(self, google_metadata) -> Dict[str, Any]:
        """Convertir metadata de formato Google a formato simple"""
        metadata = {}

        if not google_metadata:
            return metadata

        for item in google_metadata:
            key = item.get("key") or item.get("name")
            value_obj = item.get("value", {})

            if "numeric_value" in value_obj:
                metadata[key] = value_obj["numeric_value"]
            elif "string_value" in value_obj:
                metadata[key] = value_obj["string_value"]

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
            if not self.client.is_configured():
                self.client.configure()

            # Guardar el archivo temporalmente
            with tempfile.NamedTemporaryFile(delete=False, suffix=Path(filename).suffix) as tmp_file:
                tmp_file.write(file_content.read())
                tmp_path = tmp_file.name

            try:
                # Preparar metadata
                custom_metadata = None
                if metadata:
                    custom_metadata = self._convert_metadata_to_google_format(metadata)

                # Preparar configuración de chunking
                chunking_params = {}
                if chunking_config:
                    if chunking_config.max_tokens_per_chunk:
                        chunking_params["max_chunk_size_tokens"] = chunking_config.max_tokens_per_chunk
                    if chunking_config.max_overlap_tokens:
                        chunking_params["chunk_overlap_tokens"] = chunking_config.max_overlap_tokens

                # Subir usando el método conveniente
                upload_params = {
                    "path": tmp_path,
                    "store_name": store_id,
                    "display_name": display_name or filename
                }

                if custom_metadata:
                    upload_params["custom_metadata"] = custom_metadata

                if chunking_params:
                    upload_params.update(chunking_params)

                file_obj = genai.upload_to_file_search_store(**upload_params)

                logger.info(f"Document uploaded: {file_obj.name}")

                # Convertir respuesta
                return DocumentResponse(
                    name=file_obj.name,
                    display_name=file_obj.display_name or filename,
                    custom_metadata=self._convert_metadata_from_google_format(
                        getattr(file_obj, 'custom_metadata', None)
                    ),
                    create_time=getattr(file_obj, 'create_time', None),
                    update_time=getattr(file_obj, 'update_time', None),
                    state=getattr(file_obj, 'state', 'INDEXED')
                )

            finally:
                # Limpiar archivo temporal
                Path(tmp_path).unlink(missing_ok=True)

        except Exception as e:
            logger.error(f"Error uploading document: {e}")
            raise

    def list_documents(
        self,
        store_id: str,
        page_size: int = 50,
        page_token: Optional[str] = None
    ) -> DocumentList:
        """Listar documentos en un store"""
        try:
            if not self.client.is_configured():
                self.client.configure()

            kwargs = {
                "store_name": store_id,
                "page_size": page_size
            }
            if page_token:
                kwargs["page_token"] = page_token

            docs_page = genai.list_file_search_store_documents(**kwargs)

            documents = []
            next_token = None

            for doc in docs_page:
                documents.append(DocumentResponse(
                    name=doc.name,
                    display_name=doc.display_name or "Untitled",
                    custom_metadata=self._convert_metadata_from_google_format(
                        getattr(doc, 'custom_metadata', None)
                    ),
                    create_time=getattr(doc, 'create_time', None),
                    update_time=getattr(doc, 'update_time', None),
                    state=getattr(doc, 'state', 'INDEXED')
                ))

            if hasattr(docs_page, 'next_page_token'):
                next_token = docs_page.next_page_token

            logger.info(f"Listed {len(documents)} documents from store {store_id}")

            return DocumentList(documents=documents, next_page_token=next_token)

        except Exception as e:
            logger.error(f"Error listing documents: {e}")
            raise

    def delete_document(self, store_id: str, document_id: str) -> dict:
        """Eliminar un documento"""
        try:
            if not self.client.is_configured():
                self.client.configure()

            genai.delete_file_search_store_document(
                store_name=store_id,
                document_name=document_id,
                force=True
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
