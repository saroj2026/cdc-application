"""Create test table in Oracle for pipeline testing."""

from ingestion.connectors.oracle import OracleConnector

print("=" * 70)
print("Creating Test Table in Oracle")
print("=" * 70)

# Oracle connection details
config = {
    "host": "72.61.233.209",
    "port": 1521,
    "database": "XE",
    "user": "c##cdc_user",
    "password": "cdc_pass",
    "schema": "c##cdc_user"
}

try:
    # Connect to Oracle
    print("\n1. Connecting to Oracle...")
    connector = OracleConnector(config)
    if not connector.test_connection():
        print("❌ Connection failed")
        exit(1)
    print("   ✅ Connected successfully")
    
    # Get connection
    conn = connector.connect()
    cursor = conn.cursor()
    
    # Drop table if exists
    print("\n2. Dropping existing test table if it exists...")
    try:
        cursor.execute("DROP TABLE c##cdc_user.test")
        conn.commit()
        print("   ✅ Dropped existing table")
    except Exception as e:
        if "does not exist" in str(e).lower() or "ORA-00942" in str(e):
            print("   ℹ️  Table doesn't exist, will create new one")
        else:
            print(f"   ⚠️  Error dropping table: {e}")
    
    # Create test table
    print("\n3. Creating test table...")
    create_table_sql = """
    CREATE TABLE c##cdc_user.test (
        id NUMBER PRIMARY KEY,
        name VARCHAR2(100),
        email VARCHAR2(100),
        created_date DATE DEFAULT SYSDATE,
        updated_date DATE DEFAULT SYSDATE,
        status VARCHAR2(20) DEFAULT 'active'
    )
    """
    cursor.execute(create_table_sql)
    conn.commit()
    print("   ✅ Table 'test' created successfully")
    
    # Insert some test data
    print("\n4. Inserting test data...")
    insert_sql = """
    INSERT INTO c##cdc_user.test (id, name, email, status) 
    VALUES (:id, :name, :email, :status)
    """
    
    test_data = [
        (1, 'John Doe', 'john@example.com', 'active'),
        (2, 'Jane Smith', 'jane@example.com', 'active'),
        (3, 'Bob Johnson', 'bob@example.com', 'inactive'),
        (4, 'Alice Brown', 'alice@example.com', 'active'),
        (5, 'Charlie Wilson', 'charlie@example.com', 'active')
    ]
    
    cursor.executemany(insert_sql, [
        {"id": id, "name": name, "email": email, "status": status}
        for id, name, email, status in test_data
    ])
    conn.commit()
    print(f"   ✅ Inserted {len(test_data)} test records")
    
    # Verify table and data
    print("\n5. Verifying table and data...")
    cursor.execute("SELECT COUNT(*) FROM c##cdc_user.test")
    count = cursor.fetchone()[0]
    print(f"   ✅ Table has {count} records")
    
    cursor.execute("SELECT * FROM c##cdc_user.test ORDER BY id")
    rows = cursor.fetchall()
    print("\n   Sample data:")
    for row in rows[:5]:
        print(f"      ID: {row[0]}, Name: {row[1]}, Email: {row[2]}")
    
    cursor.close()
    connector.disconnect()
    
    print("\n" + "=" * 70)
    print("✅ Test table created successfully!")
    print("=" * 70)
    print("\nTable: c##cdc_user.test")
    print("Records: 5")
    print("\nReady for pipeline creation!")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

