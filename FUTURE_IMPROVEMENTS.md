# Future Improvements & Feature Roadmap

List of improvements and new features proposed for future implementation.

---

## Search & Filtering

### Documents Page - Search/Filter Feature
**Priority:** Medium
**Complexity:** Low
**Status:** Proposed

**Description:**
Add search and filtering functionality to the Documents page to facilitate navigation when there are many documents.

**Proposed features:**
- Search by filename (client-side or server-side)
- Filter by metadata (tags, categories)
- Filter by upload date (date range)
- Filter by file type (MIME type)
- Column sorting (name, date, size)

**Suggested implementation:**
```typescript
// Frontend: DocumentsPage.tsx
- Add TextField with search icon
- Filter documents locally with .filter()
- Or implement backend endpoint with ?search= parameter

// Backend (optional): documents.py
- Add search parameter to list_documents
- Filter in Google File Search API if supported
```

**Affected files:**
- `frontend/src/components/documents/DocumentsPage.tsx`
- `frontend/src/services/api.ts`
- `backend/app/api/documents.py` (optional)

**Suggested UX:**
```
┌─────────────────────────────────────────────┐
│ Documents                    [+ Upload]     │
├─────────────────────────────────────────────┤
│ 🔍 Search documents...         [Filters ▾] │
├─────────────────────────────────────────────┤
│ Name          │ Metadata  │ State │ Created│
│ document.pdf  │ ...       │ ACTIVE│ 11/30  │
└─────────────────────────────────────────────┘
```

**Benefits:**
- Better user experience with many documents
- Faster to find specific documents
- Useful for stores with hundreds of documents

---

## Security Improvements

### (Reference: see SECURITY_PLAN.md for complete plan)

**Completed:**
- ✅ API key encryption (Fernet/AES-128) - Implemented
- ✅ Audit logging system - Implemented
- ✅ File browser security restrictions - Implemented

**Pending critical points:**
1. Filesystem restriction (ALLOWED_FS_ROOT) - URGENT
2. Input validation and sanitization
3. Basic authentication (API key or JWT)
4. Backup security (tar.gz file validation)

---

## Analytics & Insights

### Document Usage Analytics
**Priority:** Low
**Complexity:** Medium

**Ideas:**
- Dashboard with document statistics per store
- Upload graph by date
- Top documents most used in queries
- Total document size per project
- Historical duplicate detection (cleanup)

---

## Sync Improvements

### Drive Sync
**Priority:** Medium
**Complexity:** Medium
**Status:** Mostly implemented

**Completed:**
- ✅ Google Picker API for file selection
- ✅ Auto-sync scheduler for AUTOMATIC mode (every 5 minutes)
- ✅ Manual sync functionality
- ✅ SQLite persistence for drive links
- ✅ Metadata tracking (drive_file_id, synced_from, last_modified)

**Pending:**
- UI progress indicator for long syncs
- Folder sync support (recursive)

### Local Files
**Priority:** Low
**Status:** Implemented

**Completed:**
- ✅ File linking to File Search stores
- ✅ SHA256 hash-based change detection
- ✅ Auto-sync scheduler (every 3 minutes)
- ✅ File versioning and update history
- ✅ Custom metadata support (up to 20 key-value pairs)
- ✅ Project association

**Future ideas:**
- Support for complete directories (recursive sync)
- Exclude patterns (.gitignore style)
- Selective sync (choose which files to sync)

---

## UI/UX Enhancements

### General
- Improved dark mode
- Toast notifications for successful/failed actions
- Drag & drop for document upload
- Document preview (PDF, images)
- Bulk actions (select multiple documents to delete)

### Documents Page
- Improved pagination (infinite scroll)
- Grid/list view toggle
- Icons by file type
- Progress bar during uploads
- Inline metadata editor

---

## Technical Debt

### Backend
- Migrate from SQLite to PostgreSQL for production
- Implement automated tests (pytest)
- API rate limiting
- Structured logging (JSON logs)
- Metrics/observability (Prometheus)

### Frontend
- TypeScript strict mode
- Error boundaries
- Unit tests (Jest/React Testing Library)
- E2E tests (Playwright/Cypress)
- Code splitting for improved performance

---

## Documentation

### Needs documentation
- Complete API Reference (improved Swagger)
- User manual/guide
- Deployment guide (Docker, Kubernetes)
- Contributing guide
- Architecture diagrams

---

## Performance Optimizations

### Documents Upload
- Chunked upload for large files (>100MB)
- Detailed progress tracking
- Retry logic for failed uploads
- Background processing

### Database
- Optimized indexes
- Query optimization
- Connection pooling
- Caching layer (Redis)

---

## Completed Features

The following features have been implemented:

- ✅ **API Key Encryption** - Fernet (AES-128) encryption for secure storage
- ✅ **Audit Logging** - Complete audit trail with user/IP tracking, success/failure, detailed information
- ✅ **Duplicate Detection** - SHA256 hashing prevents duplicate uploads with interactive warning dialog
- ✅ **Local File Sync** - Full implementation with auto-sync every 3 minutes
- ✅ **Drive Sync Scheduler** - Auto-sync every 5 minutes for AUTO mode links
- ✅ **Google Picker API** - Visual file selection from Drive (100% functional)
- ✅ **File Browser** - Server filesystem navigation with security restrictions
- ✅ **Backup System** - Both CLI (manage_backup.sh) and Web UI (/backups)
- ✅ **MCP Server** - 21 tools for LLM agent integration
- ✅ **Local CLI** - Complete command-line interface with Rich formatting
- ✅ **Multi-Project Support** - Manage multiple Google AI Studio projects
- ✅ **Custom Metadata** - Up to 20 key-value pairs per document/file

---

**Last updated:** 2026-01-11
**Maintained by:** Claude Code + User

**How to contribute:**
- Add new ideas to appropriate sections
- Mark completed items as implemented
- Update priorities as needed
