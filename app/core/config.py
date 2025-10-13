"""
Application configuration management
"""

from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    """Application settings with environment variable support"""
    
    # Application settings
    APP_NAME: str = "Facebook Ads Integration API"
    DEBUG: bool = False
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8080"]
    
    # Database settings
    DATABASE_URL: str = "postgresql://user:password@localhost/facebook_ads_db"
    
    # Redis settings
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Facebook API settings
    FACEBOOK_APP_ID: str = ""
    FACEBOOK_APP_SECRET: str = ""
    FACEBOOK_ACCESS_TOKEN: str = ""
    FACEBOOK_API_VERSION: str = "v18.0"
    FACEBOOK_API_BASE_URL: str = "https://graph.facebook.com"
    
    # Rate limiting settings
    FACEBOOK_RATE_LIMIT_POINTS: int = 9000
    FACEBOOK_RATE_LIMIT_WINDOW: int = 300  # 5 minutes
    RATE_LIMIT_RETRY_DELAY: int = 60  # 1 minute
    MAX_RETRY_ATTEMPTS: int = 3
    
    # Logging settings
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Security settings
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()
