"""Initialize database and run migrations."""

import sys
import os
import logging
from alembic import command
from alembic.config import Config

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from ingestion.database import engine
from ingestion.database.base import Base

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def init_db():
    """Initialize the database and run migrations."""
    try:
        logger.info("Initializing database...")
        
        alembic_cfg = Config("alembic.ini")
        
        logger.info("Running Alembic migrations...")
        command.upgrade(alembic_cfg, "head")
        
        logger.info("Database initialization completed successfully!")
        
    except Exception as e:
        logger.error(f"Database initialization failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    init_db()
