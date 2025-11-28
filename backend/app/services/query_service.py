"""Servicio para consultas RAG con File Search"""
from typing import Optional, List
from app.models.query import QueryRequest, QueryResponse, DocumentSource
from app.services.google_client import google_client
from app.config import settings
from app.database import SessionLocal
from app.models.db_models import ProjectDB
import logging

logger = logging.getLogger(__name__)


class QueryService:
    """Servicio para ejecutar consultas RAG"""

    def __init__(self):
        self.google_client = google_client

    def _get_model_to_use(self) -> str:
        """Obtener el modelo a usar: del proyecto activo o el default global"""
        db = SessionLocal()
        try:
            active_project = db.query(ProjectDB).filter(ProjectDB.is_active == True).first()
            if active_project and active_project.model_name:
                logger.info(f"Using model from active project: {active_project.model_name}")
                return active_project.model_name
            else:
                logger.info(f"Using default global model: {settings.model_name}")
                return settings.model_name
        finally:
            db.close()

    def _parse_metadata_filter(self, filter_str: str) -> str:
        """
        Parsear y normalizar el filtro de metadata al formato correcto de Google AIP-160

        Acepta:
        - "type: Framework" → "type=Framework"
        - "type=Framework" → "type=Framework"
        - "author: Robert Graves" → 'author="Robert Graves"'

        Retorna el formato correcto para la API de Google
        """
        if not filter_str or not filter_str.strip():
            return ""

        # Normalizar: reemplazar ":" por "=" si existe
        normalized = filter_str.replace(": ", "=").replace(":", "=")

        # Si tiene "=" procesar el key y value
        if "=" in normalized:
            parts = normalized.split("=", 1)  # Split solo en el primer =
            if len(parts) == 2:
                key = parts[0].strip()
                value = parts[1].strip()

                # Si el valor tiene espacios y no está entre comillas, añadirlas
                if " " in value and not (value.startswith('"') and value.endswith('"')):
                    value = f'"{value}"'

                return f"{key}={value}"

        return normalized

    def execute_query(self, query: QueryRequest) -> QueryResponse:
        """Ejecutar una consulta RAG usando File Search"""
        try:
            from google.genai import types

            client = self.google_client.get_client()

            # Preparar FileSearch tool según documentación oficial
            file_search_tool = types.Tool(
                file_search=types.FileSearch(
                    file_search_store_names=query.store_ids
                )
            )

            # Añadir filtro de metadata si se proporciona
            if query.metadata_filter:
                # Normalizar el filtro al formato correcto (AIP-160)
                normalized_filter = self._parse_metadata_filter(query.metadata_filter)
                logger.info(f"Metadata filter - Original: '{query.metadata_filter}' → Normalized: '{normalized_filter}'")
                file_search_tool.file_search.metadata_filter = normalized_filter

            # Configurar GenerateContentConfig - primero solo con tools
            # Los parámetros de generación pueden no ser soportados en esta versión
            config = types.GenerateContentConfig(
                tools=[file_search_tool]
            )

            # Obtener el modelo a usar (del proyecto activo o default global)
            model_to_use = self._get_model_to_use()

            # Ejecutar generateContent con el nuevo SDK
            response = client.models.generate_content(
                model=model_to_use,
                contents=query.question,
                config=config
            )

            # Extraer la respuesta
            answer_text = response.text if hasattr(response, 'text') and response.text else "No se pudo generar una respuesta."

            # Extraer grounding metadata (fuentes)
            sources = []
            if hasattr(response, 'candidates') and response.candidates:
                candidate = response.candidates[0]

                # Intentar extraer grounding metadata
                if hasattr(candidate, 'grounding_metadata'):
                    grounding = candidate.grounding_metadata

                    # Procesar chunks de grounding
                    if hasattr(grounding, 'grounding_chunks'):
                        for chunk in grounding.grounding_chunks:
                            source = DocumentSource(metadata={})

                            # Extraer información del chunk
                            if hasattr(chunk, 'retrieved_context'):
                                context = chunk.retrieved_context

                                # Obtener URI del documento
                                if hasattr(context, 'uri'):
                                    source.document_id = context.uri

                                # Obtener título/nombre
                                if hasattr(context, 'title'):
                                    source.document_display_name = context.title

                                # Obtener texto del chunk
                                if hasattr(context, 'text'):
                                    source.chunk_text = context.text[:500]  # Limitar a 500 caracteres

                            # Score de relevancia
                            if hasattr(chunk, 'score'):
                                source.relevance_score = chunk.score

                            sources.append(source)

                    # Alternativamente, procesar search_support si existe
                    elif hasattr(grounding, 'search_support'):
                        logger.info("Grounding metadata found in search_support format")
                        # Procesar formato alternativo si existe

            logger.info(f"Query executed successfully, {len(sources)} sources found")

            return QueryResponse(
                answer=answer_text,
                sources=sources,
                model_used=model_to_use
            )

        except Exception as e:
            logger.error(f"Error executing query: {e}")
            raise


# Instancia global del servicio
query_service = QueryService()
