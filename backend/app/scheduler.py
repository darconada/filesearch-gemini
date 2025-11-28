"""Scheduler para sincronización automática de Drive y archivos locales"""
from apscheduler.schedulers.background import BackgroundScheduler
from app.database import SessionLocal
from app.services.drive_service import drive_service
from app.services.local_file_service import local_file_service
import logging

logger = logging.getLogger(__name__)

# Instancia global del scheduler
scheduler = BackgroundScheduler()


def sync_auto_links_job():
    """Job que sincroniza todos los links automáticos de Drive"""
    logger.info("Running automatic Drive sync job...")

    db = SessionLocal()
    try:
        results = drive_service.sync_all_auto_links(db)
        logger.info(f"Drive auto-sync job completed: {len(results)} links processed")
    except Exception as e:
        logger.error(f"Error in Drive auto-sync job: {e}")
    finally:
        db.close()


def sync_local_files_job():
    """Job que sincroniza todos los archivos locales"""
    logger.info("Running automatic local files sync job...")

    db = SessionLocal()
    try:
        results = local_file_service.sync_all(db)
        logger.info(f"Local files auto-sync job completed: {len(results)} files processed")
    except Exception as e:
        logger.error(f"Error in local files auto-sync job: {e}")
    finally:
        db.close()


def start_scheduler():
    """Iniciar el scheduler"""
    try:
        # Job de sincronización de Drive cada 5 minutos
        scheduler.add_job(
            sync_auto_links_job,
            'interval',
            minutes=5,
            id='drive_auto_sync',
            replace_existing=True
        )

        # Job de sincronización de archivos locales cada 3 minutos
        # (más frecuente porque los archivos locales pueden cambiar más a menudo)
        scheduler.add_job(
            sync_local_files_job,
            'interval',
            minutes=3,
            id='local_files_auto_sync',
            replace_existing=True
        )

        scheduler.start()
        logger.info("Scheduler started:")
        logger.info("  - Drive auto-sync: every 5 minutes")
        logger.info("  - Local files auto-sync: every 3 minutes")
    except Exception as e:
        logger.error(f"Error starting scheduler: {e}")


def stop_scheduler():
    """Detener el scheduler"""
    try:
        scheduler.shutdown()
        logger.info("Scheduler stopped")
    except Exception as e:
        logger.error(f"Error stopping scheduler: {e}")
