# Configuración de Google Drive Sync

Esta guía explica cómo configurar la sincronización automática con Google Drive para el sistema File Search RAG.

## 🎯 ¿Qué hace Drive Sync?

La funcionalidad de Drive Sync permite:
- **Vincular archivos de Google Drive** a File Search stores
- **Sincronización automática**: detecta cuando un archivo cambia en Drive y lo actualiza en File Search
- **Sincronización manual**: sincronizar bajo demanda con un botón
- **Metadatos automáticos**: añade metadatos de Drive (file_id, última modificación)

## 📋 Requisitos Previos

1. Cuenta de Google
2. Proyecto en Google Cloud Console (gratuito)
3. Python 3.11+ instalado
4. Aplicación backend funcionando

## 🔧 Paso 1: Crear Proyecto en Google Cloud Console

### 1.1 Crear Proyecto

1. Ve a [Google Cloud Console](https://console.cloud.google.com/)
2. Haz clic en el selector de proyectos (arriba a la izquierda)
3. Clic en "Nuevo Proyecto"
4. Nombre: `File Search RAG App` (o el que prefieras)
5. Clic en "Crear"

### 1.2 Habilitar Google Drive API

1. En el menú lateral, ve a **APIs y servicios > Biblioteca**
2. Busca "Google Drive API"
3. Haz clic en "Google Drive API"
4. Clic en "HABILITAR"

## 🔑 Paso 2: Crear Credenciales OAuth 2.0

### 2.1 Configurar Pantalla de Consentimiento

1. Ve a **APIs y servicios > Pantalla de consentimiento de OAuth**
2. Selecciona **Externo** (usuarios pueden ser cualquiera con cuenta Google)
3. Clic en "Crear"
4. Completa el formulario:
   - **Nombre de la aplicación**: "File Search RAG"
   - **Correo electrónico de asistencia**: tu email
   - **Dominios autorizados**: (dejar vacío para desarrollo local)
   - **Correo electrónico del desarrollador**: tu email
5. Clic en "Guardar y continuar"
6. En "Scopes", clic en "Añadir o quitar scopes"
7. Busca y añade: `https://www.googleapis.com/auth/drive.readonly`
8. Clic en "Actualizar" y luego "Guardar y continuar"
9. En "Usuarios de prueba", añade tu email de Google
10. Clic en "Guardar y continuar"

### 2.2 Crear Credenciales

1. Ve a **APIs y servicios > Credenciales**
2. Clic en "Crear credenciales" > "ID de cliente de OAuth 2.0"
3. Tipo de aplicación: **Aplicación de escritorio**
4. Nombre: "File Search RAG Desktop Client"
5. Clic en "Crear"
6. **¡IMPORTANTE!** Descarga el archivo JSON haciendo clic en el icono de descarga
7. Guarda el archivo como `credentials.json`

## 💾 Paso 3: Configurar la Aplicación

### 3.1 Colocar Credenciales

Opción A - En el directorio del backend:
```bash
mv ~/Downloads/credentials.json /path/to/filesearch-gemini/backend/credentials.json
```

Opción B - En cualquier ubicación:
```bash
# Mantén el archivo donde quieras y anota la ruta completa
```

### 3.2 Actualizar .env

Edita el archivo `backend/.env`:

```bash
# Ruta al archivo de credenciales (OBLIGATORIO para Drive sync)
GOOGLE_DRIVE_CREDENTIALS=/path/to/filesearch-gemini/backend/credentials.json

# Ruta donde se guardará el token (generado automáticamente)
GOOGLE_DRIVE_TOKEN=/path/to/filesearch-gemini/backend/token.json
```

Alternativamente, si colocaste `credentials.json` en el directorio backend:

```bash
GOOGLE_DRIVE_CREDENTIALS=credentials.json
GOOGLE_DRIVE_TOKEN=token.json
```

## 🚀 Paso 4: Primera Autenticación

### 4.1 Iniciar Backend

```bash
cd backend
source venv/bin/activate
python -m app.main
```

### 4.2 Autenticación OAuth (Primera Vez)

La primera vez que intentes sincronizar un archivo de Drive:

1. El sistema abrirá automáticamente tu navegador
2. Verás una pantalla de Google pidiendo permiso
3. **IMPORTANTE**: Si ves "Esta app no está verificada":
   - Haz clic en "Avanzado"
   - Clic en "Ir a File Search RAG (no seguro)"
   - Esto es normal para apps en desarrollo
4. Selecciona tu cuenta de Google
5. Revisa los permisos (solo lectura de Drive)
6. Clic en "Continuar"
7. El navegador mostrará "The authentication flow has completed"

Después de esto, el archivo `token.json` se crea automáticamente y las futuras sincronizaciones no requerirán autenticación.

## 📱 Paso 5: Uso en la Aplicación

### 5.1 Crear un Vínculo Drive

1. Ve a la sección **Drive Sync** en la UI
2. Clic en "Add Link"
3. Completa el formulario:
   - **Drive File ID**: ID del archivo en Google Drive
   - **Store**: Selecciona el store de destino
   - **Sync Mode**:
     - **Manual**: sincroniza solo cuando hagas clic en "Sync"
     - **Auto**: sincroniza automáticamente cada 5 minutos
   - **Sync Interval** (solo para modo Auto): minutos entre sincronizaciones

#### ¿Cómo obtener el Drive File ID?

Método 1 - Desde la URL:
```
https://drive.google.com/file/d/1ABC...XYZ/view
                              ^^^^^^^^^ Este es el File ID
```

Método 2 - Clic derecho en archivo > Obtener enlace > Compartir
El ID está en la URL del enlace compartido.

### 5.2 Sincronizar Manualmente

1. En la tabla de Drive Links, localiza tu vínculo
2. Haz clic en el icono de sincronización (↻)
3. El estado cambiará a "syncing" y luego a "synced"
4. El documento aparecerá en el store seleccionado

### 5.3 Sincronización Automática

Si configuraste modo automático:
- El scheduler ejecuta cada 5 minutos
- Solo sincroniza si el archivo ha cambiado en Drive
- Puedes ver última sincronización en la columna "Last Synced"

## 🔍 Verificación

### Verificar que Drive API funciona:

```python
# En Python, con el backend activo:
from app.services.drive_client import drive_client

# Test de conexión
success, error = drive_client.test_connection()
if success:
    print("✅ Drive API configurada correctamente")
else:
    print(f"❌ Error: {error}")
```

### Verificar scheduler:

Los logs del backend mostrarán:
```
INFO:app.scheduler:Scheduler started: auto-sync every 5 minutes
INFO:app.scheduler:Running automatic Drive sync job...
```

## 🐛 Solución de Problemas

### Error: "credentials file not found"

**Causa**: Ruta incorrecta en `.env`

**Solución**:
```bash
# Verifica la ruta
ls -la /path/to/credentials.json

# Actualiza .env con la ruta correcta
GOOGLE_DRIVE_CREDENTIALS=/ruta/absoluta/correcta/credentials.json
```

### Error: "The authentication flow has completed" pero no funciona

**Causa**: token.json no se guardó correctamente

**Solución**:
```bash
# Elimina token.json y vuelve a autenticar
rm backend/token.json
# Reinicia backend y vuelve a intentar sincronizar
```

### Error: "Failed to retrieve file metadata"

**Causa**: File ID incorrecto o archivo no accesible

**Solución**:
- Verifica que el File ID es correcto
- Asegúrate de que tu cuenta Google tiene acceso al archivo
- El archivo debe estar en "Mi unidad" o compartido contigo

### Error: "Insufficient permissions"

**Causa**: Scope de Drive no configurado correctamente

**Solución**:
1. Ve a Google Cloud Console > APIs y servicios > Pantalla de consentimiento
2. Verifica que el scope `drive.readonly` está añadido
3. Elimina `token.json`
4. Vuelve a autenticar

### Token expirado

Los tokens expiran después de cierto tiempo. Si ves errores de autenticación:

```bash
# Elimina el token y vuelve a autenticar
rm backend/token.json
# Reinicia backend
```

## 🔒 Seguridad

### Datos Sensibles

- `credentials.json`: **NO compartir, NO subir a Git**
- `token.json`: **NO compartir, NO subir a Git**
- Ambos archivos están en `.gitignore` por defecto

### Permisos

El scope `drive.readonly` solo permite:
- ✅ Leer metadatos de archivos
- ✅ Descargar contenido de archivos
- ❌ Modificar archivos
- ❌ Eliminar archivos
- ❌ Crear archivos

### Revocar Acceso

Si quieres revocar el acceso de la aplicación:
1. Ve a [Google Account](https://myaccount.google.com/permissions)
2. Encuentra "File Search RAG"
3. Clic en "Eliminar acceso"

## 📊 Limitaciones

- **Tamaño de archivo**: Depende del plan de Google Drive
- **Tipos de archivo**: Todos los soportados por File Search
- **Frecuencia de sync**: Mínimo 5 minutos en modo automático
- **Número de vínculos**: Sin límite (pero considera cuota de API)

## 🎓 Recursos Adicionales

- [Google Drive API Documentation](https://developers.google.com/drive/api/guides/about-sdk)
- [OAuth 2.0 for Desktop Apps](https://developers.google.com/identity/protocols/oauth2/native-app)
- [File Search Documentation](https://ai.google.dev/gemini-api/docs/file-search)

## 💡 Tips

1. **Organiza tus vínculos**: Usa un store diferente para cada proyecto o tipo de documento
2. **Modo manual vs auto**: Usa manual para archivos que raramente cambian, auto para documentos dinámicos
3. **Metadatos**: Los archivos sincronizados desde Drive incluyen automáticamente:
   - `drive_file_id`: Para tracking
   - `synced_from`: "google_drive"
   - `last_modified`: Timestamp de Drive
4. **Monitoreo**: Revisa los logs del backend para ver actividad de sincronización

---

**¿Problemas?** Abre un issue en el repositorio con:
- Logs del backend
- Configuración de `.env` (sin credentials)
- Pasos que seguiste
