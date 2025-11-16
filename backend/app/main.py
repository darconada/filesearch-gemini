"""FastAPI main application"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.config import settings
from app.api import config, stores, documents, query, drive
from app.database import init_db
from app.scheduler import start_scheduler, stop_scheduler
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestionar inicio y cierre de la aplicación"""
    # Startup: Inicializar BD y scheduler
    logger.info("Initializing database...")
    init_db()

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
app.include_router(documents.router)  # Primero las rutas más específicas
app.include_router(stores.router)     # Después las rutas con :path
app.include_router(query.router)
app.include_router(drive.router)


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
