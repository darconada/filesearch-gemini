"""Servicio para consultas RAG con File Search"""
import google.generativeai as genai
from typing import Optional, List
from app.models.query import QueryRequest, QueryResponse, DocumentSource
from app.services.google_client import google_client
from app.config import settings
import logging

logger = logging.getLogger(__name__)


class QueryService:
    """Servicio para ejecutar consultas RAG"""

    def __init__(self):
        self.client = google_client

    def execute_query(self, query: QueryRequest) -> QueryResponse:
        """Ejecutar una consulta RAG usando File Search"""
        try:
            if not self.client.is_configured():
                self.client.configure()

            # Preparar configuración de file_search
            file_search_config = {
                "file_search_store_names": query.store_ids
            }

            # Añadir filtro de metadata si se proporciona
            if query.metadata_filter:
                file_search_config["metadata_filter"] = query.metadata_filter

            # Configurar el modelo con la herramienta file_search
            model = self.client.get_model()

            # Crear la configuración de generación
            generation_config = genai.types.GenerationConfig(
                temperature=0.7,
                top_p=0.95,
                top_k=40,
                max_output_tokens=2048,
            )

            # Preparar las herramientas
            tools = [
                genai.types.Tool(
                    file_search=file_search_config
                )
            ]

            # Generar contenido
            response = model.generate_content(
                query.question,
                tools=tools,
                generation_config=generation_config
            )

            # Extraer la respuesta
            answer_text = response.text if response.text else "No se pudo generar una respuesta."

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
                            source = DocumentSource()

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

                    # Alternativamente, procesar search_entry_point si existe
                    elif hasattr(grounding, 'search_entry_point'):
                        # Algunas versiones usan este formato
                        logger.info("Grounding metadata found in search_entry_point format")

            logger.info(f"Query executed successfully, {len(sources)} sources found")

            return QueryResponse(
                answer=answer_text,
                sources=sources,
                model_used=settings.model_name
            )

        except Exception as e:
            logger.error(f"Error executing query: {e}")
            raise


# Instancia global del servicio
query_service = QueryService()
