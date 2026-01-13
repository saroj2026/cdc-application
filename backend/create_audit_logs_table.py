"""Script to create audit_logs table if it doesn't exist."""
import os
import sys
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.orm import sessionmaker

# Get database URL from environment or use default
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://cdc_user:cdc_pass@72.61.233.209:5432/cdctest"
)

def create_audit_logs_table():
    """Create audit_logs table if it doesn't exist."""
    engine = create_engine(DATABASE_URL)
    inspector = inspect(engine)
    
    with engine.connect() as conn:
        # Check if table exists
        tables = inspector.get_table_names()
        
        if 'audit_logs' in tables:
            print("✓ audit_logs table already exists")
            
            # Check if it has the correct columns
            columns = [col['name'] for col in inspector.get_columns('audit_logs')]
            required_columns = ['id', 'action', 'created_at']
            new_columns = ['tenant_id', 'user_id', 'resource_type', 'resource_id', 
                          'old_value', 'new_value', 'ip_address', 'user_agent']
            
            missing_columns = [col for col in new_columns if col not in columns]
            
            if missing_columns:
                print(f"⚠ audit_logs table exists but is missing columns: {missing_columns}")
                print("  Attempting to add missing columns...")
                
                try:
                    # Add missing columns
                    if 'tenant_id' not in columns:
                        conn.execute(text("ALTER TABLE audit_logs ADD COLUMN IF NOT EXISTS tenant_id UUID;"))
                        print("  ✓ Added tenant_id column")
                    
                    if 'user_id' not in columns:
                        conn.execute(text("ALTER TABLE audit_logs ADD COLUMN IF NOT EXISTS user_id VARCHAR(36);"))
                        print("  ✓ Added user_id column")
                    
                    if 'resource_type' not in columns:
                        conn.execute(text("ALTER TABLE audit_logs ADD COLUMN IF NOT EXISTS resource_type VARCHAR(50);"))
                        print("  ✓ Added resource_type column")
                    
                    if 'resource_id' not in columns:
                        conn.execute(text("ALTER TABLE audit_logs ADD COLUMN IF NOT EXISTS resource_id VARCHAR(36);"))
                        print("  ✓ Added resource_id column")
                    
                    if 'old_value' not in columns:
                        conn.execute(text("ALTER TABLE audit_logs ADD COLUMN IF NOT EXISTS old_value JSONB;"))
                        print("  ✓ Added old_value column")
                    
                    if 'new_value' not in columns:
                        conn.execute(text("ALTER TABLE audit_logs ADD COLUMN IF NOT EXISTS new_value JSONB;"))
                        print("  ✓ Added new_value column")
                    
                    if 'ip_address' not in columns:
                        conn.execute(text("ALTER TABLE audit_logs ADD COLUMN IF NOT EXISTS ip_address VARCHAR(45);"))
                        print("  ✓ Added ip_address column")
                    
                    if 'user_agent' not in columns:
                        conn.execute(text("ALTER TABLE audit_logs ADD COLUMN IF NOT EXISTS user_agent TEXT;"))
                        print("  ✓ Added user_agent column")
                    
                    # Rename old columns if they exist
                    if 'entity_type' in columns and 'resource_type' in columns:
                        # Both exist, we can drop entity_type
                        conn.execute(text("ALTER TABLE audit_logs DROP COLUMN IF EXISTS entity_type;"))
                        print("  ✓ Removed old entity_type column")
                    
                    if 'entity_id' in columns and 'resource_id' in columns:
                        # Both exist, we can drop entity_id
                        conn.execute(text("ALTER TABLE audit_logs DROP COLUMN IF EXISTS entity_id;"))
                        print("  ✓ Removed old entity_id column")
                    
                    if 'old_values' in columns and 'old_value' in columns:
                        # Both exist, we can drop old_values
                        conn.execute(text("ALTER TABLE audit_logs DROP COLUMN IF EXISTS old_values;"))
                        print("  ✓ Removed old old_values column")
                    
                    if 'new_values' in columns and 'new_value' in columns:
                        # Both exist, we can drop new_values
                        conn.execute(text("ALTER TABLE audit_logs DROP COLUMN IF EXISTS new_values;"))
                        print("  ✓ Removed old new_values column")
                    
                    if 'timestamp' in columns and 'created_at' in columns:
                        # Both exist, we can drop timestamp
                        conn.execute(text("ALTER TABLE audit_logs DROP COLUMN IF EXISTS timestamp;"))
                        print("  ✓ Removed old timestamp column")
                    
                    conn.commit()
                    print("✓ Successfully updated audit_logs table")
                except Exception as e:
                    conn.rollback()
                    print(f"✗ Failed to update audit_logs table: {str(e)}")
                    return False
            else:
                print("✓ audit_logs table has all required columns")
        else:
            print("Creating audit_logs table...")
            try:
                # Create the table with the correct schema
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS audit_logs (
                        id VARCHAR(36) PRIMARY KEY,
                        tenant_id UUID,
                        user_id VARCHAR(36),
                        action VARCHAR(100) NOT NULL,
                        resource_type VARCHAR(50),
                        resource_id VARCHAR(36),
                        old_value JSONB,
                        new_value JSONB,
                        ip_address VARCHAR(45),
                        user_agent TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
                    );
                """))
                
                # Create indexes
                conn.execute(text("CREATE INDEX IF NOT EXISTS idx_audit_logs_tenant_id ON audit_logs(tenant_id);"))
                conn.execute(text("CREATE INDEX IF NOT EXISTS idx_audit_logs_user_id ON audit_logs(user_id);"))
                conn.execute(text("CREATE INDEX IF NOT EXISTS idx_audit_logs_action ON audit_logs(action);"))
                conn.execute(text("CREATE INDEX IF NOT EXISTS idx_audit_logs_resource_type ON audit_logs(resource_type);"))
                conn.execute(text("CREATE INDEX IF NOT EXISTS idx_audit_logs_resource_id ON audit_logs(resource_id);"))
                conn.execute(text("CREATE INDEX IF NOT EXISTS idx_audit_logs_created_at ON audit_logs(created_at);"))
                
                conn.commit()
                print("✓ Successfully created audit_logs table with indexes")
            except Exception as e:
                conn.rollback()
                print(f"✗ Failed to create audit_logs table: {str(e)}")
                return False
        
        return True

if __name__ == "__main__":
    print("=" * 60)
    print("Creating/Updating audit_logs table")
    print("=" * 60)
    
    success = create_audit_logs_table()
    
    if success:
        print("\n✓ audit_logs table is ready!")
        sys.exit(0)
    else:
        print("\n✗ Failed to create/update audit_logs table")
        sys.exit(1)

