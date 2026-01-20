"""Quick script to create ETL tables using raw SQL."""

import sys
import os
from pathlib import Path

# Add backend directory to path so imports work
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_dir)

from sqlalchemy import text
from ingestion.database import engine

def create_etl_tables():
    """Create ETL tables using SQL file."""
    try:
        print("Creating ETL tables...")
        
        # Read SQL file
        sql_file = Path(__file__).parent / "create_etl_tables.sql"
        with open(sql_file, 'r') as f:
            sql = f.read()
        
        # Execute SQL
        with engine.begin() as conn:
            print("  Executing SQL...")
            conn.execute(text(sql))
            print("ETL tables created successfully!")
            
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    create_etl_tables()

