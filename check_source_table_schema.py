"""Check PostgreSQL source table schema."""

import psycopg2

DB_CONFIG = {
    "host": "72.61.233.209",
    "port": 5432,
    "database": "cdctest",
    "user": "cdc_user",
    "password": "cdc_pass"
}

print("=" * 70)
print("Checking PostgreSQL Source Table Schema")
print("=" * 70)

try:
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    print("\n1. Getting table schema for: public.projects_simple")
    
    cursor.execute("""
        SELECT 
            column_name,
            data_type,
            character_maximum_length,
            numeric_precision,
            numeric_scale,
            is_nullable,
            column_default
        FROM information_schema.columns
        WHERE table_schema = 'public' 
        AND table_name = 'projects_simple'
        ORDER BY ordinal_position
    """)
    
    columns = cursor.fetchall()
    
    if not columns:
        print("   ❌ Table not found!")
        exit(1)
    
    print(f"\n2. Table Schema ({len(columns)} columns):")
    print("-" * 70)
    print(f"{'Column':<30} {'Type':<20} {'Nullable':<10} {'Default'}")
    print("-" * 70)
    
    for col in columns:
        col_name, data_type, max_len, precision, scale, nullable, default = col
        
        # Format type
        if data_type == 'character varying' or data_type == 'varchar':
            type_str = f"VARCHAR({max_len})" if max_len else "VARCHAR"
        elif data_type == 'numeric':
            if precision and scale:
                type_str = f"NUMERIC({precision},{scale})"
            elif precision:
                type_str = f"NUMERIC({precision})"
            else:
                type_str = "NUMERIC"
        elif data_type == 'integer':
            type_str = "INTEGER"
        elif data_type == 'bigint':
            type_str = "BIGINT"
        elif data_type == 'timestamp without time zone':
            type_str = "TIMESTAMP_NTZ"
        elif data_type == 'timestamp with time zone':
            type_str = "TIMESTAMP_TZ"
        elif data_type == 'boolean':
            type_str = "BOOLEAN"
        elif data_type == 'text':
            type_str = "TEXT"
        else:
            type_str = data_type.upper()
        
        default_str = str(default) if default else ""
        nullable_str = "YES" if nullable == "YES" else "NO"
        
        print(f"{col_name:<30} {type_str:<20} {nullable_str:<10} {default_str}")
    
    # Get primary key
    cursor.execute("""
        SELECT a.attname
        FROM pg_index i
        JOIN pg_attribute a ON a.attrelid = i.indrelid AND a.attnum = ANY(i.indkey)
        WHERE i.indrelid = 'public.projects_simple'::regclass
        AND i.indisprimary
        ORDER BY a.attnum
    """)
    
    pk_columns = [row[0] for row in cursor.fetchall()]
    
    print("\n3. Primary Key:")
    if pk_columns:
        print(f"   {', '.join(pk_columns)}")
    else:
        print("   No primary key found")
    
    # Generate Snowflake CREATE TABLE statement
    print("\n4. Snowflake CREATE TABLE Statement:")
    print("-" * 70)
    
    print(f"CREATE TABLE IF NOT EXISTS seg.public.projects_simple (")
    
    col_defs = []
    for col in columns:
        col_name, data_type, max_len, precision, scale, nullable, default = col
        
        # Map PostgreSQL types to Snowflake types
        if data_type == 'character varying' or data_type == 'varchar':
            sf_type = f"VARCHAR({max_len})" if max_len else "VARCHAR(16777216)"
        elif data_type == 'numeric':
            if precision and scale:
                sf_type = f"NUMBER({precision},{scale})"
            elif precision:
                sf_type = f"NUMBER({precision})"
            else:
                sf_type = "NUMBER(38,0)"
        elif data_type == 'integer':
            sf_type = "INTEGER"
        elif data_type == 'bigint':
            sf_type = "BIGINT"
        elif data_type == 'timestamp without time zone':
            sf_type = "TIMESTAMP_NTZ"
        elif data_type == 'timestamp with time zone':
            sf_type = "TIMESTAMP_TZ"
        elif data_type == 'boolean':
            sf_type = "BOOLEAN"
        elif data_type == 'text':
            sf_type = "TEXT"
        else:
            sf_type = data_type.upper()
        
        nullable_clause = "" if nullable == "YES" else " NOT NULL"
        col_defs.append(f"    {col_name.upper()} {sf_type}{nullable_clause}")
    
    print(",\n".join(col_defs))
    print(");")
    
    if pk_columns:
        print(f"\n-- Primary key constraint (if needed):")
        print(f"ALTER TABLE seg.public.projects_simple ADD PRIMARY KEY ({', '.join([c.upper() for c in pk_columns])});")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)

