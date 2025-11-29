# Google Picker API - Configuración

Esta guía explica cómo configurar Google Picker API para permitir seleccionar archivos de Google Drive directamente desde la UI.

## 📋 Requisitos Previos

- Proyecto en Google Cloud Console
- OAuth 2.0 configurado para Drive API (ya configurado si tienes Drive sync funcionando)

## 🔧 Pasos de Configuración

### 1. Habilitar Google Picker API

1. Ve a [Google Cloud Console](https://console.cloud.google.com/)
2. Selecciona tu proyecto
3. Ve a **APIs & Services** > **Library**
4. Busca "Google Picker API"
5. Haz clic en **Enable**

### 2. Crear/Configurar API Key (Opcional pero Recomendado)

La API Key permite cargar el Picker sin restricciones adicionales.

1. Ve a **APIs & Services** > **Credentials**
2. Haz clic en **+ CREATE CREDENTIALS** > **API key**
3. Copia la API key generada
4. **(Recomendado)** Haz clic en **Restrict Key**:
   - **Application restrictions**: HTTP referrers
   - Añade: `http://localhost:5173/*`, `http://localhost:*`
   - **API restrictions**: Google Picker API, Google Drive API
5. Guarda los cambios

### 3. Configurar OAuth 2.0 Client ID (Ya debería estar configurado)

Si ya tienes Drive OAuth funcionando, este paso ya está completo. Si no:

1. Ve a **APIs & Services** > **Credentials**
2. Busca tu **OAuth 2.0 Client ID**
3. Asegúrate que tenga:
   - **Authorized JavaScript origins**: `http://localhost:5173`
   - **Authorized redirect URIs**: `http://localhost:5173/oauth2callback` (si aplica)

### 4. Configurar Variables de Entorno (Frontend)

Crea o actualiza el archivo `.env` en el directorio `frontend/`:

```bash
# Frontend .env
VITE_GOOGLE_API_KEY=tu_api_key_aqui
VITE_GOOGLE_CLIENT_ID=tu_client_id.apps.googleusercontent.com
```

**Nota:** Estas variables son opcionales. El Picker funcionará con solo el OAuth token del backend, pero la API Key mejora la compatibilidad.

### 5. Verificar Configuración Backend

El backend ya debe tener configurado:

```bash
# Backend .env o config
GOOGLE_DRIVE_CREDENTIALS=/path/to/credentials.json
GOOGLE_DRIVE_TOKEN=/path/to/token.json
GOOGLE_DRIVE_SCOPES=https://www.googleapis.com/auth/drive.readonly
```

## 🧪 Probar la Configuración

1. **Reinicia el backend**:
   ```bash
   cd backend
   python -m uvicorn app.main:app --reload
   ```

2. **Reinicia el frontend**:
   ```bash
   cd frontend
   npm run dev
   ```

3. **Probar el Picker**:
   - Ve a la página **Drive Sync**
   - Haz clic en **Add Link**
   - Haz clic en **Browse Drive** 📁
   - Debería abrirse el Google Picker mostrando tus archivos de Drive

## ❗ Troubleshooting

### Error: "Failed to load Google Picker API"

**Causa:** Google Picker API no está habilitada o hay problemas de red.

**Solución:**
1. Verifica que Google Picker API esté habilitada en Cloud Console
2. Limpia la caché del navegador
3. Verifica la consola del navegador para errores específicos

### Error: "No valid Drive credentials"

**Causa:** El backend no tiene credenciales OAuth válidas.

**Solución:**
1. Verifica que `credentials.json` exista en `backend/`
2. Ejecuta el flujo OAuth:
   ```bash
   cd backend
   python -c "from app.services.drive_client import drive_client; drive_client.configure()"
   ```
3. Autoriza la aplicación en el navegador
4. Reinicia el backend

### El Picker se abre pero no muestra archivos

**Causa:** Scopes de OAuth insuficientes.

**Solución:**
1. Verifica que `GOOGLE_DRIVE_SCOPES` incluya:
   ```
   https://www.googleapis.com/auth/drive.readonly
   ```
   o
   ```
   https://www.googleapis.com/auth/drive
   ```
2. Elimina `token.json` y vuelve a autenticar
3. Reinicia el backend

### Error de CORS en el navegador

**Causa:** Origen no autorizado.

**Solución:**
1. Añade `http://localhost:5173` a **Authorized JavaScript origins** en OAuth 2.0 Client ID
2. Espera unos minutos (los cambios pueden tardar)
3. Limpia la caché del navegador

## 🔒 Seguridad

### Variables de Entorno

- ✅ **Backend**: Las credenciales de OAuth (`credentials.json`, `token.json`) NO se deben commitear
- ✅ **Frontend**: La API Key es pública y puede estar en el código, pero debe estar restringida por:
  - HTTP referrers (solo tu dominio)
  - APIs habilitadas (solo Picker y Drive)

### Producción

Para producción, actualiza:

1. **Google Cloud Console**:
   - Authorized JavaScript origins: `https://tu-dominio.com`
   - HTTP referrers para API Key: `https://tu-dominio.com/*`

2. **Frontend .env**:
   ```bash
   VITE_GOOGLE_API_KEY=tu_api_key_produccion
   VITE_GOOGLE_CLIENT_ID=tu_client_id_produccion.apps.googleusercontent.com
   ```

## 📚 Referencias

- [Google Picker API Documentation](https://developers.google.com/picker)
- [OAuth 2.0 for Web Server Applications](https://developers.google.com/identity/protocols/oauth2/web-server)
- [Google Drive API](https://developers.google.com/drive/api/guides/about-sdk)

## ✅ Checklist de Configuración

- [ ] Google Picker API habilitada en Cloud Console
- [ ] API Key creada y restringida (opcional)
- [ ] OAuth 2.0 Client ID configurado con orígenes autorizados
- [ ] Variables de entorno configuradas en frontend (opcional)
- [ ] Backend tiene `credentials.json` y `token.json` válidos
- [ ] Probado el flujo completo de selección de archivos

---

¿Problemas? Revisa los logs del backend y la consola del navegador para mensajes de error detallados.
