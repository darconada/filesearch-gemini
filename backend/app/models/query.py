"""Modelos para consultas RAG"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any


class QueryRequest(BaseModel):
    """Request de consulta RAG"""
    question: str = Field(..., min_length=1, description="Pregunta en lenguaje natural")
    store_ids: List[str] = Field(..., min_items=1, description="IDs de los stores a consultar")
    metadata_filter: Optional[str] = Field(None, description="Filtro opcional por metadata (ej: autor='Robert Graves')")


class DocumentSource(BaseModel):
    """Documento fuente usado en la respuesta"""
    document_display_name: Optional[str] = Field(None, description="Nombre del documento")
    document_id: Optional[str] = Field(None, description="ID del documento")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Metadatos del documento")
    chunk_text: Optional[str] = Field(None, description="Fragmento de texto relevante")
    relevance_score: Optional[float] = Field(None, description="Score de relevancia")


class QueryResponse(BaseModel):
    """Response de consulta RAG"""
    answer: str = Field(..., description="Respuesta generada por el modelo")
    sources: List[DocumentSource] = Field(default_factory=list, description="Documentos fuente usados")
    model_used: Optional[str] = Field(None, description="Modelo usado para la generación")
