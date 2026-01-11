# Google Drive Sync Setup

This guide explains how to configure automatic synchronization with Google Drive for the File Search RAG system.

## What Does Drive Sync Do?

The Drive Sync functionality allows you to:
- **Link Google Drive files** to File Search stores
- **Automatic synchronization**: detects when a file changes in Drive and updates it in File Search
- **Manual synchronization**: sync on demand with a button
- **Automatic metadata**: adds Drive metadata (file_id, last modification)

## Prerequisites

1. Google account
2. Project in Google Cloud Console (free)
3. Python 3.11+ installed
4. Backend application running

## Step 1: Create Project in Google Cloud Console

### 1.1 Create Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click the project selector (top left)
3. Click "New Project"
4. Name: `File Search RAG App` (or your preference)
5. Click "Create"

### 1.2 Enable Google Drive API

1. In the side menu, go to **APIs & Services > Library**
2. Search for "Google Drive API"
3. Click "Google Drive API"
4. Click "ENABLE"

## Step 2: Create OAuth 2.0 Credentials

### 2.1 Configure Consent Screen

1. Go to **APIs & Services > OAuth consent screen**
2. Select **External** (users can be anyone with a Google account)
3. Click "Create"
4. Complete the form:
   - **App name**: "File Search RAG"
   - **Support email**: your email
   - **Authorized domains**: (leave empty for local development)
   - **Developer email**: your email
5. Click "Save and Continue"
6. In "Scopes", click "Add or Remove Scopes"
7. Search and add: `https://www.googleapis.com/auth/drive.readonly`
8. Click "Update" then "Save and Continue"
9. In "Test users", add your Google email
10. Click "Save and Continue"

### 2.2 Create Credentials

1. Go to **APIs & Services > Credentials**
2. Click "Create credentials" > "OAuth 2.0 Client ID"
3. Application type: **Desktop Application**
4. Name: "File Search RAG Desktop Client"
5. Click "Create"
6. **IMPORTANT!** Download the JSON file by clicking the download icon
7. Save the file as `credentials.json`

## Step 3: Configure the Application

### 3.1 Place Credentials

Option A - In the backend directory:
```bash
mv ~/Downloads/credentials.json /path/to/filesearch-gemini/backend/credentials.json
```

Option B - In any location:
```bash
# Keep the file wherever you want and note the full path
```

### 3.2 Update .env

Edit the `backend/.env` file:

```bash
# Path to credentials file (REQUIRED for Drive sync)
GOOGLE_DRIVE_CREDENTIALS=/path/to/filesearch-gemini/backend/credentials.json

# Path where token will be saved (auto-generated)
GOOGLE_DRIVE_TOKEN=/path/to/filesearch-gemini/backend/token.json
```

Alternatively, if you placed `credentials.json` in the backend directory:

```bash
GOOGLE_DRIVE_CREDENTIALS=credentials.json
GOOGLE_DRIVE_TOKEN=token.json
```

## Step 4: First Authentication

### 4.1 Start Backend

```bash
cd backend
source venv/bin/activate
python -m app.main
```

### 4.2 OAuth Authentication (First Time)

The first time you try to sync a Drive file:

1. The system will automatically open your browser
2. You'll see a Google screen asking for permission
3. **IMPORTANT**: If you see "This app isn't verified":
   - Click "Advanced"
   - Click "Go to File Search RAG (unsafe)"
   - This is normal for apps in development
4. Select your Google account
5. Review the permissions (read-only Drive access)
6. Click "Continue"
7. The browser will show "The authentication flow has completed"

After this, the `token.json` file is created automatically and future syncs won't require authentication.

## Step 5: Using the Application

### 5.1 Create a Drive Link

1. Go to the **Drive Sync** section in the UI
2. Click "Add Link"
3. Complete the form:
   - **Drive File ID**: ID of the file in Google Drive
   - **Store**: Select the destination store
   - **Sync Mode**:
     - **Manual**: syncs only when you click "Sync"
     - **Auto**: syncs automatically every 5 minutes
   - **Sync Interval** (only for Auto mode): minutes between syncs

#### How to Get the Drive File ID?

Method 1 - From the URL:
```
https://drive.google.com/file/d/1ABC...XYZ/view
                              ^^^^^^^^^ This is the File ID
```

Method 2 - Right click on file > Get link > Share
The ID is in the shared link URL.

### 5.2 Manual Sync

1. In the Drive Links table, find your link
2. Click the sync icon (↻)
3. Status will change to "syncing" then to "synced"
4. The document will appear in the selected store

### 5.3 Automatic Synchronization

If you configured automatic mode:
- The scheduler runs every 5 minutes
- Only syncs if the file has changed in Drive
- You can see last sync time in the "Last Synced" column

## Verification

### Verify that Drive API works:

```python
# In Python, with the backend active:
from app.services.drive_client import drive_client

# Connection test
success, error = drive_client.test_connection()
if success:
    print("Drive API configured correctly")
else:
    print(f"Error: {error}")
```

### Verify scheduler:

Backend logs will show:
```
INFO:app.scheduler:Scheduler started: auto-sync every 5 minutes
INFO:app.scheduler:Running automatic Drive sync job...
```

## Troubleshooting

### Error: "credentials file not found"

**Cause**: Incorrect path in `.env`

**Solution**:
```bash
# Verify the path
ls -la /path/to/credentials.json

# Update .env with the correct path
GOOGLE_DRIVE_CREDENTIALS=/correct/absolute/path/credentials.json
```

### Error: "The authentication flow has completed" but doesn't work

**Cause**: token.json wasn't saved correctly

**Solution**:
```bash
# Delete token.json and re-authenticate
rm backend/token.json
# Restart backend and try syncing again
```

### Error: "Failed to retrieve file metadata"

**Cause**: Incorrect File ID or file not accessible

**Solution**:
- Verify the File ID is correct
- Make sure your Google account has access to the file
- The file must be in "My Drive" or shared with you

### Error: "Insufficient permissions"

**Cause**: Drive scope not configured correctly

**Solution**:
1. Go to Google Cloud Console > APIs & Services > OAuth consent screen
2. Verify the `drive.readonly` scope is added
3. Delete `token.json`
4. Re-authenticate

### Token expired

Tokens expire after a certain time. If you see authentication errors:

```bash
# Delete the token and re-authenticate
rm backend/token.json
# Restart backend
```

## Security

### Sensitive Data

- `credentials.json`: **DO NOT share, DO NOT commit to Git**
- `token.json`: **DO NOT share, DO NOT commit to Git**
- Both files are in `.gitignore` by default

### Permissions

The `drive.readonly` scope only allows:
- Read file metadata
- Download file content
- Modify files
- Delete files
- Create files

### Revoke Access

If you want to revoke the application's access:
1. Go to [Google Account](https://myaccount.google.com/permissions)
2. Find "File Search RAG"
3. Click "Remove access"

## Limitations

- **File size**: Depends on Google Drive plan
- **File types**: All supported by File Search
- **Sync frequency**: Minimum 5 minutes in automatic mode
- **Number of links**: No limit (but consider API quota)

## Additional Resources

- [Google Drive API Documentation](https://developers.google.com/drive/api/guides/about-sdk)
- [OAuth 2.0 for Desktop Apps](https://developers.google.com/identity/protocols/oauth2/native-app)
- [File Search Documentation](https://ai.google.dev/gemini-api/docs/file-search)

## Tips

1. **Organize your links**: Use a different store for each project or document type
2. **Manual vs auto mode**: Use manual for files that rarely change, auto for dynamic documents
3. **Metadata**: Files synced from Drive automatically include:
   - `drive_file_id`: For tracking
   - `synced_from`: "google_drive"
   - `last_modified`: Drive timestamp
4. **Monitoring**: Check backend logs to see sync activity

---

**Problems?** Open an issue in the repository with:
- Backend logs
- `.env` configuration (without credentials)
- Steps you followed
