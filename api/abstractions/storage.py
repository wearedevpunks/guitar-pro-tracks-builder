from abc import ABC, abstractmethod
from typing import BinaryIO, Optional, List
from pydantic import BaseModel, Field


class FileProviderBase(ABC):
    """Abstract base class for file storage providers."""
    
    @abstractmethod
    async def save_file(self, file_path: str, file_data: BinaryIO) -> bool:
        """Save a file to the storage provider.
        
        Args:
            file_path: The path where the file should be stored
            file_data: Binary file data
            
        Returns:
            True if successful, False otherwise
        """
        pass
    
    @abstractmethod
    async def get_file(self, file_path: str) -> Optional[bytes]:
        """Retrieve a file from the storage provider.
        
        Args:
            file_path: The path of the file to retrieve
            
        Returns:
            File contents as bytes if found, None otherwise
        """
        pass
    
    @abstractmethod
    async def delete_file(self, file_path: str) -> bool:
        """Delete a file from the storage provider.
        
        Args:
            file_path: The path of the file to delete
            
        Returns:
            True if successful, False otherwise
        """
        pass
    
    @abstractmethod
    async def file_exists(self, file_path: str) -> bool:
        """Check if a file exists in the storage provider.
        
        Args:
            file_path: The path of the file to check
            
        Returns:
            True if file exists, False otherwise
        """
        pass
    
    @abstractmethod
    async def list_files(self, directory_path: str = "") -> List[str]:
        """List all files in a directory.
        
        Args:
            directory_path: The directory path to list files from
            
        Returns:
            List of file paths
        """
        pass
    
    @abstractmethod
    async def get_file_size(self, file_path: str) -> Optional[int]:
        """Get the size of a file in bytes.
        
        Args:
            file_path: The path of the file
            
        Returns:
            File size in bytes if found, None otherwise
        """
        pass
    
    @abstractmethod
    async def copy_file(self, source_path: str, destination_path: str) -> bool:
        """Copy a file from source to destination.
        
        Args:
            source_path: The source file path
            destination_path: The destination file path
            
        Returns:
            True if successful, False otherwise
        """
        pass
    
    @abstractmethod
    async def move_file(self, source_path: str, destination_path: str) -> bool:
        """Move a file from source to destination.
        
        Args:
            source_path: The source file path
            destination_path: The destination file path
            
        Returns:
            True if successful, False otherwise
        """
        pass
    
    @abstractmethod
    async def get_file_download_url(self, file_path: str, expiration_seconds: int = 3600) -> Optional[str]:
        """Get a downloadable URL for a file.
        
        Args:
            file_path: The path of the file
            expiration_seconds: URL expiration time in seconds (default: 1 hour)
            
        Returns:
            Download URL if successful, None otherwise
        """
        pass


class FileReference(BaseModel):
    """Reference to a file stored in a storage provider."""

    provider: str = Field(..., description="Storage provider name (e.g., 'local', 's3')")
    reference: str = Field(..., description="Provider-specific file reference/path")

    class Config:
        json_schema_extra = {
            "example": {
                "provider": "s3",
                "reference": "uploads/songs/master_of_puppets.gp5"
            }
        }

    def __str__(self) -> str:
        """String representation of the file reference."""
        return f"{self.provider}://{self.reference}"

    def __repr__(self) -> str:
        """Detailed string representation."""
        return f"FileReference(provider='{self.provider}', reference='{self.reference}')"

    @classmethod
    def from_string(cls, file_ref: str) -> 'FileReference':
        """Create a FileReference from a string in format 'provider://reference'.

        Args:
            file_ref: String in format 'provider://reference'

        Returns:
            FileReference instance

        Raises:
            ValueError: If the string format is invalid
        """
        if '://' not in file_ref:
            raise ValueError("File reference must be in format 'provider://reference'")

        provider, reference = file_ref.split('://', 1)

        if not provider or not reference:
            raise ValueError("Both provider and reference must be non-empty")

        return cls(provider=provider, reference=reference)
