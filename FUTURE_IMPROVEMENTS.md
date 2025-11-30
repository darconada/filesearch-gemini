# Future Improvements & Feature Roadmap

Lista de mejoras y nuevas funcionalidades propuestas para implementación futura.

---

## 🔍 Search & Filtering

### Documents Page - Search/Filter Feature
**Prioridad:** Media
**Complejidad:** Baja
**Estado:** Propuesto

**Descripción:**
Añadir funcionalidad de búsqueda y filtrado en la página de Documents para facilitar la navegación cuando hay muchos documentos.

**Funcionalidades propuestas:**
- Búsqueda por nombre de archivo (client-side o server-side)
- Filtro por metadata (tags, categorías)
- Filtro por fecha de subida (rango de fechas)
- Filtro por tipo de archivo (MIME type)
- Ordenamiento por columnas (nombre, fecha, tamaño)

**Implementación sugerida:**
```typescript
// Frontend: DocumentsPage.tsx
- Añadir TextField con search icon
- Filtrar documentos localmente con .filter()
- O implementar backend endpoint con parámetro ?search=

// Backend (opcional): documents.py
- Añadir parámetro search a list_documents
- Filtrar en Google File Search API si lo soporta
```

**Archivos afectados:**
- `frontend/src/components/documents/DocumentsPage.tsx`
- `frontend/src/services/api.ts`
- `backend/app/api/documents.py` (opcional)

**UX sugerida:**
```
┌─────────────────────────────────────────────┐
│ Documents                    [+ Upload]     │
├─────────────────────────────────────────────┤
│ 🔍 Search documents...         [Filters ▾] │
├─────────────────────────────────────────────┤
│ Name          │ Metadata  │ State │ Created│
│ documento.pdf │ ...       │ ACTIVE│ 11/30  │
└─────────────────────────────────────────────┘
```

**Beneficios:**
- Mejor experiencia de usuario con muchos documentos
- Más rápido encontrar documentos específicos
- Útil para stores con cientos de documentos

---

## 🔐 Security Improvements

### (Referencia: ver SECURITY_PLAN.md para el plan completo)

Puntos críticos pendientes:
1. Restricción de filesystem (ALLOWED_FS_ROOT) - URGENTE
2. Input validation y sanitización
3. Autenticación básica (API key o JWT)
4. Backup security (validación de archivos .tar.gz)

---

## 📊 Analytics & Insights

### Document Usage Analytics
**Prioridad:** Baja
**Complejidad:** Media

**Ideas:**
- Dashboard con estadísticas de documentos por store
- Gráfico de uploads por fecha
- Top documentos más usados en queries
- Tamaño total de documentos por proyecto
- Detección de duplicados históricos (limpieza)

---

## 🔄 Sync Improvements

### Drive Sync - Completar implementación
**Prioridad:** Media
**Complejidad:** Media
**Estado:** Parcialmente implementado

**Pendiente:**
- Implementar lógica real de sincronización en `sync_drive_link_now()`
- Auto-sync scheduler para modo AUTOMATIC
- Detección de cambios en Drive (versioning)
- UI de progreso para syncs largos

### Local Files - Mejoras
**Prioridad:** Baja

**Ideas:**
- Soporte para directorios completos (sync recursivo)
- Exclude patterns (.gitignore style)
- Selective sync (elegir qué archivos sincronizar)

---

## 🎨 UI/UX Enhancements

### General
- Dark mode mejorado
- Notificaciones toast para acciones exitosas/fallidas
- Drag & drop para upload de documentos
- Preview de documentos (PDF, imágenes)
- Bulk actions (seleccionar múltiples documentos para eliminar)

### Documents Page
- Paginación mejorada (infinite scroll)
- Vista de grid/lista toggle
- Iconos por tipo de archivo
- Progress bar durante uploads
- Metadata editor inline

---

## 🔧 Technical Debt

### Backend
- Migrar de SQLite a PostgreSQL para producción
- Implementar tests automatizados (pytest)
- API rate limiting
- Logging estructurado (JSON logs)
- Metrics/observability (Prometheus)

### Frontend
- TypeScript strict mode
- Error boundaries
- Unit tests (Jest/React Testing Library)
- E2E tests (Playwright/Cypress)
- Code splitting para mejorar performance

---

## 📝 Documentation

### Falta documentar
- API Reference completa (Swagger mejorado)
- User manual/guide
- Deployment guide (Docker, Kubernetes)
- Contributing guide
- Architecture diagrams

---

## 🚀 Performance Optimizations

### Documents Upload
- Chunked upload para archivos grandes (>100MB)
- Progress tracking detallado
- Retry logic para uploads fallidos
- Background processing

### Database
- Índices optimizados
- Query optimization
- Connection pooling
- Caching layer (Redis)

---

**Última actualización:** 2025-11-30
**Mantenido por:** Claude Code + Usuario

**Cómo contribuir:**
- Añadir nuevas ideas a las secciones apropiadas
- Marcar como implementadas las completadas
- Actualizar prioridades según necesidades
