"""
Migration script to add versioning fields and local file links table

This migration:
1. Adds versioning fields to drive_links table:
   - version (INTEGER, default 1)
   - original_file_id (VARCHAR, nullable)
   - previous_document_ids (TEXT, nullable, stores JSON)

2. Creates new local_file_links table for local file synchronization
"""
import sqlite3
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Path to database
db_path = Path(__file__).parent / "app.db"

def migrate():
    """Run migration"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # ========== PART 1: Add versioning fields to drive_links ==========
        logger.info("Checking drive_links table for versioning fields...")

        # Get current columns
        cursor.execute("PRAGMA table_info(drive_links)")
        columns = {col[1]: col for col in cursor.fetchall()}

        # Add version column if not exists
        if 'version' not in columns:
            logger.info("Adding 'version' column to drive_links...")
            cursor.execute("ALTER TABLE drive_links ADD COLUMN version INTEGER DEFAULT 1 NOT NULL")
            conn.commit()
            logger.info("✅ Added 'version' column")
        else:
            logger.info("'version' column already exists")

        # Add original_file_id column if not exists
        if 'original_file_id' not in columns:
            logger.info("Adding 'original_file_id' column to drive_links...")
            cursor.execute("ALTER TABLE drive_links ADD COLUMN original_file_id VARCHAR")
            conn.commit()
            logger.info("✅ Added 'original_file_id' column")
        else:
            logger.info("'original_file_id' column already exists")

        # Add previous_document_ids column if not exists
        if 'previous_document_ids' not in columns:
            logger.info("Adding 'previous_document_ids' column to drive_links...")
            cursor.execute("ALTER TABLE drive_links ADD COLUMN previous_document_ids TEXT")
            conn.commit()
            logger.info("✅ Added 'previous_document_ids' column")
        else:
            logger.info("'previous_document_ids' column already exists")

        # ========== PART 2: Create local_file_links table ==========
        logger.info("Checking if local_file_links table exists...")

        cursor.execute("""
            SELECT name FROM sqlite_master
            WHERE type='table' AND name='local_file_links'
        """)

        if not cursor.fetchone():
            logger.info("Creating 'local_file_links' table...")

            cursor.execute("""
                CREATE TABLE local_file_links (
                    id VARCHAR PRIMARY KEY,
                    local_file_path VARCHAR NOT NULL,
                    file_name VARCHAR NOT NULL,
                    store_id VARCHAR NOT NULL,
                    document_id VARCHAR,

                    file_size INTEGER,
                    file_hash VARCHAR,
                    last_modified_at TIMESTAMP,
                    mime_type VARCHAR,

                    last_synced_at TIMESTAMP,
                    status VARCHAR DEFAULT 'not_synced',
                    error_message VARCHAR,

                    version INTEGER DEFAULT 1 NOT NULL,
                    original_file_id VARCHAR,
                    previous_document_ids TEXT,

                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP
                )
            """)

            # Create indexes
            cursor.execute("CREATE INDEX idx_local_file_links_path ON local_file_links(local_file_path)")
            cursor.execute("CREATE INDEX idx_local_file_links_store ON local_file_links(store_id)")

            conn.commit()
            logger.info("✅ Created 'local_file_links' table with indexes")
        else:
            logger.info("'local_file_links' table already exists")

        logger.info("\n🎉 Migration completed successfully!")

        # Show summary
        cursor.execute("PRAGMA table_info(drive_links)")
        drive_cols = cursor.fetchall()
        logger.info(f"\ndrive_links table now has {len(drive_cols)} columns")

        cursor.execute("PRAGMA table_info(local_file_links)")
        local_cols = cursor.fetchall()
        if local_cols:
            logger.info(f"local_file_links table has {len(local_cols)} columns")

    except Exception as e:
        logger.error(f"❌ Migration failed: {e}")
        conn.rollback()
        raise

    finally:
        conn.close()


if __name__ == "__main__":
    migrate()
