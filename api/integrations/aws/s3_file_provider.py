import boto3
from botocore.exceptions import ClientError, NoCredentialsError, BotoCoreError
from typing import BinaryIO, Optional, List

from api.abstractions.storage import FileProviderBase
from api.settings.app_settings import settings
from api.infrastructure.logging import get_logger


class AwsS3FileProvider(FileProviderBase):
    """AWS S3 implementation of FileProviderBase."""
    
    def __init__(self, bucket_name: Optional[str] = None, prefix: Optional[str] = None, region_name: Optional[str] = None):
        self.logger = get_logger(__name__)
        """Initialize the AWS S3 provider.
        
        Args:
            bucket_name: S3 bucket name (defaults to AWS_S3_BUCKET env var)
            prefix: Optional prefix for all file paths (defaults to AWS_S3_PREFIX env var)
            region_name: AWS region name (defaults to AWS_REGION env var)
        """
        # Use settings if parameters not provided
        self.bucket_name = bucket_name or settings.aws_s3_bucket
        if not self.bucket_name:
            self.logger.error("S3 bucket name not provided in parameters or AWS_S3_BUCKET env var")
            raise ValueError("S3 bucket name must be provided either as parameter or AWS_S3_BUCKET env var")
        
        prefix = prefix if prefix is not None else settings.aws_s3_prefix
        self.prefix = prefix.rstrip('/') + '/' if prefix else ''
        
        # Use region from settings if not provided
        region = region_name or settings.aws_region
        
        self.logger.info(f"Initializing S3 provider for bucket '{self.bucket_name}' in region '{region}' with prefix '{self.prefix}'")
        
        # Initialize S3 client with credentials from settings if available
        session_kwargs = {}
        if settings.aws_access_key_id and settings.aws_secret_access_key:
            session_kwargs.update({
                'aws_access_key_id': settings.aws_access_key_id,
                'aws_secret_access_key': settings.aws_secret_access_key,
                'region_name': region
            })
        elif region:
            session_kwargs['region_name'] = region
            
        session = boto3.Session(**session_kwargs)
        self.s3_client = session.client('s3')
        
        # Verify bucket access
        try:
            self.s3_client.head_bucket(Bucket=self.bucket_name)
            self.logger.info(f"Successfully verified access to S3 bucket '{self.bucket_name}'")
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == '404':
                self.logger.exception(f"S3 bucket '{self.bucket_name}' does not exist")
                raise ValueError(f"Bucket '{self.bucket_name}' does not exist")
            elif error_code == '403':
                self.logger.exception(f"Access denied to S3 bucket '{self.bucket_name}'")
                raise ValueError(f"Access denied to bucket '{self.bucket_name}'")
            else:
                self.logger.exception(f"Error accessing S3 bucket '{self.bucket_name}': {e}")
                raise ValueError(f"Error accessing bucket '{self.bucket_name}': {e}")
        except NoCredentialsError as e:
            self.logger.exception("AWS credentials not found")
            raise ValueError("AWS credentials not found. Please configure AWS credentials.") from e
        except BotoCoreError as e:
            self.logger.exception(f"AWS configuration error: {e}")
            raise ValueError(f"AWS configuration error: {e}") from e
    
    @classmethod
    def from_settings(cls) -> 'AwsS3FileProvider':
        """Create an S3 file provider instance using app settings."""
        return cls()
    
    def _get_s3_key(self, file_path: str) -> str:
        """Get the full S3 key for a given file path."""
        return self.prefix + file_path.lstrip('/')
    
    async def save_file(self, file_path: str, file_data: BinaryIO) -> bool:
        """Save a file to S3."""
        s3_key = self._get_s3_key(file_path)
        self.logger.debug(f"Saving file to S3: {s3_key}")
        
        try:
            # Read file data into memory
            content = file_data.read()
            if hasattr(file_data, 'seek'):
                file_data.seek(0)  # Reset file pointer
            
            # Upload to S3
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=s3_key,
                Body=content
            )
            self.logger.info(f"Successfully saved file to S3: {s3_key}")
            return True
        except ClientError as e:
            self.logger.exception(f"AWS error saving file {s3_key}: {e}")
            return False
        except (IOError, OSError) as e:
            self.logger.exception(f"File I/O error saving {s3_key}: {e}")
            return False
        except BotoCoreError as e:
            self.logger.exception(f"AWS configuration error saving {s3_key}: {e}")
            return False
        except Exception as e:
            self.logger.exception(f"Unexpected error saving file {s3_key}: {e}")
            return False
    
    async def get_file(self, file_path: str) -> Optional[bytes]:
        """Retrieve a file from S3."""
        s3_key = self._get_s3_key(file_path)
        self.logger.debug(f"Getting file from S3: {s3_key}")
        
        try:
            response = self.s3_client.get_object(
                Bucket=self.bucket_name,
                Key=s3_key
            )
            content = response['Body'].read()
            self.logger.debug(f"Successfully retrieved file from S3: {s3_key}")
            return content
        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchKey':
                self.logger.debug(f"File not found in S3: {s3_key}")
                return None
            self.logger.exception(f"AWS error getting file {s3_key}: {e}")
            return None
        except BotoCoreError as e:
            self.logger.exception(f"AWS configuration error getting {s3_key}: {e}")
            return None
        except Exception as e:
            self.logger.exception(f"Unexpected error getting file {s3_key}: {e}")
            return None
    
    async def delete_file(self, file_path: str) -> bool:
        """Delete a file from S3."""
        s3_key = self._get_s3_key(file_path)
        self.logger.debug(f"Deleting file from S3: {s3_key}")
        
        try:
            self.s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=s3_key
            )
            self.logger.info(f"Successfully deleted file from S3: {s3_key}")
            return True
        except ClientError as e:
            self.logger.exception(f"AWS error deleting file {s3_key}: {e}")
            return False
        except BotoCoreError as e:
            self.logger.exception(f"AWS configuration error deleting {s3_key}: {e}")
            return False
        except Exception as e:
            self.logger.exception(f"Unexpected error deleting file {s3_key}: {e}")
            return False
    
    async def file_exists(self, file_path: str) -> bool:
        """Check if a file exists in S3."""
        s3_key = self._get_s3_key(file_path)
        self.logger.debug(f"Checking if file exists in S3: {s3_key}")
        
        try:
            self.s3_client.head_object(
                Bucket=self.bucket_name,
                Key=s3_key
            )
            self.logger.debug(f"File exists in S3: {s3_key}")
            return True
        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                self.logger.debug(f"File does not exist in S3: {s3_key}")
                return False
            self.logger.exception(f"AWS error checking file existence {s3_key}: {e}")
            return False
        except BotoCoreError as e:
            self.logger.exception(f"AWS configuration error checking {s3_key}: {e}")
            return False
        except Exception as e:
            self.logger.exception(f"Unexpected error checking file existence {s3_key}: {e}")
            return False
    
    async def list_files(self, directory_path: str = "") -> List[str]:
        """List all files in a directory (S3 prefix)."""
        prefix = self._get_s3_key(directory_path)
        if directory_path and not prefix.endswith('/'):
            prefix += '/'
        
        self.logger.debug(f"Listing files in S3 with prefix: {prefix}")
        
        try:
            files = []
            paginator = self.s3_client.get_paginator('list_objects_v2')
            
            for page in paginator.paginate(Bucket=self.bucket_name, Prefix=prefix):
                if 'Contents' in page:
                    for obj in page['Contents']:
                        # Remove the prefix to get relative path
                        relative_path = obj['Key']
                        if self.prefix and relative_path.startswith(self.prefix):
                            relative_path = relative_path[len(self.prefix):]
                        files.append(relative_path)
            
            self.logger.debug(f"Found {len(files)} files in S3 with prefix: {prefix}")
            return files
        except ClientError as e:
            self.logger.exception(f"AWS error listing files with prefix {prefix}: {e}")
            return []
        except BotoCoreError as e:
            self.logger.exception(f"AWS configuration error listing files: {e}")
            return []
        except Exception as e:
            self.logger.exception(f"Unexpected error listing files with prefix {prefix}: {e}")
            return []
    
    async def get_file_size(self, file_path: str) -> Optional[int]:
        """Get the size of a file in bytes."""
        s3_key = self._get_s3_key(file_path)
        self.logger.debug(f"Getting file size from S3: {s3_key}")
        
        try:
            response = self.s3_client.head_object(
                Bucket=self.bucket_name,
                Key=s3_key
            )
            size = response['ContentLength']
            self.logger.debug(f"File size for {s3_key}: {size} bytes")
            return size
        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                self.logger.debug(f"File not found in S3: {s3_key}")
                return None
            self.logger.exception(f"AWS error getting file size {s3_key}: {e}")
            return None
        except BotoCoreError as e:
            self.logger.exception(f"AWS configuration error getting file size {s3_key}: {e}")
            return None
        except Exception as e:
            self.logger.exception(f"Unexpected error getting file size {s3_key}: {e}")
            return None
    
    async def copy_file(self, source_path: str, destination_path: str) -> bool:
        """Copy a file from source to destination within S3."""
        source_key = self._get_s3_key(source_path)
        dest_key = self._get_s3_key(destination_path)
        self.logger.debug(f"Copying file in S3 from {source_key} to {dest_key}")
        
        try:
            # Check if source exists
            if not await self.file_exists(source_path):
                self.logger.warning(f"Source file does not exist: {source_key}")
                return False
            
            copy_source = {
                'Bucket': self.bucket_name,
                'Key': source_key
            }
            
            self.s3_client.copy_object(
                CopySource=copy_source,
                Bucket=self.bucket_name,
                Key=dest_key
            )
            self.logger.info(f"Successfully copied file in S3 from {source_key} to {dest_key}")
            return True
        except ClientError as e:
            self.logger.exception(f"AWS error copying file from {source_key} to {dest_key}: {e}")
            return False
        except BotoCoreError as e:
            self.logger.exception(f"AWS configuration error copying file: {e}")
            return False
        except Exception as e:
            self.logger.exception(f"Unexpected error copying file from {source_key} to {dest_key}: {e}")
            return False
    
    async def move_file(self, source_path: str, destination_path: str) -> bool:
        """Move a file from source to destination within S3."""
        source_key = self._get_s3_key(source_path)
        dest_key = self._get_s3_key(destination_path)
        self.logger.debug(f"Moving file in S3 from {source_key} to {dest_key}")
        
        try:
            # Copy the file first
            if await self.copy_file(source_path, destination_path):
                # If copy succeeded, delete the source
                if await self.delete_file(source_path):
                    self.logger.info(f"Successfully moved file in S3 from {source_key} to {dest_key}")
                    return True
                else:
                    self.logger.warning(f"File copied but failed to delete source: {source_key}")
                    return False
            return False
        except Exception as e:
            self.logger.exception(f"Unexpected error moving file from {source_key} to {dest_key}: {e}")
            return False