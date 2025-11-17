# Changelog

## v2.2.0 - Soporte Multi-Proyecto

### 🆕 Nuevas Funcionalidades

#### Gestión de Múltiples Proyectos de Google AI Studio

- **Soporte completo para múltiples proyectos**:
  - Crea y gestiona múltiples proyectos de Google AI Studio
  - Cada proyecto con su propia API key independiente
  - Hasta 10 File Search stores por proyecto (límite de Google)
  - Un proyecto activo a la vez
  - Cambio rápido entre proyectos sin perder contexto

- **Nueva página "Projects"** en la interfaz web:
  - Crear nuevos proyectos con nombre, API key y descripción
  - Listar todos los proyectos con estado de activación
  - Editar proyectos existentes (nombre, API key, descripción)
  - Eliminar proyectos que ya no necesites
  - Activar/desactivar proyectos con un click
  - Validación automática de API keys al crear/actualizar

- **Selector de proyecto en el header**:
  - Dropdown en la barra superior para ver el proyecto activo
  - Cambio rápido entre proyectos desde cualquier página
  - Icono visual del proyecto activo
  - Recarga automática al cambiar de proyecto

- **Base de datos para proyectos**:
  - Tabla SQLite para almacenar proyectos
  - Campos: id, name, api_key, description, is_active, timestamps
  - Migración automática al iniciar la aplicación
  - TODO: Encriptación de API keys para producción

### 🔧 Backend - Nuevos Endpoints

- `POST /projects` - Crear nuevo proyecto con validación de API key
- `GET /projects` - Listar todos los proyectos + proyecto activo
- `GET /projects/active` - Obtener proyecto actualmente activo
- `GET /projects/{id}` - Obtener proyecto específico
- `PUT /projects/{id}` - Actualizar proyecto
- `POST /projects/{id}/activate` - Activar proyecto (desactiva los demás)
- `DELETE /projects/{id}` - Eliminar proyecto

### 🎨 Frontend - Nuevos Componentes

- `ProjectsPage.tsx` - Página completa de gestión de proyectos
- `ProjectSelector.tsx` - Selector de proyecto para el header
- Actualización de `ConfigPage.tsx` con aviso de multi-proyecto
- Nuevos tipos TypeScript: `Project`, `ProjectCreate`, `ProjectUpdate`, `ProjectList`

### 📖 Documentación

- Nuevo archivo `MULTI_PROJECT.md` con guía completa:
  - Conceptos clave (proyectos, proyecto activo)
  - Instrucciones de uso paso a paso
  - Documentación de API endpoints
  - Schema de base de datos
  - Guía de migración desde versión anterior
  - Mejores prácticas
  - Troubleshooting

### 🔄 Cambios en Componentes Existentes

- **Configuration Page**: Nuevo banner informativo sobre multi-proyecto
- **Layout**: Nuevo ítem de menú "Projects" con icono de carpeta
- **API Client**: Nuevos métodos en `projectsApi` para todas las operaciones

### 📝 Notas de Upgrade

Si actualizas desde v2.1.x:
1. La base de datos se actualizará automáticamente con la tabla `projects`
2. Tu API key actual seguirá funcionando
3. Crea tu primer proyecto en la página "Projects"
4. El primer proyecto que crees se activará automáticamente
5. Puedes seguir usando la página "Configuration" para actualizar el API key del proyecto activo

### 🎯 Casos de Uso

- **Múltiples clientes**: Un proyecto por cliente con datos aislados
- **Múltiples entornos**: Proyectos separados para desarrollo, staging y producción
- **Límite de stores**: Supera el límite de 10 stores usando múltiples proyectos
- **Organización**: Agrupa stores relacionados por proyecto

### ⚠️ Limitaciones

- Solo un proyecto puede estar activo a la vez
- Al cambiar de proyecto, la página se recarga completamente
- API keys almacenadas en texto plano (TODO: encriptación)
- No se pueden usar múltiples proyectos simultáneamente

---

## v2.1.1 - Gestión Web de Configuración MCP/CLI

### 🆕 Nuevas Funcionalidades

#### Interfaz Web para Configuración
- **Nueva sección "LLM Integration"** en la interfaz web
  - Tab "MCP Server": Configurar backend URL y habilitar/deshabilitar servidor
  - Tab "CLI Local": Configurar CLI con backend URL y store por defecto
  - Tab "Integration Guide": Guía completa con ejemplos para todos los agents
  - Botones de copiar/pegar para todas las configuraciones
  - Ejemplos actualizados dinámicamente según configuración

- **Endpoints backend** para gestión de configuración:
  - `GET/POST /integration/mcp/config` - Configuración MCP
  - `GET /integration/mcp/status` - Estado y ejemplos MCP
  - `GET/POST /integration/cli/config` - Configuración CLI
  - `GET /integration/cli/status` - Estado y ejemplos CLI
  - `GET /integration/guide` - Guía completa de integración

- **Persistencia de configuración**:
  - Archivos JSON en `backend/config/` para MCP y CLI
  - Configuración accesible desde web, MCP server y CLI

### 🔧 Mejoras

- README actualizado con sección de gestión web
- Navegación actualizada con nuevo ítem "LLM Integration"
- Componentes React modulares y reutilizables
- Type safety completo en TypeScript

### 📝 Notas de Upgrade

Si actualizas desde v2.1.0:
1. Los archivos de configuración se crean automáticamente en `backend/config/`
2. Accede a la nueva interfaz en: http://localhost:5173/integration
3. La configuración anterior (env vars, CLI config) sigue siendo válida

---

## v2.1.0 - Integración MCP y CLI para LLM Agents

### 🆕 Nuevas Funcionalidades

#### Servidor MCP (Model Context Protocol)
- **Servidor MCP completo** con 21 herramientas para LLM agents
  - Compatible con Gemini CLI, Claude Code y Codex CLI
  - Implementado con FastMCP para mejor DX
  - Transporte stdio (modo por defecto, recomendado)
  - Comunicación HTTP con el backend FastAPI

- **Herramientas MCP disponibles**:
  - **Configuración**: `set_api_key`, `get_config_status`
  - **Stores**: `create_store`, `list_stores`, `get_store`, `delete_store`
  - **Documentos**: `upload_document`, `list_documents`, `update_document`, `delete_document`
  - **Consultas RAG**: `rag_query` (con metadata filtering y citations)
  - **Drive Sync**: `create_drive_link`, `list_drive_links`, `get_drive_link`, `delete_drive_link`, `sync_drive_link_now`

#### CLI Local (filesearch-gemini)
- **Interfaz de línea de comandos completa** para uso directo o desde agents
  - Implementado con Click + Rich para excelente UX
  - Subcomandos organizados por funcionalidad
  - Salida formateada con tablas y colores
  - Soporte para JSON output (útil para scripting)

- **Comandos disponibles**:
  - `config`: Gestión de configuración (API key, backend URL, status)
  - `stores`: Operaciones con stores (list, create, get, delete)
  - `docs`: Gestión de documentos (list, upload, delete)
  - `query`: Consultas RAG con metadata filtering
  - `drive`: Sincronización con Google Drive (list, create, sync-now, delete)

- **Configuración flexible**:
  - Variables de entorno (prioridad máxima)
  - Archivo de configuración `~/.filesearch-gemini/config.yaml`
  - Valores por defecto sensatos

### 📖 Documentación

- **MCP_INTEGRATION.md**: Guía completa de integración
  - Configuración paso a paso para cada cliente MCP
  - Ejemplos de uso prácticos
  - Troubleshooting y best practices
  - Workflow completo de ejemplo

- **Ejemplos de configuración** en `examples/`:
  - `gemini-cli-settings.json` - Config para Gemini CLI
  - `claude-code-mcp.json` - Config para Claude Code
  - `codex-mcp-config.json` - Config para Codex CLI
  - `cli-config.yaml` - Config para el CLI local

- **README actualizado** con sección de integración MCP/CLI

### 🧪 Tests

- Tests básicos para MCP server (`tests/test_mcp_server.py`)
- Tests básicos para CLI (`tests/test_cli.py`)
- Infraestructura de testing con pytest

### 🔧 Dependencias Nuevas

- `fastmcp==0.6.1` - Framework MCP simplificado
- `httpx==0.28.1` - Cliente HTTP moderno para MCP y CLI
- `click==8.1.8` - Framework CLI
- `rich==13.9.4` - Terminal output mejorado
- `pyyaml==6.0.2` - Configuración YAML
- `pytest==8.3.4` - Testing framework
- `pytest-mock==3.14.0` - Mocking para tests

### 🎯 Casos de Uso Habilitados

Ahora puedes usar File Search desde:
1. **Interfaz Web** (navegador) - experiencia visual completa
2. **API REST** (curl, Postman) - integración HTTP directa
3. **Servidor MCP** (Gemini CLI, Claude Code, Codex) - integración con LLM agents
4. **CLI local** (terminal) - uso manual o scripting

### 📝 Notas de Upgrade

Si actualizas desde v2.0.0:
1. Instala las nuevas dependencias: `pip install -r backend/requirements.txt`
2. El servidor MCP se inicia con: `python backend/mcp_server.py`
3. El CLI se ejecuta con: `./filesearch-gemini --help`
4. Ver [MCP_INTEGRATION.md](./MCP_INTEGRATION.md) para configurar tu LLM agent

---

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
