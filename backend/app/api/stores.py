"""Endpoints para gestión de stores"""
from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from app.models.store import StoreCreate, StoreResponse, StoreList
from app.services.store_service import store_service
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/stores", tags=["stores"])


@router.post("", response_model=StoreResponse, status_code=201)
async def create_store(store_data: StoreCreate) -> StoreResponse:
    """Crear un nuevo File Search store"""
    try:
        return store_service.create_store(store_data)
    except Exception as e:
        logger.error(f"Error in create_store endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("", response_model=StoreList)
async def list_stores(
    page_size: int = Query(20, ge=1, le=20),
    page_token: Optional[str] = Query(None)
) -> StoreList:
    """Listar todos los stores"""
    try:
        return store_service.list_stores(page_size=page_size, page_token=page_token)
    except Exception as e:
        logger.error(f"Error in list_stores endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{store_id:path}", response_model=StoreResponse)
async def get_store(store_id: str) -> StoreResponse:
    """Obtener un store específico"""
    try:
        return store_service.get_store(store_id)
    except Exception as e:
        logger.error(f"Error in get_store endpoint: {e}")
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/{store_id:path}")
async def delete_store(store_id: str) -> dict:
    """Eliminar un store"""
    try:
        return store_service.delete_store(store_id)
    except Exception as e:
        logger.error(f"Error in delete_store endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))
