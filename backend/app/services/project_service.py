"""Servicio para gestionar proyectos"""
import logging
from typing import Optional, List
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.db_models import ProjectDB
from app.models.project import ProjectCreate, ProjectUpdate, Project, ProjectList
from app.services.google_client import google_client

logger = logging.getLogger(__name__)


class ProjectService:
    """Servicio para gestionar proyectos de Google AI Studio"""

    def create_project(self, db: Session, project_data: ProjectCreate) -> Project:
        """Crear un nuevo proyecto"""
        # Verificar que no exista otro proyecto con el mismo nombre
        existing = db.query(ProjectDB).filter(ProjectDB.name == project_data.name).first()
        if existing:
            raise HTTPException(status_code=400, detail=f"Project '{project_data.name}' already exists")

        # Validar la API key intentando configurar el cliente
        try:
            google_client.configure(project_data.api_key)
            is_valid, error = google_client.test_connection()
            if not is_valid:
                raise HTTPException(status_code=400, detail=f"Invalid API key: {error}")
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error validating API key: {str(e)}")

        # Si este es el primer proyecto, marcarlo como activo
        has_projects = db.query(ProjectDB).first() is not None
        is_first = not has_projects

        # Crear el proyecto
        db_project = ProjectDB(
            name=project_data.name,
            api_key=project_data.api_key,
            description=project_data.description,
            is_active=is_first  # El primer proyecto se marca como activo automáticamente
        )

        db.add(db_project)
        db.commit()
        db.refresh(db_project)

        logger.info(f"Project created: {project_data.name} (ID: {db_project.id}, active: {db_project.is_active})")

        # Si es el primer proyecto y se marcó como activo, configurar el cliente
        if is_first:
            google_client.configure(db_project.api_key)
            logger.info(f"Google client configured with project: {db_project.name}")

        return self._to_project_model(db_project)

    def list_projects(self, db: Session) -> ProjectList:
        """Listar todos los proyectos"""
        projects = db.query(ProjectDB).order_by(ProjectDB.created_at.desc()).all()
        active_project = db.query(ProjectDB).filter(ProjectDB.is_active == True).first()

        return ProjectList(
            projects=[self._to_project_model(p) for p in projects],
            active_project_id=active_project.id if active_project else None
        )

    def get_project(self, db: Session, project_id: int) -> Project:
        """Obtener un proyecto por ID"""
        project = db.query(ProjectDB).filter(ProjectDB.id == project_id).first()
        if not project:
            raise HTTPException(status_code=404, detail=f"Project {project_id} not found")

        return self._to_project_model(project)

    def get_active_project(self, db: Session) -> Optional[Project]:
        """Obtener el proyecto activo actual"""
        project = db.query(ProjectDB).filter(ProjectDB.is_active == True).first()
        if not project:
            return None

        return self._to_project_model(project)

    def update_project(self, db: Session, project_id: int, project_data: ProjectUpdate) -> Project:
        """Actualizar un proyecto"""
        project = db.query(ProjectDB).filter(ProjectDB.id == project_id).first()
        if not project:
            raise HTTPException(status_code=404, detail=f"Project {project_id} not found")

        # Si se actualiza el nombre, verificar que no exista otro con ese nombre
        if project_data.name and project_data.name != project.name:
            existing = db.query(ProjectDB).filter(
                ProjectDB.name == project_data.name,
                ProjectDB.id != project_id
            ).first()
            if existing:
                raise HTTPException(status_code=400, detail=f"Project '{project_data.name}' already exists")
            project.name = project_data.name

        # Si se actualiza la API key, validarla
        if project_data.api_key:
            try:
                google_client.configure(project_data.api_key)
                is_valid, error = google_client.test_connection()
                if not is_valid:
                    raise HTTPException(status_code=400, detail=f"Invalid API key: {error}")
                project.api_key = project_data.api_key

                # Si este es el proyecto activo, reconfigurar el cliente
                if project.is_active:
                    google_client.configure(project.api_key)
                    logger.info(f"Google client reconfigured with updated API key for project: {project.name}")

            except HTTPException:
                raise
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"Error validating API key: {str(e)}")

        if project_data.description is not None:
            project.description = project_data.description

        db.commit()
        db.refresh(project)

        logger.info(f"Project updated: {project.name} (ID: {project.id})")

        return self._to_project_model(project)

    def activate_project(self, db: Session, project_id: int) -> Project:
        """Activar un proyecto (desactiva todos los demás)"""
        project = db.query(ProjectDB).filter(ProjectDB.id == project_id).first()
        if not project:
            raise HTTPException(status_code=404, detail=f"Project {project_id} not found")

        # Desactivar todos los proyectos
        db.query(ProjectDB).update({ProjectDB.is_active: False})

        # Activar el proyecto seleccionado
        project.is_active = True
        db.commit()
        db.refresh(project)

        # Reconfigurar el cliente de Google con la API key del nuevo proyecto activo
        try:
            google_client.configure(project.api_key)
            logger.info(f"Google client configured with project: {project.name}")
        except Exception as e:
            logger.error(f"Error configuring Google client: {e}")
            raise HTTPException(status_code=500, detail=f"Error activating project: {str(e)}")

        return self._to_project_model(project)

    def delete_project(self, db: Session, project_id: int) -> dict:
        """Eliminar un proyecto"""
        project = db.query(ProjectDB).filter(ProjectDB.id == project_id).first()
        if not project:
            raise HTTPException(status_code=404, detail=f"Project {project_id} not found")

        was_active = project.is_active
        project_name = project.name

        db.delete(project)
        db.commit()

        logger.info(f"Project deleted: {project_name} (ID: {project_id})")

        # Si era el proyecto activo, activar otro si existe
        if was_active:
            next_project = db.query(ProjectDB).first()
            if next_project:
                next_project.is_active = True
                db.commit()
                google_client.configure(next_project.api_key)
                logger.info(f"Activated next project: {next_project.name}")
            else:
                logger.warning("No projects remaining, Google client not configured")

        return {"message": f"Project '{project_name}' deleted successfully"}

    def _to_project_model(self, db_project: ProjectDB) -> Project:
        """Convertir ProjectDB a Project (sin exponer API key)"""
        return Project(
            id=db_project.id,
            name=db_project.name,
            description=db_project.description,
            is_active=db_project.is_active,
            created_at=db_project.created_at,
            updated_at=db_project.updated_at,
            has_api_key=bool(db_project.api_key)
        )


# Instancia global del servicio
project_service = ProjectService()
