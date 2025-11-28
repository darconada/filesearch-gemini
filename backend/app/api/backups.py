from fastapi import APIRouter, HTTPException, UploadFile, File, BackgroundTasks
from fastapi.responses import FileResponse
from app.services.backup_service import backup_service
from typing import List
from pydantic import BaseModel

router = APIRouter()

class BackupInfo(BaseModel):
    filename: str
    size: int
    created_at: str

@router.get("", response_model=List[BackupInfo])
async def list_backups():
    """List all available backups"""
    return backup_service.list_backups()

@router.post("", response_model=BackupInfo)
async def create_backup():
    """Create a new backup"""
    try:
        return backup_service.create_backup()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{filename}/restore")
async def restore_backup(filename: str):
    """Restore a specific backup"""
    try:
        backup_service.restore_backup(filename)
        return {"message": f"Backup {filename} restored successfully"}
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Backup not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{filename}/download")
async def download_backup(filename: str):
    """Download a backup file"""
    try:
        path = backup_service.get_backup_path(filename)
        return FileResponse(
            path=path, 
            filename=filename,
            media_type="application/gzip"
        )
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Backup not found")

@router.post("/upload")
async def upload_backup(file: UploadFile = File(...)):
    """Upload a backup file"""
    if not file.filename.endswith(".tar.gz"):
        raise HTTPException(status_code=400, detail="Invalid file format. Must be .tar.gz")
        
    try:
        content = await file.read()
        filename = backup_service.save_uploaded_backup(content, file.filename)
        return {"message": "Backup uploaded successfully", "filename": filename}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
