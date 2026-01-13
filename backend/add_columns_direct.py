"""Directly add columns to users table."""
import os
from sqlalchemy import create_engine, text

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://cdc_user:cdc_pass@72.61.233.209:5432/cdctest"
)

engine = create_engine(DATABASE_URL)

print("Adding columns directly...")

with engine.begin() as conn:
    # Check if columns exist first
    result = conn.execute(text("""
        SELECT column_name
        FROM information_schema.columns
        WHERE table_name = 'users' 
        AND column_name IN ('tenant_id', 'status', 'last_login');
    """))
    existing = {row[0] for row in result}
    
    # Add tenant_id
    if 'tenant_id' not in existing:
        try:
            conn.execute(text("ALTER TABLE users ADD COLUMN tenant_id UUID;"))
            print("✓ Added tenant_id column")
        except Exception as e:
            print(f"✗ Failed to add tenant_id: {e}")
    else:
        print("✓ tenant_id already exists")
    
    # Add status
    if 'status' not in existing:
        try:
            conn.execute(text("ALTER TABLE users ADD COLUMN status VARCHAR(20);"))
            print("✓ Added status column")
        except Exception as e:
            print(f"✗ Failed to add status: {e}")
    else:
        print("✓ status already exists")
    
    # Add last_login
    if 'last_login' not in existing:
        try:
            conn.execute(text("ALTER TABLE users ADD COLUMN last_login TIMESTAMP;"))
            print("✓ Added last_login column")
        except Exception as e:
            print(f"✗ Failed to add last_login: {e}")
    else:
        print("✓ last_login already exists")
    
    # Set default values
    try:
        conn.execute(text("""
            UPDATE users 
            SET tenant_id = '00000000-0000-0000-0000-000000000000'::UUID 
            WHERE tenant_id IS NULL;
        """))
        conn.execute(text("""
            UPDATE users 
            SET status = 'active' 
            WHERE status IS NULL;
        """))
        print("✓ Set default values")
    except Exception as e:
        print(f"⚠ Default values: {e}")
    
    # Create index
    try:
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_users_tenant_id ON users(tenant_id);"))
        print("✓ Created index")
    except Exception as e:
        print(f"⚠ Index: {e}")

print("\nVerifying...")
with engine.connect() as conn:
    result = conn.execute(text("""
        SELECT column_name
        FROM information_schema.columns
        WHERE table_name = 'users' 
        AND column_name IN ('tenant_id', 'status', 'last_login');
    """))
    new_columns = [row[0] for row in result]
    print(f"Columns now exist: {new_columns}")

