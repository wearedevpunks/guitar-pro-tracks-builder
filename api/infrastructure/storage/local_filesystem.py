import os
import shutil
from pathlib import Path
from typing import BinaryIO, Optional, List
import aiofiles
import aiofiles.os

from api.abstractions.storage import FileProviderBase


class LocalFilesystemFileProvider(FileProviderBase):
    """Local filesystem implementation of FileProviderBase."""
    
    def __init__(self, base_path: str = "uploads"):
        """Initialize the local filesystem provider.
        
        Args:
            base_path: Base directory for file storage
        """
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
    
    def _get_full_path(self, file_path: str) -> Path:
        """Get the full filesystem path for a given file path."""
        return self.base_path / file_path
    
    async def save_file(self, file_path: str, file_data: BinaryIO) -> bool:
        """Save a file to the local filesystem."""
        try:
            full_path = self._get_full_path(file_path)
            full_path.parent.mkdir(parents=True, exist_ok=True)
            
            async with aiofiles.open(full_path, 'wb') as f:
                content = file_data.read()
                await f.write(content)
            return True
        except Exception:
            return False
    
    async def get_file(self, file_path: str) -> Optional[bytes]:
        """Retrieve a file from the local filesystem."""
        try:
            full_path = self._get_full_path(file_path)
            if not full_path.exists():
                return None
            
            async with aiofiles.open(full_path, 'rb') as f:
                return await f.read()
        except Exception:
            return None
    
    async def delete_file(self, file_path: str) -> bool:
        """Delete a file from the local filesystem."""
        try:
            full_path = self._get_full_path(file_path)
            if full_path.exists():
                await aiofiles.os.remove(full_path)
            return True
        except Exception:
            return False
    
    async def file_exists(self, file_path: str) -> bool:
        """Check if a file exists in the local filesystem."""
        try:
            full_path = self._get_full_path(file_path)
            return full_path.exists()
        except Exception:
            return False
    
    async def list_files(self, directory_path: str = "") -> List[str]:
        """List all files in a directory."""
        try:
            full_path = self._get_full_path(directory_path)
            if not full_path.exists() or not full_path.is_dir():
                return []
            
            files = []
            for item in full_path.rglob('*'):
                if item.is_file():
                    relative_path = item.relative_to(self.base_path)
                    files.append(str(relative_path))
            return files
        except Exception:
            return []
    
    async def get_file_size(self, file_path: str) -> Optional[int]:
        """Get the size of a file in bytes."""
        try:
            full_path = self._get_full_path(file_path)
            if not full_path.exists():
                return None
            
            stat_result = await aiofiles.os.stat(full_path)
            return stat_result.st_size
        except Exception:
            return None
    
    async def copy_file(self, source_path: str, destination_path: str) -> bool:
        """Copy a file from source to destination."""
        try:
            source_full_path = self._get_full_path(source_path)
            dest_full_path = self._get_full_path(destination_path)
            
            if not source_full_path.exists():
                return False
            
            dest_full_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source_full_path, dest_full_path)
            return True
        except Exception:
            return False
    
    async def move_file(self, source_path: str, destination_path: str) -> bool:
        """Move a file from source to destination."""
        try:
            source_full_path = self._get_full_path(source_path)
            dest_full_path = self._get_full_path(destination_path)
            
            if not source_full_path.exists():
                return False
            
            dest_full_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(source_full_path, dest_full_path)
            return True
        except Exception:
            return False
    
    async def get_file_download_url(self, file_path: str, expiration_seconds: int = 3600) -> Optional[str]:
        """Get a downloadable URL for a file.
        
        Local filesystem provider does not support downloadable URLs.
        """
        raise NotImplementedError("Local filesystem provider does not support downloadable URLs")