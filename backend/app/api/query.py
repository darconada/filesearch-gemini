"""Endpoints para consultas RAG"""
from fastapi import APIRouter, HTTPException, Depends, Request
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.query import QueryRequest, QueryResponse
from app.services.query_service import query_service
from app.services.audit_service import audit_service
from app.models.db_models import AuditAction
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/query", tags=["query"])


@router.post("", response_model=QueryResponse)
async def execute_query(query: QueryRequest, request: Request, db: Session = Depends(get_db)) -> QueryResponse:
    """Ejecutar una consulta RAG con File Search"""
    try:
        if not query.store_ids:
            raise HTTPException(
                status_code=400,
                detail="Debe proporcionar al menos un store_id"
            )

        result = query_service.execute_query(query)

        # Audit log
        audit_service.log(
            db=db,
            action=AuditAction.QUERY_EXECUTE,
            resource_type="query",
            details={
                "question": query.question[:100],  # Primeros 100 chars
                "store_ids": query.store_ids,
                "model_used": result.model_used,
                "sources_count": len(result.sources)
            },
            request=request
        )

        return result

    except HTTPException as e:
        # Audit log del error
        audit_service.log(
            db=db,
            action=AuditAction.QUERY_EXECUTE,
            resource_type="query",
            details={
                "question": query.question[:100],
                "store_ids": query.store_ids
            },
            success=False,
            error_message=str(e.detail),
            request=request
        )
        raise
    except Exception as e:
        logger.error(f"Error in execute_query endpoint: {e}")
        audit_service.log(
            db=db,
            action=AuditAction.QUERY_EXECUTE,
            resource_type="query",
            success=False,
            error_message=str(e),
            request=request
        )
        raise HTTPException(status_code=500, detail=str(e))
