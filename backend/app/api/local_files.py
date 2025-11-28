"""API endpoints para sincronización de archivos locales"""
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.local_file import (
    LocalFileLinkCreate,
    LocalFileLinkResponse,
    LocalFileLinkList,
    LocalFileSyncRequest
)
from app.services.local_file_service import local_file_service
from app.services.audit_service import audit_service
from app.models.db_models import AuditAction
import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/local-files",
    tags=["local-files"]
)


@router.post("/links", response_model=LocalFileLinkResponse, status_code=201)
async def create_local_file_link(
    link_data: LocalFileLinkCreate,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Crear un vínculo para sincronizar un archivo local con File Search

    - **local_file_path**: Ruta absoluta al archivo local
    - **store_id**: ID del vector store de destino

    El archivo será validado pero NO será sincronizado automáticamente.
    Use el endpoint de sync para subir el archivo a File Search.
    """
    try:
        result = local_file_service.create_link(link_data, db)

        # Audit log
        audit_service.log(
            db=db,
            action=AuditAction.LOCAL_FILE_LINK_CREATE,
            resource_type="local_file",
            resource_id=result.id,
            details={
                "file_name": result.file_name,
                "file_path": result.local_file_path,
                "store_id": result.store_id
            },
            request=request
        )

        return result
    except ValueError as e:
        audit_service.log(
            db=db,
            action=AuditAction.LOCAL_FILE_LINK_CREATE,
            resource_type="local_file",
            details={"file_path": link_data.local_file_path},
            success=False,
            error_message=str(e),
            request=request
        )
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating local file link: {e}")
        audit_service.log(
            db=db,
            action=AuditAction.LOCAL_FILE_LINK_CREATE,
            resource_type="local_file",
            success=False,
            error_message=str(e),
            request=request
        )
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/links", response_model=LocalFileLinkList)
async def list_local_file_links(
    store_id: str = Query(None, description="Filtrar por store_id"),
    project_id: int = Query(None, description="Filtrar por project_id"),
    all_projects: bool = Query(False, description="Mostrar archivos de todos los proyectos"),
    db: Session = Depends(get_db)
):
    """
    Listar todos los vínculos de archivos locales

    Por defecto muestra solo archivos del proyecto activo.
    Usa all_projects=true para ver archivos de todos los proyectos.
    """
    try:
        return local_file_service.list_links(
            db,
            store_id=store_id,
            project_id=project_id,
            all_projects=all_projects
        )
    except Exception as e:
        logger.error(f"Error listing local file links: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/links/{link_id}", response_model=LocalFileLinkResponse)
async def get_local_file_link(
    link_id: str,
    db: Session = Depends(get_db)
):
    """
    Obtener un vínculo específico por ID
    """
    link = local_file_service.get_link(link_id, db)
    if not link:
        raise HTTPException(status_code=404, detail=f"Link {link_id} not found")
    return link


@router.delete("/links/{link_id}")
async def delete_local_file_link(
    link_id: str,
    delete_from_store: bool = Query(False, description="También eliminar del File Search store"),
    db: Session = Depends(get_db)
):
    """
    Eliminar un vínculo de archivo local

    - **delete_from_store**: Si es True, también elimina el documento del File Search store
    """
    try:
        return local_file_service.delete_link(link_id, db, delete_from_store=delete_from_store)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error deleting local file link: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/links/{link_id}/sync", response_model=LocalFileLinkResponse)
async def sync_local_file(
    link_id: str,
    request: Request,
    sync_request: LocalFileSyncRequest = LocalFileSyncRequest(),
    db: Session = Depends(get_db)
):
    """
    Sincronizar un archivo local con File Search

    El servicio:
    1. Verifica que el archivo existe
    2. Calcula hash SHA256 del contenido
    3. Compara con última sincronización
    4. Si cambió (o force=True): sube el archivo a File Search
    5. Si ya existe un documento, lo reemplaza (delete + create)

    - **force**: Si es True, fuerza la sincronización aunque no haya cambios detectados
    """
    try:
        result = local_file_service.sync_file(link_id, sync_request.force, db)

        # Audit log
        audit_service.log(
            db=db,
            action=AuditAction.LOCAL_FILE_SYNC,
            resource_type="local_file",
            resource_id=link_id,
            details={
                "file_name": result.file_name,
                "file_path": result.local_file_path,
                "store_id": result.store_id,
                "status": result.status,
                "force": sync_request.force
            },
            request=request
        )

        return result
    except ValueError as e:
        audit_service.log(
            db=db,
            action=AuditAction.LOCAL_FILE_SYNC,
            resource_type="local_file",
            resource_id=link_id,
            success=False,
            error_message=str(e),
            request=request
        )
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error syncing local file: {e}")
        audit_service.log(
            db=db,
            action=AuditAction.LOCAL_FILE_SYNC,
            resource_type="local_file",
            resource_id=link_id,
            success=False,
            error_message=str(e),
            request=request
        )
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sync-all", response_model=LocalFileLinkList)
async def sync_all_local_files(
    store_id: str = Query(None, description="Filtrar por store_id"),
    project_id: int = Query(None, description="Filtrar por project_id"),
    all_projects: bool = Query(False, description="Sincronizar archivos de todos los proyectos"),
    db: Session = Depends(get_db)
):
    """
    Sincronizar todos los archivos locales

    Por defecto sincroniza solo archivos del proyecto activo.
    Usa all_projects=true para sincronizar archivos de todos los proyectos.
    Solo sincroniza archivos que hayan cambiado.
    """
    try:
        links = local_file_service.sync_all(
            db,
            store_id=store_id,
            project_id=project_id,
            all_projects=all_projects
        )
        return LocalFileLinkList(links=links)
    except Exception as e:
        logger.error(f"Error syncing all local files: {e}")
        raise HTTPException(status_code=500, detail=str(e))
