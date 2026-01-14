"""Create test table in cdc_user schema or copy from c##cdc_user."""
import oracledb

ORACLE_CONFIG = {
    "host": "72.61.233.209",
    "port": 1521,
    "user": "c##cdc_user",
    "password": "cdc_pass",
    "service_name": "XE"
}

try:
    dsn = oracledb.makedsn(ORACLE_CONFIG["host"], ORACLE_CONFIG["port"], service_name=ORACLE_CONFIG["service_name"])
    
    # First, try to connect as cdc_user directly
    try:
        conn = oracledb.connect(
            user="cdc_user",
            password="cdc_pass",
            dsn=dsn
        )
        cursor = conn.cursor()
        print("✓ Connected as cdc_user")
        
        # Check if table exists
        cursor.execute("""
            SELECT COUNT(*) 
            FROM USER_TABLES 
            WHERE TABLE_NAME = 'TEST'
        """)
        exists = cursor.fetchone()[0] > 0
        
        if not exists:
            # Create test table
            cursor.execute("""
                CREATE TABLE test (
                    id NUMBER PRIMARY KEY,
                    name VARCHAR2(100),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()
            print("✓ Created TEST table in cdc_user schema")
            
            # Insert sample data
            cursor.execute("INSERT INTO test (id, name) VALUES (1, 'Test Record 1')")
            cursor.execute("INSERT INTO test (id, name) VALUES (2, 'Test Record 2')")
            cursor.execute("INSERT INTO test (id, name) VALUES (3, 'Test Record 3')")
            conn.commit()
            print("✓ Inserted sample data")
        else:
            print("✓ TEST table already exists in cdc_user schema")
            cursor.execute("SELECT COUNT(*) FROM test")
            count = cursor.fetchone()[0]
            print(f"  Row count: {count}")
        
        cursor.close()
        conn.close()
        
    except oracledb.exceptions.DatabaseError as e:
        if "ORA-01017" in str(e):
            print("⚠ Cannot connect as cdc_user (invalid credentials)")
            print("Trying to create/copy using c##cdc_user...")
            
            # Connect as c##cdc_user and try to create table in cdc_user schema
            conn = oracledb.connect(
                user=ORACLE_CONFIG["user"],
                password=ORACLE_CONFIG["password"],
                dsn=dsn
            )
            cursor = conn.cursor()
            
            # Grant privileges to cdc_user
            try:
                cursor.execute("GRANT CREATE TABLE TO cdc_user")
                cursor.execute("GRANT UNLIMITED TABLESPACE TO cdc_user")
                conn.commit()
                print("✓ Granted privileges to cdc_user")
            except Exception as e:
                print(f"Note: {e}")
            
            # Try to create table in cdc_user schema
            try:
                cursor.execute("""
                    CREATE TABLE cdc_user.test (
                        id NUMBER PRIMARY KEY,
                        name VARCHAR2(100),
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                conn.commit()
                print("✓ Created TEST table in cdc_user schema")
                
                # Copy data from c##cdc_user.test if it exists
                cursor.execute("SELECT COUNT(*) FROM ALL_TABLES WHERE OWNER = 'C##CDC_USER' AND TABLE_NAME = 'TEST'")
                if cursor.fetchone()[0] > 0:
                    cursor.execute("INSERT INTO cdc_user.test (id, name) SELECT id, name FROM c##cdc_user.test")
                    conn.commit()
                    print("✓ Copied data from c##cdc_user.test")
                else:
                    # Insert sample data
                    cursor.execute("INSERT INTO cdc_user.test (id, name) VALUES (1, 'Test Record 1')")
                    cursor.execute("INSERT INTO cdc_user.test (id, name) VALUES (2, 'Test Record 2')")
                    conn.commit()
                    print("✓ Inserted sample data")
            except Exception as e:
                print(f"Error creating table: {e}")
                print("\nYou may need to run this manually in Oracle:")
                print("  CONNECT cdc_user/cdc_pass;")
                print("  CREATE TABLE test (id NUMBER PRIMARY KEY, name VARCHAR2(100));")
                print("  INSERT INTO test VALUES (1, 'Test 1');")
            
            cursor.close()
            conn.close()
        else:
            raise

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

