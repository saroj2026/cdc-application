"""Add missing columns to etl_runs table."""

import sys
import os

backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_dir)

from sqlalchemy import text
from ingestion.database import engine

SQL = """
-- Add missing columns to etl_runs table if they don't exist
DO $$ 
BEGIN
    -- Add triggered_by column
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_schema = 'public' 
        AND table_name = 'etl_runs' 
        AND column_name = 'triggered_by'
    ) THEN
        ALTER TABLE etl_runs ADD COLUMN triggered_by VARCHAR(50) NOT NULL DEFAULT 'manual';
    END IF;
    
    -- Add triggered_by_user_id column
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_schema = 'public' 
        AND table_name = 'etl_runs' 
        AND column_name = 'triggered_by_user_id'
    ) THEN
        ALTER TABLE etl_runs ADD COLUMN triggered_by_user_id VARCHAR(36) REFERENCES users(id) ON DELETE SET NULL;
    END IF;
    
    -- Drop default after adding (if we just added it)
    ALTER TABLE etl_runs ALTER COLUMN triggered_by DROP DEFAULT;
END $$;

-- Add run_metadata column if it doesn't exist
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_schema = 'public' 
        AND table_name = 'etl_runs' 
        AND column_name = 'run_metadata'
    ) THEN
        ALTER TABLE etl_runs ADD COLUMN run_metadata JSONB DEFAULT '{}';
    END IF;
END $$;
"""

def fix_columns():
    try:
        print("Adding missing columns to etl_runs table...")
        with engine.begin() as conn:
            conn.execute(text(SQL))
            print("✓ Columns added successfully!")
    except Exception as e:
        error_str = str(e).lower()
        if 'already exists' in error_str or 'duplicate' in error_str:
            print("✓ Columns already exist")
        else:
            print(f"✗ Error: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)

if __name__ == "__main__":
    fix_columns()

