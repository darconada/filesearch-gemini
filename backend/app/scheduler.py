"""Scheduler para sincronización automática de Drive"""
from apscheduler.schedulers.background import BackgroundScheduler
from app.database import SessionLocal
from app.services.drive_service import drive_service
import logging

logger = logging.getLogger(__name__)

# Instancia global del scheduler
scheduler = BackgroundScheduler()


def sync_auto_links_job():
    """Job que sincroniza todos los links automáticos"""
    logger.info("Running automatic Drive sync job...")

    db = SessionLocal()
    try:
        results = drive_service.sync_all_auto_links(db)
        logger.info(f"Auto-sync job completed: {len(results)} links processed")
    except Exception as e:
        logger.error(f"Error in auto-sync job: {e}")
    finally:
        db.close()


def start_scheduler():
    """Iniciar el scheduler"""
    try:
        # Añadir job de sincronización cada 5 minutos
        scheduler.add_job(
            sync_auto_links_job,
            'interval',
            minutes=5,
            id='drive_auto_sync',
            replace_existing=True
        )

        scheduler.start()
        logger.info("Scheduler started: auto-sync every 5 minutes")
    except Exception as e:
        logger.error(f"Error starting scheduler: {e}")


def stop_scheduler():
    """Detener el scheduler"""
    try:
        scheduler.shutdown()
        logger.info("Scheduler stopped")
    except Exception as e:
        logger.error(f"Error stopping scheduler: {e}")
