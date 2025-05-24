from typing import Optional, List, BinaryIO
from enum import Enum

from api.abstractions.storage import FileProviderBase
from api.infrastructure.storage.local_filesystem import LocalFilesystemFileProvider
from api.integrations.aws.s3_file_provider import AwsS3FileProvider
from api.settings.app_settings import settings
from api.infrastructure.logging import get_logger


class StorageProvider(str, Enum):
    """Available storage providers."""
    LOCAL = "local"
    S3 = "s3"


class FileStorageService:
    """Service for file operations using configurable storage providers."""
    
    def __init__(self, provider: Optional[FileProviderBase] = None):
        """Initialize the file storage service.
        
        Args:
            provider: Optional file provider instance. If None, will be created from settings.
        """
        self.logger = get_logger(__name__)
        self._provider = provider or self._create_provider_from_settings()
        self.logger.info(f"Initialized FileStorageService with {type(self._provider).__name__}")
    
    def _create_provider_from_settings(self) -> FileProviderBase:
        """Create a file provider based on application settings."""
        provider_type = settings.storage_provider.lower()
        
        self.logger.debug(f"Creating storage provider: {provider_type}")
        
        if provider_type == StorageProvider.LOCAL:
            return LocalFilesystemFileProvider(base_path=settings.storage_base_path)
        
        elif provider_type == StorageProvider.S3:
            if not settings.aws_s3_bucket:
                self.logger.error("S3 provider selected but AWS_S3_BUCKET not configured")
                raise ValueError("AWS_S3_BUCKET must be configured when using S3 storage provider")
            
            return AwsS3FileProvider.from_settings()
        
        else:
            self.logger.error(f"Unknown storage provider: {provider_type}")
            raise ValueError(f"Unknown storage provider: {provider_type}. Supported: {[p.value for p in StorageProvider]}")
    
    @classmethod
    def create_from_settings(cls) -> 'FileStorageService':
        """Create a FileStorageService instance using application settings."""
        return cls()
    
    async def save_file(self, file_path: str, file_data: BinaryIO) -> bool:
        """Save a file to storage.
        
        Args:
            file_path: The path where the file should be stored
            file_data: Binary file data
            
        Returns:
            True if successful, False otherwise
        """
        self.logger.debug(f"Saving file: {file_path}")
        result = await self._provider.save_file(file_path, file_data)
        
        if result:
            self.logger.info(f"Successfully saved file: {file_path}")
        else:
            self.logger.error(f"Failed to save file: {file_path}")
        
        return result
    
    async def get_file(self, file_path: str) -> Optional[bytes]:
        """Retrieve a file from storage.
        
        Args:
            file_path: The path of the file to retrieve
            
        Returns:
            File contents as bytes if found, None otherwise
        """
        self.logger.debug(f"Getting file: {file_path}")
        content = await self._provider.get_file(file_path)
        
        if content is not None:
            self.logger.debug(f"Successfully retrieved file: {file_path}")
        else:
            self.logger.debug(f"File not found: {file_path}")
        
        return content
    
    async def delete_file(self, file_path: str) -> bool:
        """Delete a file from storage.
        
        Args:
            file_path: The path of the file to delete
            
        Returns:
            True if successful, False otherwise
        """
        self.logger.debug(f"Deleting file: {file_path}")
        result = await self._provider.delete_file(file_path)
        
        if result:
            self.logger.info(f"Successfully deleted file: {file_path}")
        else:
            self.logger.error(f"Failed to delete file: {file_path}")
        
        return result
    
    async def file_exists(self, file_path: str) -> bool:
        """Check if a file exists in storage.
        
        Args:
            file_path: The path of the file to check
            
        Returns:
            True if file exists, False otherwise
        """
        self.logger.debug(f"Checking if file exists: {file_path}")
        exists = await self._provider.file_exists(file_path)
        
        self.logger.debug(f"File {'exists' if exists else 'does not exist'}: {file_path}")
        return exists
    
    async def list_files(self, directory_path: str = "") -> List[str]:
        """List all files in a directory.
        
        Args:
            directory_path: The directory path to list files from
            
        Returns:
            List of file paths
        """
        self.logger.debug(f"Listing files in directory: {directory_path}")
        files = await self._provider.list_files(directory_path)
        
        self.logger.debug(f"Found {len(files)} files in directory: {directory_path}")
        return files
    
    async def get_file_size(self, file_path: str) -> Optional[int]:
        """Get the size of a file in bytes.
        
        Args:
            file_path: The path of the file
            
        Returns:
            File size in bytes if found, None otherwise
        """
        self.logger.debug(f"Getting file size: {file_path}")
        size = await self._provider.get_file_size(file_path)
        
        if size is not None:
            self.logger.debug(f"File size for {file_path}: {size} bytes")
        else:
            self.logger.debug(f"Could not get file size for: {file_path}")
        
        return size
    
    async def copy_file(self, source_path: str, destination_path: str) -> bool:
        """Copy a file from source to destination.
        
        Args:
            source_path: The source file path
            destination_path: The destination file path
            
        Returns:
            True if successful, False otherwise
        """
        self.logger.debug(f"Copying file from {source_path} to {destination_path}")
        result = await self._provider.copy_file(source_path, destination_path)
        
        if result:
            self.logger.info(f"Successfully copied file from {source_path} to {destination_path}")
        else:
            self.logger.error(f"Failed to copy file from {source_path} to {destination_path}")
        
        return result
    
    async def move_file(self, source_path: str, destination_path: str) -> bool:
        """Move a file from source to destination.
        
        Args:
            source_path: The source file path
            destination_path: The destination file path
            
        Returns:
            True if successful, False otherwise
        """
        self.logger.debug(f"Moving file from {source_path} to {destination_path}")
        result = await self._provider.move_file(source_path, destination_path)
        
        if result:
            self.logger.info(f"Successfully moved file from {source_path} to {destination_path}")
        else:
            self.logger.error(f"Failed to move file from {source_path} to {destination_path}")
        
        return result
    
    def get_provider_info(self) -> dict:
        """Get information about the current storage provider.
        
        Returns:
            Dictionary with provider information
        """
        provider_class = type(self._provider).__name__
        provider_type = settings.storage_provider
        
        info = {
            "provider_type": provider_type,
            "provider_class": provider_class,
            "max_file_size": settings.max_file_size,
        }
        
        # Add provider-specific info
        if provider_type == StorageProvider.LOCAL:
            info["base_path"] = settings.storage_base_path
        elif provider_type == StorageProvider.S3:
            info["bucket"] = settings.aws_s3_bucket
            info["prefix"] = settings.aws_s3_prefix
            info["region"] = settings.aws_region
        
        return info


# Global service instance - lazy loaded
_storage_service: Optional[FileStorageService] = None


def get_storage_service() -> FileStorageService:
    """Get the global storage service instance."""
    global _storage_service
    
    if _storage_service is None:
        _storage_service = FileStorageService.create_from_settings()
    
    return _storage_service


def reset_storage_service() -> None:
    """Reset the global storage service instance (useful for testing)."""
    global _storage_service
    _storage_service = None