"""API endpoints para actualización/reemplazo de archivos"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.file_update import FileReplaceResponse, FileVersionHistory
from app.services.file_update_service import file_update_service
import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/file-updates",
    tags=["file-updates"]
)


@router.post("/replace/{link_id}", response_model=FileReplaceResponse)
async def replace_file(
    link_id: str,
    file: UploadFile = File(..., description="Nuevo archivo para reemplazar"),
    db: Session = Depends(get_db)
):
    """
    Reemplazar/actualizar un archivo existente en File Search

    Este endpoint:
    1. Elimina el documento viejo del File Search store
    2. Sube la nueva versión del archivo
    3. Mantiene el historial de versiones en la BD
    4. Incrementa el contador de versión

    Funciona tanto para archivos de Drive como archivos locales.

    **IMPORTANTE**: Como la API de Gemini no permite actualizar archivos,
    este endpoint implementa la estrategia "delete + re-create".
    El document_id cambiará, pero mantenemos el vínculo lógico.

    Args:
        link_id: ID del link (Drive o Local)
        file: Archivo nuevo a subir

    Returns:
        FileReplaceResponse con información de la actualización
    """
    try:
        # Leer contenido del archivo
        file_content = await file.read()

        if not file_content:
            raise HTTPException(status_code=400, detail="File is empty")

        # Llamar al servicio
        result = file_update_service.replace_file(
            link_id=link_id,
            new_file_content=file_content,
            db=db,
            filename=file.filename
        )

        return result

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error replacing file for link {link_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history/{link_id}", response_model=FileVersionHistory)
async def get_file_version_history(
    link_id: str,
    db: Session = Depends(get_db)
):
    """
    Obtener el historial de versiones de un archivo

    Retorna:
    - Versión actual y document_id actual
    - Lista de versiones anteriores con sus document_ids
    - Timestamps de creación y actualización

    Args:
        link_id: ID del link (Drive o Local)

    Returns:
        FileVersionHistory con el historial completo
    """
    try:
        return file_update_service.get_version_history(link_id, db)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting version history for link {link_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
