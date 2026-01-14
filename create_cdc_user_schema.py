"""Create a new Oracle user/schema 'cdc_user' without special characters."""
import oracledb

# Oracle connection details (using existing admin user)
ORACLE_CONFIG = {
    "host": "72.61.233.209",
    "port": 1521,
    "user": "c##cdc_user",  # Current user with DBA privileges
    "password": "cdc_pass",
    "service_name": "XE"
}

NEW_USER = "cdc_user"
NEW_PASSWORD = "cdc_pass"

try:
    dsn = oracledb.makedsn(ORACLE_CONFIG["host"], ORACLE_CONFIG["port"], service_name=ORACLE_CONFIG["service_name"])
    conn = oracledb.connect(
        user=ORACLE_CONFIG["user"],
        password=ORACLE_CONFIG["password"],
        dsn=dsn,
        mode=oracledb.AUTH_MODE_SYSDBA  # Need SYSDBA to create users
    )
    cursor = conn.cursor()
    
    print(f"=== CREATING NEW ORACLE USER: {NEW_USER} ===")
    
    # Check if user already exists
    cursor.execute(f"""
        SELECT COUNT(*) 
        FROM ALL_USERS 
        WHERE USERNAME = UPPER('{NEW_USER}')
    """)
    exists = cursor.fetchone()[0] > 0
    
    if exists:
        print(f"User {NEW_USER} already exists. Dropping and recreating...")
        try:
            cursor.execute(f"DROP USER {NEW_USER} CASCADE")
            conn.commit()
            print(f"✓ Dropped existing user {NEW_USER}")
        except Exception as e:
            print(f"Note: {e}")
    
    # Create new user
    cursor.execute(f"""
        CREATE USER {NEW_USER} IDENTIFIED BY {NEW_PASSWORD}
        DEFAULT TABLESPACE USERS
        TEMPORARY TABLESPACE TEMP
        QUOTA UNLIMITED ON USERS
    """)
    conn.commit()
    print(f"✓ Created user {NEW_USER}")
    
    # Grant necessary privileges
    cursor.execute(f"GRANT CONNECT, RESOURCE TO {NEW_USER}")
    cursor.execute(f"GRANT CREATE SESSION TO {NEW_USER}")
    cursor.execute(f"GRANT CREATE TABLE TO {NEW_USER}")
    cursor.execute(f"GRANT UNLIMITED TABLESPACE TO {NEW_USER}")
    # Grant LogMiner privileges for CDC
    cursor.execute(f"GRANT SELECT_CATALOG_ROLE TO {NEW_USER}")
    cursor.execute(f"GRANT EXECUTE_CATALOG_ROLE TO {NEW_USER}")
    conn.commit()
    print(f"✓ Granted privileges to {NEW_USER}")
    
    # Create test table in new schema
    # Connect as new user
    cursor.close()
    conn.close()
    
    # Connect as new user
    conn2 = oracledb.connect(
        user=NEW_USER,
        password=NEW_PASSWORD,
        dsn=dsn
    )
    cursor2 = conn2.cursor()
    
    # Create test table
    cursor2.execute("""
        CREATE TABLE test (
            id NUMBER PRIMARY KEY,
            name VARCHAR2(100),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn2.commit()
    print(f"✓ Created test table in {NEW_USER} schema")
    
    # Insert some test data
    cursor2.execute("""
        INSERT INTO test (id, name) VALUES (1, 'Test Record 1')
    """)
    cursor2.execute("""
        INSERT INTO test (id, name) VALUES (2, 'Test Record 2')
    """)
    conn2.commit()
    print(f"✓ Inserted test data")
    
    cursor2.close()
    conn2.close()
    
    print(f"\n=== SUCCESS ===")
    print(f"Created Oracle user: {NEW_USER}")
    print(f"Created test table with sample data")
    print(f"Pipeline can now use schema: {NEW_USER}")
    
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
    # Try without SYSDBA mode
    print(f"\nTrying without SYSDBA mode...")
    try:
        dsn = oracledb.makedsn(ORACLE_CONFIG["host"], ORACLE_CONFIG["port"], service_name=ORACLE_CONFIG["service_name"])
        conn = oracledb.connect(
            user=ORACLE_CONFIG["user"],
            password=ORACLE_CONFIG["password"],
            dsn=dsn
        )
        cursor = conn.cursor()
        
        # Try to create user (might work if current user has CREATE USER privilege)
        cursor.execute(f"""
            CREATE USER {NEW_USER} IDENTIFIED BY {NEW_PASSWORD}
            DEFAULT TABLESPACE USERS
            TEMPORARY TABLESPACE TEMP
        """)
        conn.commit()
        print(f"✓ Created user {NEW_USER} (without SYSDBA)")
        
        cursor.execute(f"GRANT CONNECT, RESOURCE TO {NEW_USER}")
        cursor.execute(f"GRANT CREATE SESSION TO {NEW_USER}")
        cursor.execute(f"GRANT CREATE TABLE TO {NEW_USER}")
        conn.commit()
        print(f"✓ Granted privileges")
        
        cursor.close()
        conn.close()
    except Exception as e2:
        print(f"ERROR (without SYSDBA): {e2}")
        print(f"\nYou may need to create the user manually in Oracle:")
        print(f"  CREATE USER {NEW_USER} IDENTIFIED BY {NEW_PASSWORD};")
        print(f"  GRANT CONNECT, RESOURCE, CREATE SESSION, CREATE TABLE TO {NEW_USER};")
        print(f"  GRANT UNLIMITED TABLESPACE TO {NEW_USER};")

