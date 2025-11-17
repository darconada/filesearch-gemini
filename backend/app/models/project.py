"""Modelos Pydantic para proyectos"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class ProjectCreate(BaseModel):
    """Request para crear un proyecto"""
    name: str = Field(..., min_length=1, max_length=100, description="Nombre del proyecto")
    api_key: str = Field(..., min_length=1, description="Google API Key del proyecto")
    description: Optional[str] = Field(None, max_length=500, description="Descripción opcional")


class ProjectUpdate(BaseModel):
    """Request para actualizar un proyecto"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    api_key: Optional[str] = Field(None, min_length=1)
    description: Optional[str] = Field(None, max_length=500)


class Project(BaseModel):
    """Response de un proyecto"""
    id: int
    name: str
    description: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime]

    # No exponemos la API key en las responses por seguridad
    # Solo mostramos si está configurada
    has_api_key: bool = True

    class Config:
        from_attributes = True


class ProjectList(BaseModel):
    """Lista de proyectos"""
    projects: list[Project]
    active_project_id: Optional[int] = None
