"""FastAPI main application"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.config import settings
from app.api import config, stores, documents, query, drive, mcp_config, projects, local_files, file_updates, file_browser
from app.database import init_db, SessionLocal
from app.scheduler import start_scheduler, stop_scheduler
from app.models.db_models import ProjectDB
from app.services.google_client import google_client
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def load_active_project():
    """Cargar el proyecto activo y configurar GoogleClient"""
    db = SessionLocal()
    try:
        active_project = db.query(ProjectDB).filter(ProjectDB.is_active == True).first()

        if active_project:
            logger.info(f"Loading active project: {active_project.name} (ID: {active_project.id})")
            google_client.configure(active_project.api_key)
        else:
            # Si no hay proyecto activo, intentar usar la API key de settings (retrocompatibilidad)
            if settings.api_key:
                logger.info("No active project found, using API key from settings/env")
                google_client.configure(settings.api_key)
            else:
                logger.warning("No active project or API key configured. Some operations may fail.")
    except Exception as e:
        logger.error(f"Error loading active project: {e}")
        # Intentar usar API key de settings como fallback
        if settings.api_key:
            logger.info("Falling back to API key from settings/env")
            try:
                google_client.configure(settings.api_key)
            except:
                pass
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestionar inicio y cierre de la aplicación"""
    # Startup: Inicializar BD y scheduler
    logger.info("Initializing database...")
    init_db()

    # Cargar proyecto activo y configurar GoogleClient
    logger.info("Loading active project...")
    load_active_project()

    logger.info("Starting scheduler...")
    start_scheduler()

    yield

    # Shutdown: Detener scheduler
    logger.info("Stopping scheduler...")
    stop_scheduler()


# Crear aplicación FastAPI
app = FastAPI(
    title="File Search RAG API",
    description="API REST para gestionar Google File Search y consultas RAG con sincronización Drive",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
# IMPORTANTE: documents.router debe ir ANTES que stores.router
# porque stores tiene /{store_id:path} que es greedy y capturaría
# las rutas de documents si stores se registra primero
app.include_router(config.router)
app.include_router(projects.router)   # Projects management
app.include_router(documents.router)  # Primero las rutas más específicas
app.include_router(stores.router)     # Después las rutas con :path
app.include_router(query.router)
app.include_router(drive.router)
app.include_router(local_files.router)  # Local file sync
app.include_router(file_updates.router)  # File updates/replace
app.include_router(file_browser.router)  # Server file browser
app.include_router(mcp_config.router)  # MCP y CLI configuration


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "File Search RAG API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health():
    """Health check"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=True
    )
