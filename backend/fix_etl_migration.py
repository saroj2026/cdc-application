"""Fix ETL migration and create tables if needed."""

import sys
import os

# Add backend directory to path so imports work
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_dir)

from sqlalchemy import text
from ingestion.database import engine
from ingestion.database.base import Base
from ingestion.database.models_db import (
    ETLPipelineModel, ETLTransformationModel, ETLRunModel,
    DataQualityRuleModel, ETLScheduleModel
)

def fix_etl_tables():
    """Create ETL tables if they don't exist."""
    try:
        print("Checking ETL tables...")
        
        # Use a transaction
        with engine.begin() as conn:
            # Check if etl_pipelines table exists
            result = conn.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = 'etl_pipelines'
                );
            """))
            exists = result.scalar()
            
            if not exists:
                print("Creating ETL tables...")
                
                # Create enum type if it doesn't exist
                print("  Creating enum type...")
                conn.execute(text("""
                    DO $$ BEGIN
                        CREATE TYPE etlpipelinestatus AS ENUM ('draft', 'active', 'paused', 'failed', 'completed');
                    EXCEPTION
                        WHEN duplicate_object THEN null;
                    END $$;
                """))
                
                # Create all ETL tables using SQLAlchemy Base metadata
                print("  Creating etl_pipelines table...")
                ETLPipelineModel.__table__.create(conn, checkfirst=True)
                
                print("  Creating etl_transformations table...")
                ETLTransformationModel.__table__.create(conn, checkfirst=True)
                
                print("  Creating etl_runs table...")
                ETLRunModel.__table__.create(conn, checkfirst=True)
                
                print("  Creating data_quality_rules table...")
                DataQualityRuleModel.__table__.create(conn, checkfirst=True)
                
                print("  Creating etl_schedules table...")
                ETLScheduleModel.__table__.create(conn, checkfirst=True)
                
                print("ETL tables created successfully!")
            else:
                print("ETL tables already exist.")
                
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    fix_etl_tables()

