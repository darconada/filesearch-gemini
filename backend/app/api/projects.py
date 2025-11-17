"""Endpoints para gestión de proyectos"""
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.project import ProjectCreate, ProjectUpdate, Project, ProjectList
from app.services.project_service import project_service
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/projects", tags=["projects"])


@router.post("", response_model=Project, status_code=201)
async def create_project(project: ProjectCreate, db: Session = Depends(get_db)):
    """
    Crear un nuevo proyecto de Google AI Studio

    El proyecto contendrá una API key y podrá tener sus propios stores.
    Si es el primer proyecto, se marcará como activo automáticamente.
    """
    try:
        return project_service.create_project(db, project)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating project: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("", response_model=ProjectList)
async def list_projects(db: Session = Depends(get_db)):
    """Listar todos los proyectos configurados"""
    try:
        return project_service.list_projects(db)
    except Exception as e:
        logger.error(f"Error listing projects: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/active", response_model=Project)
async def get_active_project(db: Session = Depends(get_db)):
    """Obtener el proyecto activo actual"""
    try:
        project = project_service.get_active_project(db)
        if not project:
            raise HTTPException(status_code=404, detail="No active project found. Please create and activate a project.")
        return project
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting active project: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{project_id}", response_model=Project)
async def get_project(project_id: int, db: Session = Depends(get_db)):
    """Obtener un proyecto específico por ID"""
    try:
        return project_service.get_project(db, project_id)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting project: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{project_id}", response_model=Project)
async def update_project(
    project_id: int,
    project: ProjectUpdate,
    db: Session = Depends(get_db)
):
    """Actualizar un proyecto (nombre, descripción o API key)"""
    try:
        return project_service.update_project(db, project_id, project)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating project: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{project_id}/activate", response_model=Project)
async def activate_project(project_id: int, db: Session = Depends(get_db)):
    """
    Activar un proyecto

    Esto desactivará todos los demás proyectos y reconfigurará el cliente
    de Google para usar la API key de este proyecto.
    """
    try:
        return project_service.activate_project(db, project_id)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error activating project: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{project_id}")
async def delete_project(project_id: int, db: Session = Depends(get_db)):
    """
    Eliminar un proyecto

    Si era el proyecto activo, se activará otro automáticamente (si existe).
    """
    try:
        return project_service.delete_project(db, project_id)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting project: {e}")
        raise HTTPException(status_code=500, detail=str(e))
