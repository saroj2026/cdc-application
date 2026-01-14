#!/usr/bin/env python3
"""Fix aws_s3 database_type to s3 in database directly"""
import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Database connection
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://cdc_user:cdc_pass@72.61.233.209:5432/cdctest"
)

def main():
    print("="*70)
    print("FIXING AWS_S3 TO S3 IN DATABASE")
    print("="*70 + "\n")
    
    try:
        # Create engine and session
        engine = create_engine(DATABASE_URL)
        Session = sessionmaker(bind=engine)
        session = Session()
        
        # First, check if we need to add 's3' to the enum if it doesn't exist
        print("1. Checking database_type enum values...")
        result = session.execute(text("""
            SELECT unnest(enum_range(NULL::databasetype))::text as enum_value
            ORDER BY enum_value;
        """))
        enum_values = [row[0] for row in result]
        print(f"   Current enum values: {', '.join(enum_values)}")
        
        if 's3' not in enum_values:
            print("   Adding 's3' to enum...")
            session.execute(text("ALTER TYPE databasetype ADD VALUE IF NOT EXISTS 's3'"))
            session.commit()
            print("   ✅ Added 's3' to enum")
        else:
            print("   ✅ 's3' already exists in enum")
        
        # Find connections with aws_s3
        print("\n2. Finding connections with 'aws_s3' database_type...")
        result = session.execute(text("""
            SELECT id, name, database_type::text, connection_type::text
            FROM connections
            WHERE database_type::text = 'aws_s3'
            AND deleted_at IS NULL;
        """))
        connections = result.fetchall()
        
        if not connections:
            print("   ✅ No connections with 'aws_s3' found")
            return 0
        
        print(f"   Found {len(connections)} connection(s) with 'aws_s3':")
        for conn in connections:
            print(f"     - {conn[1]} (ID: {conn[0]}, Type: {conn[3]})")
        
        # Update each connection
        print("\n3. Updating connections to use 's3'...")
        for conn in connections:
            conn_id = conn[0]
            conn_name = conn[1]
            
            # Cast to text, update, then cast back to enum
            session.execute(text("""
                UPDATE connections
                SET database_type = 's3'::databasetype,
                    updated_at = NOW()
                WHERE id = :conn_id
            """), {"conn_id": conn_id})
            
            print(f"   ✅ Updated {conn_name} (ID: {conn_id})")
        
        session.commit()
        print("\n   ✅ All connections updated successfully")
        
        # Verify
        print("\n4. Verifying updates...")
        result = session.execute(text("""
            SELECT id, name, database_type::text, connection_type::text
            FROM connections
            WHERE database_type::text IN ('aws_s3', 's3')
            AND deleted_at IS NULL;
        """))
        remaining = result.fetchall()
        
        if remaining:
            print("   Remaining connections:")
            for conn in remaining:
                print(f"     - {conn[1]} (ID: {conn[0]}, Type: {conn[2]}, Connection: {conn[3]})")
        
        aws_s3_count = sum(1 for conn in remaining if str(conn[2]) == 'aws_s3')
        if aws_s3_count == 0:
            print("\n   ✅ All 'aws_s3' values have been converted to 's3'")
        else:
            print(f"\n   ⚠️  {aws_s3_count} connection(s) still have 'aws_s3'")
        
        session.close()
        
        print("\n" + "="*70)
        print("✅ FIX COMPLETE")
        print("="*70)
        print("\nYou can now try starting the pipeline again:")
        print("  python3 start_as400_pipeline.py")
        print("="*70 + "\n")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())

