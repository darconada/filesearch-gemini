"""API para navegación de archivos del servidor"""
from fastapi import APIRouter, HTTPException, Query
from app.models.file_browser import DirectoryListing, FileSystemItem
from app.services.file_browser_service import file_browser_service
from typing import Optional
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/file-browser", tags=["file-browser"])


@router.get("/list", response_model=DirectoryListing)
async def list_directory(
    path: Optional[str] = Query(None, description="Directory path to list. If not provided, lists home directory")
):
    """
    Listar contenido de un directorio del servidor
    
    Restricciones de seguridad:
    - No permite acceso a directorios del sistema (/etc, /root, /sys, etc.)
    - Solo directorios con permisos de lectura
    """
    try:
        return file_browser_service.list_directory(path)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except (PermissionError, NotADirectoryError) as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        logger.error(f"Error listing directory: {e}")
        raise HTTPException(status_code=500, detail=f"Error listing directory: {e}")


@router.get("/file-info", response_model=FileSystemItem)
async def get_file_info(
    path: str = Query(..., description="File path")
):
    """Obtener información de un archivo específico"""
    try:
        return file_browser_service.get_file_info(path)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting file info: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting file info: {e}")
