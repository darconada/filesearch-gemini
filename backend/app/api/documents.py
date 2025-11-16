"""Endpoints para gestión de documentos"""
from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Query
from typing import Optional, Dict, Any
from app.models.document import DocumentResponse, DocumentList, ChunkingConfig
from app.services.document_service import document_service
import logging
import json

logger = logging.getLogger(__name__)

# Usar rutas específicas sin :path después de literal
router = APIRouter(tags=["documents"])


@router.post("/stores/fileSearchStores/{store_id}/documents", response_model=DocumentResponse, status_code=201)
async def upload_document(
    store_id: str,
    file: UploadFile = File(...),
    display_name: Optional[str] = Form(None),
    metadata: Optional[str] = Form(None),  # JSON string
    max_tokens_per_chunk: Optional[int] = Form(None),
    max_overlap_tokens: Optional[int] = Form(None)
) -> DocumentResponse:
    """Subir un documento al store"""
    try:
        # Construir store_id completo
        full_store_id = f"fileSearchStores/{store_id}"
        logger.info(f"upload_document: store_id='{full_store_id}'")

        # Parsear metadata si se proporciona
        metadata_dict: Dict[str, Any] = {}
        if metadata:
            try:
                metadata_dict = json.loads(metadata)
            except json.JSONDecodeError:
                raise HTTPException(status_code=400, detail="Metadata inválida: debe ser JSON válido")

        # Preparar chunking config
        chunking_config = None
        if max_tokens_per_chunk or max_overlap_tokens:
            chunking_config = ChunkingConfig(
                max_tokens_per_chunk=max_tokens_per_chunk,
                max_overlap_tokens=max_overlap_tokens
            )

        # Subir documento
        return document_service.upload_document(
            store_id=full_store_id,
            file_content=file.file,
            filename=file.filename or "untitled",
            display_name=display_name,
            metadata=metadata_dict,
            chunking_config=chunking_config
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in upload_document endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stores/fileSearchStores/{store_id}/documents", response_model=DocumentList)
async def list_documents(
    store_id: str,
    page_size: int = Query(20, ge=1, le=20),
    page_token: Optional[str] = Query(None)
) -> DocumentList:
    """Listar documentos en un store"""
    try:
        # Construir store_id completo
        full_store_id = f"fileSearchStores/{store_id}"
        logger.info(f"========================================")
        logger.info(f"list_documents ENDPOINT CALLED")
        logger.info(f"  store_id parameter: '{store_id}'")
        logger.info(f"  full_store_id: '{full_store_id}'")
        logger.info(f"  page_size: {page_size}")
        logger.info(f"========================================")

        result = document_service.list_documents(
            store_id=full_store_id,
            page_size=page_size,
            page_token=page_token
        )

        logger.info(f"list_documents SUCCESS: {len(result.documents)} documents found")
        return result
    except Exception as e:
        logger.error(f"Error in list_documents endpoint: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/stores/fileSearchStores/{store_id}/documents/{doc_id}")
async def delete_document(store_id: str, doc_id: str) -> dict:
    """Eliminar un documento"""
    try:
        # Construir IDs completos
        full_store_id = f"fileSearchStores/{store_id}"
        full_document_id = f"fileSearchStores/{store_id}/documents/{doc_id}"
        logger.info(f"delete_document: store_id='{full_store_id}', document_id='{full_document_id}'")

        return document_service.delete_document(full_store_id, full_document_id)
    except Exception as e:
        logger.error(f"Error in delete_document endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/stores/fileSearchStores/{store_id}/documents/{doc_id}", response_model=DocumentResponse)
async def update_document(
    store_id: str,
    doc_id: str,
    file: UploadFile = File(...),
    display_name: Optional[str] = Form(None),
    metadata: Optional[str] = Form(None)  # JSON string
) -> DocumentResponse:
    """Actualizar un documento (eliminar y recrear)"""
    try:
        # Construir IDs completos
        full_store_id = f"fileSearchStores/{store_id}"
        full_document_id = f"fileSearchStores/{store_id}/documents/{doc_id}"
        logger.info(f"update_document: store_id='{full_store_id}', document_id='{full_document_id}'")

        # Parsear metadata
        metadata_dict: Dict[str, Any] = {}
        if metadata:
            try:
                metadata_dict = json.loads(metadata)
            except json.JSONDecodeError:
                raise HTTPException(status_code=400, detail="Metadata inválida: debe ser JSON válido")

        # Actualizar documento
        return document_service.update_document(
            store_id=full_store_id,
            document_id=full_document_id,
            file_content=file.file,
            filename=file.filename or "untitled",
            display_name=display_name,
            metadata=metadata_dict
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in update_document endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))
