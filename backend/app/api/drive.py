"""Endpoints para sincronización con Google Drive (base futura)"""
from fastapi import APIRouter, HTTPException
from app.models.drive import (
    DriveLinkCreate,
    DriveLinkResponse,
    DriveLinkList,
    DriveSyncRequest
)
from app.services.drive_service import drive_service
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/drive-links", tags=["drive"])


@router.post("", response_model=DriveLinkResponse, status_code=201)
async def create_drive_link(link_data: DriveLinkCreate) -> DriveLinkResponse:
    """Crear un vínculo Drive -> File Search"""
    try:
        return drive_service.create_link(link_data)
    except Exception as e:
        logger.error(f"Error in create_drive_link endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("", response_model=DriveLinkList)
async def list_drive_links() -> DriveLinkList:
    """Listar todos los vínculos Drive"""
    try:
        return drive_service.list_links()
    except Exception as e:
        logger.error(f"Error in list_drive_links endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{link_id}", response_model=DriveLinkResponse)
async def get_drive_link(link_id: str) -> DriveLinkResponse:
    """Obtener un vínculo específico"""
    try:
        link = drive_service.get_link(link_id)
        if not link:
            raise HTTPException(status_code=404, detail=f"Link {link_id} not found")
        return link
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_drive_link endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{link_id}")
async def delete_drive_link(link_id: str) -> dict:
    """Eliminar un vínculo"""
    try:
        return drive_service.delete_link(link_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error in delete_drive_link endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{link_id}/sync-now", response_model=DriveLinkResponse)
async def sync_drive_link(link_id: str, sync_request: DriveSyncRequest) -> DriveLinkResponse:
    """Sincronizar manualmente un vínculo (STUB - base futura)"""
    try:
        return drive_service.sync_link(link_id, force=sync_request.force)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error in sync_drive_link endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))
