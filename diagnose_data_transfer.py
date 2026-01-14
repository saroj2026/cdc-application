"""Diagnose data transfer issue - check source and target data."""

import sys
import requests
import psycopg2
import pyodbc
from typing import Dict, Any, Optional

# Configure encoding for Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

API_BASE_URL = "http://localhost:8000"

def print_status(message: str, status: str = "INFO"):
    """Print colored status message."""
    colors = {
        "INFO": "\033[94m",
        "SUCCESS": "\033[92m",
        "ERROR": "\033[91m",
        "WARNING": "\033[93m",
        "RESET": "\033[0m"
    }
    symbol = {
        "INFO": "ℹ",
        "SUCCESS": "✓",
        "ERROR": "✗",
        "WARNING": "⚠"
    }
    print(f"{colors.get(status, '')}{symbol.get(status, '')} {message}{colors['RESET']}")

def get_pipeline_info():
    """Get pipeline information."""
    try:
        response = requests.get(f"{API_BASE_URL}/api/pipelines")
        response.raise_for_status()
        pipelines = response.json()
        
        for pipeline in pipelines:
            if pipeline.get("name") == "final_test":
                return pipeline
        return None
    except Exception as e:
        print_status(f"Failed to get pipeline: {e}", "ERROR")
        return None

def get_connection_details(connection_id: str):
    """Get connection details."""
    try:
        response = requests.get(f"{API_BASE_URL}/api/v1/connections/{connection_id}")
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print_status(f"Failed to get connection: {e}", "ERROR")
        return None

def check_postgresql_data(host: str, port: int, database: str, user: str, password: str, schema: str, table: str):
    """Check PostgreSQL data."""
    try:
        conn = psycopg2.connect(
            host=host,
            port=port,
            database=database,
            user=user,
            password=password,
            connect_timeout=10
        )
        cursor = conn.cursor()
        
        # Get row count
        cursor.execute(f"SELECT COUNT(*) FROM {schema}.{table}")
        row_count = cursor.fetchone()[0]
        
        # Get sample data
        cursor.execute(f"SELECT * FROM {schema}.{table} LIMIT 5")
        columns = [desc[0] for desc in cursor.description]
        rows = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return {
            "row_count": row_count,
            "columns": columns,
            "sample_rows": rows
        }
    except Exception as e:
        print_status(f"Failed to check PostgreSQL: {e}", "ERROR")
        return None

def check_sqlserver_data(server: str, port: int, database: str, user: str, password: str, schema: str, table: str):
    """Check SQL Server data."""
    try:
        # Build connection string
        conn_str = (
            f"DRIVER={{ODBC Driver 17 for SQL Server}};"
            f"SERVER={server},{port};"
            f"DATABASE={database};"
            f"UID={user};"
            f"PWD={password};"
            f"TrustServerCertificate=yes;"
            f"Encrypt=no;"
        )
        
        conn = pyodbc.connect(conn_str, timeout=10)
        cursor = conn.cursor()
        
        # Get row count
        cursor.execute(f"SELECT COUNT(*) FROM [{schema}].[{table}]")
        row_count = cursor.fetchone()[0]
        
        # Get sample data
        cursor.execute(f"SELECT TOP 5 * FROM [{schema}].[{table}]")
        columns = [desc[0] for desc in cursor.description]
        rows = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return {
            "row_count": row_count,
            "columns": columns,
            "sample_rows": rows
        }
    except Exception as e:
        print_status(f"Failed to check SQL Server: {e}", "ERROR")
        return None

def main():
    """Main diagnostic function."""
    print("\n" + "="*60)
    print("DATA TRANSFER DIAGNOSTIC")
    print("="*60 + "\n")
    
    # Step 1: Get pipeline info
    print_status("Step 1: Getting pipeline information...", "INFO")
    pipeline = get_pipeline_info()
    if not pipeline:
        print_status("Pipeline 'final_test' not found", "ERROR")
        return 1
    
    pipeline_id = pipeline.get("id")
    source_conn_id = pipeline.get("source_connection_id")
    target_conn_id = pipeline.get("target_connection_id")
    source_table = pipeline.get("source_tables", [])[0] if pipeline.get("source_tables") else None
    
    print_status(f"Pipeline ID: {pipeline_id}", "INFO")
    print_status(f"Source Connection: {source_conn_id}", "INFO")
    print_status(f"Target Connection: {target_conn_id}", "INFO")
    print_status(f"Table: {source_table}", "INFO")
    
    # Step 2: Get connection details
    print_status("\nStep 2: Getting connection details...", "INFO")
    source_conn = get_connection_details(source_conn_id)
    target_conn = get_connection_details(target_conn_id)
    
    if not source_conn or not target_conn:
        print_status("Failed to get connection details", "ERROR")
        return 1
    
    # Step 3: Check PostgreSQL data
    print_status("\nStep 3: Checking PostgreSQL source data...", "INFO")
    pg_data = check_postgresql_data(
        host=source_conn.get("host"),
        port=source_conn.get("port"),
        database=source_conn.get("database"),
        user=source_conn.get("username"),
        password=source_conn.get("password"),
        schema=pipeline.get("source_schema", "public"),
        table=source_table
    )
    
    if pg_data:
        print_status(f"PostgreSQL row count: {pg_data['row_count']}", "SUCCESS" if pg_data['row_count'] > 0 else "WARNING")
        print_status(f"Columns: {', '.join(pg_data['columns'])}", "INFO")
        if pg_data['sample_rows']:
            print_status("Sample rows:", "INFO")
            for i, row in enumerate(pg_data['sample_rows'], 1):
                print(f"  Row {i}: {row}")
    else:
        print_status("Failed to retrieve PostgreSQL data", "ERROR")
        return 1
    
    # Step 4: Check SQL Server data
    print_status("\nStep 4: Checking SQL Server target data...", "INFO")
    sql_data = check_sqlserver_data(
        server=target_conn.get("host"),
        port=target_conn.get("port"),
        database=target_conn.get("database"),
        user=target_conn.get("username"),
        password=target_conn.get("password"),
        schema=pipeline.get("target_schema", "dbo"),
        table=source_table
    )
    
    if sql_data:
        print_status(f"SQL Server row count: {sql_data['row_count']}", "SUCCESS" if sql_data['row_count'] > 0 else "ERROR")
        print_status(f"Columns: {', '.join(sql_data['columns'])}", "INFO")
        if sql_data['sample_rows']:
            print_status("Sample rows:", "INFO")
            for i, row in enumerate(sql_data['sample_rows'], 1):
                print(f"  Row {i}: {row}")
        else:
            print_status("No rows found in SQL Server", "ERROR")
    else:
        print_status("Failed to retrieve SQL Server data", "ERROR")
        return 1
    
    # Step 5: Compare
    print_status("\nStep 5: Comparison...", "INFO")
    print("="*60)
    print(f"PostgreSQL: {pg_data['row_count']} rows")
    print(f"SQL Server: {sql_data['row_count']} rows")
    print("="*60)
    
    if pg_data['row_count'] > 0 and sql_data['row_count'] == 0:
        print_status("ISSUE DETECTED: Source has data but target is empty!", "ERROR")
        print_status("This should have been caught by validation", "ERROR")
        return 1
    elif pg_data['row_count'] == sql_data['row_count']:
        print_status("Data matches!", "SUCCESS")
        return 0
    else:
        print_status(f"Row count mismatch: {pg_data['row_count']} vs {sql_data['row_count']}", "WARNING")
        return 1

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print_status("\nDiagnostic interrupted", "WARNING")
        sys.exit(1)
    except Exception as e:
        print_status(f"Unexpected error: {e}", "ERROR")
        import traceback
        traceback.print_exc()
        sys.exit(1)


import sys
import requests
import psycopg2
import pyodbc
from typing import Dict, Any, Optional

# Configure encoding for Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

API_BASE_URL = "http://localhost:8000"

def print_status(message: str, status: str = "INFO"):
    """Print colored status message."""
    colors = {
        "INFO": "\033[94m",
        "SUCCESS": "\033[92m",
        "ERROR": "\033[91m",
        "WARNING": "\033[93m",
        "RESET": "\033[0m"
    }
    symbol = {
        "INFO": "ℹ",
        "SUCCESS": "✓",
        "ERROR": "✗",
        "WARNING": "⚠"
    }
    print(f"{colors.get(status, '')}{symbol.get(status, '')} {message}{colors['RESET']}")

def get_pipeline_info():
    """Get pipeline information."""
    try:
        response = requests.get(f"{API_BASE_URL}/api/pipelines")
        response.raise_for_status()
        pipelines = response.json()
        
        for pipeline in pipelines:
            if pipeline.get("name") == "final_test":
                return pipeline
        return None
    except Exception as e:
        print_status(f"Failed to get pipeline: {e}", "ERROR")
        return None

def get_connection_details(connection_id: str):
    """Get connection details."""
    try:
        response = requests.get(f"{API_BASE_URL}/api/v1/connections/{connection_id}")
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print_status(f"Failed to get connection: {e}", "ERROR")
        return None

def check_postgresql_data(host: str, port: int, database: str, user: str, password: str, schema: str, table: str):
    """Check PostgreSQL data."""
    try:
        conn = psycopg2.connect(
            host=host,
            port=port,
            database=database,
            user=user,
            password=password,
            connect_timeout=10
        )
        cursor = conn.cursor()
        
        # Get row count
        cursor.execute(f"SELECT COUNT(*) FROM {schema}.{table}")
        row_count = cursor.fetchone()[0]
        
        # Get sample data
        cursor.execute(f"SELECT * FROM {schema}.{table} LIMIT 5")
        columns = [desc[0] for desc in cursor.description]
        rows = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return {
            "row_count": row_count,
            "columns": columns,
            "sample_rows": rows
        }
    except Exception as e:
        print_status(f"Failed to check PostgreSQL: {e}", "ERROR")
        return None

def check_sqlserver_data(server: str, port: int, database: str, user: str, password: str, schema: str, table: str):
    """Check SQL Server data."""
    try:
        # Build connection string
        conn_str = (
            f"DRIVER={{ODBC Driver 17 for SQL Server}};"
            f"SERVER={server},{port};"
            f"DATABASE={database};"
            f"UID={user};"
            f"PWD={password};"
            f"TrustServerCertificate=yes;"
            f"Encrypt=no;"
        )
        
        conn = pyodbc.connect(conn_str, timeout=10)
        cursor = conn.cursor()
        
        # Get row count
        cursor.execute(f"SELECT COUNT(*) FROM [{schema}].[{table}]")
        row_count = cursor.fetchone()[0]
        
        # Get sample data
        cursor.execute(f"SELECT TOP 5 * FROM [{schema}].[{table}]")
        columns = [desc[0] for desc in cursor.description]
        rows = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return {
            "row_count": row_count,
            "columns": columns,
            "sample_rows": rows
        }
    except Exception as e:
        print_status(f"Failed to check SQL Server: {e}", "ERROR")
        return None

def main():
    """Main diagnostic function."""
    print("\n" + "="*60)
    print("DATA TRANSFER DIAGNOSTIC")
    print("="*60 + "\n")
    
    # Step 1: Get pipeline info
    print_status("Step 1: Getting pipeline information...", "INFO")
    pipeline = get_pipeline_info()
    if not pipeline:
        print_status("Pipeline 'final_test' not found", "ERROR")
        return 1
    
    pipeline_id = pipeline.get("id")
    source_conn_id = pipeline.get("source_connection_id")
    target_conn_id = pipeline.get("target_connection_id")
    source_table = pipeline.get("source_tables", [])[0] if pipeline.get("source_tables") else None
    
    print_status(f"Pipeline ID: {pipeline_id}", "INFO")
    print_status(f"Source Connection: {source_conn_id}", "INFO")
    print_status(f"Target Connection: {target_conn_id}", "INFO")
    print_status(f"Table: {source_table}", "INFO")
    
    # Step 2: Get connection details
    print_status("\nStep 2: Getting connection details...", "INFO")
    source_conn = get_connection_details(source_conn_id)
    target_conn = get_connection_details(target_conn_id)
    
    if not source_conn or not target_conn:
        print_status("Failed to get connection details", "ERROR")
        return 1
    
    # Step 3: Check PostgreSQL data
    print_status("\nStep 3: Checking PostgreSQL source data...", "INFO")
    pg_data = check_postgresql_data(
        host=source_conn.get("host"),
        port=source_conn.get("port"),
        database=source_conn.get("database"),
        user=source_conn.get("username"),
        password=source_conn.get("password"),
        schema=pipeline.get("source_schema", "public"),
        table=source_table
    )
    
    if pg_data:
        print_status(f"PostgreSQL row count: {pg_data['row_count']}", "SUCCESS" if pg_data['row_count'] > 0 else "WARNING")
        print_status(f"Columns: {', '.join(pg_data['columns'])}", "INFO")
        if pg_data['sample_rows']:
            print_status("Sample rows:", "INFO")
            for i, row in enumerate(pg_data['sample_rows'], 1):
                print(f"  Row {i}: {row}")
    else:
        print_status("Failed to retrieve PostgreSQL data", "ERROR")
        return 1
    
    # Step 4: Check SQL Server data
    print_status("\nStep 4: Checking SQL Server target data...", "INFO")
    sql_data = check_sqlserver_data(
        server=target_conn.get("host"),
        port=target_conn.get("port"),
        database=target_conn.get("database"),
        user=target_conn.get("username"),
        password=target_conn.get("password"),
        schema=pipeline.get("target_schema", "dbo"),
        table=source_table
    )
    
    if sql_data:
        print_status(f"SQL Server row count: {sql_data['row_count']}", "SUCCESS" if sql_data['row_count'] > 0 else "ERROR")
        print_status(f"Columns: {', '.join(sql_data['columns'])}", "INFO")
        if sql_data['sample_rows']:
            print_status("Sample rows:", "INFO")
            for i, row in enumerate(sql_data['sample_rows'], 1):
                print(f"  Row {i}: {row}")
        else:
            print_status("No rows found in SQL Server", "ERROR")
    else:
        print_status("Failed to retrieve SQL Server data", "ERROR")
        return 1
    
    # Step 5: Compare
    print_status("\nStep 5: Comparison...", "INFO")
    print("="*60)
    print(f"PostgreSQL: {pg_data['row_count']} rows")
    print(f"SQL Server: {sql_data['row_count']} rows")
    print("="*60)
    
    if pg_data['row_count'] > 0 and sql_data['row_count'] == 0:
        print_status("ISSUE DETECTED: Source has data but target is empty!", "ERROR")
        print_status("This should have been caught by validation", "ERROR")
        return 1
    elif pg_data['row_count'] == sql_data['row_count']:
        print_status("Data matches!", "SUCCESS")
        return 0
    else:
        print_status(f"Row count mismatch: {pg_data['row_count']} vs {sql_data['row_count']}", "WARNING")
        return 1

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print_status("\nDiagnostic interrupted", "WARNING")
        sys.exit(1)
    except Exception as e:
        print_status(f"Unexpected error: {e}", "ERROR")
        import traceback
        traceback.print_exc()
        sys.exit(1)

