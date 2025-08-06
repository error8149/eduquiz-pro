#!/usr/bin/env python3
"""
Database migration script for EduQuiz Pro
Run this script when you need to update the database schema
"""

import os
import sys
import shutil
from datetime import datetime

# Add the project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Import from app module
from app.database import engine, Base
from app.config import settings
from sqlalchemy import text


def backup_database():
    """Create a backup of the current database"""
    if settings.DATABASE_URL.startswith("sqlite"):
        db_file = settings.DATABASE_URL.replace("sqlite:///", "").replace("sqlite://", "")
        if os.path.exists(db_file):
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = f"{db_file}.backup_{timestamp}"
            shutil.copy2(db_file, backup_file)
            print(f"✅ Database backed up to: {backup_file}")
            return backup_file
    return None


def run_migrations():
    """Run database migrations"""
    print("🔄 Starting database migration...")
    
    # Create backup
    backup_file = backup_database()
    
    try:
        # Create all tables (this will create new tables if they don't exist)
        Base.metadata.create_all(bind=engine)
        print("✅ Tables created/updated successfully")
        
        # Add any custom migrations here
        with engine.connect() as conn:
            # Example: Add new columns if they don't exist
            try:
                conn.execute(text("SELECT grade_level FROM quizzes LIMIT 1"))
                print("✅ grade_level column already exists")
            except:
                try:
                    conn.execute(text("ALTER TABLE quizzes ADD COLUMN grade_level VARCHAR DEFAULT 'high school'"))
                    conn.commit()
                    print("✅ Added grade_level column")
                except Exception as e:
                    print(f"⚠️  Could not add grade_level column (may already exist): {e}")
            
            try:
                conn.execute(text("SELECT difficulty FROM quizzes LIMIT 1"))
                print("✅ difficulty column already exists") 
            except:
                try:
                    conn.execute(text("ALTER TABLE quizzes ADD COLUMN difficulty VARCHAR DEFAULT 'medium'"))
                    conn.commit()
                    print("✅ Added difficulty column")
                except Exception as e:
                    print(f"⚠️  Could not add difficulty column (may already exist): {e}")
        
        print("🎉 Migration completed successfully!")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        if backup_file and os.path.exists(backup_file):
            print(f"💡 You can restore from backup: {backup_file}")
        sys.exit(1)


def check_database():
    """Check database health and schema"""
    print("🔍 Checking database...")
    
    try:
        with engine.connect() as conn:
            # Test connection
            conn.execute(text("SELECT 1"))
            print("✅ Database connection OK")
            
            # Check tables exist
            tables = conn.execute(text("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name NOT LIKE 'sqlite_%'
            """)).fetchall()
            
            print(f"📊 Found {len(tables)} tables:")
            for table in tables:
                print(f"  - {table[0]}")
            
            if tables:
                # Check quiz count
                try:
                    quiz_count = conn.execute(text("SELECT COUNT(*) FROM quizzes")).scalar()
                    print(f"📈 Total quizzes: {quiz_count}")
                except:
                    print("📈 Quizzes table not found or empty")
                
                # Check columns in quizzes table
                try:
                    columns = conn.execute(text("PRAGMA table_info(quizzes)")).fetchall()
                    print(f"📋 Quizzes table columns:")
                    for col in columns:
                        print(f"  - {col[1]} ({col[2]})")
                except:
                    print("📋 Could not read quizzes table schema")
            
    except Exception as e:
        print(f"❌ Database check failed: {e}")
        print(f"💡 Database URL: {settings.DATABASE_URL}")
        sys.exit(1)


def init_fresh_database():
    """Initialize a fresh database with all tables"""
    print("🆕 Initializing fresh database...")
    
    try:
        # Create all tables
        Base.metadata.create_all(bind=engine)
        print("✅ All tables created successfully")
        
        # Verify tables were created
        with engine.connect() as conn:
            tables = conn.execute(text("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name NOT LIKE 'sqlite_%'
            """)).fetchall()
            
            print(f"✅ Created {len(tables)} tables:")
            for table in tables:
                print(f"  - {table[0]}")
        
        print("🎉 Fresh database initialized!")
        
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="EduQuiz Database Migration Tool")
    parser.add_argument("--check", action="store_true", help="Check database status")
    parser.add_argument("--migrate", action="store_true", help="Run migrations")
    parser.add_argument("--backup", action="store_true", help="Create backup only")
    parser.add_argument("--init", action="store_true", help="Initialize fresh database")
    
    args = parser.parse_args()
    
    print(f"🔧 EduQuiz Database Migration Tool")
    print(f"📁 Project root: {project_root}")
    print(f"🗄️  Database URL: {settings.DATABASE_URL}")
    print(f"🌍 Environment: {settings.ENVIRONMENT}")
    print("-" * 50)
    
    if args.check:
        check_database()
    elif args.migrate:
        run_migrations()
    elif args.backup:
        backup_database()
    elif args.init:
        init_fresh_database()
    else:
        print("Usage: python migrate_db.py [--check|--migrate|--backup|--init]")
        print("\nCommands:")
        print("  --check    Check database status")
        print("  --migrate  Run database migrations") 
        print("  --backup   Create database backup")
        print("  --init     Initialize fresh database")