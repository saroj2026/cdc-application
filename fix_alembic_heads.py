"""Fix Alembic multiple heads issue and upgrade to include Oracle enum."""

import subprocess
import sys

print("=" * 70)
print("Fixing Alembic Multiple Heads Issue")
print("=" * 70)

try:
    # Check current heads
    print("\n1. Checking current Alembic heads...")
    result = subprocess.run(["alembic", "heads"], capture_output=True, text=True)
    print(result.stdout)
    
    # Get all head revisions
    heads = [line.strip().split()[0] for line in result.stdout.split('\n') if line.strip() and not line.startswith('INFO')]
    print(f"\n   Found {len(heads)} head(s): {heads}")
    
    # Upgrade to all heads
    print("\n2. Upgrading to all heads...")
    result = subprocess.run(["alembic", "upgrade", "heads"], capture_output=True, text=True)
    
    if result.returncode == 0:
        print("   ✅ Migration successful!")
        print(result.stdout)
    else:
        print("   ⚠️  Migration had issues:")
        print(result.stderr)
        
        # Try upgrading to specific head
        print("\n3. Trying to upgrade to add_oracle_enum head...")
        result2 = subprocess.run(["alembic", "upgrade", "add_oracle_enum"], capture_output=True, text=True)
        if result2.returncode == 0:
            print("   ✅ Upgraded to add_oracle_enum")
            print(result2.stdout)
        else:
            print("   ⚠️  Could not upgrade to add_oracle_enum")
            print(result2.stderr)
    
    # Verify Oracle is in enum
    print("\n4. Verifying Oracle in DatabaseType enum...")
    from ingestion.database.models_db import DatabaseType
    db_types = [e.value for e in DatabaseType]
    if 'oracle' in db_types:
        print("   ✅ Oracle is in DatabaseType enum")
        print(f"   All types: {', '.join(db_types)}")
    else:
        print("   ⚠️  Oracle not found in enum")
        print(f"   Current types: {', '.join(db_types)}")
    
    print("\n" + "=" * 70)
    print("✅ Complete!")
    print("=" * 70)
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()

