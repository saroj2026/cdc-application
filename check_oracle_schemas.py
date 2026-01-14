"""Check available schemas in Oracle to find one without special characters."""
import oracledb

# Oracle connection details
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
    
    # Get current user
    cursor.execute("SELECT USER FROM DUAL")
    current_user = cursor.fetchone()[0]
    print(f"Current User: {current_user}")
    
    # Check if we can create a new user or use a different schema
    # For now, let's check if we can use the username without the ##
    # Or create a new user
    
    # Check if we can access tables in current schema
    cursor.execute("""
        SELECT TABLE_NAME 
        FROM USER_TABLES 
        WHERE TABLE_NAME = 'TEST'
    """)
    tables = cursor.fetchall()
    print(f"\nTables in current schema: {[t[0] for t in tables]}")
    
    # Check if we can create a new user (need DBA privileges)
    try:
        cursor.execute("SELECT USER FROM DUAL")
        print(f"\nCan create new user? Need to check privileges...")
    except Exception as e:
        print(f"Cannot create user: {e}")
    
    # Alternative: Check if we can use a different existing schema
    cursor.execute("""
        SELECT USERNAME 
        FROM ALL_USERS 
        WHERE USERNAME NOT LIKE 'C##%' 
        AND USERNAME NOT LIKE 'SYS%'
        AND USERNAME NOT LIKE 'SYSTEM%'
        ORDER BY USERNAME
    """)
    other_users = cursor.fetchall()
    print(f"\nOther available schemas (without C##):")
    for user in other_users[:10]:  # Show first 10
        print(f"  - {user[0]}")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

