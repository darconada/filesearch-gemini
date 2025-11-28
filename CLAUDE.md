# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

File Search RAG Application - A full-stack web application for managing Google File Search and executing RAG (Retrieval-Augmented Generation) queries with Google Drive synchronization support.

**Stack:**
- Backend: Python 3.11+ with FastAPI, SQLAlchemy, google-genai SDK
- Frontend: React 18 + TypeScript + Vite + Material-UI
- Database: SQLite (filesearch.db)
- Additional: MCP server integration, CLI tool, Google Drive API

**Important SDK Note:** This project uses the **official `google-genai` SDK** (v1.6.1+). The older `google-generativeai` SDK does NOT support File Search and will cause errors.

## Common Commands

### Backend Development

```bash
# Activate virtual environment
cd backend
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt

# Run backend server
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Run MCP server (for LLM agent integration)
python mcp_server.py

# Run database migrations
python migrate_add_versioning_and_local_files.py
```

### Frontend Development

```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev

# Build for production
npm run build

# Lint code
npm run lint
```

### CLI Tool

```bash
# From project root
./filesearch-gemini --help

# Common CLI operations
./filesearch-gemini config status
./filesearch-gemini stores list
./filesearch-gemini docs upload --store-id <id> --file <path>
./filesearch-gemini query --question "Your question" --stores <id>
```

### Full Application Startup

```bash
# Start both backend and frontend
./start.sh
```

### Testing

```bash
# Run backend tests
cd backend
pytest tests/

# Frontend uses vite test (if configured)
cd frontend
npm run test
```

### Backup & Restore

**CLI-based backup:**
```bash
# Create a backup (from project root)
./manage_backup.sh backup

# Restore from a backup
./manage_backup.sh restore backups/backup_filesearch_YYYYMMDD_HHMMSS.tar.gz
```

**Web-based backup (available at `/backups` route):**
- Create backups via web UI
- Download existing backups
- Upload external backups
- Restore backups with confirmation

**What gets backed up:**
- `backend/app.db` - SQLite database (projects, stores, documents, drive links, local file tracking, audit logs)
- `backend/token.json` - Google Drive OAuth session token
- `backend/credentials.json` - Google OAuth credentials
- `backend/.encryption_key` - **CRITICAL** - Encryption key for API keys (if lost, encrypted keys cannot be recovered)

**Important:**
- Backups are saved to `backups/` directory as `.tar.gz` files
- Restore will overwrite current data (confirmation required)
- Useful before major updates or testing destructive operations
- Web interface provides easier management than CLI script

## Architecture Overview

### Backend Layer Structure

The backend follows a clean layered architecture:

**API Layer** (`backend/app/api/`) → **Service Layer** (`backend/app/services/`) → **Google Client** (`backend/app/services/google_client.py`)

- **API endpoints** handle HTTP requests/responses and validation
- **Services** contain business logic and orchestration
- **GoogleClient** is a singleton managing the google-genai SDK connection

### Multi-Project Support

The application supports managing multiple Google AI Studio projects:

- Each project has its own API key and stores (max 10 stores/project)
- The **active project** is loaded at startup and determines which API key to use
- Project data is persisted in SQLite (`ProjectDB` model)
- When switching projects, the backend must be restarted to load the new active project's API key
- If no active project exists, the system falls back to the `GOOGLE_API_KEY` environment variable

### Database Models and Persistence

Key SQLAlchemy models in `backend/app/models/db_models.py`:

- **ProjectDB**: Multi-project management (name, api_key [encrypted], is_active)
- **DriveLinkDB**: Google Drive sync configurations (drive_file_id, store_id, sync_mode)
- **LocalFileDB**: Tracks locally uploaded files with versioning
- **FileUpdateDB**: Tracks file update history and sync status
- **AuditLogDB**: Audit trail of all system actions (action, user, resource, success/failure)

All data persists to `backend/app.db` (SQLite).

### Security Features

**API Key Encryption:**
- All API keys are encrypted using Fernet (AES-128) before storage
- Encryption key stored in `backend/.encryption_key` (auto-generated, restrictive permissions)
- Transparent encryption/decryption in `encryption_service.py`
- Migration script available to encrypt existing keys: `migrate_encrypt_api_keys.py`
- **CRITICAL**: Backup `.encryption_key` - if lost, encrypted keys are unrecoverable

**Audit Logging:**
- Complete audit trail of all critical operations
- Tracks: action type, timestamp, user/IP, resource, success/failure, details
- Web UI at `/audit-logs` with filtering, statistics, and pagination
- Automatic cleanup of old logs (configurable retention period)
- Currently integrated in: projects endpoints (example for other endpoints)

### Google Drive Synchronization

The Drive sync functionality is partially implemented:

- OAuth2 authentication flow using `credentials.json` and `token.json`
- Models and endpoints exist for creating drive links (Drive file → File Search store)
- Scheduler infrastructure (`apscheduler`) ready for auto-sync
- Actual sync logic (`sync_drive_link_now`) needs OAuth implementation
- File versioning tracks Drive file updates to detect changes

### Local File Synchronization

The application supports automatic synchronization of local files to File Search stores:

- **Location**: `backend/app/api/local_files.py` and `backend/app/services/local_file_service.py`
- **Database models**: `LocalFileDB` tracks file paths, stores, and sync status
- **File versioning**: Detects file changes using SHA256 hash comparison
- **Auto-sync**: Background scheduler checks and syncs modified files every 3 minutes
- **Update tracking**: `FileUpdateDB` maintains history of all file updates
- **Web UI**: Available at `/local-files` route with file browser integration

**Key features:**
- Create links between local files and File Search stores
- Automatic detection of file modifications
- Manual sync on-demand
- Track sync history and status
- File browser dialog for easy path selection

**File browser** (`/file-browser`):
- Navigate server filesystem from web UI
- Security restrictions prevent access to system directories
- Lists files and directories with metadata (size, modified date, type)
- Integrated with local file sync for easy file selection

### Backup Management

The backup system provides both CLI and web-based backup/restore:

- **Location**: `backend/app/api/backups.py` and `backend/app/services/backup_service.py`
- **Storage**: Backups saved to `backups/` directory as `.tar.gz` archives
- **Contents**: Database (app.db), OAuth tokens (token.json, credentials.json)
- **Web interface**: Full CRUD operations at `/backups` route

**Operations:**
- List all available backups with size and creation date
- Create new backups on-demand
- Download backups for external storage
- Upload previously downloaded backups
- Restore from any backup (with confirmation)

### MCP Server Integration

The MCP (Model Context Protocol) server enables LLM agents to use File Search operations:

- **Location**: `backend/mcp_server.py` and `backend/app/mcp/server.py`
- **21 available tools**: config, stores CRUD, document CRUD, RAG queries, Drive sync operations
- **Transport modes**: stdio (default) or HTTP
- **Compatible with**: Gemini CLI, Claude Code, Codex CLI
- Configuration managed via web UI at `/integration` route

### Frontend Architecture

- **React Router** for navigation between pages
- **React Query (@tanstack/react-query)** for server state management
- **Material-UI** theming with light/dark mode support
- **API client** in `frontend/src/services/api.ts` handles all backend communication
- **TypeScript interfaces** in `frontend/src/types/index.ts` mirror backend Pydantic models

Component organization:
- `components/common/`: Layout, navigation, ProjectSelector
- `components/config/`: API key configuration
- `components/projects/`: Multi-project management UI
- `components/stores/`: File Search store management
- `components/documents/`: Document upload/list/delete with metadata
- `components/query/`: RAG query interface
- `components/drive/`: Drive sync configuration
- `components/local/`: Local file synchronization UI with file browser dialog
- `components/backups/`: Backup management interface (create, restore, download, upload)
- `components/integration/`: MCP/CLI configuration and examples

### Metadata Handling

Documents support up to 20 custom metadata key/value pairs:

- **Conversion logic** in `backend/app/services/document_service.py`
- Simple format: `{"author": "John", "year": 2024}`
- Google format: `{"custom_metadata": [{"key": "author", "string_value": "John"}, {"key": "year", "numeric_value": 2024}]}`
- The service layer handles bidirectional conversion automatically

### Local Files with Metadata and Project Association

Local files now support custom metadata and automatic project association:

**Database Schema** (`backend/app/models/db_models.py - LocalFileLinkDB`):
- `project_id` (Integer): Associates file to a project (auto-assigned to active project)
- `custom_metadata` (JSON): User-defined key-value pairs (up to 20)

**Key Features**:
1. **Automatic Project Assignment**: Files created without explicit `project_id` are assigned to the active project
2. **Metadata Merging**: Custom metadata is merged with automatic metadata (file_hash, synced_from, last_modified)
3. **Project Filtering**: `list_links()` and `sync_all()` filter by active project by default
4. **Frontend Auto-Reload**: Listens to `activeProjectChanged` event and reloads data automatically

**Implementation** (`backend/app/services/local_file_service.py`):
```python
# Auto-assign to active project
project_id = link_data.project_id or active_project.id

# Merge metadata
auto_metadata = {"file_hash": hash, "synced_from": "local_filesystem"}
combined_metadata = {**auto_metadata, **(link.custom_metadata or {})}

# Filter by project
query.filter(LocalFileLinkDB.project_id == active_project.id)
```

**Migration**: `backend/migrate_add_local_files_enhancements.py` adds both columns and assigns existing files to active project

### Force Delete Pattern

Documents in File Search cannot be deleted while indexed. The pattern used:

1. Try normal delete
2. If fails with "document is indexed", wait 2 seconds
3. Retry with force delete (internal Google operation)
4. Implemented in `document_service.delete_document()`

### Router Registration Order

**CRITICAL**: In `backend/app/main.py`, routers must be registered in specific order:

```python
app.include_router(documents.router)  # First (specific routes)
app.include_router(stores.router)     # After (has /{store_id:path} which is greedy)
```

The `{store_id:path}` parameter captures all paths, so more specific routes must come first.

## Key Files to Know

### Backend
- `backend/app/main.py` - FastAPI app, lifespan events, router registration, active project loading
- `backend/app/config.py` - Environment variables and settings
- `backend/app/database.py` - SQLAlchemy setup and session management
- `backend/app/services/google_client.py` - Singleton GoogleClient managing google-genai SDK
- `backend/app/services/document_service.py` - Document operations and metadata conversion
- `backend/app/services/local_file_service.py` - Local file synchronization and versioning
- `backend/app/services/file_update_service.py` - File update tracking and history
- `backend/app/services/file_browser_service.py` - Server filesystem navigation
- `backend/app/services/backup_service.py` - Backup creation and restoration
- `backend/app/models/db_models.py` - SQLAlchemy models for persistence
- `backend/app/api/backups.py` - Backup management endpoints
- `backend/app/api/local_files.py` - Local file sync endpoints
- `backend/app/api/file_browser.py` - File browser endpoints
- `backend/app/api/file_updates.py` - File update tracking endpoints
- `backend/mcp_server.py` - MCP server entry point
- `backend/requirements.txt` - Python dependencies

### Frontend
- `frontend/src/App.tsx` - Main app component with routing
- `frontend/src/services/api.ts` - HTTP client for all backend endpoints
- `frontend/src/types/index.ts` - TypeScript type definitions
- `frontend/src/theme/theme.ts` - MUI theme configuration
- `frontend/src/components/backups/BackupsPage.tsx` - Backup management UI
- `frontend/src/components/local/LocalFilesPage.tsx` - Local file sync management
- `frontend/src/components/local/FileBrowserDialog.tsx` - File browser dialog component
- `frontend/package.json` - Node dependencies

### CLI
- `cli/main.py` - Click-based CLI with Rich formatting
- `cli/config.py` - CLI configuration management
- `filesearch-gemini` - Executable entry point

### Configuration
- `backend/.env` - Backend environment variables (API key, CORS origins)
- `backend/credentials.json` - Google OAuth2 credentials for Drive API
- `backend/token.json` - OAuth2 token cache (auto-generated)

### Utilities
- `manage_backup.sh` - Backup and restore script for database and credentials
- `start.sh` - Script to start both backend and frontend

## Development Workflow Patterns

### Adding a New API Endpoint

1. Define Pydantic models in `backend/app/models/`
2. Implement business logic in `backend/app/services/`
3. Create API endpoint in `backend/app/api/`
4. Add TypeScript types in `frontend/src/types/index.ts`
5. Add API client method in `frontend/src/services/api.ts`
6. Create or update React component in `frontend/src/components/`

### Working with Google File Search API

The `google_client.py` service handles all SDK interactions:

- Use `google_client.configure(api_key)` to set/change API key
- Use `google_client.client` to access the configured GenAI client
- The client is a singleton - one instance shared across the app
- All File Search operations use the pattern: `client.aip.file_search_stores.*`

### Database Migrations

This project doesn't use Alembic for migrations. Manual migration scripts:

- `backend/migrate_add_drive_file_name.py` - Adds drive_file_name column
- `backend/migrate_add_versioning_and_local_files.py` - Adds versioning support
- `backend/migrate_encrypt_api_keys.py` - Encrypts existing plain text API keys
- `backend/migrate_add_local_files_enhancements.py` - Adds custom_metadata and project_id to local files

To add new columns/tables:
1. Update SQLAlchemy models in `db_models.py`
2. Create a migration script that checks if columns exist before adding
3. Run the script manually: `python migrate_script_name.py`

### Testing Approach

Limited test coverage exists:

- `tests/test_cli.py` - CLI command tests
- `tests/test_mcp_server.py` - MCP server tool tests
- Uses `pytest` and `pytest-mock`
- Tests mock the backend HTTP responses

When adding tests:
- Mock external dependencies (Google API, HTTP calls)
- Test the service layer logic independently
- Use fixtures for common test data

## Common Issues and Solutions

### "module 'google.generativeai' has no attribute 'list_file_search_stores'"

**Cause:** Wrong SDK installed.
**Solution:** `pip install -r requirements.txt` to get `google-genai` (not `google-generativeai`)

### Backend fails to start - "No active project"

**Cause:** No project activated or API key configured.
**Solution:** Create a project via web UI at `/projects` or set `GOOGLE_API_KEY` in `.env`

### CORS errors in browser

**Cause:** Frontend origin not allowed.
**Solution:** Add origin to `CORS_ORIGINS` in `backend/.env` (default includes `http://localhost:5173`)

### Documents not indexing

**Check:**
1. API key is valid and has correct permissions
2. File format is supported by Google File Search
3. Backend logs for detailed error messages
4. Store exists and is accessible

### Drive sync not working

**Status:** Drive sync is partially implemented. OAuth flow exists but actual sync logic is stubbed.
**Next steps:** Implement the sync logic in `drive_service.sync_drive_link_now()`

## URLs and Ports

- **Frontend**: http://localhost:5173 (Vite dev server)
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs (Swagger)
- **API Documentation**: http://localhost:8000/redoc (ReDoc)
- **MCP Server**: Configurable (stdio or HTTP mode)

### Web UI Routes

- `/` - Home/Configuration page
- `/projects` - Multi-project management
- `/stores` - File Search stores management
- `/documents` - Document upload and management
- `/query` - RAG query interface
- `/drive` - Google Drive synchronization
- `/local-files` - Local file synchronization
- `/backups` - Backup management (create, restore, download, upload)
- `/audit-logs` - System audit trail with statistics and filtering
- `/integration` - MCP/CLI configuration and examples

## Important Notes

- The CLI and MCP server both communicate with the backend API - they don't run standalone
- Project switching requires backend restart to reload the active project's API key
- The `google-genai` SDK is required - older SDKs won't work
- Metadata conversion between simple and Google format is automatic in document service
- Force delete is needed for indexed documents - always use the service layer delete method
- SQLite is used for development - consider PostgreSQL for production
- **Local file sync** monitors file changes using SHA256 hashing and auto-syncs every 3 minutes to File Search stores
- **Drive sync** auto-syncs every 5 minutes for links in AUTO mode
- **Backup system** is available both via CLI (`manage_backup.sh`) and web UI (`/backups`)
- **File browser** has security restrictions to prevent access to sensitive system directories
- **API keys are encrypted** - `.encryption_key` file must be backed up; if lost, encrypted keys are unrecoverable
- **Audit logs** track all critical operations with user/IP, success/failure, and detailed information
