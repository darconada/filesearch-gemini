"""
Basic tests for CLI

These tests verify the CLI commands work correctly.

Run with: pytest tests/test_cli.py
"""

import pytest
from click.testing import CliRunner
from unittest.mock import Mock, patch
import json


@pytest.fixture
def runner():
    """Create a Click test runner"""
    return CliRunner()


def test_cli_help(runner):
    """Test that CLI help works"""
    from cli.main import cli

    result = runner.invoke(cli, ['--help'])
    assert result.exit_code == 0
    assert 'File Search CLI' in result.output


def test_config_help(runner):
    """Test config command help"""
    from cli.main import cli

    result = runner.invoke(cli, ['config', '--help'])
    assert result.exit_code == 0
    assert 'Manage configuration' in result.output


def test_stores_list_help(runner):
    """Test stores list command help"""
    from cli.main import cli

    result = runner.invoke(cli, ['stores', 'list', '--help'])
    assert result.exit_code == 0


@patch('cli.main.get_client')
def test_stores_list_command(mock_get_client, runner):
    """Test stores list command"""
    from cli.main import cli

    # Mock HTTP client
    mock_client = Mock()
    mock_response = Mock()
    mock_response.json.return_value = {
        "stores": [
            {
                "name": "fileSearchStores/abc123",
                "display_name": "Test Store",
                "create_time": "2024-01-01T00:00:00Z"
            }
        ]
    }
    mock_response.raise_for_status = Mock()
    mock_client.get.return_value = mock_response
    mock_client.__enter__ = Mock(return_value=mock_client)
    mock_client.__exit__ = Mock(return_value=False)
    mock_get_client.return_value = mock_client

    # Run command
    result = runner.invoke(cli, ['stores', 'list'])

    # Verify
    assert result.exit_code == 0
    assert 'Test Store' in result.output


@patch('cli.main.get_client')
def test_stores_create_command(mock_get_client, runner):
    """Test stores create command"""
    from cli.main import cli

    # Mock HTTP client
    mock_client = Mock()
    mock_response = Mock()
    mock_response.json.return_value = {
        "name": "fileSearchStores/abc123",
        "display_name": "New Store"
    }
    mock_response.raise_for_status = Mock()
    mock_client.post.return_value = mock_response
    mock_client.__enter__ = Mock(return_value=mock_client)
    mock_client.__exit__ = Mock(return_value=False)
    mock_get_client.return_value = mock_client

    # Run command
    result = runner.invoke(cli, ['stores', 'create', '--name', 'New Store'])

    # Verify
    assert result.exit_code == 0
    assert 'Store created successfully' in result.output


@patch('cli.main.get_client')
def test_query_command(mock_get_client, runner):
    """Test query command"""
    from cli.main import cli

    # Mock HTTP client
    mock_client = Mock()
    mock_response = Mock()
    mock_response.json.return_value = {
        "answer": "This is the answer",
        "model_used": "gemini-2.5-flash",
        "sources": [
            {
                "document_display_name": "Doc 1",
                "document_id": "documents/123",
                "metadata": {"author": "Test"}
            }
        ]
    }
    mock_response.raise_for_status = Mock()
    mock_client.post.return_value = mock_response
    mock_client.__enter__ = Mock(return_value=mock_client)
    mock_client.__exit__ = Mock(return_value=False)
    mock_get_client.return_value = mock_client

    # Run command
    result = runner.invoke(cli, [
        'query',
        '--question', 'What is X?',
        '--stores', 'fileSearchStores/abc123'
    ])

    # Verify
    assert result.exit_code == 0
    assert 'This is the answer' in result.output


@patch('cli.main.get_client')
def test_query_json_output(mock_get_client, runner):
    """Test query command with JSON output"""
    from cli.main import cli

    # Mock HTTP client
    mock_client = Mock()
    mock_response = Mock()
    response_data = {
        "answer": "Test answer",
        "model_used": "gemini-2.5-flash",
        "sources": []
    }
    mock_response.json.return_value = response_data
    mock_response.raise_for_status = Mock()
    mock_client.post.return_value = mock_response
    mock_client.__enter__ = Mock(return_value=mock_client)
    mock_client.__exit__ = Mock(return_value=False)
    mock_get_client.return_value = mock_client

    # Run command with --json flag
    result = runner.invoke(cli, [
        'query',
        '--question', 'What is X?',
        '--stores', 'fileSearchStores/abc123',
        '--json'
    ])

    # Verify
    assert result.exit_code == 0
    # Output should contain JSON


@patch('cli.main.get_client')
def test_docs_list_command(mock_get_client, runner):
    """Test docs list command"""
    from cli.main import cli

    # Mock HTTP client
    mock_client = Mock()
    mock_response = Mock()
    mock_response.json.return_value = {
        "documents": [
            {
                "name": "documents/xyz",
                "display_name": "Test Doc",
                "state": "INDEXED",
                "custom_metadata": {"author": "Test"}
            }
        ]
    }
    mock_response.raise_for_status = Mock()
    mock_client.get.return_value = mock_response
    mock_client.__enter__ = Mock(return_value=mock_client)
    mock_client.__exit__ = Mock(return_value=False)
    mock_get_client.return_value = mock_client

    # Run command
    result = runner.invoke(cli, [
        'docs', 'list',
        '--store-id', 'fileSearchStores/abc123'
    ])

    # Verify
    assert result.exit_code == 0
    assert 'Test Doc' in result.output


def test_config_module():
    """Test CLI config module"""
    from cli.config import CLIConfig

    config = CLIConfig()
    assert config is not None
    assert hasattr(config, 'backend_url')
    assert hasattr(config, 'api_key')


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
