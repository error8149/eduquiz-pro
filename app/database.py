import logging
import os
from typing import Generator

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from tenacity import (before_sleep_log, retry, retry_if_exception_type,
                      stop_after_attempt, wait_exponential)

from .base import Base
from .config import db_config, settings

# Setup logging
logger = logging.getLogger(__name__)

# Configure SQLAlchemy engine with connection pooling
engine = create_engine(
    db_config.URL,
    connect_args={"check_same_thread": False} if db_config.URL.startswith("sqlite") else {},
    pool_size=db_config.POOL_SIZE,
    max_overflow=db_config.MAX_OVERFLOW,
    pool_timeout=db_config.POOL_TIMEOUT,
    pool_recycle=db_config.POOL_RECYCLE,
    echo=db_config.ECHO,
)

# Session factory for synchronous database operations
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def add_column_if_not_exists(conn, table_name, column_name, column_definition):
    """Add a column to a table if it doesn't already exist."""
    try:
        # Try to select from the column to see if it exists
        conn.execute(text(f"SELECT {column_name} FROM {table_name} LIMIT 1"))
        logger.debug(f"Column {column_name} already exists in {table_name}")
    except Exception:
        # Column doesn't exist, add it
        try:
            conn.execute(text(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_definition}"))
            conn.commit()
            logger.info(f"Added column {column_name} to {table_name}")
        except Exception as e:
            logger.warning(f"Failed to add column {column_name} to {table_name}: {str(e)}")

def backup_database():
    """Create a backup of the database before migration."""
    if db_config.URL.startswith("sqlite"):
        import shutil
        db_file = db_config.URL.replace("sqlite:///", "").replace("sqlite://", "")
        if os.path.exists(db_file):
            backup_file = f"{db_file}.backup"
            shutil.copy2(db_file, backup_file)
            logger.info(f"Database backed up to {backup_file}")

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type(Exception),
    before_sleep=before_sleep_log(logger, logging.WARNING)
)
def init_db():
    """
    Initialize the database by creating all tables defined in models.
    Retries on failure to handle transient database connection issues.
    """
    try:
        logger.info(f"Initializing database with URL: {db_config.URL}")
        
        # Create backup before any changes
        if settings.is_production:
            backup_database()
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        
        # Add new columns if they don't exist (for existing databases)
        if db_config.URL.startswith("sqlite"):
            with engine.connect() as conn:
                # Add grade_level column if it doesn't exist
                add_column_if_not_exists(conn, "quizzes", "grade_level", "VARCHAR DEFAULT 'high school'")
                
                # Add difficulty column if it doesn't exist
                add_column_if_not_exists(conn, "quizzes", "difficulty", "VARCHAR DEFAULT 'medium'")
        
        logger.info("Database tables created/updated successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {str(e)}", exc_info=True)
        raise

def get_db() -> Generator:
    """
    Dependency function to provide a database session for each request.
    Ensures the session is closed after the request is completed.
    """
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Database session error: {str(e)}", exc_info=True)
        db.rollback()
        raise
    finally:
        db.close()
        logger.debug("Database session closed")

def check_database_health():
    """Check if database connection is healthy."""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}")
        return False

# Initialize database on module import
try:
    init_db()
except Exception as e:
    logger.critical(f"Database initialization failed: {str(e)}", exc_info=True)
    raise