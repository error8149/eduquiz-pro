import logging
from typing import Generator

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from tenacity import (before_sleep_log, retry, retry_if_exception_type,
                      stop_after_attempt, wait_exponential)

from .base import Base
from .config import settings

logger = logging.getLogger(__name__)

# Database configuration using settings
database_url = settings.database_url
logger.info(f"🗄️  Configuring database: {database_url[:30]}...")

# Engine configuration based on database type
engine_kwargs = {
    "pool_size": 5,
    "max_overflow": 10,
    "pool_timeout": 30,
    "pool_recycle": 1800,
}

# SQLite specific configuration
if database_url.startswith("sqlite"):
    engine_kwargs["connect_args"] = {"check_same_thread": False}
    logger.info("📝 Using SQLite database")
elif database_url.startswith("postgresql"):
    logger.info("🐘 Using PostgreSQL database")
else:
    logger.info(f"🔗 Using database: {database_url.split('://')[0]}")

engine = create_engine(database_url, **engine_kwargs)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def add_column_if_not_exists(conn, table_name, column_name, column_definition):
    """Add a column to a table if it doesn't already exist."""
    try:
        # Try to select from the column to see if it exists
        conn.execute(text(f"SELECT {column_name} FROM {table_name} LIMIT 1"))
        logger.debug(f"✅ Column {column_name} already exists in {table_name}")
    except Exception:
        # Column doesn't exist, add it
        try:
            conn.execute(text(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_definition}"))
            conn.commit()
            logger.info(f"➕ Added column {column_name} to {table_name}")
        except Exception as e:
            logger.warning(f"⚠️  Failed to add column {column_name} to {table_name}: {str(e)}")

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type(Exception),
    before_sleep=before_sleep_log(logger, logging.WARNING)
)
def init_db():
    """Initialize the database with retry logic"""
    try:
        logger.info("🔧 Initializing database tables...")
        Base.metadata.create_all(bind=engine)
        
        # Add new columns for existing databases (migration support)
        if database_url.startswith("sqlite"):
            with engine.connect() as conn:
                # Add grade_level column if it doesn't exist
                add_column_if_not_exists(
                    conn, "quizzes", "grade_level", 
                    f"VARCHAR DEFAULT '{settings.default_grade_level}'"
                )
                
                # Add difficulty column if it doesn't exist
                add_column_if_not_exists(
                    conn, "quizzes", "difficulty", 
                    f"VARCHAR DEFAULT '{settings.default_difficulty}'"
                )
        
        logger.info("✅ Database initialization completed successfully")
        
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {str(e)}")
        raise

def get_db() -> Generator:
    """Database dependency for FastAPI"""
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"💥 Database session error: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()
        if settings.debug:
            logger.debug("🔒 Database session closed")

# Initialize database on module import
try:
    init_db()
except Exception as e:
    logger.critical(f"💀 Critical database error: {str(e)}")
    if settings.is_production:
        # In production, log but don't crash immediately
        logger.error("🚨 Database initialization failed, but continuing...")
    else:
        # In development, crash to get developer attention
        raise