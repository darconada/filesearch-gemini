# Changelog

## v2.0.0 - Migración a SDK Oficial y Sincronización Completa con Google Drive

### ⚠️ BREAKING CHANGES

- **Migrado de `google-generativeai` (legacy) a `google-genai` (oficial)**
  - El SDK anterior termina soporte en agosto 2025
  - El nuevo SDK es el oficial y soporta File Search correctamente
  - Modelo por defecto cambiado a `gemini-2.5-flash`

### ✨ Nuevas Funcionalidades

#### Google Drive Sync COMPLETA
- **OAuth 2.0** implementado para autenticación con Google Drive
- **Sincronización real** de archivos Drive → File Search:
  - Detección automática de cambios (modifiedTime)
  - Download de archivos desde Drive
  - Upload a File Search stores
  - Actualización incremental (solo sincroniza si cambió)
- **Modos de sincronización**:
  - Manual: sincronizar bajo demanda con botón
  - Automático: sincronización cada 5 minutos via scheduler
- **Persistencia en base de datos** (SQLite por defecto)
- **Scheduler automático** con APScheduler
- **Metadatos de sincronización**:
  - `drive_file_id`: ID del archivo en Drive
  - `synced_from`: "google_drive"
  - `last_modified`: timestamp de última modificación

#### Mejoras en File Search
- Métodos actualizados para usar el SDK oficial:
  - `client.file_search_stores.create()`
  - `client.file_search_stores.list()`
  - `client.file_search_stores.upload_to_file_search_store()`
  - etc.
- Mejor manejo de metadatos personalizados
- Soporte completo para chunking configuration

### 🔧 Mejoras Técnicas

#### Backend
- Base de datos SQLAlchemy con SQLite
- Migraciones con Alembic (pendiente configurar)
- Scheduler Background con APScheduler
- Cliente Drive separado (`drive_client.py`)
- Gestión del ciclo de vida de la app (lifespan)
- Endpoints actualizados con dependencias de BD

#### Configuración
- Nuevas variables de entorno:
  - `GOOGLE_DRIVE_CREDENTIALS`: ruta al archivo credentials.json de OAuth
  - `GOOGLE_DRIVE_TOKEN`: ruta al token.json (generado automáticamente)
  - `DATABASE_URL`: URL de la base de datos (default: SQLite)
- Modelo actualizado: `gemini-2.5-flash` (compatible con File Search)

#### Dependencias Actualizadas
- `google-genai==1.6.1` (nuevo SDK oficial)
- `google-auth-oauthlib==1.2.1`
- `google-auth-httplib2==0.2.0`
- `google-api-python-client==2.154.0`
- `sqlalchemy==2.0.36`
- `alembic==1.14.0`
- `apscheduler==3.10.4`

### 📝 Documentación

- README actualizado con instrucciones de OAuth
- Guía para obtener credentials.json de Google Cloud Console
- Ejemplos de configuración de Drive sync
- Documentación del scheduler y sincronización automática

### 🐛 Correcciones

- **CRÍTICO**: Solucionado error `module 'google.generativeai' has no attribute 'list_file_search_stores'`
  - Causa: SDK legacy no tiene File Search
  - Solución: Migración completa al SDK oficial `google-genai`
- Metadatos ahora usan formato correcto del nuevo SDK
- Query service actualizado para nueva API de generación

### 🔄 Migración desde v1.0.0

#### Para usuarios existentes:

1. **Actualizar dependencias**:
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

2. **Configurar Google Drive** (opcional):
   - Crear proyecto en Google Cloud Console
   - Habilitar Drive API
   - Descargar `credentials.json`
   - Añadir ruta en `.env`: `GOOGLE_DRIVE_CREDENTIALS=path/to/credentials.json`

3. **Primera ejecución**:
   - La BD se crea automáticamente
   - Para Drive sync, ejecutar autenticación OAuth la primera vez
   - Token se guarda en `token.json` para futuras sesiones

4. **API key**:
   - Las API keys existentes siguen funcionando
   - Modelo cambiado automáticamente a `gemini-2.5-flash`

### 📊 Estadísticas

- **Archivos modificados**: 15+
- **Archivos nuevos**: 4
- **Líneas añadidas**: ~800+
- **Funcionalidades nuevas**: 8+

### 🚀 Próximos Pasos

- [ ] Configurar Alembic para migraciones de BD
- [ ] Añadir tests automatizados
- [ ] UI para configurar OAuth desde el frontend
- [ ] Listado de archivos Drive en la UI
- [ ] Métricas de sincronización
- [ ] Logs detallados de sync operations

---

## v1.0.0 - Versión Inicial

### Funcionalidades
- Gestión básica de File Search stores
- Upload y gestión de documentos
- Consultas RAG multi-store
- Metadatos personalizados
- UI con Material-UI
- Temas claro/oscuro
- API REST completa

### Stack
- Backend: FastAPI + google-generativeai (legacy)
- Frontend: React + TypeScript + Vite
- Modelo: gemini-2.0-flash-exp
