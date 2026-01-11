# Changelog

## v2.2.0 - Multi-Project Support

### New Features

#### Multiple Google AI Studio Project Management

- **Full support for multiple projects**:
  - Create and manage multiple Google AI Studio projects
  - Each project with its own independent API key
  - Up to 10 File Search stores per project (Google limit)
  - One active project at a time
  - Quick switching between projects without losing context

- **New "Projects" page** in the web interface:
  - Create new projects with name, API key, and description
  - List all projects with activation status
  - Edit existing projects (name, API key, description)
  - Delete projects you no longer need
  - Activate/deactivate projects with one click
  - Automatic API key validation when creating/updating

- **Project selector in header**:
  - Dropdown in the top bar to view active project
  - Quick switching between projects from any page
  - Visual icon for active project
  - Automatic reload when switching projects

- **Database for projects**:
  - SQLite table to store projects
  - Fields: id, name, api_key, description, is_active, timestamps
  - Automatic migration on application startup
  - TODO: API key encryption for production

### Backend - New Endpoints

- `POST /projects` - Create new project with API key validation
- `GET /projects` - List all projects + active project
- `GET /projects/active` - Get currently active project
- `GET /projects/{id}` - Get specific project
- `PUT /projects/{id}` - Update project
- `POST /projects/{id}/activate` - Activate project (deactivates others)
- `DELETE /projects/{id}` - Delete project

### Frontend - New Components

- `ProjectsPage.tsx` - Full project management page
- `ProjectSelector.tsx` - Project selector for header
- Updated `ConfigPage.tsx` with multi-project notice
- New TypeScript types: `Project`, `ProjectCreate`, `ProjectUpdate`, `ProjectList`

### Documentation

- New `MULTI_PROJECT.md` file with complete guide:
  - Key concepts (projects, active project)
  - Step-by-step usage instructions
  - API endpoint documentation
  - Database schema
  - Migration guide from previous version
  - Best practices
  - Troubleshooting

### Changes to Existing Components

- **Configuration Page**: New informational banner about multi-project
- **Layout**: New "Projects" menu item with folder icon
- **API Client**: New methods in `projectsApi` for all operations

### Upgrade Notes

If upgrading from v2.1.x:
1. Database will automatically update with the `projects` table
2. Your current API key will continue to work
3. Create your first project on the "Projects" page
4. The first project you create will automatically become active
5. You can continue using the "Configuration" page to update the active project's API key

### Use Cases

- **Multiple clients**: One project per client with isolated data
- **Multiple environments**: Separate projects for development, staging, and production
- **Store limit**: Overcome the 10-store limit using multiple projects
- **Organization**: Group related stores by project

### Limitations

- Only one project can be active at a time
- When switching projects, the page reloads completely
- API keys stored in plain text (TODO: encryption)
- Cannot use multiple projects simultaneously

---

## v2.1.1 - Web-based MCP/CLI Configuration Management

### New Features

#### Web Interface for Configuration
- **New "LLM Integration" section** in the web interface
  - Tab "MCP Server": Configure backend URL and enable/disable server
  - Tab "CLI Local": Configure CLI with backend URL and default store
  - Tab "Integration Guide": Complete guide with examples for all agents
  - Copy/paste buttons for all configurations
  - Dynamically updated examples based on configuration

- **Backend endpoints** for configuration management:
  - `GET/POST /integration/mcp/config` - MCP configuration
  - `GET /integration/mcp/status` - MCP status and examples
  - `GET/POST /integration/cli/config` - CLI configuration
  - `GET /integration/cli/status` - CLI status and examples
  - `GET /integration/guide` - Complete integration guide

- **Configuration persistence**:
  - JSON files in `backend/config/` for MCP and CLI
  - Configuration accessible from web, MCP server, and CLI

### Improvements

- Updated README with web management section
- Updated navigation with new "LLM Integration" item
- Modular and reusable React components
- Complete TypeScript type safety

### Upgrade Notes

If upgrading from v2.1.0:
1. Configuration files are automatically created in `backend/config/`
2. Access the new interface at: http://localhost:5173/integration
3. Previous configuration (env vars, CLI config) remains valid

---

## v2.1.0 - MCP and CLI Integration for LLM Agents

### New Features

#### MCP Server (Model Context Protocol)
- **Complete MCP server** with 21 tools for LLM agents
  - Compatible with Gemini CLI, Claude Code, and Codex CLI
  - Implemented with FastMCP for better DX
  - stdio transport (default mode, recommended)
  - HTTP communication with FastAPI backend

- **Available MCP tools**:
  - **Configuration**: `set_api_key`, `get_config_status`
  - **Stores**: `create_store`, `list_stores`, `get_store`, `delete_store`
  - **Documents**: `upload_document`, `list_documents`, `update_document`, `delete_document`
  - **RAG Queries**: `rag_query` (with metadata filtering and citations)
  - **Drive Sync**: `create_drive_link`, `list_drive_links`, `get_drive_link`, `delete_drive_link`, `sync_drive_link_now`

#### Local CLI (filesearch-gemini)
- **Complete command-line interface** for direct use or from agents
  - Implemented with Click + Rich for excellent UX
  - Subcommands organized by functionality
  - Formatted output with tables and colors
  - Support for JSON output (useful for scripting)

- **Available commands**:
  - `config`: Configuration management (API key, backend URL, status)
  - `stores`: Store operations (list, create, get, delete)
  - `docs`: Document management (list, upload, delete)
  - `query`: RAG queries with metadata filtering
  - `drive`: Google Drive synchronization (list, create, sync-now, delete)

- **Flexible configuration**:
  - Environment variables (highest priority)
  - Configuration file `~/.filesearch-gemini/config.yaml`
  - Sensible default values

### Documentation

- **MCP_INTEGRATION.md**: Complete integration guide
  - Step-by-step configuration for each MCP client
  - Practical usage examples
  - Troubleshooting and best practices
  - Complete example workflow

- **Configuration examples** in `examples/`:
  - `gemini-cli-settings.json` - Config for Gemini CLI
  - `claude-code-mcp.json` - Config for Claude Code
  - `codex-mcp-config.json` - Config for Codex CLI
  - `cli-config.yaml` - Config for local CLI

- **Updated README** with MCP/CLI integration section

### Tests

- Basic tests for MCP server (`tests/test_mcp_server.py`)
- Basic tests for CLI (`tests/test_cli.py`)
- Testing infrastructure with pytest

### New Dependencies

- `fastmcp==0.6.1` - Simplified MCP framework
- `httpx==0.28.1` - Modern HTTP client for MCP and CLI
- `click==8.1.8` - CLI framework
- `rich==13.9.4` - Enhanced terminal output
- `pyyaml==6.0.2` - YAML configuration
- `pytest==8.3.4` - Testing framework
- `pytest-mock==3.14.0` - Mocking for tests

### Enabled Use Cases

You can now use File Search from:
1. **Web Interface** (browser) - complete visual experience
2. **REST API** (curl, Postman) - direct HTTP integration
3. **MCP Server** (Gemini CLI, Claude Code, Codex) - LLM agent integration
4. **Local CLI** (terminal) - manual use or scripting

### Upgrade Notes

If upgrading from v2.0.0:
1. Install new dependencies: `pip install -r backend/requirements.txt`
2. MCP server starts with: `python backend/mcp_server.py`
3. CLI runs with: `./filesearch-gemini --help`
4. See [MCP_INTEGRATION.md](./MCP_INTEGRATION.md) to configure your LLM agent

---

## v2.0.0 - Migration to Official SDK and Complete Google Drive Synchronization

### BREAKING CHANGES

- **Migrated from `google-generativeai` (legacy) to `google-genai` (official)**
  - Previous SDK ends support in August 2025
  - New SDK is official and correctly supports File Search
  - Default model changed to `gemini-2.5-flash`

### New Features

#### Complete Google Drive Sync
- **OAuth 2.0** implemented for Google Drive authentication
- **Real synchronization** of Drive files → File Search:
  - Automatic change detection (modifiedTime)
  - File download from Drive
  - Upload to File Search stores
  - Incremental update (only syncs if changed)
- **Synchronization modes**:
  - Manual: sync on demand with button
  - Automatic: synchronization every 5 minutes via scheduler
- **Database persistence** (SQLite by default)
- **Automatic scheduler** with APScheduler
- **Synchronization metadata**:
  - `drive_file_id`: Drive file ID
  - `synced_from`: "google_drive"
  - `last_modified`: last modification timestamp

#### File Search Improvements
- Updated methods to use official SDK:
  - `client.file_search_stores.create()`
  - `client.file_search_stores.list()`
  - `client.file_search_stores.upload_to_file_search_store()`
  - etc.
- Better custom metadata handling
- Full support for chunking configuration

### Technical Improvements

#### Backend
- SQLAlchemy database with SQLite
- Migrations with Alembic (pending configuration)
- Background Scheduler with APScheduler
- Separate Drive client (`drive_client.py`)
- App lifecycle management (lifespan)
- Updated endpoints with DB dependencies

#### Configuration
- New environment variables:
  - `GOOGLE_DRIVE_CREDENTIALS`: path to OAuth credentials.json
  - `GOOGLE_DRIVE_TOKEN`: path to token.json (auto-generated)
  - `DATABASE_URL`: database URL (default: SQLite)
- Updated model: `gemini-2.5-flash` (compatible with File Search)

#### Updated Dependencies
- `google-genai==1.6.1` (new official SDK)
- `google-auth-oauthlib==1.2.1`
- `google-auth-httplib2==0.2.0`
- `google-api-python-client==2.154.0`
- `sqlalchemy==2.0.36`
- `alembic==1.14.0`
- `apscheduler==3.10.4`

### Documentation

- Updated README with OAuth instructions
- Guide to obtain credentials.json from Google Cloud Console
- Drive sync configuration examples
- Scheduler and automatic synchronization documentation

### Bug Fixes

- **CRITICAL**: Fixed error `module 'google.generativeai' has no attribute 'list_file_search_stores'`
  - Cause: Legacy SDK doesn't have File Search
  - Solution: Complete migration to official `google-genai` SDK
- Metadata now uses correct format from new SDK
- Query service updated for new generation API

### Migration from v1.0.0

#### For existing users:

1. **Update dependencies**:
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

2. **Configure Google Drive** (optional):
   - Create project in Google Cloud Console
   - Enable Drive API
   - Download `credentials.json`
   - Add path in `.env`: `GOOGLE_DRIVE_CREDENTIALS=path/to/credentials.json`

3. **First run**:
   - Database is created automatically
   - For Drive sync, run OAuth authentication the first time
   - Token is saved in `token.json` for future sessions

4. **API key**:
   - Existing API keys continue to work
   - Model automatically changed to `gemini-2.5-flash`

### Statistics

- **Modified files**: 15+
- **New files**: 4
- **Lines added**: ~800+
- **New features**: 8+

### Next Steps

- [ ] Configure Alembic for DB migrations
- [ ] Add automated tests
- [ ] UI to configure OAuth from frontend
- [ ] Drive file listing in UI
- [ ] Synchronization metrics
- [ ] Detailed sync operation logs

---

## v1.0.0 - Initial Version

### Features
- Basic File Search store management
- Document upload and management
- Multi-store RAG queries
- Custom metadata
- Material-UI interface
- Light/dark themes
- Complete REST API

### Stack
- Backend: FastAPI + google-generativeai (legacy)
- Frontend: React + TypeScript + Vite
- Model: gemini-2.0-flash-exp
