"""
Basic tests for MCP Server

These tests verify the MCP server tools are properly configured
and can communicate with the backend API.

Run with: pytest tests/test_mcp_server.py
"""

import pytest
from unittest.mock import Mock, patch
import httpx


def test_mcp_server_imports():
    """Test that MCP server module can be imported"""
    try:
        from app.mcp import server
        assert server is not None
        assert hasattr(server, 'mcp')
    except ImportError as e:
        pytest.fail(f"Failed to import MCP server: {e}")


def test_mcp_tools_registered():
    """Test that MCP tools are properly registered"""
    from app.mcp.server import mcp

    # Check that tools are registered
    # FastMCP decorates functions, we just verify the module loaded
    assert mcp is not None
    assert mcp.name == "filesearch-gemini"


@patch('app.mcp.server.http_client')
def test_set_api_key_tool(mock_client):
    """Test the set_api_key MCP tool"""
    from app.mcp.server import set_api_key

    # Mock successful response
    mock_response = Mock()
    mock_response.json.return_value = {"success": True, "valid": True}
    mock_response.raise_for_status = Mock()
    mock_client.post.return_value = mock_response

    # Call the tool
    result = set_api_key("test_api_key_123")

    # Verify
    assert result["success"] == True
    mock_client.post.assert_called_once_with(
        "/config/api-key",
        json={"api_key": "test_api_key_123"}
    )


@patch('app.mcp.server.http_client')
def test_list_stores_tool(mock_client):
    """Test the list_stores MCP tool"""
    from app.mcp.server import list_stores

    # Mock successful response
    mock_response = Mock()
    mock_response.json.return_value = {
        "stores": [
            {"name": "fileSearchStores/abc123", "display_name": "Test Store"}
        ]
    }
    mock_response.raise_for_status = Mock()
    mock_client.get.return_value = mock_response

    # Call the tool
    result = list_stores()

    # Verify
    assert "stores" in result
    assert len(result["stores"]) == 1
    assert result["stores"][0]["display_name"] == "Test Store"
    mock_client.get.assert_called_once_with("/stores")


@patch('app.mcp.server.http_client')
def test_rag_query_tool(mock_client):
    """Test the rag_query MCP tool"""
    from app.mcp.server import rag_query

    # Mock successful response
    mock_response = Mock()
    mock_response.json.return_value = {
        "answer": "Test answer",
        "model_used": "gemini-2.5-flash",
        "sources": [
            {
                "document_display_name": "Test Doc",
                "document_id": "documents/xyz",
                "metadata": {"author": "Test"},
                "relevance_score": 0.95
            }
        ]
    }
    mock_response.raise_for_status = Mock()
    mock_client.post.return_value = mock_response

    # Call the tool
    result = rag_query(
        question="What is X?",
        store_ids=["fileSearchStores/abc123"]
    )

    # Verify
    assert result["answer"] == "Test answer"
    assert result["model_used"] == "gemini-2.5-flash"
    assert len(result["sources"]) == 1
    assert result["sources"][0]["document_name"] == "Test Doc"


@patch('app.mcp.server.http_client')
def test_upload_document_tool(mock_client):
    """Test the upload_document MCP tool"""
    from app.mcp.server import upload_document
    import tempfile
    import os

    # Create a temporary test file
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
        f.write("Test content")
        temp_file = f.name

    try:
        # Mock successful response
        mock_response = Mock()
        mock_response.json.return_value = {
            "name": "documents/test123",
            "display_name": "Test Document",
            "state": "PROCESSING"
        }
        mock_response.raise_for_status = Mock()
        mock_client.post.return_value = mock_response

        # Call the tool
        result = upload_document(
            store_id="fileSearchStores/abc123",
            file_path=temp_file,
            display_name="Test Document"
        )

        # Verify
        assert "name" in result
        assert result["display_name"] == "Test Document"

    finally:
        # Clean up
        os.unlink(temp_file)


@patch('app.mcp.server.http_client')
def test_error_handling(mock_client):
    """Test error handling in MCP tools"""
    from app.mcp.server import get_config_status

    # Mock HTTP error
    mock_client.get.side_effect = httpx.HTTPError("Connection failed")

    # Call the tool
    result = get_config_status()

    # Verify error is handled gracefully
    assert "error" in result
    assert result["api_key_valid"] == False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
