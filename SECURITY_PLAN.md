# Security Hardening Plan

**Estado:** En desarrollo - Plan de seguridad para implementación antes de producción

**Objetivo:** Cerrar superficie de ataque sin romper flujos actuales. Orden de ejecución por prioridad de riesgo.

---

## 🔴 CRÍTICO - Implementar ANTES de producción

### 1) Restricción de sistema de archivos ⚠️ URGENTE

**Problema:** File browser y local files pueden acceder a TODO el filesystem del servidor.

**Solución:**
- Introducir env `ALLOWED_FS_ROOT` (p.ej. `/data/files`). Validar que `file_browser` y `local_files` no puedan salir de ese root.
- Implementar validación que rechace path traversal (`../`, `..\\`, symlinks que apunten fuera del root).
- Añadir blocklist hardcodeada de rutas sensibles: `/etc`, `/root`, `/home`, `/var`, `/sys`, `/proc`, `.ssh`, `.env`, `token.json`, `credentials.json`.
- Normalizar paths con `os.path.realpath()` y validar que empiecen con `ALLOWED_FS_ROOT`.

**Archivos afectados:**
- `backend/app/services/file_browser_service.py`
- `backend/app/services/local_file_service.py`

**Verificación:**
```python
# Tests que deben FALLAR con 403:
- Acceso a ../../etc/passwd
- Acceso a /root/
- Symlink fuera del root
- Rutas con null bytes
- Rutas URL-encoded maliciosas
```

**Código ejemplo:**
```python
import os
from pathlib import Path

ALLOWED_FS_ROOT = os.getenv("ALLOWED_FS_ROOT", "/data/files")
BLOCKED_PATHS = ["/etc", "/root", "/home", "/var", "/sys", "/proc", ".ssh", ".env", "token.json", "credentials.json"]

def validate_path(requested_path: str) -> Path:
    """Valida que el path esté dentro del root permitido"""
    # Normalizar y resolver symlinks
    real_path = Path(requested_path).resolve()
    root_path = Path(ALLOWED_FS_ROOT).resolve()

    # Verificar que está dentro del root
    if not str(real_path).startswith(str(root_path)):
        raise PermissionError(f"Access denied: path outside allowed root")

    # Verificar blocklist
    for blocked in BLOCKED_PATHS:
        if blocked in str(real_path):
            raise PermissionError(f"Access denied: blocked path pattern")

    return real_path
```

---

### 2) Input validation y sanitización

**Problema:** Falta validación estricta de inputs que pueden causar vulnerabilidades.

**Solución:**
- **File IDs de Google:** Validar formato (alfanumérico + `-_`, longitud esperada).
- **Nombres de archivo:** Sanitizar antes de guardar (sin `../`, sin null bytes, sin caracteres especiales peligrosos).
- **Metadata:** Validar tipos, límites (max 20 keys), longitud de valores.
- **Store IDs:** Validar formato esperado de Google.
- **Project names:** Sanitizar SQL injection, XSS (aunque uses ORM).

**Archivos afectados:**
- `backend/app/models/schemas.py` - Añadir validators de Pydantic
- Todos los services que manejen input de usuario

**Código ejemplo:**
```python
from pydantic import validator, Field
import re

class DocumentUpload(BaseModel):
    store_id: str = Field(..., min_length=10, max_length=200)

    @validator('store_id')
    def validate_store_id(cls, v):
        # Formato: fileSearchStores/xxx-xxx-xxx
        if not re.match(r'^fileSearchStores/[a-z0-9-]+$', v):
            raise ValueError('Invalid store ID format')
        return v

class LocalFileLinkCreate(BaseModel):
    local_path: str

    @validator('local_path')
    def validate_local_path(cls, v):
        # No permitir path traversal
        if '..' in v or v.startswith('/'):
            raise ValueError('Invalid path: path traversal detected')
        # No null bytes
        if '\x00' in v:
            raise ValueError('Invalid path: null byte detected')
        return v
```

---

### 3) Gestión segura de secretos

**Problema:** Secretos en archivos `.env` y permisos de archivos.

**Solución:**
- **Desarrollo:** Continuar usando `.env` pero con `.env.example` documentado.
- **Producción:** Mover a variables de entorno del sistema o secret manager (AWS Secrets Manager, HashiCorp Vault, etc.).
- Asegurar permisos restrictivos: `chmod 600` para `.encryption_key`, `token.json`, `credentials.json`.
- **CRÍTICO:** Documentar proceso de backup seguro de `.encryption_key` - si se pierde, las API keys encriptadas son irrecuperables.
- Añadir validación al arrancar: si falta `.encryption_key` en prod, FAIL FAST.

**Verificación:**
```bash
# Permisos correctos
ls -la backend/.encryption_key  # debe ser 600 (-rw-------)
ls -la backend/token.json       # debe ser 600
ls -la backend/credentials.json # debe ser 600

# En producción, estas variables NO deben estar en .env
- GOOGLE_API_KEY
- GOOGLE_CLIENT_ID
- GOOGLE_CLIENT_SECRET
```

---

### 4) Backup security

**Problema:** `/backups/restore` es destructivo y no tiene validación suficiente.

**Solución:**
- **Doble confirmación:** Requiere parámetro `confirm=true` + timestamp reciente para evitar CSRF.
- **Validación de archivo:**
  - Verificar que es un `.tar.gz` válido
  - Verificar tamaño máximo (e.g., 100MB)
  - Escanear contenido antes de extraer (no archivos ejecutables sospechosos)
- **Checksum:** Generar SHA256 al crear backup, validar al restaurar.
- **Audit:** Log detallado de quién restauró qué y cuándo.
- **Rate limiting:** Máximo 1 restore cada 5 minutos.

**Código ejemplo:**
```python
import hashlib
import tarfile

def validate_backup_file(file_path: str) -> bool:
    # Verificar tamaño
    if os.path.getsize(file_path) > 100 * 1024 * 1024:  # 100MB
        raise ValueError("Backup file too large")

    # Verificar que es tar.gz válido
    if not tarfile.is_tarfile(file_path):
        raise ValueError("Invalid tar.gz file")

    # Verificar contenido
    with tarfile.open(file_path, 'r:gz') as tar:
        for member in tar.getmembers():
            # No archivos fuera del backup dir
            if member.name.startswith('/') or '..' in member.name:
                raise ValueError("Suspicious file path in backup")
            # No ejecutables
            if member.mode & 0o111:
                raise ValueError("Executable files not allowed in backup")

    return True
```

---

## 🟡 IMPORTANTE - Implementar antes de usuarios externos

### 5) Autenticación básica con flag de compatibilidad

**Contexto:** Definir modelo de autenticación según caso de uso:
- **Single-user/personal:** API key fija simple
- **Multi-user:** JWT con roles
- **Enterprise:** OAuth2 con Google/SAML

**Solución inicial (single-user):**
- Implementar API key simple usando `Depends` global en FastAPI.
- Añadir env `AUTH_DISABLED=true` para dev/local; en prod debe ser `false`.
- API key en header: `Authorization: Bearer <token>` o `x-api-key: <key>`.
- Actualizar frontend/CLI/MCP para enviar header.

**Archivos afectados:**
- `backend/app/main.py` - Dependency global
- `frontend/src/services/api.ts` - Añadir header
- `cli/main.py` - Añadir header
- `backend/mcp_server.py` - Autenticación MCP

**Verificación:**
```bash
# Con AUTH_DISABLED=false
curl http://localhost:8000/stores  # 401 Unauthorized
curl -H "x-api-key: SECRET" http://localhost:8000/stores  # 200 OK
```

**Código ejemplo:**
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

# En cada router:
@router.get("/stores", dependencies=[Depends(verify_api_key)])
```

---

### 6) Roles y scopes mínimos

**Requisito:** Implementar DESPUÉS de punto 5 (autenticación).

**Solución:**
- Definir roles: `admin` y `user` (o `read-only`).
- Asociar roles en el token/claim.
- Marcar como admin-only:
  - `/config/*` - Gestión de API keys
  - `/projects/*` (write) - Creación/edición de proyectos
  - `/file-browser/*` - Navegación del filesystem
  - `/local-files/*` (write) - Sincronización local
  - `/backups/*` - Backup/restore
  - `/audit-logs/*` - Logs de auditoría
  - `/mcp_config/*` - Configuración MCP
  - Operaciones de escritura en stores/docs (POST, PUT, DELETE)
- Mantener para `user`:
  - `/query` - Consultas RAG
  - GET en stores/docs - Lectura
  - `/drive/*` (read) - Ver links de Drive

**Verificación:**
```python
# Tests por rol:
- admin puede crear/eliminar stores ✓
- user puede solo listar stores ✓
- user no puede acceder a /file-browser ✗ 403
- user puede hacer queries ✓
```

---

### 7) MCP Server security

**Problema:** MCP server tiene acceso completo a la aplicación.

**Solución:**
- **Modo stdio (local):** Sin autenticación adicional - confianza en proceso padre.
- **Modo HTTP (remoto):** REQUIERE autenticación (API key o JWT).
- Implementar scopes limitados para MCP: no permitir operaciones destructivas por defecto.
- Rate limiting específico para MCP (10 req/min por operación costosa).
- Audit log con identificación del cliente MCP.

**Configuración:**
```python
# backend/mcp_server.py
MCP_MODE = os.getenv("MCP_MODE", "stdio")  # stdio | http
MCP_API_KEY = os.getenv("MCP_API_KEY", "")

if MCP_MODE == "http":
    if not MCP_API_KEY:
        raise ValueError("MCP_API_KEY required for HTTP mode")
```

---

## 🟢 BUENO TENER - Hardening adicional

### 8) CORS, host y docs

**Solución:**
- Separar CORS por entorno:
  - **Dev:** `CORS_ORIGINS=http://localhost:5173,http://localhost:*`
  - **Prod:** `CORS_ORIGINS=https://yourdomain.com`
- En producción: `docs_url=None, redoc_url=None` para deshabilitar `/docs` y `/redoc`.
- No exponer `uvicorn` directamente - usar Nginx/Caddy con TLS.
- Considerar `HOST=127.0.0.1` si está detrás de reverse proxy.

**Verificación:**
```bash
# En prod, estos deben fallar:
curl http://localhost:8000/docs  # 404
curl -H "Origin: http://evil.com" http://localhost:8000/stores  # CORS blocked
```

---

### 9) Rate limiting y observabilidad

**Solución:**
- Implementar rate limiting con `slowapi` o `fastapi-limiter`.
- Priorizar endpoints sensibles:
  - **Alta prioridad (5 req/min):** `/file-browser/*`, `/backups/restore`
  - **Media prioridad (30 req/min):** `/query`, `/drive-links/sync`
  - **Baja prioridad (100 req/min):** GET stores/docs
- Incluir identidad autenticada en todos los `audit_logs`.
- Métricas de Prometheus/Grafana (opcional pero recomendado).

**Código ejemplo:**
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

### 10) Auditoría de superficie de ataque actual

**Acción:** Antes de implementar, hacer inventario completo.

```bash
# 1. Endpoints que acceden al filesystem
grep -rn "open(\|Path(\|os.path\|pathlib" backend/app/ > filesystem_access.txt

# 2. Endpoints sin autenticación
grep -rn "@router\.\(get\|post\|put\|delete\)" backend/app/api/ > all_endpoints.txt

# 3. Operaciones destructivas
grep -rn "delete\|remove\|unlink\|rmtree" backend/app/ > destructive_ops.txt

# 4. Acceso a base de datos
grep -rn "db.execute\|db.query\|session.execute" backend/app/ > db_access.txt
```

**Crear matriz de riesgo:**
| Endpoint | Método | Auth Required | FS Access | DB Write | Destructive | Risk Level |
|----------|--------|---------------|-----------|----------|-------------|------------|
| /file-browser/list | GET | No | Yes | No | No | HIGH |
| /backups/restore | POST | No | Yes | Yes | Yes | CRITICAL |
| /stores | GET | No | No | No | No | LOW |
| ... | ... | ... | ... | ... | ... | ... |

---

## 📋 Plan de despliegue y migración

### Fase 1: Desarrollo (Ahora)
- ✅ Encriptación de API keys (completado)
- ✅ Audit logs (completado)
- ⏳ Implementar puntos 1-4 (CRÍTICO)
- ⏳ Tests de seguridad automatizados

### Fase 2: Staging
- Implementar puntos 5-7 (IMPORTANTE)
- Habilitar `AUTH_DISABLED=false`
- Pruebas de penetración básicas
- Actualizar todos los clientes (frontend/CLI/MCP)

### Fase 3: Pre-producción
- Implementar puntos 8-9 (BUENO TENER)
- TLS configurado
- Secrets en secret manager
- Reverse proxy configurado
- Monitoreo y alertas

### Fase 4: Producción
- Checklist final:
  - [ ] TLS activo y certificado válido
  - [ ] Secrets fuera de .env
  - [ ] AUTH_DISABLED=false
  - [ ] ALLOWED_FS_ROOT configurado
  - [ ] CORS restrictivo
  - [ ] Docs deshabilitadas
  - [ ] Rate limiting activo
  - [ ] Backups automatizados
  - [ ] Monitoreo configurado
  - [ ] Tests de seguridad pasan
  - [ ] Audit logs funcionando

---

## 🔧 Herramientas recomendadas

**Testing:**
- `pytest` + tests de seguridad específicos
- `bandit` - Static analysis para Python
- `safety` - Check de dependencias vulnerables
- `sqlmap` - Test de SQL injection (aunque uses ORM)

**Runtime:**
- `slowapi` - Rate limiting
- `python-jose` - JWT handling
- `bcrypt` - Password hashing (si implementas usuarios)

**Monitoring:**
- `prometheus-fastapi-instrumentator` - Métricas
- `sentry-sdk` - Error tracking

---

## 📚 Referencias

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)
- [CWE-22: Path Traversal](https://cwe.mitre.org/data/definitions/22.html)
- [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework)

---

**Última actualización:** 2025-11-29
**Estado:** Plan completo - Pendiente de implementación
