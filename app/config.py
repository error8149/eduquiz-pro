import os
from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import validator

class Settings(BaseSettings):
    # Application settings
    app_name: str = "EduQuiz Pro"
    app_version: str = "1.0.0"
    environment: str = "development"
    debug: bool = True
    
    # Server settings
    host: str = "0.0.0.0"
    port: int = 8000
    
    # Database settings
    database_url: str = "sqlite:///./quizapp.db"
    
    # API settings
    api_base_url: str = "/api/v1"
    api_timeout: int = 30
    
    # CORS settings
    allowed_origins: str = "http://127.0.0.1:8000,http://localhost:8000"
    cors_allow_credentials: bool = True
    cors_max_age: int = 86400
    
    # Logging settings
    log_level: str = "INFO"
    log_file: str = "quizapp.log"
    log_max_size: int = 10485760  # 10MB
    log_backup_count: int = 5
    
    # Security settings
    secret_key: str = "your-super-secret-key-change-in-production"
    
    # Rate limiting settings
    rate_limit_enabled: bool = False
    rate_limit_requests: int = 100
    rate_limit_window: int = 60
    redis_url: Optional[str] = None
    
    # Frontend settings
    frontend_path: str = "frontend"
    static_url: str = "/static"
    
    # AI Provider defaults
    default_ai_provider: str = "gemini"
    default_grade_level: str = "high school"
    default_difficulty: str = "medium"
    default_num_questions: int = 10
    default_time_limit: int = 15
    
    # Deployment settings
    deployment_type: str = "development"
    base_url: str = "http://127.0.0.1:8000"
    
    @validator("allowed_origins")
    def parse_origins(cls, v):
        """Parse comma-separated origins into a list"""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v
    
    @validator("database_url")
    def validate_database_url(cls, v):
        """Handle PostgreSQL URL format"""
        if v.startswith("postgres://"):
            return v.replace("postgres://", "postgresql://", 1)
        return v
    
    @property
    def is_production(self) -> bool:
        return self.environment.lower() == "production"
    
    @property
    def is_development(self) -> bool:
        return self.environment.lower() == "development"
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Global settings instance
settings = Settings()

# Runtime environment detection
if os.getenv("RENDER"):
    settings.environment = "production"
    settings.debug = False
    settings.deployment_type = "production"
elif os.getenv("RAILWAY_ENVIRONMENT"):
    settings.environment = "production"
    settings.debug = False
    settings.deployment_type = "production"
elif os.getenv("PYTHONANYWHERE_DOMAIN"):
    settings.environment = "production"
    settings.debug = False
    settings.deployment_type = "production"