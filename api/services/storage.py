from typing import Optional, List, BinaryIO, Dict, Union
from enum import Enum

from api.abstractions.storage import FileProviderBase, FileReference
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
    
    def __init__(self, default_provider: Optional[FileProviderBase] = None):
        """Initialize the file storage service.
        
        Args:
            default_provider: Optional default file provider instance. If None, will be created from settings.
        """
        self.logger = get_logger(__name__)
        self._default_provider = default_provider or self._create_provider_from_settings()
        self._providers: Dict[str, FileProviderBase] = {}
        
        # Register the default provider
        provider_type = settings.storage_provider.lower()
        self._providers[provider_type] = self._default_provider
        
        self.logger.info(f"Initialized FileStorageService with default provider: {type(self._default_provider).__name__}")
    
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
    
    def register_provider(self, provider_name: str, provider: FileProviderBase) -> None:
        """Register an additional storage provider.
        
        Args:
            provider_name: Name of the provider (e.g., 'local', 's3')
            provider: File provider instance
        """
        self._providers[provider_name.lower()] = provider
        self.logger.info(f"Registered storage provider: {provider_name}")
    
    def get_provider(self, provider_name: str) -> Optional[FileProviderBase]:
        """Get a registered storage provider by name.
        
        Args:
            provider_name: Name of the provider
            
        Returns:
            File provider instance if found, None otherwise
        """
        return self._providers.get(provider_name.lower())
    
    def _get_provider_for_reference(self, file_ref: Union[str, FileReference]) -> FileProviderBase:
        """Get the appropriate provider for a file reference.
        
        Args:
            file_ref: File reference (string or FileReference object)
            
        Returns:
            File provider instance
            
        Raises:
            ValueError: If provider is not found or registered
        """
        if isinstance(file_ref, str):
            # If it's a plain string, use default provider
            return self._default_provider
        
        if isinstance(file_ref, FileReference):
            provider = self.get_provider(file_ref.provider)
            if provider is None:
                raise ValueError(f"Provider '{file_ref.provider}' is not registered")
            return provider
        
        raise ValueError(f"Invalid file reference type: {type(file_ref)}")
    
    def get_default_provider_name(self) -> str:
        """Get the name of the default storage provider."""
        return settings.storage_provider.lower()
    
    def create_file_reference(self, file_path: str, provider_name: Optional[str] = None) -> FileReference:
        """Create a FileReference for a given path.
        
        Args:
            file_path: The file path
            provider_name: Optional provider name. If None, uses default provider.
            
        Returns:
            FileReference instance
        """
        actual_provider_name = provider_name or self.get_default_provider_name()
        return FileReference(provider=actual_provider_name, reference=file_path)
    
    async def copy_file_reference(self, source_ref: FileReference, destination_path: str, 
                                  destination_provider: Optional[str] = None) -> Optional[FileReference]:
        """Copy a file from one reference to another, potentially across providers.
        
        Args:
            source_ref: Source file reference
            destination_path: Destination file path
            destination_provider: Optional destination provider. If None, uses source provider.
            
        Returns:
            FileReference for the destination if successful, None otherwise
        """
        try:
            # Get source content
            content = await self.get_file(source_ref)
            if content is None:
                self.logger.error(f"Source file not found: {source_ref}")
                return None
            
            # Save to destination
            dest_provider = destination_provider or source_ref.provider
            
            # Convert bytes to BinaryIO
            import io
            file_data = io.BytesIO(content)
            
            dest_ref = await self.save_file(destination_path, file_data, dest_provider)
            
            if dest_ref:
                self.logger.info(f"Successfully copied file from {source_ref} to {dest_ref}")
            
            return dest_ref
            
        except Exception as e:
            self.logger.exception(f"Error copying file from {source_ref} to {destination_path}: {e}")
            return None
    
    async def move_file_reference(self, source_ref: FileReference, destination_path: str,
                                  destination_provider: Optional[str] = None) -> Optional[FileReference]:
        """Move a file from one reference to another, potentially across providers.
        
        Args:
            source_ref: Source file reference
            destination_path: Destination file path
            destination_provider: Optional destination provider. If None, uses source provider.
            
        Returns:
            FileReference for the destination if successful, None otherwise
        """
        # Copy the file first
        dest_ref = await self.copy_file_reference(source_ref, destination_path, destination_provider)
        
        if dest_ref:
            # Delete the source file
            if await self.delete_file(source_ref):
                self.logger.info(f"Successfully moved file from {source_ref} to {dest_ref}")
                return dest_ref
            else:
                # Copy succeeded but delete failed - log warning but return the destination
                self.logger.warning(f"File copied to {dest_ref} but failed to delete source {source_ref}")
                return dest_ref
        
        return None
    
    async def save_file(self, file_path: str, file_data: BinaryIO, provider_name: Optional[str] = None) -> Optional[FileReference]:
        """Save a file to storage using the default provider.
        
        Args:
            file_path: The path where the file should be stored
            file_data: Binary file data
            provider_name: Optional provider name. If None, uses default provider.
            
        Returns:
            FileReference if successful, None otherwise
        """
        # Determine which provider to use
        if provider_name:
            provider = self.get_provider(provider_name)
            if provider is None:
                self.logger.error(f"Provider '{provider_name}' is not registered")
                return None
            actual_provider_name = provider_name.lower()
        else:
            provider = self._default_provider
            actual_provider_name = self.get_default_provider_name()
        
        self.logger.debug(f"Saving file: {file_path} using provider: {actual_provider_name}")
        result = await provider.save_file(file_path, file_data)
        
        if result:
            file_ref = FileReference(provider=actual_provider_name, reference=file_path)
            self.logger.info(f"Successfully saved file: {file_ref}")
            return file_ref
        else:
            self.logger.error(f"Failed to save file: {file_path}")
            return None
    
    async def get_file(self, file_ref: Union[str, FileReference]) -> Optional[bytes]:
        """Retrieve a file from storage.
        
        Args:
            file_ref: File reference (path string or FileReference object)
            
        Returns:
            File contents as bytes if found, None otherwise
        """
        try:
            provider = self._get_provider_for_reference(file_ref)
            
            # Extract the actual file path
            if isinstance(file_ref, FileReference):
                file_path = file_ref.reference
                self.logger.debug(f"Getting file: {file_ref}")
            else:
                file_path = file_ref
                self.logger.debug(f"Getting file: {file_path}")
            
            content = await provider.get_file(file_path)
            
            if content is not None:
                self.logger.debug(f"Successfully retrieved file: {file_ref}")
            else:
                self.logger.debug(f"File not found: {file_ref}")
            
            return content
            
        except ValueError as e:
            self.logger.exception(f"Error getting file {file_ref}: {e}")
            return None
    
    async def delete_file(self, file_ref: Union[str, FileReference]) -> bool:
        """Delete a file from storage.
        
        Args:
            file_ref: File reference (path string or FileReference object)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            provider = self._get_provider_for_reference(file_ref)
            
            # Extract the actual file path
            if isinstance(file_ref, FileReference):
                file_path = file_ref.reference
                self.logger.debug(f"Deleting file: {file_ref}")
            else:
                file_path = file_ref
                self.logger.debug(f"Deleting file: {file_path}")
            
            result = await provider.delete_file(file_path)
            
            if result:
                self.logger.info(f"Successfully deleted file: {file_ref}")
            else:
                self.logger.error(f"Failed to delete file: {file_ref}")
            
            return result
            
        except ValueError as e:
            self.logger.exception(f"Error deleting file {file_ref}: {e}")
            return False
    
    async def file_exists(self, file_ref: Union[str, FileReference]) -> bool:
        """Check if a file exists in storage.
        
        Args:
            file_ref: File reference (path string or FileReference object)
            
        Returns:
            True if file exists, False otherwise
        """
        try:
            provider = self._get_provider_for_reference(file_ref)
            
            # Extract the actual file path
            if isinstance(file_ref, FileReference):
                file_path = file_ref.reference
            else:
                file_path = file_ref
            
            exists = await provider.file_exists(file_path)
            
            self.logger.debug(f"File {'exists' if exists else 'does not exist'}: {file_ref}")
            return exists
            
        except ValueError as e:
            self.logger.exception(f"Error checking file existence {file_ref}: {e}")
            return False
    
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
    
    async def get_file_size(self, file_ref: Union[str, FileReference]) -> Optional[int]:
        """Get the size of a file in bytes.
        
        Args:
            file_ref: File reference (path string or FileReference object)
            
        Returns:
            File size in bytes if found, None otherwise
        """
        try:
            provider = self._get_provider_for_reference(file_ref)
            
            # Extract the actual file path
            if isinstance(file_ref, FileReference):
                file_path = file_ref.reference
            else:
                file_path = file_ref
            
            size = await provider.get_file_size(file_path)
            
            if size is not None:
                self.logger.debug(f"File size for {file_ref}: {size} bytes")
            else:
                self.logger.debug(f"Could not get file size for: {file_ref}")
            
            return size
            
        except ValueError as e:
            self.logger.exception(f"Error getting file size {file_ref}: {e}")
            return None
    
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