"""Python script to grant Oracle permissions - connects to Oracle and grants privileges."""
import oracledb
import sys

# Oracle connection details
ORACLE_HOST = "72.61.233.209"
ORACLE_PORT = 1521
ORACLE_SERVICE = "XE"
ORACLE_USER_SYS = "sys"  # Change if needed
ORACLE_PASSWORD_SYS = "oracle"  # Change if needed - you need to provide this

# Users to grant permissions to
USERS = ["cdc_user", "c##cdc_user"]

print("=== GRANTING ORACLE PERMISSIONS FOR DEBEZIUM ===")
print(f"This script grants necessary permissions to: {', '.join(USERS)}")
print(f"WARNING: This requires SYSDBA privileges")
print()

# Get sys password if not provided
if ORACLE_PASSWORD_SYS == "oracle":
    password = input("Enter SYSDBA password (default: oracle): ").strip()
    if password:
        ORACLE_PASSWORD_SYS = password

try:
    # Connect as SYSDBA
    dsn = f"{ORACLE_HOST}:{ORACLE_PORT}/{ORACLE_SERVICE}"
    print(f"Connecting to Oracle as SYSDBA...")
    conn = oracledb.connect(
        user=ORACLE_USER_SYS,
        password=ORACLE_PASSWORD_SYS,
        dsn=dsn,
        mode=oracledb.AUTH_MODE_SYSDBA
    )
    cursor = conn.cursor()
    
    print("✓ Connected successfully")
    print()
    
    # Permissions to grant
    permissions = [
        "CREATE SESSION",
        "CONNECT",
        "RESOURCE",
        "LOGMINING",
        "SELECT ANY TRANSACTION",
        "SELECT ANY DICTIONARY",
        "FLASHBACK ANY TABLE",
        "SELECT_CATALOG_ROLE"
    ]
    
    # Grant permissions to each user
    for user in USERS:
        print(f"Granting permissions to {user}...")
        for perm in permissions:
            try:
                if perm == "SELECT_CATALOG_ROLE":
                    # This is a role, not a privilege
                    sql = f"GRANT {perm} TO {user}"
                else:
                    sql = f"GRANT {perm} TO {user}"
                cursor.execute(sql)
                print(f"  ✓ Granted {perm}")
            except Exception as e:
                print(f"  ⚠ Error granting {perm}: {e}")
        
        # Grant execute on DBMS_LOGMNR
        try:
            cursor.execute(f"GRANT EXECUTE ON SYS.DBMS_LOGMNR TO {user}")
            print(f"  ✓ Granted EXECUTE ON SYS.DBMS_LOGMNR")
        except Exception as e:
            print(f"  ⚠ Error granting EXECUTE ON DBMS_LOGMNR: {e}")
        
        # Grant execute on DBMS_LOGMNR_D
        try:
            cursor.execute(f"GRANT EXECUTE ON SYS.DBMS_LOGMNR_D TO {user}")
            print(f"  ✓ Granted EXECUTE ON SYS.DBMS_LOGMNR_D")
        except Exception as e:
            print(f"  ⚠ Error granting EXECUTE ON DBMS_LOGMNR_D: {e}")
        
        # Grant select on test table (if using c##cdc_user to access cdc_user schema)
        if user == "c##cdc_user":
            try:
                cursor.execute("GRANT SELECT ON cdc_user.test TO c##cdc_user")
                print(f"  ✓ Granted SELECT ON cdc_user.test")
            except Exception as e:
                print(f"  ⚠ Error granting SELECT ON cdc_user.test: {e}")
        
        print()
    
    # Commit
    conn.commit()
    print("✓ All permissions granted successfully!")
    print()
    
    # Verify permissions
    print("=== VERIFYING PERMISSIONS ===")
    for user in USERS:
        print(f"\nPermissions for {user}:")
        cursor.execute("""
            SELECT PRIVILEGE 
            FROM DBA_SYS_PRIVS 
            WHERE GRANTEE = :user
            ORDER BY PRIVILEGE
        """, user=user.upper())
        privs = cursor.fetchall()
        for priv in privs:
            print(f"  - {priv[0]}")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"ERROR: {e}")
    print()
    print("Make sure:")
    print("1. Oracle client library is installed: pip install oracledb")
    print("2. You have SYSDBA credentials")
    print("3. Oracle is accessible from this machine")
    print()
    print("Alternatively, you can run the SQL script directly on the Oracle server:")
    print("  sqlplus sys/password@XE as sysdba")
    print("  @grant_oracle_permissions.sql")
    sys.exit(1)

print()
print("=== NEXT STEPS ===")
print("1. Permissions have been granted")
print("2. Restart the Oracle connector")
print("3. The connector should now be able to perform snapshots and start CDC")

