import os
from typing import Optional


class AppSettings:
    """Singleton class for managing application settings."""
    
    _instance: Optional['AppSettings'] = None
    _initialized: bool = False
    
    def __new__(cls) -> 'AppSettings':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self) -> None:
        if not self._initialized:
            self._load_settings()
            self._initialized = True
    
    def _load_settings(self) -> None:
        """Load settings from environment variables."""
        # OpenAI settings
        self.openai_api_key = os.getenv("OPENAI_API_KEY", "")
        self.openai_model = os.getenv("OPENAI_MODEL", "gpt-4")
        
        # File storage settings
        self.storage_base_path = os.getenv("STORAGE_BASE_PATH", "uploads")
        self.max_file_size = int(os.getenv("MAX_FILE_SIZE", "10485760"))  # 10MB default
        
        # Server settings
        self.host = os.getenv("HOST", "0.0.0.0")
        self.port = int(os.getenv("PORT", "8000"))
        self.debug = os.getenv("DEBUG", "false").lower() == "true"
        
        # Redis settings (if using Redis for collections)
        self.redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
        self.redis_db = int(os.getenv("REDIS_DB", "0"))
        
        # CORS settings
        self.cors_origins = os.getenv("CORS_ORIGINS", "*").split(",")
        
        # Security settings
        self.secret_key = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
        
        # Environment
        self.environment = os.getenv("ENVIRONMENT", "development")
        
        # AWS settings
        self.aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID")
        self.aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")
        self.aws_region = os.getenv("AWS_REGION", "us-east-1")
        self.aws_s3_bucket = os.getenv("AWS_S3_BUCKET")
        self.aws_s3_prefix = os.getenv("AWS_S3_PREFIX", "")
        
        # Logging settings
        self.log_level = os.getenv("LOG_LEVEL", "INFO")
        self.log_file = os.getenv("LOG_FILE")
    
    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.environment.lower() == "production"
    
    @property
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.environment.lower() == "development"
    
    def get(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """Get a setting value by key, with optional default."""
        return getattr(self, key, default)
    
    def reload(self) -> None:
        """Reload settings from environment variables."""
        self._load_settings()


# Global settings instance
settings = AppSettings()
