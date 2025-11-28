"""Migración: Añadir custom_metadata y project_id a local_file_links"""
import sqlite3
from pathlib import Path
import sys

def migrate():
    """
    Añade:
    - custom_metadata (JSON): Para metadata personalizada del usuario
    - project_id (INTEGER): Para asociar archivos locales a proyectos

    Asigna todos los archivos existentes al proyecto activo actual.
    """
    db_path = Path(__file__).parent / "app.db"

    if not db_path.exists():
        print(f"❌ Database not found at: {db_path}")
        print("   Make sure you're running this from the backend directory")
        sys.exit(1)

    print(f"📂 Using database: {db_path}")
    print()

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # 1. Verificar que la tabla existe
        cursor.execute("""
            SELECT COUNT(*) FROM sqlite_master
            WHERE type='table' AND name='local_file_links'
        """)
        if cursor.fetchone()[0] == 0:
            print("⚠️  Table 'local_file_links' does not exist. Nothing to migrate.")
            return

        print("✓ Table 'local_file_links' found")
        print()

        # 2. Añadir columna custom_metadata
        cursor.execute("""
            SELECT COUNT(*) FROM pragma_table_info('local_file_links')
            WHERE name='custom_metadata'
        """)
        if cursor.fetchone()[0] == 0:
            print("📝 Adding custom_metadata column...")
            cursor.execute("ALTER TABLE local_file_links ADD COLUMN custom_metadata TEXT")
            print("   ✓ custom_metadata column added")
        else:
            print("⚠️  custom_metadata column already exists, skipping")

        print()

        # 3. Añadir columna project_id
        cursor.execute("""
            SELECT COUNT(*) FROM pragma_table_info('local_file_links')
            WHERE name='project_id'
        """)
        if cursor.fetchone()[0] == 0:
            print("📝 Adding project_id column...")
            cursor.execute("ALTER TABLE local_file_links ADD COLUMN project_id INTEGER")
            print("   ✓ project_id column added")

            # 4. Asignar todos los archivos existentes al proyecto activo
            cursor.execute("SELECT COUNT(*) FROM local_file_links WHERE project_id IS NULL")
            unassigned_count = cursor.fetchone()[0]

            if unassigned_count > 0:
                print()
                print(f"🔗 Found {unassigned_count} local files without project assignment")

                cursor.execute("SELECT id, name FROM projects WHERE is_active = 1 LIMIT 1")
                active_project = cursor.fetchone()

                if active_project:
                    project_id, project_name = active_project
                    print(f"   Assigning to active project: '{project_name}' (ID: {project_id})")

                    cursor.execute(
                        "UPDATE local_file_links SET project_id = ? WHERE project_id IS NULL",
                        (project_id,)
                    )

                    affected = cursor.rowcount
                    print(f"   ✓ Assigned {affected} files to project '{project_name}'")
                else:
                    print("   ⚠️  No active project found")
                    print("   Files will remain unassigned (project_id = NULL)")
                    print("   They will be assigned to the active project when you create a link")
        else:
            print("⚠️  project_id column already exists, skipping")

        print()

        # 5. Commit changes
        conn.commit()
        print("=" * 60)
        print("✅ Migration completed successfully!")
        print("=" * 60)
        print()
        print("Next steps:")
        print("1. Restart the backend server to apply the changes")
        print("2. New local files will automatically be assigned to the active project")
        print("3. You can now add custom metadata when creating local file links")
        print()

    except Exception as e:
        conn.rollback()
        print()
        print("=" * 60)
        print("❌ Migration failed!")
        print("=" * 60)
        print(f"Error: {e}")
        print()
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        conn.close()


if __name__ == "__main__":
    print()
    print("=" * 60)
    print("LOCAL FILES ENHANCEMENT MIGRATION")
    print("=" * 60)
    print()
    print("This migration will:")
    print("  • Add custom_metadata column (JSON) for user metadata")
    print("  • Add project_id column (INTEGER) to associate files with projects")
    print("  • Assign existing files to the current active project")
    print()

    response = input("Continue? [y/N]: ").strip().lower()
    if response != 'y':
        print("Aborted.")
        sys.exit(0)

    print()
    migrate()
