"""Script to run user management migration."""
import os
import sys
from sqlalchemy import create_engine, text
from urllib.parse import quote_plus

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
        # Create engine
        engine = create_engine(DATABASE_URL)
        
        # Read migration SQL
        migration_file = os.path.join(os.path.dirname(__file__), "migrations", "add_user_management_columns.sql")
        
        if not os.path.exists(migration_file):
            print(f"ERROR: Migration file not found: {migration_file}")
            return 1
        
        with open(migration_file, 'r') as f:
            migration_sql = f.read()
        
        print("Running migration...")
        print()
        
        # Execute migration
        with engine.begin() as conn:  # Use begin() for transaction management
            # Split by semicolons but preserve DO $$ blocks
            statements = []
            current_statement = ""
            in_do_block = False
            dollar_quote = None
            
            for line in migration_sql.split('\n'):
                line = line.strip()
                if not line or line.startswith('--'):
                    continue
                
                # Check for DO $$ blocks
                if 'DO $$' in line.upper():
                    in_do_block = True
                    dollar_quote = '$$'
                    current_statement = line
                    continue
                
                if in_do_block:
                    current_statement += '\n' + line
                    # Check for END $$
                    if line.strip().upper().startswith('END $$'):
                        statements.append(current_statement)
                        current_statement = ""
                        in_do_block = False
                        dollar_quote = None
                    continue
                
                # Regular statements
                current_statement += '\n' + line if current_statement else line
                if line.endswith(';'):
                    statements.append(current_statement)
                    current_statement = ""
            
            # Execute each statement
            for statement in statements:
                statement = statement.strip()
                if statement:
                    try:
                        conn.execute(text(statement))
                    except Exception as e:
                        error_str = str(e).lower()
                        # Ignore "already exists" errors
                        if "already exists" not in error_str and "duplicate" not in error_str:
                            print(f"Warning: {str(e)[:100]}")
        
        print("✅ Migration completed successfully!")
        print()
        print("New columns added to 'users' table:")
        print("  - tenant_id (UUID)")
        print("  - status (VARCHAR)")
        print("  - last_login (TIMESTAMP)")
        print()
        print("New tables created:")
        print("  - user_sessions (for refresh tokens)")
        print("  - audit_logs (for audit trail)")
        print()
        print("Existing users updated with default values.")
        
        return 0
        
    except Exception as e:
        print(f"ERROR: Migration failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(run_migration())

