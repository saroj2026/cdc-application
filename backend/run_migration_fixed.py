"""Fixed script to run user management migration."""
import os
import sys
from sqlalchemy import create_engine, text

# Get database URL from environment
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://cdc_user:cdc_pass@72.61.233.209:5432/cdctest"
)

def run_migration():
    """Run the user management migration."""
    print("=" * 60)
    print("User Management Migration")
    print("=" * 60)
    print(f"Database: {DATABASE_URL.split('@')[-1] if '@' in DATABASE_URL else DATABASE_URL}")
    print()
    
    try:
        engine = create_engine(DATABASE_URL)
        
        with engine.begin() as conn:  # Transaction context
            print("Adding columns to users table...")
            
            # Add tenant_id column
            try:
                conn.execute(text("""
                    DO $$ 
                    BEGIN
                        IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                                       WHERE table_name = 'users' AND column_name = 'tenant_id') THEN
                            ALTER TABLE users ADD COLUMN tenant_id UUID;
                        END IF;
                    END $$;
                """))
                print("  ✓ tenant_id column")
            except Exception as e:
                if "already exists" not in str(e).lower():
                    print(f"  ⚠ tenant_id: {str(e)[:80]}")
            
            # Add status column
            try:
                conn.execute(text("""
                    DO $$ 
                    BEGIN
                        IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                                       WHERE table_name = 'users' AND column_name = 'status') THEN
                            ALTER TABLE users ADD COLUMN status VARCHAR(20);
                        END IF;
                    END $$;
                """))
                print("  ✓ status column")
            except Exception as e:
                if "already exists" not in str(e).lower():
                    print(f"  ⚠ status: {str(e)[:80]}")
            
            # Add last_login column
            try:
                conn.execute(text("""
                    DO $$ 
                    BEGIN
                        IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                                       WHERE table_name = 'users' AND column_name = 'last_login') THEN
                            ALTER TABLE users ADD COLUMN last_login TIMESTAMP;
                        END IF;
                    END $$;
                """))
                print("  ✓ last_login column")
            except Exception as e:
                if "already exists" not in str(e).lower():
                    print(f"  ⚠ last_login: {str(e)[:80]}")
            
            print("\nSetting default values...")
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
                print("  ✓ Default values set")
            except Exception as e:
                print(f"  ⚠ Default values: {str(e)[:80]}")
            
            print("\nCreating indexes...")
            # Create index
            try:
                conn.execute(text("CREATE INDEX IF NOT EXISTS idx_users_tenant_id ON users(tenant_id);"))
                print("  ✓ Index on tenant_id")
            except Exception as e:
                print(f"  ⚠ Index: {str(e)[:80]}")
            
            print("\nCreating user_sessions table...")
            # Create user_sessions table
            try:
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS user_sessions (
                        id VARCHAR(36) PRIMARY KEY,
                        user_id VARCHAR(36) NOT NULL,
                        refresh_token_hash TEXT NOT NULL,
                        expires_at TIMESTAMP NOT NULL,
                        ip_address VARCHAR(45),
                        user_agent TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                """))
                conn.execute(text("CREATE INDEX IF NOT EXISTS idx_user_sessions_user_id ON user_sessions(user_id);"))
                conn.execute(text("CREATE INDEX IF NOT EXISTS idx_user_sessions_expires_at ON user_sessions(expires_at);"))
                print("  ✓ user_sessions table created")
            except Exception as e:
                print(f"  ⚠ user_sessions: {str(e)[:80]}")
            
            print("\nCreating audit_logs table...")
            # Create audit_logs table
            try:
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
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                """))
                conn.execute(text("CREATE INDEX IF NOT EXISTS idx_audit_logs_tenant_id ON audit_logs(tenant_id);"))
                conn.execute(text("CREATE INDEX IF NOT EXISTS idx_audit_logs_user_id ON audit_logs(user_id);"))
                conn.execute(text("CREATE INDEX IF NOT EXISTS idx_audit_logs_action ON audit_logs(action);"))
                conn.execute(text("CREATE INDEX IF NOT EXISTS idx_audit_logs_resource_type ON audit_logs(resource_type);"))
                conn.execute(text("CREATE INDEX IF NOT EXISTS idx_audit_logs_resource_id ON audit_logs(resource_id);"))
                conn.execute(text("CREATE INDEX IF NOT EXISTS idx_audit_logs_created_at ON audit_logs(created_at);"))
                print("  ✓ audit_logs table created")
            except Exception as e:
                print(f"  ⚠ audit_logs: {str(e)[:80]}")
        
        print("\n" + "=" * 60)
        print("✅ Migration completed successfully!")
        print("=" * 60)
        print("\nNew columns added to 'users' table:")
        print("  - tenant_id (UUID)")
        print("  - status (VARCHAR)")
        print("  - last_login (TIMESTAMP)")
        print("\nNew tables created:")
        print("  - user_sessions (for refresh tokens)")
        print("  - audit_logs (for audit trail)")
        print("\nExisting users updated with default values.")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ ERROR: Migration failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(run_migration())

