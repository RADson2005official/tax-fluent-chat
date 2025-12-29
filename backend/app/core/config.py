"""
Centralized configuration management using Pydantic Settings.

This module provides:
- Environment variable validation at startup
- Type-safe configuration access
- Default values with override capability
- Automatic .env file loading
"""
from functools import lru_cache
from typing import List, Optional
from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings with environment variable validation.
    
    All settings can be overridden via environment variables.
    Sensitive defaults are only used in development mode.
    """
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )
    
    # ==========================================================================
    # Application Settings
    # ==========================================================================
    APP_NAME: str = "Tax Filing System API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = Field(default=False, description="Enable debug mode")
    ENVIRONMENT: str = Field(default="development", description="deployment environment")
    
    # ==========================================================================
    # Server Settings
    # ==========================================================================
    HOST: str = Field(default="0.0.0.0", description="Server host")
    PORT: int = Field(default=8000, description="Server port")
    RELOAD: bool = Field(default=True, description="Enable auto-reload in development")
    
    # ==========================================================================
    # Database Settings
    # ==========================================================================
    DATABASE_URL: str = Field(
        default="postgresql://taxagent:taxagent_secure_password_2024@localhost:5432/tax_filing_db",
        description="PostgreSQL database URL"
    )
    DB_POOL_SIZE: int = Field(default=10, description="Database connection pool size")
    DB_MAX_OVERFLOW: int = Field(default=20, description="Max connections beyond pool size")
    DB_POOL_RECYCLE: int = Field(default=3600, description="Recycle connections after N seconds")
    DB_ECHO: bool = Field(default=False, description="Echo SQL statements")
    
    # ==========================================================================
    # Security Settings
    # ==========================================================================
    SECRET_KEY: str = Field(
        default="dev_secret_key_change_in_production_32_chars_minimum",
        description="JWT signing secret key"
    )
    ALGORITHM: str = Field(default="HS256", description="JWT algorithm")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, description="JWT expiration in minutes")
    ENCRYPTION_KEY: Optional[str] = Field(
        default=None,
        description="Fernet encryption key for sensitive data (SSN, etc.)"
    )
    
    # ==========================================================================
    # CORS Settings
    # ==========================================================================
    CORS_ORIGINS: List[str] = Field(
        default=[
            "http://localhost:5173",
            "http://localhost:3000",
            "http://127.0.0.1:5173",
            "http://127.0.0.1:3000",
            "http://localhost:8080",
            "http://127.0.0.1:8080",
        ],
        description="Allowed CORS origins"
    )
    CORS_ALLOW_CREDENTIALS: bool = Field(default=True)
    CORS_ALLOW_METHODS: List[str] = Field(default=["*"])
    CORS_ALLOW_HEADERS: List[str] = Field(default=["*"])
    
    # ==========================================================================
    # LLM Provider Settings
    # ==========================================================================
    OPENAI_API_KEY: Optional[str] = Field(default=None, description="OpenAI API key")
    ANTHROPIC_API_KEY: Optional[str] = Field(default=None, description="Anthropic API key")
    GOOGLE_API_KEY: Optional[str] = Field(default=None, description="Google AI API key")
    XAI_API_KEY: Optional[str] = Field(default=None, description="X.AI API key")
    
    # Default LLM provider
    DEFAULT_LLM_PROVIDER: str = Field(default="openai", description="Default LLM provider")
    DEFAULT_LLM_MODEL: str = Field(default="gpt-4o-mini", description="Default LLM model")
    
    # ==========================================================================
    # RAG Settings (pgvector)
    # ==========================================================================
    EMBEDDING_MODEL: str = Field(
        default="all-MiniLM-L6-v2",
        description="Sentence transformer model for embeddings"
    )
    EMBEDDING_DIMENSION: int = Field(
        default=384,
        description="Vector embedding dimension (must match model output)"
    )
    RAG_TOP_K: int = Field(
        default=3,
        description="Number of documents to retrieve for RAG queries"
    )
    
    # ==========================================================================
    # Logging Settings
    # ==========================================================================
    LOG_LEVEL: str = Field(default="INFO", description="Logging level")
    LOG_FORMAT: str = Field(default="json", description="Log format (json or text)")
    
    # ==========================================================================
    # Validators
    # ==========================================================================
    
    @field_validator("SECRET_KEY")
    @classmethod
    def validate_secret_key(cls, v: str, info) -> str:
        """Warn if using default secret key in non-development environment."""
        if "dev_secret_key" in v:
            import warnings
            warnings.warn(
                "Using default SECRET_KEY. Set a secure SECRET_KEY in production!",
                UserWarning,
                stacklevel=2
            )
        if len(v) < 32:
            raise ValueError("SECRET_KEY must be at least 32 characters")
        return v
    
    @field_validator("ENVIRONMENT")
    @classmethod
    def validate_environment(cls, v: str) -> str:
        """Validate environment is one of allowed values."""
        allowed = {"development", "staging", "production", "testing"}
        if v.lower() not in allowed:
            raise ValueError(f"ENVIRONMENT must be one of: {allowed}")
        return v.lower()
    
    @model_validator(mode="after")
    def validate_production_settings(self) -> "Settings":
        """Ensure production has proper security settings."""
        if self.ENVIRONMENT == "production":
            if "dev_secret_key" in self.SECRET_KEY:
                raise ValueError("Cannot use default SECRET_KEY in production")
            if self.DEBUG:
                raise ValueError("DEBUG must be False in production")
            if "*" in self.CORS_ORIGINS:
                raise ValueError("Cannot use wildcard CORS origins in production")
        return self
    
    @model_validator(mode="after")
    def generate_encryption_key_if_needed(self) -> "Settings":
        """Generate encryption key if not provided (dev only)."""
        if self.ENCRYPTION_KEY is None:
            if self.ENVIRONMENT == "production":
                raise ValueError("ENCRYPTION_KEY must be set in production")
            from cryptography.fernet import Fernet
            self.ENCRYPTION_KEY = Fernet.generate_key().decode()
            import warnings
            warnings.warn(
                "Generated new ENCRYPTION_KEY. Set a persistent key to avoid data loss!",
                UserWarning,
                stacklevel=2
            )
        return self
    
    # ==========================================================================
    # Computed Properties
    # ==========================================================================
    
    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.ENVIRONMENT == "development"
    
    @property
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return self.ENVIRONMENT == "production"
    
    @property
    def database_url_async(self) -> str:
        """Get async database URL (for future async support)."""
        return self.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.
    
    Uses lru_cache to ensure settings are only loaded once.
    
    Returns:
        Settings: Application settings instance
    """
    return Settings()


# Export singleton for convenience
settings = get_settings()
