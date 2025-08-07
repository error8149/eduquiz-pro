import logging
import os
from typing import List, Optional

from pydantic import validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Application configuration settings.
    All settings can be overridden by environment variables.
    """
    
    # Application Info
    APP_NAME: str = "EduQuiz Pro"
    APP_VERSION: str = "1.0.0"
    APP_DESCRIPTION: str = "AI-powered quiz generation and management system"
    
    # Environment Configuration
    ENVIRONMENT: str = "development"  # development, staging, production
    DEBUG: bool = True
    
    # Server Configuration
    HOST: str = "127.0.0.1"
    PORT: int = 8000
    RELOAD: bool = True  # For development only
    
    # Database Configuration
    DATABASE_URL: str = "sqlite:///./quizapp.db"
    DATABASE_POOL_SIZE: int = 5
    DATABASE_MAX_OVERFLOW: int = 10
    DATABASE_POOL_TIMEOUT: int = 30
    DATABASE_POOL_RECYCLE: int = 1800
    
    # CORS Configuration
    CORS_ORIGINS: List[str] = [
        "http://127.0.0.1:8001",
        "http://localhost:8001", 
        "http://127.0.0.1:8000",
        "http://localhost:8000",
        "http://localhost:3000",  # React dev server
        "http://127.0.0.1:3000"
    ]
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: List[str] = ["GET", "POST", "OPTIONS", "PUT", "DELETE"]
    CORS_ALLOW_HEADERS: List[str] = [
        "Content-Type", 
        "Authorization", 
        "Origin", 
        "Access-Control-Request-Method", 
        "Access-Control-Request-Headers"
    ]
    
    # API Configuration
    API_V1_PREFIX: str = "/api/v1"
    API_TIMEOUT: int = 30
    MAX_QUESTIONS_PER_QUIZ: int = 50
    MIN_QUESTIONS_PER_QUIZ: int = 1
    
    # Frontend Configuration
    FRONTEND_DIR: str = "frontend"
    STATIC_FILES_DIR: str = "static"
    
    # Logging Configuration
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    LOG_FILE: str = "quizapp.log"
    LOG_MAX_BYTES: int = 1000000  # 1MB
    LOG_BACKUP_COUNT: int = 5
    ENABLE_FILE_LOGGING: bool = True
    ENABLE_CONSOLE_LOGGING: bool = True
    
    # AI Provider Configuration
    SUPPORTED_AI_PROVIDERS: List[str] = ["gemini", "openai", "groq"]
    AI_REQUEST_TIMEOUT: int = 30
    AI_MAX_RETRIES: int = 3
    
    # Security Configuration
    SECRET_KEY: Optional[str] = None
    ALLOWED_HOSTS: List[str] = ["*"]
    
    # Rate Limiting (if implemented)
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW: int = 3600  # 1 hour in seconds
    
    # Cache Configuration (if implemented)
    CACHE_TTL: int = 3600  # 1 hour
    ENABLE_CACHING: bool = False
    
    # Feature Flags
    ENABLE_HISTORY: bool = True
    ENABLE_EXPORT: bool = True
    ENABLE_AI_EXPLANATIONS: bool = True
    ENABLE_MANUAL_MODE: bool = True
    
    # Validation and Processing
    @validator("ENVIRONMENT")
    def validate_environment(cls, v):
        if v not in ["development", "staging", "production"]:
            raise ValueError("ENVIRONMENT must be development, staging, or production")
        return v
    
    @validator("LOG_LEVEL")
    def validate_log_level(cls, v):
        if v not in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
            raise ValueError("LOG_LEVEL must be a valid logging level")
        return v
    
    @validator("DEBUG", pre=True)
    def set_debug_based_on_env(cls, v, values):
        if "ENVIRONMENT" in values:
            if values["ENVIRONMENT"] == "production":
                return False
            elif values["ENVIRONMENT"] == "development":
                return True
        return v
    
    @validator("RELOAD", pre=True)
    def set_reload_based_on_env(cls, v, values):
        if "ENVIRONMENT" in values:
            if values["ENVIRONMENT"] == "production":
                return False
        return v
    
    @validator("CORS_ORIGINS", pre=True)
    def parse_cors_origins(cls, v):
        logging.info(f"Raw CORS_ORIGINS value (type: {type(v)}): {v}")  # Detailed debug log
        try:
            if v is None:
                logging.warning("CORS_ORIGINS is None, using default")
                return ["https://eduquiz-pro.up.railway.app"]
            v_str = str(v).strip()
            if not v_str:
                logging.warning("CORS_ORIGINS is empty, using default")
                return ["https://eduquiz-pro.up.railway.app"]
            if isinstance(v, str):
                cleaned = [origin.strip() for origin in v_str.split(",") if origin.strip()]
                if not cleaned:
                    logging.warning("CORS_ORIGINS string is invalid, using default")
                    return ["https://eduquiz-pro.up.railway.app"]
                return cleaned
            if isinstance(v, list):
                cleaned = [origin for origin in v if isinstance(origin, str) and origin.strip()]
                if not cleaned:
                    logging.warning("CORS_ORIGINS list is invalid, using default")
                    return ["https://eduquiz-pro.up.railway.app"]
                return cleaned
            logging.error(f"Unexpected CORS_ORIGINS type: {type(v)}, using default")
            return ["https://eduquiz-pro.up.railway.app"]
        except Exception as e:
            logging.error(f"Error parsing CORS_ORIGINS: {e}, using default")
            return ["https://eduquiz-pro.up.railway.app"]
    
    @property
    def is_development(self) -> bool:
        return self.ENVIRONMENT == "development"
    
    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT == "production"
    
    @property
    def is_staging(self) -> bool:
        return self.ENVIRONMENT == "staging"
    
    @property
    def database_url_sync(self) -> str:
        return self.DATABASE_URL
    
    @property
    def database_url_async(self) -> str:
        if self.DATABASE_URL.startswith("sqlite"):
            return self.DATABASE_URL.replace("sqlite://", "sqlite+aiosqlite://")
        elif self.DATABASE_URL.startswith("postgresql"):
            return self.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")
        return self.DATABASE_URL
    
    @property
    def log_level_int(self) -> int:
        return getattr(logging, self.LOG_LEVEL.upper())
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True

class DevelopmentSettings(Settings):
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    RELOAD: bool = True
    LOG_LEVEL: str = "DEBUG"
    
    class Config:
        env_file = ".env.development"

class ProductionSettings(Settings):
    ENVIRONMENT: str = "production"
    DEBUG: bool = False
    RELOAD: bool = False
    LOG_LEVEL: str = "INFO"
    HOST: str = "0.0.0.0"
    PORT: int = int(os.getenv("PORT", 8000))  # Use Railway's dynamic PORT
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://postgres@localhost:5432/quizapp")  # Fallback
    CORS_ORIGINS: List[str] = ["https://eduquiz-pro.up.railway.app"]  # Default for Railway
    ALLOWED_HOSTS: List[str] = ["eduquiz-pro.up.railway.app", "localhost", "127.0.0.1"]
    
    class Config:
        env_file = ".env.production"

class StagingSettings(Settings):
    ENVIRONMENT: str = "staging"
    DEBUG: bool = False
    RELOAD: bool = False
    LOG_LEVEL: str = "INFO"
    
    class Config:
        env_file = ".env.staging"

def get_settings() -> Settings:
    env = os.getenv("ENVIRONMENT", "development").lower()
    
    if env == "production":
        return ProductionSettings()
    elif env == "staging":
        return StagingSettings()
    else:
        return DevelopmentSettings()

# Export the settings instance
settings = get_settings()

class DatabaseConfig:
    URL = settings.DATABASE_URL
    POOL_SIZE = settings.DATABASE_POOL_SIZE
    MAX_OVERFLOW = settings.DATABASE_MAX_OVERFLOW
    POOL_TIMEOUT = settings.DATABASE_POOL_TIMEOUT
    POOL_RECYCLE = settings.DATABASE_POOL_RECYCLE
    ECHO = settings.DEBUG

class LoggingConfig:
    LEVEL = settings.log_level_int
    FORMAT = settings.LOG_FORMAT
    FILE = settings.LOG_FILE
    MAX_BYTES = settings.LOG_MAX_BYTES
    BACKUP_COUNT = settings.LOG_BACKUP_COUNT
    ENABLE_FILE = settings.ENABLE_FILE_LOGGING
    ENABLE_CONSOLE = settings.ENABLE_CONSOLE_LOGGING

class APIConfig:
    TIMEOUT = settings.API_TIMEOUT
    MAX_QUESTIONS = settings.MAX_QUESTIONS_PER_QUIZ
    MIN_QUESTIONS = settings.MIN_QUESTIONS_PER_QUIZ
    SUPPORTED_PROVIDERS = settings.SUPPORTED_AI_PROVIDERS
    MAX_RETRIES = settings.AI_MAX_RETRIES

# Export individual configs for easy importing
db_config = DatabaseConfig()
log_config = LoggingConfig()
api_config = APIConfig()