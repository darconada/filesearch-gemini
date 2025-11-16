# File Search RAG Application

Una aplicación web completa para gestionar Google File Search y ejecutar consultas RAG (Retrieval-Augmented Generation) con una interfaz moderna, API REST y **sincronización completa con Google Drive**.

## ⚠️ IMPORTANTE - Versión 2.0

Esta aplicación usa el **SDK oficial `google-genai`** (v1.6.1+). El SDK anterior `google-generativeai` **NO soporta File Search** y causará errores.

**Si tienes el error**: `module 'google.generativeai' has no attribute 'list_file_search_stores'`
- ✅ **Solución**: Instala las dependencias correctas: `pip install -r requirements.txt`
- ✅ El SDK correcto es `google-genai` (no `google-generativeai`)

**Novedades v2.0**:
- ✨ **Sincronización COMPLETA con Google Drive** (OAuth 2.0 + detección automática de cambios)
- ✨ Scheduler automático cada 5 minutos para sync mode AUTO
- ✨ Base de datos SQLite para persistencia de vínculos Drive
- ✨ Modelo actualizado: `gemini-2.5-flash` (compatible con File Search)
- 📖 Ver [CHANGELOG.md](CHANGELOG.md) para detalles completos
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
  - Subida de documentos con metadatos personalizados (hasta 20 pares clave/valor)
  - Listado paginado de documentos
  - Actualización de documentos (eliminar + recrear)
  - Eliminación de documentos
  - Configuración avanzada de chunking (tokens por chunk, overlap)
  - Soporte para metadatos numéricos y de texto

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
│   ├── models/              # Modelos Pydantic
│   │   ├── store.py
│   │   ├── document.py
│   │   ├── query.py
│   │   ├── config.py
│   │   └── drive.py
│   ├── services/            # Lógica de negocio
│   │   ├── google_client.py
│   │   ├── store_service.py
│   │   ├── document_service.py
│   │   ├── query_service.py
│   │   └── drive_service.py
│   └── api/                 # Endpoints REST
│       ├── config.py
│       ├── stores.py
│       ├── documents.py
│       ├── query.py
│       └── drive.py
└── requirements.txt
```

### Frontend (React + TypeScript + Vite)

```
frontend/
├── src/
│   ├── components/          # Componentes React
│   │   ├── common/         # Layout, navegación
│   │   ├── config/         # Configuración
│   │   ├── stores/         # Gestión de stores
│   │   ├── documents/      # Gestión de documentos
│   │   ├── query/          # Consultas RAG
│   │   └── drive/          # Sincronización Drive
│   ├── services/           # Cliente API
│   │   └── api.ts
│   ├── types/              # Tipos TypeScript
│   │   └── index.ts
│   ├── theme/              # Temas MUI
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
python -m app.main
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

## 📖 Uso de la Aplicación

### 1. Configurar API Key

1. Navega a la sección **Configuration**
2. Introduce tu Google API Key
3. Haz clic en **Save API Key**
4. Verifica que el estado muestre "API Key Valid: Valid"

### 2. Crear un Store

1. Ve a la sección **Stores**
2. Haz clic en **Create Store**
3. Introduce un nombre descriptivo
4. El store se marcará como activo automáticamente

### 3. Subir Documentos

1. Ve a la sección **Documents**
2. Haz clic en **Upload Document**
3. Selecciona un archivo
4. (Opcional) Añade metadatos personalizados:
   - Clave: `author`, Valor: `Robert Graves`
   - Clave: `year`, Valor: `2021`
5. (Opcional) Configura opciones avanzadas de chunking
6. Haz clic en **Upload**

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

## 🔐 Seguridad

- La API key se almacena en el backend (archivo `.env`)
- No se expone en el frontend
- CORS configurado solo para orígenes locales
- Para producción, considera:
  - Añadir autenticación (JWT, OAuth)
  - Usar HTTPS
  - Configurar CORS apropiadamente
  - Usar variables de entorno seguras

## 🛠️ Desarrollo

### Estructura de Código

- **Backend**: Arquitectura por capas (API → Services → Google Client)
- **Frontend**: Componentes funcionales con React Hooks
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

1. **Sincronización con Drive**: Implementada como stub, requiere:
   - Autenticación OAuth 2.0
   - Integración con Google Drive API
   - Scheduler para sincronización automática

2. **Paginación**: Implementada en backend, UI básica en frontend

3. **Persistencia de Drive Links**: En memoria (se pierden al reiniciar el servidor)
   - Para producción: usar base de datos (PostgreSQL, MongoDB, etc.)

## 🚧 Futuras Mejoras

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
