# Multi-Project Support

## Overview

The File Search RAG application now supports managing multiple Google AI Studio projects, each with its own API key and set of File Search stores. This feature allows you to:

- **Organize stores by project**: Each Google AI Studio project can have up to 10 File Search stores
- **Manage multiple API keys**: Store and switch between different Google AI Studio API keys
- **Isolate data**: Keep stores and documents separated by project
- **Easy switching**: Quickly switch between projects using the header selector

## Key Concepts

### Projects

A **Project** represents a Google AI Studio project with:
- **Unique name**: A descriptive name for the project
- **API Key**: The Google AI Studio API key for accessing File Search
- **Description** (optional): Additional information about the project
- **Active status**: Only one project can be active at a time

### Active Project

The **active project** is the currently selected project whose API key is being used for all File Search operations. When you switch the active project:
- All API calls use the new project's API key
- Stores and documents are automatically filtered to the new project
- The page reloads to ensure consistency

## Using Multi-Project Support

### Creating a New Project

1. Navigate to the **Projects** page from the sidebar menu
2. Click the **Create Project** button
3. Fill in the form:
   - **Project Name**: A unique identifier (e.g., "Production", "Development", "Client A")
   - **API Key**: Your Google AI Studio API key for this project
   - **Description**: Optional description
4. Click **Create**

The first project you create will automatically become the active project.

### Switching Between Projects

You can switch the active project in two ways:

#### Method 1: Using the Header Selector

1. Look for the project selector in the top-right corner of the header
2. Click the dropdown to see all available projects
3. Select a different project
4. The page will reload with the new active project

#### Method 2: Using the Projects Page

1. Navigate to the **Projects** page
2. Find the project you want to activate
3. Click the inactive status icon (circle) in the Status column
4. The project will become active and the page will reload

### Editing a Project

1. Navigate to the **Projects** page
2. Find the project you want to edit
3. Click the **Edit** icon (pencil)
4. Update the information:
   - **Project Name**: Change the display name
   - **API Key**: Update the API key (leave empty to keep current)
   - **Description**: Update the description
5. Click **Update**

**Note**: If you update the API key, it will be validated before saving.

### Deleting a Project

1. Navigate to the **Projects** page
2. Find the project you want to delete
3. Click the **Delete** icon (trash can)
4. Confirm the deletion

**Important**:
- Deleting a project only removes it from the application's database
- The actual stores and documents remain in Google AI Studio
- If you delete the active project and other projects exist, another project will automatically become active
- You cannot delete the active project if it's the only project

## API Endpoints

The following API endpoints are available for managing projects:

### List Projects
```
GET /projects
```
Returns all projects and the currently active project ID.

**Response:**
```json
{
  "projects": [
    {
      "id": 1,
      "name": "Production",
      "description": "Production environment",
      "is_active": true,
      "created_at": "2024-01-15T10:00:00Z",
      "has_api_key": true
    }
  ],
  "active_project_id": 1
}
```

### Get Active Project
```
GET /projects/active
```
Returns only the currently active project.

### Create Project
```
POST /projects
```

**Request Body:**
```json
{
  "name": "My Project",
  "api_key": "AIza...",
  "description": "Optional description"
}
```

**Response:** The created project (API key not included)

### Get Project by ID
```
GET /projects/{id}
```

### Update Project
```
PUT /projects/{id}
```

**Request Body:**
```json
{
  "name": "Updated Name",
  "api_key": "NewKey...",  // Optional
  "description": "Updated description"
}
```

### Activate Project
```
POST /projects/{id}/activate
```
Makes the specified project the active one.

### Delete Project
```
DELETE /projects/{id}
```

## Database Schema

The projects are stored in a SQLite database (by default) with the following schema:

```sql
CREATE TABLE projects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    api_key TEXT NOT NULL,
    description TEXT,
    is_active BOOLEAN NOT NULL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP
);
```

**Security Note**: API keys are currently stored in plain text in the database. For production use, consider implementing encryption. This is marked as a TODO in the code.

## Migration from Single Project

If you're upgrading from a version without multi-project support:

1. Your existing API key configuration will continue to work
2. Create your first project using the **Projects** page
3. The first project you create will become the active project
4. All existing stores will be accessible through this project
5. You can continue to use the **Configuration** page to update the API key for the active project

The Configuration page now displays an informational message about multi-project support.

## Limitations

- **10 stores per project**: Google File Search allows a maximum of 10 stores per Google AI Studio project
- **One active project**: Only one project can be active at a time
- **No concurrent access**: When switching projects, the application must reload to ensure all data is consistent

## Best Practices

1. **Descriptive names**: Use clear, descriptive names for your projects (e.g., "Production - Company A", "Development - Testing")
2. **Document your projects**: Use the description field to note important information about each project
3. **Organize by environment**: Create separate projects for development, staging, and production
4. **Organize by client**: If you serve multiple clients, create one project per client
5. **Regular cleanup**: Delete projects you no longer need to keep your project list manageable

## Troubleshooting

### "Invalid API key" error when creating a project

- Verify the API key is correct
- Check that the API key has File Search API enabled in Google AI Studio
- Ensure the API key hasn't been deleted or restricted

### Project selector shows "No projects"

- Create your first project using the **Projects** page
- Refresh the browser if you just created a project

### Can't delete a project

- You cannot delete the only remaining project
- Create a new project first, then delete the old one

### Stores not showing after switching projects

- This is expected - each project has its own set of stores
- Verify you're looking at the correct project in the header selector
- The page should have automatically reloaded after switching

## Technical Details

### Architecture

The multi-project feature is implemented across the full stack:

**Backend (Python/FastAPI):**
- `app/models/db_models.py`: ProjectDB database model
- `app/models/project.py`: Pydantic models for API
- `app/services/project_service.py`: Business logic for project management
- `app/api/projects.py`: REST API endpoints

**Frontend (React/TypeScript):**
- `frontend/src/types/index.ts`: TypeScript type definitions
- `frontend/src/services/api.ts`: API client methods
- `frontend/src/components/projects/ProjectsPage.tsx`: Project management UI
- `frontend/src/components/common/ProjectSelector.tsx`: Header project selector

### Project Activation Flow

When a project is activated:

1. All other projects are marked as inactive in the database
2. The selected project is marked as active
3. The GoogleClient is reconfigured with the new project's API key
4. The frontend reloads to refresh all data with the new project context

### API Key Validation

When creating or updating a project with a new API key:

1. The GoogleClient is temporarily configured with the new key
2. A test connection is made to Google's API
3. If the connection succeeds, the key is saved
4. If it fails, an error is returned and the key is not saved

## Future Enhancements

Potential improvements for future versions:

- [ ] API key encryption in the database
- [ ] Project-level permissions and access control
- [ ] Project cloning (duplicate stores and settings)
- [ ] Project export/import functionality
- [ ] Usage statistics per project
- [ ] Project archiving instead of deletion
