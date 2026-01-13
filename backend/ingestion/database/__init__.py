"""Database module."""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool, NullPool
import os
import logging

# Database URL from environment or default
# Default to remote VPS database if DATABASE_URL not set
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://cdc_user:cdc_pass@72.61.233.209:5432/cdctest"
)

# Configure connection pool based on database type
if "sqlite" in DATABASE_URL:
    # SQLite uses StaticPool
    from sqlalchemy.pool import StaticPool
    engine = create_engine(
        DATABASE_URL,
        poolclass=StaticPool,
        connect_args={"check_same_thread": False},
        echo=False
    )
else:
    # PostgreSQL uses QueuePool with connection timeouts
    pool_size = int(os.getenv("DATABASE_POOL_SIZE", "10"))
    max_overflow = int(os.getenv("DATABASE_MAX_OVERFLOW", "20"))
    
    engine = create_engine(
        DATABASE_URL,
        poolclass=QueuePool,
        pool_size=pool_size,
        max_overflow=max_overflow,
        pool_pre_ping=True,  # Verify connections before using
        pool_recycle=3600,  # Recycle connections after 1 hour
        connect_args={
            "connect_timeout": 10,  # 10 second connection timeout
            "options": "-c statement_timeout=30000"  # 30 second statement timeout
        },
        echo=False
    )

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Log database connection info
logging.info(f"Database engine created: {DATABASE_URL.split('@')[-1] if '@' in DATABASE_URL else 'local'}")


def get_db() -> Session:
    """Get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

