"""Verify etl_runs table has all required columns."""

import sys
import os

backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_dir)

from sqlalchemy import text
from ingestion.database import engine

def verify_columns():
    try:
        print("Verifying etl_runs table columns...")
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns
                WHERE table_schema = 'public' 
                AND table_name = 'etl_runs'
                ORDER BY ordinal_position;
            """))
            columns = result.fetchall()
            
            print("\nCurrent columns in etl_runs table:")
            for col in columns:
                print(f"  - {col[0]} ({col[1]}, nullable: {col[2]})")
            
            # Check for required columns
            required_cols = ['triggered_by', 'triggered_by_user_id', 'run_metadata']
            existing_cols = [col[0] for col in columns]
            
            print("\nChecking for required columns:")
            all_present = True
            for req_col in required_cols:
                if req_col in existing_cols:
                    print(f"  ✓ {req_col} - exists")
                else:
                    print(f"  ✗ {req_col} - MISSING")
                    all_present = False
            
            if all_present:
                print("\n✓ All required columns are present!")
            else:
                print("\n✗ Some required columns are missing!")
                
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    verify_columns()

