"""Verify cdc_user schema and test table exist."""
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
    conn = oracledb.connect(
        user=ORACLE_CONFIG["user"],
        password=ORACLE_CONFIG["password"],
        dsn=dsn
    )
    cursor = conn.cursor()
    
    print("=== CHECKING CDC_USER SCHEMA ===")
    
    # Check if cdc_user schema exists
    cursor.execute("""
        SELECT COUNT(*) 
        FROM ALL_USERS 
        WHERE USERNAME = 'CDC_USER'
    """)
    exists = cursor.fetchone()[0] > 0
    print(f"CDC_USER schema exists: {exists}")
    
    if exists:
        # Check if test table exists in cdc_user schema
        cursor.execute("""
            SELECT COUNT(*) 
            FROM ALL_TABLES 
            WHERE OWNER = 'CDC_USER' AND TABLE_NAME = 'TEST'
        """)
        table_exists = cursor.fetchone()[0] > 0
        print(f"TEST table in CDC_USER schema: {table_exists}")
        
        if table_exists:
            # Check row count
            cursor.execute("SELECT COUNT(*) FROM CDC_USER.TEST")
            row_count = cursor.fetchone()[0]
            print(f"Rows in CDC_USER.TEST: {row_count}")
            
            # Show sample data
            cursor.execute("SELECT * FROM CDC_USER.TEST ORDER BY ID")
            rows = cursor.fetchall()
            print(f"\nSample data from CDC_USER.TEST:")
            for row in rows[:5]:
                print(f"  {row}")
        else:
            print("\n⚠ TEST table does not exist in CDC_USER schema!")
            print("Options:")
            print("  1. Create the table manually")
            print("  2. Copy data from C##CDC_USER.TEST")
            
            # Try to create the table
            try:
                print("\nAttempting to create TEST table in CDC_USER schema...")
                # Need to connect as CDC_USER or grant privileges
                print("  (Need to connect as CDC_USER or grant CREATE TABLE privilege)")
            except Exception as e:
                print(f"  Error: {e}")
    else:
        print("\n⚠ CDC_USER schema does not exist!")
        print("You need to create it manually in Oracle:")
        print("  CREATE USER cdc_user IDENTIFIED BY cdc_pass;")
        print("  GRANT CONNECT, RESOURCE, CREATE SESSION, CREATE TABLE TO cdc_user;")
        print("  GRANT UNLIMITED TABLESPACE TO cdc_user;")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

