"""Fix connection database types that have invalid enum values."""

import sys
import os

# Add the ingestion directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'ingestion'))

try:
    from ingestion.database import SessionLocal
    from ingestion.database.models_db import ConnectionModel, DatabaseType
    from sqlalchemy import text
    
    print("=" * 70)
    print("Fixing Connection Database Types")
    print("=" * 70)
    
    session = SessionLocal()
    
    try:
        # Use raw SQL to update the database directly (bypassing enum validation)
        # This is necessary because the enum validation fails when reading invalid values
        
        # First, check what invalid values exist
        result = session.execute(text("""
            SELECT id, name, database_type 
            FROM connections 
            WHERE database_type NOT IN ('postgresql', 'sqlserver', 'mysql', 's3')
        """))
        
        invalid_connections = result.fetchall()
        
        if not invalid_connections:
            print("\n✅ No connections with invalid database_type found.")
        else:
            print(f"\nFound {len(invalid_connections)} connection(s) with invalid database_type:\n")
            
            for conn_id, conn_name, db_type in invalid_connections:
                print(f"  - {conn_name} (ID: {conn_id}): {db_type}")
                
                # Map invalid values to valid ones
                db_type_lower = str(db_type).lower() if db_type else ""
                new_type = None
                
                if 'aws_s3' in db_type_lower or db_type_lower == 'aws_s3':
                    new_type = 's3'
                elif 'postgres' in db_type_lower or db_type_lower == 'postgres':
                    new_type = 'postgresql'
                elif 'mssql' in db_type_lower or 'sql_server' in db_type_lower or db_type_lower == 'mssql':
                    new_type = 'sqlserver'
                elif 'mysql' in db_type_lower:
                    new_type = 'mysql'
                else:
                    print(f"    ⚠️  Cannot auto-detect correct type for '{db_type}'. Skipping.")
                    continue
                
                # Update using raw SQL to bypass enum validation
                session.execute(text("""
                    UPDATE connections 
                    SET database_type = :new_type 
                    WHERE id = :conn_id
                """), {"new_type": new_type, "conn_id": conn_id})
                
                print(f"    ✅ Updated to: {new_type}")
            
            session.commit()
            print(f"\n✅ Fixed {len([c for c in invalid_connections if c])} connection(s).")
        
        # Verify all connections now have valid types
        print("\n" + "-" * 70)
        print("Verifying all connections have valid database_type:\n")
        
        connections = session.query(ConnectionModel).all()
        all_valid = True
        
        for conn in connections:
            db_type = conn.database_type
            if hasattr(db_type, 'value'):
                db_type = db_type.value
            db_type_str = str(db_type).lower()
            
            valid_types = ['postgresql', 'sqlserver', 'mysql', 's3']
            is_valid = db_type_str in valid_types
            
            status = "✅" if is_valid else "❌"
            print(f"{status} {conn.name}: {db_type_str}")
            
            if not is_valid:
                all_valid = False
        
        if all_valid:
            print("\n✅ All connections have valid database_type values!")
        else:
            print("\n⚠️  Some connections still have invalid database_type values.")
            print("   You may need to manually update them in the database.")
        
    except Exception as e:
        session.rollback()
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        session.close()
    
    print("\n" + "=" * 70)
    print("Fix Complete")
    print("=" * 70)
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()


