"""
Migration script to add documents table for duplicate detection

This migration adds a new 'documents' table to track all documents uploaded
to File Search stores, enabling duplicate detection via SHA256 hash comparison.

Run this script once to create the table:
    python migrate_add_documents_table.py
"""
import sys
from pathlib import Path

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy import Column, String, Integer, DateTime, JSON, inspect
from sqlalchemy.sql import func
from app.database import engine, Base, SessionLocal
from app.models.db_models import DocumentDB
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def table_exists(table_name: str) -> bool:
    """Check if a table exists in the database"""
    inspector = inspect(engine)
    return table_name in inspector.get_table_names()


def run_migration():
    """Run the migration to add the documents table"""
    logger.info("Starting migration: add documents table")

    # Check if table already exists
    if table_exists("documents"):
        logger.info("✓ Table 'documents' already exists. No migration needed.")
        return

    try:
        # Create the documents table
        logger.info("Creating 'documents' table...")
        DocumentDB.__table__.create(engine)
        logger.info("✓ Table 'documents' created successfully")

        logger.info("Migration completed successfully!")
        logger.info("")
        logger.info("The documents table is now available for duplicate detection.")
        logger.info("All future document uploads will be tracked in this table.")

    except Exception as e:
        logger.error(f"❌ Migration failed: {e}")
        raise


if __name__ == "__main__":
    run_migration()
