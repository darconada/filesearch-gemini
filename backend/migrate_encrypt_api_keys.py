"""
Migración para encriptar API keys existentes en la base de datos

Este script:
1. Lee todos los proyectos de la BD
2. Verifica si las API keys ya están encriptadas
3. Si no lo están, las encripta usando el servicio de encriptación
4. Actualiza los registros en la BD

IMPORTANTE: Hacer backup de la BD antes de ejecutar este script
"""
import sys
import os

# Añadir el directorio app al path para poder importar los módulos
sys.path.insert(0, os.path.dirname(__file__))

from app.database import SessionLocal, init_db
from app.models.db_models import ProjectDB
from app.services.encryption_service import encryption_service
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def migrate_encrypt_api_keys():
    """Encriptar todas las API keys existentes"""
    logger.info("=== Starting API key encryption migration ===")

    # Inicializar BD
    init_db()

    db = SessionLocal()
    try:
        # Obtener todos los proyectos
        projects = db.query(ProjectDB).all()

        if not projects:
            logger.info("No projects found in database")
            return

        logger.info(f"Found {len(projects)} projects to process")

        encrypted_count = 0
        skipped_count = 0
        error_count = 0

        for project in projects:
            try:
                # Verificar si la API key ya está encriptada
                if encryption_service.is_encrypted(project.api_key):
                    logger.info(f"Project '{project.name}' (ID: {project.id}) - API key already encrypted, skipping")
                    skipped_count += 1
                    continue

                # La key no está encriptada, encriptarla
                logger.info(f"Project '{project.name}' (ID: {project.id}) - Encrypting API key...")

                # Guardar la key original para validación
                original_key = project.api_key

                # Encriptar
                encrypted_key = encryption_service.encrypt(original_key)

                # Actualizar en BD
                project.api_key = encrypted_key
                db.commit()

                # Validar que se puede desencriptar
                decrypted_key = encryption_service.decrypt(encrypted_key)
                if decrypted_key != original_key:
                    raise Exception("Encryption validation failed: decrypted key doesn't match original")

                logger.info(f"Project '{project.name}' (ID: {project.id}) - API key encrypted successfully ✓")
                encrypted_count += 1

            except Exception as e:
                logger.error(f"Error encrypting API key for project '{project.name}': {e}")
                db.rollback()
                error_count += 1

        logger.info("=== Migration completed ===")
        logger.info(f"  Encrypted: {encrypted_count}")
        logger.info(f"  Skipped (already encrypted): {skipped_count}")
        logger.info(f"  Errors: {error_count}")

        if error_count > 0:
            logger.warning("Migration completed with errors. Please check the logs above.")
            return False
        else:
            logger.info("All API keys encrypted successfully!")
            return True

    except Exception as e:
        logger.error(f"Fatal error during migration: {e}")
        db.rollback()
        return False
    finally:
        db.close()


if __name__ == "__main__":
    logger.info("API Key Encryption Migration Tool")
    logger.info("===================================")
    logger.info("")
    logger.warning("IMPORTANT: Make sure you have a backup of your database before proceeding!")
    logger.info("")

    # Confirmar antes de continuar
    response = input("Do you want to continue? (yes/no): ")
    if response.lower() not in ['yes', 'y']:
        logger.info("Migration cancelled by user")
        sys.exit(0)

    success = migrate_encrypt_api_keys()
    sys.exit(0 if success else 1)
