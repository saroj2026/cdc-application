"""Database session management with connection pooling."""

import os
from typing import Generator
from sqlalchemy import create_engine, event, pool
from sqlalchemy.orm import sessionmaker, Session
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://cdc_user:cdc_pass@72.61.233.209:5432/cdctest")
DATABASE_POOL_SIZE = int(os.getenv("DATABASE_POOL_SIZE", "10"))
DATABASE_MAX_OVERFLOW = int(os.getenv("DATABASE_MAX_OVERFLOW", "20"))

engine = create_engine(
    DATABASE_URL,
    poolclass=pool.QueuePool,
    pool_size=DATABASE_POOL_SIZE,
    max_overflow=DATABASE_MAX_OVERFLOW,
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=False,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """Get database session.
    
    Yields:
        Database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_conn, connection_record):
    """Set database-specific settings on connection."""
    pass
