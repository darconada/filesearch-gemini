# Security Hardening Plan

**Status:** In development - Security plan for implementation before production

**Goal:** Close attack surface without breaking current flows. Execution order by risk priority.

---

## CRITICAL - Implement BEFORE production

### 1) Filesystem restriction - URGENT

**Problem:** File browser and local files can access the ENTIRE server filesystem.

**Solution:**
- Introduce env `ALLOWED_FS_ROOT` (e.g., `/data/files`). Validate that `file_browser` and `local_files` cannot escape that root.
- Implement validation that rejects path traversal (`../`, `..\\`, symlinks pointing outside root).
- Add hardcoded blocklist of sensitive paths: `/etc`, `/root`, `/home`, `/var`, `/sys`, `/proc`, `.ssh`, `.env`, `token.json`, `credentials.json`.
- Normalize paths with `os.path.realpath()` and validate they start with `ALLOWED_FS_ROOT`.

**Affected files:**
- `backend/app/services/file_browser_service.py`
- `backend/app/services/local_file_service.py`

**Verification:**
```python
# Tests that should FAIL with 403:
- Access to ../../etc/passwd
- Access to /root/
- Symlink outside root
- Paths with null bytes
- Malicious URL-encoded paths
```

**Example code:**
```python
import os
from pathlib import Path

ALLOWED_FS_ROOT = os.getenv("ALLOWED_FS_ROOT", "/data/files")
BLOCKED_PATHS = ["/etc", "/root", "/home", "/var", "/sys", "/proc", ".ssh", ".env", "token.json", "credentials.json"]

def validate_path(requested_path: str) -> Path:
    """Validates that path is within allowed root"""
    # Normalize and resolve symlinks
    real_path = Path(requested_path).resolve()
    root_path = Path(ALLOWED_FS_ROOT).resolve()

    # Verify it's within root
    if not str(real_path).startswith(str(root_path)):
        raise PermissionError(f"Access denied: path outside allowed root")

    # Check blocklist
    for blocked in BLOCKED_PATHS:
        if blocked in str(real_path):
            raise PermissionError(f"Access denied: blocked path pattern")

    return real_path
```

---

### 2) Input validation and sanitization

**Problem:** Lack of strict input validation that can cause vulnerabilities.

**Solution:**
- **Google File IDs:** Validate format (alphanumeric + `-_`, expected length).
- **Filenames:** Sanitize before saving (no `../`, no null bytes, no dangerous special characters).
- **Metadata:** Validate types, limits (max 20 keys), value lengths.
- **Store IDs:** Validate expected Google format.
- **Project names:** Sanitize SQL injection, XSS (even using ORM).

**Affected files:**
- `backend/app/models/schemas.py` - Add Pydantic validators
- All services that handle user input

**Example code:**
```python
from pydantic import validator, Field
import re

class DocumentUpload(BaseModel):
    store_id: str = Field(..., min_length=10, max_length=200)

    @validator('store_id')
    def validate_store_id(cls, v):
        # Format: fileSearchStores/xxx-xxx-xxx
        if not re.match(r'^fileSearchStores/[a-z0-9-]+$', v):
            raise ValueError('Invalid store ID format')
        return v

class LocalFileLinkCreate(BaseModel):
    local_path: str

    @validator('local_path')
    def validate_local_path(cls, v):
        # Don't allow path traversal
        if '..' in v or v.startswith('/'):
            raise ValueError('Invalid path: path traversal detected')
        # No null bytes
        if '\x00' in v:
            raise ValueError('Invalid path: null byte detected')
        return v
```

---

### 3) Secure secrets management

**Problem:** Secrets in `.env` files and file permissions.

**Solution:**
- **Development:** Continue using `.env` but with documented `.env.example`.
- **Production:** Move to system environment variables or secret manager (AWS Secrets Manager, HashiCorp Vault, etc.).
- Ensure restrictive permissions: `chmod 600` for `.encryption_key`, `token.json`, `credentials.json`.
- **CRITICAL:** Document secure backup process for `.encryption_key` - if lost, encrypted API keys are unrecoverable.
- Add startup validation: if `.encryption_key` is missing in prod, FAIL FAST.

**Verification:**
```bash
# Correct permissions
ls -la backend/.encryption_key  # should be 600 (-rw-------)
ls -la backend/token.json       # should be 600
ls -la backend/credentials.json # should be 600

# In production, these variables should NOT be in .env
- GOOGLE_API_KEY
- GOOGLE_CLIENT_ID
- GOOGLE_CLIENT_SECRET
```

---

### 4) Backup security

**Problem:** `/backups/restore` is destructive and lacks sufficient validation.

**Solution:**
- **Double confirmation:** Require `confirm=true` parameter + recent timestamp to prevent CSRF.
- **File validation:**
  - Verify it's a valid `.tar.gz`
  - Verify maximum size (e.g., 100MB)
  - Scan content before extracting (no suspicious executable files)
- **Checksum:** Generate SHA256 when creating backup, validate when restoring.
- **Audit:** Detailed log of who restored what and when.
- **Rate limiting:** Maximum 1 restore every 5 minutes.

**Example code:**
```python
import hashlib
import tarfile

def validate_backup_file(file_path: str) -> bool:
    # Verify size
    if os.path.getsize(file_path) > 100 * 1024 * 1024:  # 100MB
        raise ValueError("Backup file too large")

    # Verify it's valid tar.gz
    if not tarfile.is_tarfile(file_path):
        raise ValueError("Invalid tar.gz file")

    # Verify content
    with tarfile.open(file_path, 'r:gz') as tar:
        for member in tar.getmembers():
            # No files outside backup dir
            if member.name.startswith('/') or '..' in member.name:
                raise ValueError("Suspicious file path in backup")
            # No executables
            if member.mode & 0o111:
                raise ValueError("Executable files not allowed in backup")

    return True
```

---

## IMPORTANT - Implement before external users

### 5) Basic authentication with compatibility flag

**Context:** Define authentication model based on use case:
- **Single-user/personal:** Simple fixed API key
- **Multi-user:** JWT with roles
- **Enterprise:** OAuth2 with Google/SAML

**Initial solution (single-user):**
- Implement simple API key using global `Depends` in FastAPI.
- Add env `AUTH_DISABLED=true` for dev/local; in prod must be `false`.
- API key in header: `Authorization: Bearer <token>` or `x-api-key: <key>`.
- Update frontend/CLI/MCP to send header.

**Affected files:**
- `backend/app/main.py` - Global dependency
- `frontend/src/services/api.ts` - Add header
- `cli/main.py` - Add header
- `backend/mcp_server.py` - MCP authentication

**Verification:**
```bash
# With AUTH_DISABLED=false
curl http://localhost:8000/stores  # 401 Unauthorized
curl -H "x-api-key: SECRET" http://localhost:8000/stores  # 200 OK
```

**Example code:**
```python
from fastapi import Security, HTTPException, status
from fastapi.security import APIKeyHeader

API_KEY = os.getenv("API_KEY", "")
AUTH_DISABLED = os.getenv("AUTH_DISABLED", "false").lower() == "true"

api_key_header = APIKeyHeader(name="x-api-key", auto_error=False)

async def verify_api_key(api_key: str = Security(api_key_header)):
    if AUTH_DISABLED:
        return True
    if not api_key or api_key != API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key"
        )
    return True

# In each router:
@router.get("/stores", dependencies=[Depends(verify_api_key)])
```

---

### 6) Minimal roles and scopes

**Requirement:** Implement AFTER point 5 (authentication).

**Solution:**
- Define roles: `admin` and `user` (or `read-only`).
- Associate roles in token/claim.
- Mark as admin-only:
  - `/config/*` - API key management
  - `/projects/*` (write) - Project creation/editing
  - `/file-browser/*` - Filesystem navigation
  - `/local-files/*` (write) - Local sync
  - `/backups/*` - Backup/restore
  - `/audit-logs/*` - Audit logs
  - `/mcp_config/*` - MCP configuration
  - Write operations on stores/docs (POST, PUT, DELETE)
- Keep for `user`:
  - `/query` - RAG queries
  - GET on stores/docs - Reading
  - `/drive/*` (read) - View Drive links

**Verification:**
```python
# Tests by role:
- admin can create/delete stores ✓
- user can only list stores ✓
- user cannot access /file-browser ✗ 403
- user can do queries ✓
```

---

### 7) MCP Server security

**Problem:** MCP server has full access to the application.

**Solution:**
- **stdio mode (local):** No additional authentication - trust parent process.
- **HTTP mode (remote):** REQUIRES authentication (API key or JWT).
- Implement limited scopes for MCP: don't allow destructive operations by default.
- Specific rate limiting for MCP (10 req/min for expensive operations).
- Audit log with MCP client identification.

**Configuration:**
```python
# backend/mcp_server.py
MCP_MODE = os.getenv("MCP_MODE", "stdio")  # stdio | http
MCP_API_KEY = os.getenv("MCP_API_KEY", "")

if MCP_MODE == "http":
    if not MCP_API_KEY:
        raise ValueError("MCP_API_KEY required for HTTP mode")
```

---

## NICE TO HAVE - Additional hardening

### 8) CORS, host, and docs

**Solution:**
- Separate CORS by environment:
  - **Dev:** `CORS_ORIGINS=http://localhost:5173,http://localhost:*`
  - **Prod:** `CORS_ORIGINS=https://yourdomain.com`
- In production: `docs_url=None, redoc_url=None` to disable `/docs` and `/redoc`.
- Don't expose `uvicorn` directly - use Nginx/Caddy with TLS.
- Consider `HOST=127.0.0.1` if behind reverse proxy.

**Verification:**
```bash
# In prod, these should fail:
curl http://localhost:8000/docs  # 404
curl -H "Origin: http://evil.com" http://localhost:8000/stores  # CORS blocked
```

---

### 9) Rate limiting and observability

**Solution:**
- Implement rate limiting with `slowapi` or `fastapi-limiter`.
- Prioritize sensitive endpoints:
  - **High priority (5 req/min):** `/file-browser/*`, `/backups/restore`
  - **Medium priority (30 req/min):** `/query`, `/drive-links/sync`
  - **Low priority (100 req/min):** GET stores/docs
- Include authenticated identity in all `audit_logs`.
- Prometheus/Grafana metrics (optional but recommended).

**Example code:**
```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.get("/file-browser/list")
@limiter.limit("5/minute")
async def list_files(...):
    ...

@app.post("/query")
@limiter.limit("30/minute")
async def query(...):
    ...
```

---

### 10) Current attack surface audit

**Action:** Before implementing, do complete inventory.

```bash
# 1. Endpoints that access filesystem
grep -rn "open(\|Path(\|os.path\|pathlib" backend/app/ > filesystem_access.txt

# 2. Endpoints without authentication
grep -rn "@router\.\(get\|post\|put\|delete\)" backend/app/api/ > all_endpoints.txt

# 3. Destructive operations
grep -rn "delete\|remove\|unlink\|rmtree" backend/app/ > destructive_ops.txt

# 4. Database access
grep -rn "db.execute\|db.query\|session.execute" backend/app/ > db_access.txt
```

**Create risk matrix:**
| Endpoint | Method | Auth Required | FS Access | DB Write | Destructive | Risk Level |
|----------|--------|---------------|-----------|----------|-------------|------------|
| /file-browser/list | GET | No | Yes | No | No | HIGH |
| /backups/restore | POST | No | Yes | Yes | Yes | CRITICAL |
| /stores | GET | No | No | No | No | LOW |
| ... | ... | ... | ... | ... | ... | ... |

---

## Deployment and Migration Plan

### Phase 1: Development (Now)
- ✅ API key encryption (completed)
- ✅ Audit logs (completed)
- ⏳ Implement points 1-4 (CRITICAL)
- ⏳ Automated security tests

### Phase 2: Staging
- Implement points 5-7 (IMPORTANT)
- Enable `AUTH_DISABLED=false`
- Basic penetration testing
- Update all clients (frontend/CLI/MCP)

### Phase 3: Pre-production
- Implement points 8-9 (NICE TO HAVE)
- TLS configured
- Secrets in secret manager
- Reverse proxy configured
- Monitoring and alerts

### Phase 4: Production
- Final checklist:
  - [ ] TLS active and valid certificate
  - [ ] Secrets outside .env
  - [ ] AUTH_DISABLED=false
  - [ ] ALLOWED_FS_ROOT configured
  - [ ] Restrictive CORS
  - [ ] Docs disabled
  - [ ] Rate limiting active
  - [ ] Automated backups
  - [ ] Monitoring configured
  - [ ] Security tests pass
  - [ ] Audit logs working

---

## Recommended Tools

**Testing:**
- `pytest` + specific security tests
- `bandit` - Static analysis for Python
- `safety` - Vulnerable dependency check
- `sqlmap` - SQL injection test (even using ORM)

**Runtime:**
- `slowapi` - Rate limiting
- `python-jose` - JWT handling
- `bcrypt` - Password hashing (if implementing users)

**Monitoring:**
- `prometheus-fastapi-instrumentator` - Metrics
- `sentry-sdk` - Error tracking

---

## References

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)
- [CWE-22: Path Traversal](https://cwe.mitre.org/data/definitions/22.html)
- [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework)

---

**Last updated:** 2026-01-11
**Status:** Complete plan - Pending implementation
