# MCP Integration Guide

This document explains how to use the File Search RAG application with LLM agents via the Model Context Protocol (MCP).

## Overview

The File Search application now supports two methods for integration with LLM agents:

1. **MCP Server** - Full-featured integration using Model Context Protocol (recommended for Claude Code, Gemini CLI, Codex)
2. **CLI Tool** - Simple command-line interface for direct shell access or as an alternative integration method

## Quick Start

### Prerequisites

1. Install the dependencies:

```bash
cd backend
pip install -r requirements.txt
```

2. Ensure the backend is running:

```bash
cd backend
python -m app.main
```

The backend should be running on `http://localhost:8000`.

3. Configure your Google API key (one of these methods):

```bash
# Option 1: Using the CLI
./filesearch-gemini config set-api-key YOUR_API_KEY

# Option 2: Via environment variable
export GOOGLE_API_KEY=YOUR_API_KEY

# Option 3: Via the web UI at http://localhost:5173
```

---

## Method 1: MCP Server Integration

The MCP server exposes all File Search operations as tools that can be called by LLM agents.

### Available MCP Tools

The server provides 21 tools organized in 5 categories:

#### Configuration
- `set_api_key` - Configure Google API key
- `get_config_status` - Check configuration status

#### Store Management
- `create_store` - Create a new File Search store
- `list_stores` - List all stores
- `get_store` - Get store details
- `delete_store` - Delete a store

#### Document Management
- `upload_document` - Upload a document with optional metadata
- `list_documents` - List documents with optional metadata filtering
- `update_document` - Update document content or metadata
- `delete_document` - Delete a document

#### RAG Queries
- `rag_query` - Execute RAG queries with citations and metadata support

#### Google Drive Sync
- `create_drive_link` - Link a Google Drive file/folder to a store
- `list_drive_links` - List all sync links
- `get_drive_link` - Get sync link details
- `delete_drive_link` - Delete a sync link
- `sync_drive_link_now` - Manually trigger synchronization

### Running the MCP Server

The MCP server runs in **stdio mode** by default (recommended for most clients):

```bash
cd backend
python mcp_server.py
```

You can also set a custom backend URL:

```bash
export FILESEARCH_BACKEND_URL=http://localhost:8000
python mcp_server.py
```

---

## Integration with Gemini CLI

Gemini CLI supports MCP servers via its settings configuration.

### Configuration

1. Locate or create your Gemini CLI settings file (usually `~/.config/gemini-cli/settings.json` or similar)

2. Add the File Search MCP server:

```json
{
  "mcpServers": {
    "filesearch-gemini": {
      "type": "stdio",
      "command": "python",
      "args": [
        "/absolute/path/to/filesearch-gemini/backend/mcp_server.py"
      ],
      "env": {
        "FILESEARCH_BACKEND_URL": "http://localhost:8000"
      }
    }
  }
}
```

**Important**: Replace `/absolute/path/to/filesearch-gemini` with your actual project path.

### Alternative: Using Python with -m

```json
{
  "mcpServers": {
    "filesearch-gemini": {
      "type": "stdio",
      "command": "python",
      "args": ["-m", "app.mcp.server"],
      "cwd": "/absolute/path/to/filesearch-gemini/backend",
      "env": {
        "FILESEARCH_BACKEND_URL": "http://localhost:8000"
      }
    }
  }
}
```

### Usage Examples with Gemini CLI

Once configured, you can ask Gemini to use the File Search tools:

```bash
# Example 1: Create a store and upload documents
gemini chat
> Use the filesearch-gemini MCP server to create a new store called "Research Papers"
> Then upload all PDF files from ./papers/ to that store

# Example 2: Query with metadata filtering
> Use filesearch-gemini to find documents in store fileSearchStores/abc123
> where author="Robert Graves" and answer: "What are the main themes?"

# Example 3: Set up Drive sync
> Use filesearch-gemini to create a Drive link for folder ID xyz789
> to store fileSearchStores/abc123 with auto sync mode
```

---

## Integration with Claude Code

Claude Code has excellent MCP support via its built-in configuration system.

### Configuration

1. In your Claude Code settings, add the MCP server using one of these methods:

#### Method A: Using claude CLI (Recommended)

```bash
# Navigate to your project
cd /path/to/filesearch-gemini

# Add the MCP server
claude mcp add filesearch-gemini \
  --transport stdio \
  --command "python" \
  --args "backend/mcp_server.py"
```

#### Method B: Manual Configuration

Create or edit `~/.config/claude-code/mcp_servers.json`:

```json
{
  "mcpServers": {
    "filesearch-gemini": {
      "command": "python",
      "args": ["/absolute/path/to/filesearch-gemini/backend/mcp_server.py"],
      "env": {
        "FILESEARCH_BACKEND_URL": "http://localhost:8000"
      }
    }
  }
}
```

### Usage Examples with Claude Code

Once configured, Claude Code will automatically discover the tools:

```
You: I need to set up a RAG system for my research documents

Claude: I'll help you set up File Search. Let me use the filesearch-gemini server.
[Uses create_store to create a store]
[Uses upload_document to upload your PDFs]

You: Now ask it: "What are the main findings about X?"

Claude: [Uses rag_query with your store ID to answer]
```

### Best Practices with Claude Code

1. **Explicit tool references**: You can explicitly tell Claude to use specific tools:
   ```
   "Use the filesearch-gemini tool rag_query to search for..."
   ```

2. **Metadata workflows**: Claude can help you organize documents with metadata:
   ```
   "Upload all PDFs from ./docs to the store and add metadata
   {project: 'X', year: 2024}"
   ```

3. **Batch operations**: Claude can orchestrate multiple operations:
   ```
   "Create a store, upload all my PDFs, then query for documents
   about topic Y published after 2020"
   ```

---

## Integration with Codex CLI (OpenAI)

Codex CLI supports MCP servers for tool integration.

### Configuration

1. Configure the MCP server for Codex (check the latest Codex CLI docs for exact syntax):

```bash
# Example command (syntax may vary by Codex version)
codex mcp-server add filesearch-gemini \
  --command "python" \
  --args "/absolute/path/to/filesearch-gemini/backend/mcp_server.py"
```

2. Alternative: Some Codex versions may use a config file (e.g., `~/.codex/mcp.json`):

```json
{
  "servers": {
    "filesearch-gemini": {
      "command": "python",
      "args": ["/absolute/path/to/filesearch-gemini/backend/mcp_server.py"],
      "transport": "stdio"
    }
  }
}
```

### Usage Examples with Codex

```bash
# Start Codex in your project directory
codex

# Example interactions
> Create a File Search store for my documentation
> Upload all markdown files from ./docs with metadata {type: "documentation"}
> Query the store: "How do I configure authentication?"
```

---

## Method 2: CLI Tool Integration

For LLM agents that prefer executing shell commands directly, or for manual use, the CLI tool provides a simpler alternative.

### CLI Installation

The CLI is already included. To use it:

```bash
# Option 1: Run from project root
./filesearch-gemini --help

# Option 2: Add to PATH for global access
export PATH="$PATH:/absolute/path/to/filesearch-gemini"
filesearch-gemini --help

# Option 3: Create a symlink
sudo ln -s /absolute/path/to/filesearch-gemini/filesearch-gemini /usr/local/bin/
```

### CLI Configuration

The CLI uses configuration from:

1. Environment variables (highest priority)
2. Config file at `~/.filesearch-gemini/config.yaml`
3. Default values

```bash
# Set backend URL
filesearch-gemini config set-backend http://localhost:8000

# Set API key
filesearch-gemini config set-api-key YOUR_API_KEY

# Check status
filesearch-gemini config status
```

### CLI Usage Examples

#### Store Management

```bash
# List stores
filesearch-gemini stores list

# Create a store
filesearch-gemini stores create --name "My Documents"

# Delete a store
filesearch-gemini stores delete fileSearchStores/abc123 --force
```

#### Document Management

```bash
# Upload a document
filesearch-gemini docs upload \
  --store-id fileSearchStores/abc123 \
  --file ./document.pdf \
  --name "Research Paper" \
  --metadata '{"author":"John Doe","year":2024}'

# List documents with metadata filter
filesearch-gemini docs list \
  --store-id fileSearchStores/abc123 \
  --metadata-filter 'author="John Doe"'

# Delete a document
filesearch-gemini docs delete \
  --store-id fileSearchStores/abc123 \
  --doc-id documents/xyz789
```

#### RAG Queries

```bash
# Execute a query
filesearch-gemini query \
  --question "What are the main findings?" \
  --stores fileSearchStores/abc123,fileSearchStores/def456 \
  --metadata-filter 'year>=2020'

# Get JSON output for programmatic use
filesearch-gemini query \
  --question "Summarize the key points" \
  --stores fileSearchStores/abc123 \
  --json
```

#### Drive Sync

```bash
# Create a Drive link
filesearch-gemini drive create \
  --drive-id 1abc123xyz \
  --store-id fileSearchStores/abc123 \
  --mode auto

# List Drive links
filesearch-gemini drive list

# Manually sync a link
filesearch-gemini drive sync-now LINK_ID
```

### Using CLI with LLM Agents

LLM agents can call the CLI as shell commands:

#### Gemini CLI with Shell Access

```
You: Search my documents for information about quantum computing

Gemini: I'll use the filesearch-gemini CLI to search.
[Executes: filesearch-gemini query --question "quantum computing" --stores ...]
```

#### Claude Code with Bash Tool

```
You: Upload all PDFs from ./papers to File Search

Claude: I'll upload those documents for you.
[Uses Bash tool to run: filesearch-gemini docs upload --store-id ... --file ...]
```

---

## Complete Workflow Example

Here's a complete example using the MCP server (works with all three agents):

### Step 1: Create a Store

Agent uses: `create_store(display_name="Research Papers 2024")`

Response:
```json
{
  "name": "fileSearchStores/abc123xyz",
  "display_name": "Research Papers 2024",
  "create_time": "2024-01-15T10:30:00Z"
}
```

### Step 2: Upload Documents with Metadata

Agent uses:
```
upload_document(
  store_id="fileSearchStores/abc123xyz",
  file_path="./papers/quantum_computing.pdf",
  display_name="Quantum Computing Review 2024",
  metadata='{"author":"Dr. Smith","year":2024,"topic":"quantum"}'
)
```

### Step 3: Query with Metadata Filter

Agent uses:
```
rag_query(
  question="What are the latest developments in quantum computing?",
  store_ids=["fileSearchStores/abc123xyz"],
  metadata_filter='topic="quantum" AND year>=2024'
)
```

Response:
```json
{
  "answer": "Recent developments in quantum computing include...",
  "model_used": "gemini-2.5-flash",
  "sources": [
    {
      "document_name": "Quantum Computing Review 2024",
      "document_id": "documents/doc123",
      "metadata": {
        "author": "Dr. Smith",
        "year": 2024,
        "topic": "quantum"
      },
      "relevance_score": 0.95,
      "excerpt": "The field has seen significant advances..."
    }
  ]
}
```

---

## Advanced Configuration

### Custom Backend URL

If your backend runs on a different host/port:

```bash
# For MCP server
export FILESEARCH_BACKEND_URL=http://192.168.1.100:8000

# For CLI
filesearch-gemini config set-backend http://192.168.1.100:8000
```

### Timeout Configuration

For large file uploads or slow queries, you may need to increase timeouts.

Edit `backend/app/mcp/server.py`:

```python
http_client = httpx.Client(base_url=BACKEND_URL, timeout=120.0)  # 2 minutes
```

Edit `cli/main.py`:

```python
return httpx.Client(base_url=config.backend_url, timeout=120.0)
```

### Debug Mode

Enable detailed logging:

```bash
# For MCP server
export LOG_LEVEL=DEBUG
python backend/mcp_server.py

# For CLI
export FILESEARCH_LOG_LEVEL=DEBUG
./filesearch-gemini query ...
```

---

## Troubleshooting

### MCP Server Not Starting

1. Check Python path and dependencies:
   ```bash
   cd backend
   python -c "import fastmcp; print('OK')"
   ```

2. Check backend is running:
   ```bash
   curl http://localhost:8000/health
   ```

3. Check logs in the agent's output for error messages

### CLI Not Working

1. Check the script is executable:
   ```bash
   chmod +x filesearch-gemini
   ```

2. Check backend connectivity:
   ```bash
   ./filesearch-gemini config status
   ```

3. Verify API key:
   ```bash
   ./filesearch-gemini config set-api-key YOUR_KEY
   ```

### Agent Can't Find Tools

1. For Gemini CLI: Restart the CLI after config changes
2. For Claude Code: Reload the MCP servers in settings
3. For Codex: Check `codex mcp-server list`

### Upload Fails

1. Check file exists and is readable
2. Check file size (very large files may timeout)
3. Verify store ID is correct (format: `fileSearchStores/xxx`)

---

## Best Practices

1. **Store Organization**: Create separate stores for different document collections
   ```
   - Research Papers Store
   - Technical Documentation Store
   - Customer Support Store
   ```

2. **Metadata Usage**: Always add metadata for better filtering
   ```json
   {
     "author": "John Doe",
     "year": 2024,
     "department": "Engineering",
     "classification": "public"
   }
   ```

3. **Query Optimization**: Use metadata filters to narrow searches
   ```
   metadata_filter='department="Engineering" AND year>=2023'
   ```

4. **Batch Operations**: Upload multiple documents in a workflow
   ```python
   for file in files:
       upload_document(store_id=store, file_path=file, metadata=meta)
   ```

5. **Drive Sync**: Use "auto" mode for frequently updated folders
   ```
   mode="auto"  # Syncs every 5 minutes
   mode="manual"  # Sync only when triggered
   ```

---

## API Reference

For complete API documentation, see:

- **Backend API**: http://localhost:8000/docs (Swagger UI)
- **MCP Tools**: Run `python backend/mcp_server.py --help` (when available)
- **CLI Help**: `./filesearch-gemini --help` and `./filesearch-gemini COMMAND --help`

---

## Additional Resources

- [Model Context Protocol Specification](https://modelcontextprotocol.io)
- [FastMCP Documentation](https://gofastmcp.com)
- [Google File Search API](https://ai.google.dev/gemini-api/docs/file-search)
- [Project README](./README.md)

---

## Support

For issues or questions:

1. Check the troubleshooting section above
2. Review backend logs: `tail -f backend/logs/app.log` (if logging to file)
3. Open an issue on the project repository

---

**Last Updated**: 2024-01-15
