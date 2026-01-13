"""Verify migration was successful."""
import os
from sqlalchemy import create_engine, text

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://cdc_user:cdc_pass@72.61.233.209:5432/cdctest"
)

engine = create_engine(DATABASE_URL)

with engine.connect() as conn:
    result = conn.execute(text("""
        SELECT column_name, data_type, is_nullable
        FROM information_schema.columns
        WHERE table_name = 'users'
        ORDER BY ordinal_position;
    """))
    
    print("Users table columns:")
    print("-" * 60)
    for row in result:
        print(f"  {row[0]:20} {row[1]:20} nullable={row[2]}")
    
    # Check if new columns exist
    result = conn.execute(text("""
        SELECT column_name
        FROM information_schema.columns
        WHERE table_name = 'users' 
        AND column_name IN ('tenant_id', 'status', 'last_login');
    """))
    
    new_columns = [row[0] for row in result]
    print("\nNew columns check:")
    print(f"  tenant_id: {'✓' if 'tenant_id' in new_columns else '✗'}")
    print(f"  status: {'✓' if 'status' in new_columns else '✗'}")
    print(f"  last_login: {'✓' if 'last_login' in new_columns else '✗'}")

