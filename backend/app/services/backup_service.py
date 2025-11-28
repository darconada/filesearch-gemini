import os
import subprocess
import shutil
from pathlib import Path
from typing import List, Optional
from datetime import datetime

class BackupService:
    def __init__(self):
        self.root_dir = Path(__file__).parent.parent.parent.parent
        self.backup_dir = self.root_dir / "backups"
        self.script_path = self.root_dir / "manage_backup.sh"

    def list_backups(self) -> List[dict]:
        """List all available backup files"""
        if not self.backup_dir.exists():
            return []

        backups = []
        for file_path in self.backup_dir.glob("*.tar.gz"):
            stat = file_path.stat()
            backups.append({
                "filename": file_path.name,
                "size": stat.st_size,
                "created_at": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "path": str(file_path)
            })
        
        # Sort by creation time desc
        return sorted(backups, key=lambda x: x["created_at"], reverse=True)

    def create_backup(self) -> dict:
        """Execute backup script to create a new backup"""
        try:
            result = subprocess.run(
                [str(self.script_path), "backup"],
                cwd=str(self.root_dir),
                capture_output=True,
                text=True,
                check=True
            )
            
            # Find the newest file
            backups = self.list_backups()
            if not backups:
                raise Exception("Backup script ran but no file was created")
                
            return backups[0]
            
        except subprocess.CalledProcessError as e:
            raise Exception(f"Backup failed: {e.stderr}")

    def restore_backup(self, filename: str) -> bool:
        """Restore from a specific backup file"""
        backup_path = self.backup_dir / filename
        if not backup_path.exists():
            raise FileNotFoundError(f"Backup file {filename} not found")

        try:
            # Run with --force to skip confirmation
            subprocess.run(
                [str(self.script_path), "restore", str(backup_path), "--force"],
                cwd=str(self.root_dir),
                capture_output=True,
                text=True,
                check=True
            )
            return True
        except subprocess.CalledProcessError as e:
            raise Exception(f"Restore failed: {e.stderr}")

    def save_uploaded_backup(self, file_content: bytes, filename: str) -> str:
        """Save an uploaded backup file to the backups directory"""
        if not self.backup_dir.exists():
            self.backup_dir.mkdir(parents=True)
            
        # Ensure filename is safe
        safe_filename = Path(filename).name
        target_path = self.backup_dir / safe_filename
        
        target_path.write_bytes(file_content)
        return safe_filename

    def get_backup_path(self, filename: str) -> Path:
        """Get absolute path to a backup file"""
        path = self.backup_dir / filename
        if not path.exists():
            raise FileNotFoundError(f"Backup file {filename} not found")
        return path

backup_service = BackupService()
