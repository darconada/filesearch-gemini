# File Search RAG Application

Una aplicación web completa para gestionar Google File Search y ejecutar consultas RAG (Retrieval-Augmented Generation) con una interfaz moderna, API REST y **sincronización completa con Google Drive**.

## ⚠️ IMPORTANTE - Versión 2.0

Esta aplicación usa el **SDK oficial `google-genai`** (v1.6.1+). El SDK anterior `google-generativeai` **NO soporta File Search** y causará errores.

**Si tienes el error**: `module 'google.generativeai' has no attribute 'list_file_search_stores'`
- ✅ **Solución**: Instala las dependencias correctas: `pip install -r requirements.txt`
- ✅ El SDK correcto es `google-genai` (no `google-generativeai`)

**Novedades v2.2**:
- ✨ **Soporte Multi-Proyecto**: Gestiona múltiples proyectos de Google AI Studio con diferentes API keys
- ✨ **Servidor MCP completo**: 21 herramientas para Gemini CLI, Claude Code y Codex CLI
- ✨ **CLI Local**: Interfaz de línea de comandos con Rich para terminal y agents
- ✨ **Gestión Web de MCP/CLI**: Configuración desde la interfaz web
- 📖 Ver [CHANGELOG.md](CHANGELOG.md) para detalles completos v2.2, v2.1 y v2.0
- 📖 Ver [MCP_INTEGRATION.md](MCP_INTEGRATION.md) para integración con LLM agents
- 📖 Ver [MULTI_PROJECT.md](MULTI_PROJECT.md) para gestión multi-proyecto
- 📖 Ver [DRIVE_SETUP.md](DRIVE_SETUP.md) para configurar Google Drive

## 📋 Características

### ✅ Funcionalidades Implementadas

- **Gestión de Configuración**
  - Configuración de API key de Google
  - Validación de conexión en tiempo real
  - Almacenamiento seguro en backend

- **Gestión de File Search Stores**
  - Crear, listar y eliminar stores
  - Selección de store activo
  - Visualización de metadatos

- **Gestión de Documentos**
  - Subida de documentos al File Search store
  - Listado paginado de documentos
  - Actualización de documentos (eliminar + recrear)
  - Eliminación de documentos con forzado (force delete para documentos indexados)
  - Preservación de nombres de archivo originales
  - ⚠️ **Pendiente**: Subida de metadatos personalizados (funcionalidad en desarrollo)

- **Consultas RAG**
  - Preguntas en lenguaje natural
  - Búsqueda multi-store
  - Filtros por metadata personalizados
  - Visualización de respuestas con citas a documentos fuente
  - Extracción de grounding metadata

- **Interfaz de Usuario**
  - UI moderna con Material-UI
  - Temas claro y oscuro
  - Navegación responsive
  - Visualización clara de estados y errores

- **API REST Completa**
  - Endpoints documentados con FastAPI (Swagger/OpenAPI)
  - CORS configurado para desarrollo local
  - Manejo robusto de errores
  - Soporte para multipart/form-data

- **🆕 Integración MCP (Model Context Protocol)**
  - Servidor MCP completo con 21 herramientas
  - Compatible con Gemini CLI, Claude Code y Codex CLI
  - Soporte para stdio y HTTP
  - Documentación completa de integración

- **🆕 CLI Local (filesearch-gemini)**
  - Interfaz de línea de comandos completa
  - Subcomandos para todas las operaciones
  - Compatible con LLM agents
  - Salida formateada con Rich

- **🆕 Soporte Multi-Proyecto**
  - Gestiona múltiples proyectos de Google AI Studio
  - Cada proyecto con su propia API key
  - Hasta 10 stores por proyecto
  - Selector de proyecto en el header
  - Activación rápida entre proyectos
  - Ver [MULTI_PROJECT.md](MULTI_PROJECT.md) para más detalles

- **Base para Sincronización con Google Drive**
  - Modelos de datos preparados
  - Endpoints stub implementados
  - UI para configurar vínculos Drive → File Search
  - Estructura para sincronización manual/automática

## 🏗️ Arquitectura

### Backend (Python + FastAPI)

```
backend/
├── app/
│   ├── main.py              # Aplicación FastAPI principal
│   ├── config.py            # Configuración global
│   ├── database.py          # SQLAlchemy setup
│   ├── models/              # Modelos Pydantic y DB
│   │   ├── db_models.py     # Modelos SQLAlchemy (ProjectDB, DriveLinkDB)
│   │   ├── store.py
│   │   ├── document.py
│   │   ├── query.py
│   │   ├── config.py
│   │   ├── drive.py
│   │   ├── project.py       # Modelos multi-proyecto
│   │   └── mcp_config.py    # Modelos MCP/CLI config
│   ├── services/            # Lógica de negocio
│   │   ├── google_client.py
│   │   ├── store_service.py
│   │   ├── document_service.py
│   │   ├── query_service.py
│   │   ├── drive_service.py
│   │   ├── project_service.py      # Gestión de proyectos
│   │   └── mcp_config_service.py   # Gestión config MCP/CLI
│   ├── api/                 # Endpoints REST
│   │   ├── config.py
│   │   ├── stores.py
│   │   ├── documents.py
│   │   ├── query.py
│   │   ├── drive.py
│   │   ├── projects.py      # Endpoints multi-proyecto
│   │   └── mcp_config.py    # Endpoints config MCP/CLI
│   └── mcp/                 # Servidor MCP
│       └── server.py        # 21 herramientas MCP
├── mcp_server.py            # Entry point servidor MCP
├── requirements.txt
└── filesearch.db            # Base de datos SQLite
```

### Frontend (React + TypeScript + Vite)

```
frontend/
├── src/
│   ├── components/          # Componentes React
│   │   ├── common/          # Layout, navegación, ProjectSelector
│   │   ├── config/          # Configuración
│   │   ├── projects/        # Gestión multi-proyecto
│   │   ├── stores/          # Gestión de stores
│   │   ├── documents/       # Gestión de documentos
│   │   ├── query/           # Consultas RAG
│   │   ├── drive/           # Sincronización Drive
│   │   └── integration/     # MCP Server & CLI Config
│   ├── services/            # Cliente API
│   │   └── api.ts           # Incluye projectsApi, mcpApi, cliApi
│   ├── types/               # Tipos TypeScript
│   │   └── index.ts         # Incluye Project, MCP, CLI types
│   ├── theme/               # Temas MUI
│   │   └── theme.ts
│   ├── App.tsx
│   └── main.tsx
└── package.json
```

## 🚀 Instalación y Configuración

### Requisitos Previos

- **Python 3.11+**
- **Node.js 18+** y **npm**
- **Google API Key** para Generative Language API ([Obtener aquí](https://aistudio.google.com/app/apikey))

### 1. Clonar el Repositorio

```bash
git clone <repository-url>
cd filesearch-gemini
```

### 2. Configurar el Backend

```bash
cd backend

# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
# En Linux/Mac:
source venv/bin/activate
# En Windows:
# venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Crear archivo .env (opcional, también se puede configurar desde la UI)
cp .env.example .env
# Editar .env y añadir tu GOOGLE_API_KEY si lo deseas
```

### 3. Configurar el Frontend

```bash
cd ../frontend

# Instalar dependencias
npm install

# Crear archivo .env (opcional)
cp .env.example .env
```

### 4. Iniciar la Aplicación

#### Opción A: Usar dos terminales

**Terminal 1 - Backend:**
```bash
cd backend
source venv/bin/activate  # o venv\Scripts\activate en Windows
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

El backend estará disponible en: `http://localhost:8000`
Documentación de la API: `http://localhost:8000/docs`

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

El frontend estará disponible en: `http://localhost:5173`

#### Opción B: Script de inicio (crear un script bash)

```bash
#!/bin/bash
# start.sh

# Iniciar backend en background
cd backend
source venv/bin/activate
python -m app.main &
BACKEND_PID=$!

# Iniciar frontend
cd ../frontend
npm run dev

# Cleanup al salir
kill $BACKEND_PID
```

## 🤖 Integración con LLM Agents (MCP y CLI)

Esta aplicación ahora se puede usar desde **agentes LLM** como **Gemini CLI**, **Claude Code** y **Codex CLI** mediante dos métodos:

### Método 1: Servidor MCP (Recomendado)

El servidor MCP expone todas las operaciones de File Search como herramientas que los agentes pueden invocar:

```bash
# Iniciar el servidor MCP
cd backend
python mcp_server.py
```

**Herramientas MCP disponibles (21 en total)**:
- Configuración: `set_api_key`, `get_config_status`
- Stores: `create_store`, `list_stores`, `get_store`, `delete_store`
- Documentos: `upload_document`, `list_documents`, `update_document`, `delete_document`
- Consultas RAG: `rag_query`
- Drive Sync: `create_drive_link`, `list_drive_links`, `sync_drive_link_now`, etc.

### Método 2: CLI Local

También puedes usar el CLI directamente desde tu terminal o desde agentes LLM:

```bash
# Ver ayuda
./filesearch-gemini --help

# Ejemplos rápidos
./filesearch-gemini stores list
./filesearch-gemini docs upload --store-id xxx --file doc.pdf
./filesearch-gemini query --question "¿Qué dice sobre X?" --stores xxx
```

### 🌐 Gestión desde la Interfaz Web

La nueva sección **LLM Integration** en la interfaz web te permite:

- **Configurar el servidor MCP**: URL del backend, habilitar/deshabilitar
- **Ver ejemplos de configuración** para Gemini CLI, Claude Code y Codex con botones copiar/pegar
- **Configurar el CLI local**: URL backend, store por defecto
- **Acceder a la guía completa** de integración con instrucciones paso a paso

Accede a: **http://localhost:5173/integration** después de iniciar el frontend.

### Configuración para Agentes

#### Gemini CLI

Añade a tu `settings.json`:

```json
{
  "mcpServers": {
    "filesearch-gemini": {
      "type": "stdio",
      "command": "python",
      "args": ["/path/to/filesearch-gemini/backend/mcp_server.py"]
    }
  }
}
```

#### Claude Code

```bash
claude mcp add filesearch-gemini \
  --transport stdio \
  --command "python" \
  --args "backend/mcp_server.py"
```

#### Codex CLI

```bash
codex mcp-server add filesearch-gemini \
  --command "python" \
  --args "/path/to/filesearch-gemini/backend/mcp_server.py"
```

**📖 Documentación completa**: Ver [MCP_INTEGRATION.md](./MCP_INTEGRATION.md) para instrucciones detalladas, ejemplos de uso y troubleshooting.

---

## 📖 Uso de la Aplicación

La aplicación se puede usar de **4 formas diferentes**:

1. **Interfaz Web** (navegador en http://localhost:5173)
2. **API REST** (HTTP requests a http://localhost:8000)
3. **Servidor MCP** (para agentes LLM)
4. **CLI local** (comando `filesearch-gemini`)

### 🚀 Configuración Inicial (Primer Uso)

#### Opción 1: Crear un Proyecto (Recomendado - Multi-Proyecto)

1. **Navega a la sección Projects** en `http://localhost:5173/projects`
2. **Click en "Create Project"**
3. **Rellena el formulario:**
   - **Name**: Por ejemplo "Mi Proyecto Principal"
   - **API Key**: Tu Google AI Studio API key ([Obtener aquí](https://aistudio.google.com/app/apikey))
   - **Description** (opcional): Descripción del proyecto
4. **Click en "Create"**
5. El proyecto se activará automáticamente y aparecerá en el selector del header
6. **Reinicia el backend** para que cargue el proyecto activo

#### Opción 2: Configurar API Key directamente (Sin Multi-Proyecto)

1. **Navega a la sección Configuration**
2. **Introduce tu Google API Key**
3. **Haz clic en "Save API Key"**
4. Verifica que el estado muestre "API Key Valid: Valid"

**Nota**: Con la opción 2, solo puedes usar un proyecto. La opción 1 te permite gestionar múltiples proyectos de Google AI Studio.

### Uso desde la Interfaz Web

### 2. Crear un Store

1. Ve a la sección **Stores**
2. Haz clic en **Create Store**
3. Introduce un nombre descriptivo
4. El store se marcará como activo automáticamente

### 3. Subir Documentos

1. Ve a la sección **Documents**
2. Haz clic en **Upload Document**
3. Selecciona un archivo
4. Haz clic en **Upload**
5. El documento se indexará automáticamente en el File Search store

**Nota**: La funcionalidad de metadatos personalizados está pendiente de implementación.

### 4. Realizar Consultas RAG

1. Ve a la sección **RAG Query**
2. Selecciona uno o más stores
3. Escribe tu pregunta
4. (Opcional) Añade un filtro de metadata: `author="Robert Graves"`
5. Haz clic en **Query**
6. Revisa la respuesta y las fuentes citadas

### 5. Configurar Sincronización con Drive (Base Futura)

1. Ve a la sección **Drive Sync**
2. Haz clic en **Add Link**
3. Introduce el ID del archivo de Google Drive
4. Selecciona el store de destino
5. Elige modo manual o automático
6. La funcionalidad completa se implementará en versiones futuras

## 🔌 API REST

La API está completamente documentada con Swagger/OpenAPI. Accede a:
- **Documentación interactiva**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

### Endpoints Principales

#### Configuración
- `POST /config/api-key` - Configurar API key
- `GET /config/status` - Obtener estado de configuración

#### Stores
- `POST /stores` - Crear store
- `GET /stores` - Listar stores
- `GET /stores/{store_id}` - Obtener store
- `DELETE /stores/{store_id}` - Eliminar store

#### Documentos
- `POST /stores/{store_id}/documents` - Subir documento
- `GET /stores/{store_id}/documents` - Listar documentos
- `PUT /stores/{store_id}/documents/{document_id}` - Actualizar documento
- `DELETE /stores/{store_id}/documents/{document_id}` - Eliminar documento

#### Consultas RAG
- `POST /query` - Ejecutar consulta RAG

#### Drive Links
- `POST /drive-links` - Crear vínculo Drive
- `GET /drive-links` - Listar vínculos
- `GET /drive-links/{link_id}` - Obtener vínculo
- `DELETE /drive-links/{link_id}` - Eliminar vínculo
- `POST /drive-links/{link_id}/sync-now` - Sincronizar (stub)

#### Proyectos (Multi-Proyecto)
- `POST /projects` - Crear proyecto
- `GET /projects` - Listar proyectos + proyecto activo
- `GET /projects/active` - Obtener proyecto activo
- `GET /projects/{id}` - Obtener proyecto específico
- `PUT /projects/{id}` - Actualizar proyecto
- `POST /projects/{id}/activate` - Activar proyecto
- `DELETE /projects/{id}` - Eliminar proyecto

#### Integración MCP/CLI
- `GET /integration/mcp/config` - Obtener configuración MCP
- `POST /integration/mcp/config` - Actualizar configuración MCP
- `GET /integration/mcp/status` - Estado y ejemplos MCP
- `GET /integration/cli/config` - Obtener configuración CLI
- `POST /integration/cli/config` - Actualizar configuración CLI
- `GET /integration/cli/status` - Estado y ejemplos CLI
- `GET /integration/guide` - Guía completa de integración

### Ejemplo de Uso con cURL

```bash
# Configurar API key
curl -X POST http://localhost:8000/config/api-key \
  -H "Content-Type: application/json" \
  -d '{"api_key": "your_api_key_here"}'

# Crear un store
curl -X POST http://localhost:8000/stores \
  -H "Content-Type: application/json" \
  -d '{"display_name": "My Documents"}'

# Subir un documento
curl -X POST http://localhost:8000/stores/{store_id}/documents \
  -F "file=@/path/to/document.pdf" \
  -F "display_name=Important Document" \
  -F 'metadata={"author":"John Doe","year":2024}'

# Ejecutar consulta RAG
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is the main topic?",
    "store_ids": ["fileSearchStores/abc123"],
    "metadata_filter": "author=\"John Doe\""
  }'
```

## 🎨 Características de la UI

- **Temas**: Alterna entre modo claro y oscuro usando el botón en la esquina superior derecha
- **Navegación**: Menú lateral con acceso a todas las secciones
- **Responsive**: Se adapta a diferentes tamaños de pantalla
- **Feedback visual**: Estados de carga, mensajes de error y éxito
- **Validación**: Validación de formularios en tiempo real

## 🌐 Puertos y Servicios

La aplicación utiliza los siguientes puertos por defecto:

- **Frontend**: `http://localhost:5173` (Vite dev server)
- **Backend FastAPI**: `http://localhost:8000` (uvicorn)
- **MCP Server**: Configurable desde la GUI (recomendado: puerto 8001)
- **CLI Local**: Se conecta al backend (puerto configurable desde GUI)

**Importante**:
- El **CLI** y el **MCP Server** NO son servidores independientes
- El **CLI** es una herramienta de línea de comandos que se conecta al backend FastAPI
- El **MCP Server** se puede ejecutar en modo stdio (sin puerto) o HTTP (con puerto configurable)

## 🔐 Seguridad

- Las API keys se almacenan en la base de datos SQLite (backend/filesearch.db)
- También se pueden configurar en el archivo `backend/.env` para retrocompatibilidad
- Las API keys no se exponen en las respuestas de la API (campo `has_api_key`)
- CORS configurado solo para orígenes locales
- Para producción, considera:
  - **Encriptar API keys** en la base de datos (TODO marcado en el código)
  - Añadir autenticación (JWT, OAuth)
  - Usar HTTPS
  - Configurar CORS apropiadamente
  - Usar variables de entorno seguras
  - Implementar rate limiting

## 🛠️ Desarrollo

### Estructura de Código

- **Backend**: Arquitectura por capas (API → Services → Google Client)
- **Frontend**: Componentes funcionales con React Hooks
- **MCP Server**: FastMCP para exposición de herramientas a LLM agents
- **CLI**: Click + Rich para interfaz de línea de comandos
- **Tipado**: TypeScript estricto en frontend, Pydantic en backend
- **Estado**: React Query para datos del servidor, useState para UI local

### Logging

El backend registra todas las operaciones importantes:
- Conexiones a Google
- Creación/eliminación de stores
- Subida de documentos
- Consultas RAG

Los logs aparecen en la consola del servidor backend.

### Manejo de Errores

- Errores de API capturados y mostrados en la UI
- Respuestas HTTP con códigos de estado apropiados
- Mensajes de error descriptivos

## 📝 Limitaciones Conocidas

1. **⚠️ Metadatos en Documentos**: La subida de metadatos personalizados al subir archivos NO está funcional actualmente
   - **Estado**: Pendiente de implementación
   - **Problema**: El SDK `google-genai` (v1.50.1) requiere un formato específico de metadatos que aún no está correctamente implementado
   - **Funcionalidad actual**: Los documentos se suben correctamente pero sin metadatos
   - **Próximos pasos**: Investigar la sintaxis correcta del SDK para el parámetro `customMetadata` en `upload_to_file_search_store()`
   - La UI permite introducir metadatos pero estos se ignoran durante la subida (se registra un warning en los logs)

2. **Sincronización con Drive**: Implementada como stub, requiere:
   - Autenticación OAuth 2.0
   - Integración con Google Drive API
   - Scheduler para sincronización automática

3. **Paginación**: Implementada en backend, UI básica en frontend

4. **Persistencia de Drive Links**: En memoria (se pierden al reiniciar el servidor)
   - Para producción: usar base de datos (PostgreSQL, MongoDB, etc.)

## 🚧 Futuras Mejoras

### Prioridad Alta
- [ ] **Implementar subida de metadatos personalizados en documentos** (funcionalidad crítica pendiente)
  - Investigar formato correcto para `customMetadata` en el SDK
  - Implementar conversión de metadatos a formato Google
  - Probar con metadatos numéricos y de texto

### Otras Mejoras
- [ ] Implementación completa de sincronización con Google Drive
- [ ] Base de datos para persistencia de vínculos Drive
- [ ] Autenticación y autorización de usuarios
- [ ] Gestión de permisos por usuario
- [ ] Exportación de consultas y respuestas
- [ ] Historial de consultas
- [ ] Análisis y estadísticas de uso
- [ ] Soporte para más formatos de documentos
- [ ] Búsqueda y filtrado avanzado de documentos en UI
- [ ] Tests unitarios y de integración
- [x] **✅ COMPLETADO**: Servidor MCP para integración con LLM agents
- [x] **✅ COMPLETADO**: CLI local para uso desde terminal y agents

## 📚 Documentación de Referencia

- [Google File Search Documentation](https://ai.google.dev/gemini-api/docs/file-search)
- [Google Generative AI Python SDK](https://github.com/google/generative-ai-python)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Material-UI Documentation](https://mui.com/)
- [React Router](https://reactrouter.com/)

## 🐛 Solución de Problemas

### Backend no inicia

```bash
# Verificar que el entorno virtual está activado
source venv/bin/activate  # Linux/Mac
# o
venv\Scripts\activate  # Windows

# Verificar instalación de dependencias
pip install -r requirements.txt
```

### Frontend no inicia

```bash
# Reinstalar dependencias
rm -rf node_modules package-lock.json
npm install
```

### Error "API key not configured"

1. Configura la API key desde la UI (sección Configuration)
2. O edita el archivo `backend/.env` y añade:
   ```
   GOOGLE_API_KEY=tu_api_key_aqui
   ```

### Error de CORS

Verifica que:
- El backend está en `http://localhost:8000`
- El frontend está en `http://localhost:5173`
- Los orígenes están configurados en `backend/.env`:
  ```
  CORS_ORIGINS=http://localhost:5173,http://localhost:3000
  ```

### Documentos no se indexan

- Verifica que el formato del archivo es compatible
- Revisa los logs del backend para errores
- Asegúrate de que la API key tiene los permisos necesarios

## 📄 Licencia

Este proyecto es un sistema de demostración. Ajusta la licencia según tus necesidades.

## 👥 Contribuciones

Las contribuciones son bienvenidas. Por favor:
1. Fork el proyecto
2. Crea una rama para tu feature
3. Commit tus cambios
4. Push a la rama
5. Abre un Pull Request

## 📧 Contacto

Para preguntas o sugerencias, abre un issue en el repositorio.

---

**Desarrollado con ❤️ usando Google Gemini API, FastAPI, React y Material-UI**
