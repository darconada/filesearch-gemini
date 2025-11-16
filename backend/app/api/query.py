"""Endpoints para consultas RAG"""
from fastapi import APIRouter, HTTPException
from app.models.query import QueryRequest, QueryResponse
from app.services.query_service import query_service
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/query", tags=["query"])


@router.post("", response_model=QueryResponse)
async def execute_query(query: QueryRequest) -> QueryResponse:
    """Ejecutar una consulta RAG con File Search"""
    try:
        if not query.store_ids:
            raise HTTPException(
                status_code=400,
                detail="Debe proporcionar al menos un store_id"
            )

        return query_service.execute_query(query)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in execute_query endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))
