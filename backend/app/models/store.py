"""Modelos para File Search Stores"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class StoreCreate(BaseModel):
    """Request para crear un store"""
    display_name: str = Field(..., min_length=1, max_length=256, description="Nombre legible del store")


class StoreResponse(BaseModel):
    """Response de un store"""
    name: str = Field(..., description="ID interno del store (ej: fileSearchStores/...)")
    display_name: str = Field(..., description="Nombre legible")
    create_time: Optional[datetime] = Field(None, description="Fecha de creación")
    update_time: Optional[datetime] = Field(None, description="Fecha de actualización")


class StoreList(BaseModel):
    """Lista de stores"""
    stores: list[StoreResponse]
    next_page_token: Optional[str] = None
