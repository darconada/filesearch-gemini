"""Servicio para navegación de archivos del servidor"""
import os
import mimetypes
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional
from app.models.file_browser import FileSystemItem, DirectoryListing
import logging

logger = logging.getLogger(__name__)


class FileBrowserService:
    """Servicio para navegación segura del sistema de archivos del servidor"""

    # Directorios bloqueados por seguridad
    BLOCKED_PATHS = {
        '/etc',
        '/root',
        '/sys',
        '/proc',
        '/dev',
        '/boot',
        '/var/log',
        '/usr/bin',
        '/usr/sbin',
        '/sbin',
        '/bin'
    }

    def __init__(self):
        pass

    def _is_path_safe(self, path: Path) -> bool:
        """Verificar que la ruta es segura para navegar"""
        try:
            # Resolver ruta absoluta
            resolved = path.resolve()
            
            # Verificar que no está en rutas bloqueadas
            for blocked in self.BLOCKED_PATHS:
                blocked_path = Path(blocked).resolve()
                try:
                    resolved.relative_to(blocked_path)
                    logger.warning(f"Blocked access to sensitive path: {resolved}")
                    return False
                except ValueError:
                    # No es relativo a la ruta bloqueada, continuar
                    continue
            
            return True
        except Exception as e:
            logger.error(f"Error checking path safety: {e}")
            return False

    def list_directory(self, directory_path: Optional[str] = None) -> DirectoryListing:
        """
        Listar contenido de un directorio
        
        Args:
            directory_path: Ruta del directorio a listar. Si es None, usa el home del usuario
            
        Returns:
            DirectoryListing con el contenido del directorio
        """
        # Si no se especifica ruta, usar el home del usuario
        if directory_path is None:
            directory_path = str(Path.home())
        
        # Convertir a Path y resolver
        dir_path = Path(directory_path).expanduser().resolve()
        
        # Verificar que es seguro
        if not self._is_path_safe(dir_path):
            raise PermissionError(f"Access to path {directory_path} is not allowed")
        
        # Verificar que existe y es un directorio
        if not dir_path.exists():
            raise FileNotFoundError(f"Directory does not exist: {directory_path}")
        
        if not dir_path.is_dir():
            raise NotADirectoryError(f"Path is not a directory: {directory_path}")
        
        # Obtener directorio padre
        parent_path = str(dir_path.parent) if dir_path.parent != dir_path else None
        
        # Listar contenido
        items = []
        try:
            for entry in sorted(dir_path.iterdir(), key=lambda x: (not x.is_dir(), x.name.lower())):
                try:
                    stat = entry.stat()
                    
                    # Determinar si es legible
                    is_readable = os.access(entry, os.R_OK)
                    
                    item = FileSystemItem(
                        name=entry.name,
                        path=str(entry),
                        is_directory=entry.is_dir(),
                        size=stat.st_size if entry.is_file() else None,
                        modified_time=datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc),
                        mime_type=mimetypes.guess_type(str(entry))[0] if entry.is_file() else None,
                        is_readable=is_readable
                    )
                    items.append(item)
                    
                except (PermissionError, OSError) as e:
                    # Si no se puede acceder a un item específico, continuar
                    logger.debug(f"Could not access {entry}: {e}")
                    continue
                    
        except PermissionError as e:
            raise PermissionError(f"Permission denied to read directory: {directory_path}")
        
        logger.info(f"Listed {len(items)} items in {dir_path}")
        
        return DirectoryListing(
            current_path=str(dir_path),
            parent_path=parent_path,
            items=items
        )

    def get_file_info(self, file_path: str) -> FileSystemItem:
        """
        Obtener información de un archivo específico
        
        Args:
            file_path: Ruta del archivo
            
        Returns:
            FileSystemItem con la información del archivo
        """
        path = Path(file_path).expanduser().resolve()
        
        # Verificar que es seguro
        if not self._is_path_safe(path):
            raise PermissionError(f"Access to path {file_path} is not allowed")
        
        # Verificar que existe
        if not path.exists():
            raise FileNotFoundError(f"File does not exist: {file_path}")
        
        stat = path.stat()
        is_readable = os.access(path, os.R_OK)
        
        return FileSystemItem(
            name=path.name,
            path=str(path),
            is_directory=path.is_dir(),
            size=stat.st_size if path.is_file() else None,
            modified_time=datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc),
            mime_type=mimetypes.guess_type(str(path))[0] if path.is_file() else None,
            is_readable=is_readable
        )


# Instancia global del servicio
file_browser_service = FileBrowserService()
