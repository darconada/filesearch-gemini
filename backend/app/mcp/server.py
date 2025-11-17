"""
MCP Server for File Search RAG Application

This server exposes all File Search operations as MCP tools,
allowing LLM agents (Claude Code, Gemini CLI, Codex) to interact
with the File Search backend via the Model Context Protocol.
"""

import httpx
import logging
from typing import Optional, Dict, Any, List
from pathlib import Path
import os

from fastmcp import FastMCP

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Crear servidor MCP
mcp = FastMCP("filesearch-gemini")

# URL base del backend (configurable vía env)
BACKEND_URL = os.getenv("FILESEARCH_BACKEND_URL", "http://localhost:8000")

# Cliente HTTP reutilizable
http_client = httpx.Client(base_url=BACKEND_URL, timeout=60.0)


# ============================================================================
# CONFIGURATION TOOLS
# ============================================================================

@mcp.tool()
def set_api_key(api_key: str) -> Dict[str, Any]:
    """
    Configure the Google API key for File Search operations.

    Args:
        api_key: Google Generative Language API key

    Returns:
        Configuration status with validation result
    """
    try:
        response = http_client.post(
            "/config/api-key",
            json={"api_key": api_key}
        )
        response.raise_for_status()
        return response.json()
    except httpx.HTTPError as e:
        logger.error(f"Error setting API key: {e}")
        return {"error": str(e), "success": False}


@mcp.tool()
def get_config_status() -> Dict[str, Any]:
    """
    Get the current configuration status including API key validity.

    Returns:
        Configuration status with API key validation info
    """
    try:
        response = http_client.get("/config/status")
        response.raise_for_status()
        return response.json()
    except httpx.HTTPError as e:
        logger.error(f"Error getting config status: {e}")
        return {"error": str(e), "api_key_valid": False}


# ============================================================================
# STORE MANAGEMENT TOOLS
# ============================================================================

@mcp.tool()
def create_store(display_name: str) -> Dict[str, Any]:
    """
    Create a new File Search store for document indexing.

    Args:
        display_name: Human-readable name for the store

    Returns:
        Created store information including store ID
    """
    try:
        response = http_client.post(
            "/stores",
            json={"display_name": display_name}
        )
        response.raise_for_status()
        return response.json()
    except httpx.HTTPError as e:
        logger.error(f"Error creating store: {e}")
        return {"error": str(e), "success": False}


@mcp.tool()
def list_stores() -> Dict[str, Any]:
    """
    List all available File Search stores.

    Returns:
        List of stores with their metadata
    """
    try:
        response = http_client.get("/stores")
        response.raise_for_status()
        return response.json()
    except httpx.HTTPError as e:
        logger.error(f"Error listing stores: {e}")
        return {"error": str(e), "stores": []}


@mcp.tool()
def get_store(store_id: str) -> Dict[str, Any]:
    """
    Get detailed information about a specific store.

    Args:
        store_id: Store identifier (format: fileSearchStores/xxx)

    Returns:
        Store details including metadata and timestamps
    """
    try:
        response = http_client.get(f"/stores/{store_id}")
        response.raise_for_status()
        return response.json()
    except httpx.HTTPError as e:
        logger.error(f"Error getting store: {e}")
        return {"error": str(e)}


@mcp.tool()
def delete_store(store_id: str, force: bool = False) -> Dict[str, Any]:
    """
    Delete a File Search store and all its documents.

    Args:
        store_id: Store identifier (format: fileSearchStores/xxx)
        force: If True, force deletion even if documents are indexed

    Returns:
        Deletion result status
    """
    try:
        params = {"force": str(force).lower()}
        response = http_client.delete(f"/stores/{store_id}", params=params)
        response.raise_for_status()
        return response.json()
    except httpx.HTTPError as e:
        logger.error(f"Error deleting store: {e}")
        return {"error": str(e), "success": False}


# ============================================================================
# DOCUMENT MANAGEMENT TOOLS
# ============================================================================

@mcp.tool()
def upload_document(
    store_id: str,
    file_path: str,
    display_name: Optional[str] = None,
    metadata: Optional[str] = None
) -> Dict[str, Any]:
    """
    Upload a document to a File Search store for indexing.

    Args:
        store_id: Target store identifier (format: fileSearchStores/xxx)
        file_path: Path to the file to upload (must exist locally)
        display_name: Optional human-readable name for the document
        metadata: Optional JSON string with custom metadata (e.g., '{"author":"John","year":2024}')

    Returns:
        Uploaded document information including document ID
    """
    try:
        file_path_obj = Path(file_path)
        if not file_path_obj.exists():
            return {"error": f"File not found: {file_path}", "success": False}

        # Preparar form data
        files = {
            "file": (file_path_obj.name, open(file_path_obj, "rb"))
        }

        data = {}
        if display_name:
            data["display_name"] = display_name
        if metadata:
            data["metadata"] = metadata

        response = http_client.post(
            f"/stores/{store_id}/documents",
            files=files,
            data=data
        )
        response.raise_for_status()
        return response.json()

    except httpx.HTTPError as e:
        logger.error(f"Error uploading document: {e}")
        return {"error": str(e), "success": False}
    finally:
        # Cerrar el archivo si fue abierto
        if 'files' in locals():
            files["file"][1].close()


@mcp.tool()
def list_documents(
    store_id: str,
    page_size: int = 50,
    page_token: Optional[str] = None,
    metadata_filter: Optional[str] = None
) -> Dict[str, Any]:
    """
    List documents in a File Search store with optional filtering.

    Args:
        store_id: Store identifier (format: fileSearchStores/xxx)
        page_size: Number of documents per page (default: 50)
        page_token: Token for pagination (from previous response)
        metadata_filter: Optional metadata filter (e.g., 'author="John Doe"')

    Returns:
        List of documents with pagination info
    """
    try:
        params = {"page_size": page_size}
        if page_token:
            params["page_token"] = page_token
        if metadata_filter:
            params["metadata_filter"] = metadata_filter

        response = http_client.get(
            f"/stores/{store_id}/documents",
            params=params
        )
        response.raise_for_status()
        return response.json()

    except httpx.HTTPError as e:
        logger.error(f"Error listing documents: {e}")
        return {"error": str(e), "documents": []}


@mcp.tool()
def update_document(
    store_id: str,
    document_id: str,
    file_path: Optional[str] = None,
    metadata: Optional[str] = None
) -> Dict[str, Any]:
    """
    Update a document's content or metadata.

    Args:
        store_id: Store identifier (format: fileSearchStores/xxx)
        document_id: Document identifier
        file_path: Optional path to new file content
        metadata: Optional JSON string with updated metadata

    Returns:
        Updated document information
    """
    try:
        files = None
        data = {}

        if file_path:
            file_path_obj = Path(file_path)
            if not file_path_obj.exists():
                return {"error": f"File not found: {file_path}", "success": False}
            files = {"file": (file_path_obj.name, open(file_path_obj, "rb"))}

        if metadata:
            data["metadata"] = metadata

        response = http_client.put(
            f"/stores/{store_id}/documents/{document_id}",
            files=files,
            data=data
        )
        response.raise_for_status()
        return response.json()

    except httpx.HTTPError as e:
        logger.error(f"Error updating document: {e}")
        return {"error": str(e), "success": False}
    finally:
        if files:
            files["file"][1].close()


@mcp.tool()
def delete_document(
    store_id: str,
    document_id: str,
    force: bool = False
) -> Dict[str, Any]:
    """
    Delete a document from a File Search store.

    Args:
        store_id: Store identifier (format: fileSearchStores/xxx)
        document_id: Document identifier
        force: If True, force deletion even if document is indexed

    Returns:
        Deletion result status
    """
    try:
        params = {"force": str(force).lower()}
        response = http_client.delete(
            f"/stores/{store_id}/documents/{document_id}",
            params=params
        )
        response.raise_for_status()
        return response.json()

    except httpx.HTTPError as e:
        logger.error(f"Error deleting document: {e}")
        return {"error": str(e), "success": False}


# ============================================================================
# RAG QUERY TOOLS
# ============================================================================

@mcp.tool()
def rag_query(
    question: str,
    store_ids: List[str],
    metadata_filter: Optional[str] = None,
    max_output_tokens: Optional[int] = None,
    temperature: Optional[float] = None
) -> Dict[str, Any]:
    """
    Execute a RAG query using File Search across one or more stores.

    This is the main tool for asking questions about documents stored in File Search.
    The system will retrieve relevant documents and generate an answer with citations.

    Args:
        question: Natural language question to answer
        store_ids: List of store IDs to search (format: ["fileSearchStores/xxx", ...])
        metadata_filter: Optional metadata filter (e.g., 'author="John Doe" AND year>=2020')
        max_output_tokens: Optional maximum tokens in response (default: 2048)
        temperature: Optional temperature for generation (0.0-1.0, default: 0.2)

    Returns:
        Answer with citations to source documents and their metadata
    """
    try:
        payload = {
            "question": question,
            "store_ids": store_ids
        }

        if metadata_filter:
            payload["metadata_filter"] = metadata_filter
        if max_output_tokens:
            payload["max_output_tokens"] = max_output_tokens
        if temperature is not None:
            payload["temperature"] = temperature

        response = http_client.post("/query", json=payload)
        response.raise_for_status()

        result = response.json()

        # Formatear respuesta para mejor legibilidad
        formatted_result = {
            "answer": result.get("answer", ""),
            "model_used": result.get("model_used", "gemini-2.5-flash"),
            "sources": []
        }

        # Incluir fuentes con metadata
        for source in result.get("sources", []):
            formatted_source = {
                "document_name": source.get("document_display_name"),
                "document_id": source.get("document_id"),
                "metadata": source.get("metadata", {}),
                "relevance_score": source.get("relevance_score")
            }
            if source.get("chunk_text"):
                formatted_source["excerpt"] = source["chunk_text"][:200] + "..."
            formatted_result["sources"].append(formatted_source)

        return formatted_result

    except httpx.HTTPError as e:
        logger.error(f"Error executing RAG query: {e}")
        return {"error": str(e), "answer": "Error executing query"}


# ============================================================================
# GOOGLE DRIVE SYNC TOOLS
# ============================================================================

@mcp.tool()
def create_drive_link(
    drive_file_id: str,
    store_id: str,
    mode: str = "manual",
    description: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create a link between a Google Drive file and a File Search store.

    Args:
        drive_file_id: Google Drive file or folder ID
        store_id: Target store identifier (format: fileSearchStores/xxx)
        mode: Sync mode - "manual" (sync only when requested) or "auto" (sync every 5 min)
        description: Optional description for this link

    Returns:
        Created drive link information
    """
    try:
        payload = {
            "drive_file_id": drive_file_id,
            "store_id": store_id,
            "mode": mode
        }

        if description:
            payload["description"] = description

        response = http_client.post("/drive-links", json=payload)
        response.raise_for_status()
        return response.json()

    except httpx.HTTPError as e:
        logger.error(f"Error creating drive link: {e}")
        return {"error": str(e), "success": False}


@mcp.tool()
def list_drive_links() -> Dict[str, Any]:
    """
    List all configured Google Drive sync links.

    Returns:
        List of drive links with their sync status
    """
    try:
        response = http_client.get("/drive-links")
        response.raise_for_status()
        return response.json()

    except httpx.HTTPError as e:
        logger.error(f"Error listing drive links: {e}")
        return {"error": str(e), "links": []}


@mcp.tool()
def get_drive_link(link_id: str) -> Dict[str, Any]:
    """
    Get details about a specific Google Drive sync link.

    Args:
        link_id: Drive link identifier

    Returns:
        Drive link details including sync history
    """
    try:
        response = http_client.get(f"/drive-links/{link_id}")
        response.raise_for_status()
        return response.json()

    except httpx.HTTPError as e:
        logger.error(f"Error getting drive link: {e}")
        return {"error": str(e)}


@mcp.tool()
def delete_drive_link(link_id: str) -> Dict[str, Any]:
    """
    Delete a Google Drive sync link (does not delete documents).

    Args:
        link_id: Drive link identifier

    Returns:
        Deletion result status
    """
    try:
        response = http_client.delete(f"/drive-links/{link_id}")
        response.raise_for_status()
        return response.json()

    except httpx.HTTPError as e:
        logger.error(f"Error deleting drive link: {e}")
        return {"error": str(e), "success": False}


@mcp.tool()
def sync_drive_link_now(link_id: str) -> Dict[str, Any]:
    """
    Manually trigger synchronization for a Google Drive link.

    Args:
        link_id: Drive link identifier

    Returns:
        Sync operation result with updated documents count
    """
    try:
        response = http_client.post(f"/drive-links/{link_id}/sync-now")
        response.raise_for_status()
        return response.json()

    except httpx.HTTPError as e:
        logger.error(f"Error syncing drive link: {e}")
        return {"error": str(e), "success": False}


# ============================================================================
# ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    # Ejecutar servidor MCP en modo stdio (por defecto)
    logger.info(f"Starting MCP server for File Search (backend: {BACKEND_URL})")
    mcp.run()
