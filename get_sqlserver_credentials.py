"""Get SQL Server credentials from API and test data transfer."""

import sys
import requests
import psycopg2
import pyodbc
from ingestion.connectors.postgresql import PostgreSQLConnector
from ingestion.connectors.sqlserver import SQLServerConnector
from ingestion.transfer import DataTransfer

# Configure encoding for Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

API_BASE_URL = "http://localhost:8000"

def print_status(message: str, status: str = "INFO"):
    """Print colored status message."""
    colors = {
        "INFO": "\033[94m", "SUCCESS": "\033[92m", "ERROR": "\033[91m", 
        "WARNING": "\033[93m", "RESET": "\033[0m"
    }
    symbol = {"INFO": "ℹ", "SUCCESS": "✓", "ERROR": "✗", "WARNING": "⚠"}
    print(f"{colors.get(status, '')}{symbol.get(status, '')} {message}{colors['RESET']}")

def main():
    """Get credentials and test transfer."""
    print("\n" + "="*60)
    print("DATA TRANSFER DIAGNOSTIC")
    print("="*60 + "\n")
    
    # Get pipeline
    try:
        response = requests.get(f"{API_BASE_URL}/api/pipelines")
        response.raise_for_status()
        pipelines = response.json()
        pipeline = next((p for p in pipelines if p.get("name") == "final_test"), None)
        if not pipeline:
            print_status("Pipeline not found", "ERROR")
            return 1
    except Exception as e:
        print_status(f"Failed to get pipeline: {e}", "ERROR")
        return 1
    
    # Get connections
    try:
        source_conn_id = pipeline.get("source_connection_id")
        target_conn_id = pipeline.get("target_connection_id")
        
        response = requests.get(f"{API_BASE_URL}/api/v1/connections/{source_conn_id}")
        source_conn = response.json()
        
        response = requests.get(f"{API_BASE_URL}/api/v1/connections/{target_conn_id}")
        target_conn = response.json()
        
        print_status("Got connection details from API", "SUCCESS")
    except Exception as e:
        print_status(f"Failed to get connections: {e}", "ERROR")
        return 1
    
    # Test PostgreSQL
    print_status("\n=== PostgreSQL Source ===", "INFO")
    try:
        pg_conn = psycopg2.connect(
            host=source_conn["host"],
            port=source_conn["port"],
            database=source_conn["database"],
            user=source_conn["username"],
            password=source_conn["password"],
            connect_timeout=10
        )
        cursor = pg_conn.cursor()
        cursor.execute(f"SELECT COUNT(*) FROM {pipeline.get('source_schema', 'public')}.projects_simple")
        pg_count = cursor.fetchone()[0]
        print_status(f"PostgreSQL has {pg_count} rows", "SUCCESS")
        cursor.close()
        pg_conn.close()
    except Exception as e:
        print_status(f"PostgreSQL check failed: {e}", "ERROR")
        return 1
    
    # Test SQL Server
    print_status("\n=== SQL Server Target ===", "INFO")
    try:
        sql_conn_str = (
            f"DRIVER={{ODBC Driver 17 for SQL Server}};"
            f"SERVER={target_conn['host']},{target_conn['port']};"
            f"DATABASE={target_conn['database']};"
            f"UID={target_conn['username']};"
            f"PWD={target_conn['password']};"
            f"TrustServerCertificate=yes;"
            f"Encrypt=no;"
        )
        
        sql_conn = pyodbc.connect(sql_conn_str, timeout=10)
        cursor = sql_conn.cursor()
        cursor.execute(f"SELECT COUNT(*) FROM [{pipeline.get('target_schema', 'dbo')}].[projects_simple]")
        sql_count = cursor.fetchone()[0]
        print_status(f"SQL Server has {sql_count} rows", "SUCCESS" if sql_count > 0 else "ERROR")
        cursor.close()
        sql_conn.close()
    except Exception as e:
        print_status(f"SQL Server check failed: {e}", "ERROR")
        print_status("This confirms the connection issue", "WARNING")
        return 1
    
    # Compare
    print_status("\n=== Comparison ===", "INFO")
    print(f"PostgreSQL: {pg_count} rows")
    print(f"SQL Server: {sql_count} rows")
    
    if pg_count > 0 and sql_count == 0:
        print_status("ISSUE CONFIRMED: Data not transferred!", "ERROR")
        
        # Try manual transfer
        print_status("\n=== Attempting Manual Transfer ===", "INFO")
        try:
            from ingestion.models import Connection
            
            source_connection = Connection(
                id=source_conn["id"],
                name=source_conn["name"],
                connection_type="source",
                database_type=source_conn["database_type"],
                host=source_conn["host"],
                port=source_conn["port"],
                database=source_conn["database"],
                username=source_conn["username"],
                password=source_conn["password"],
                schema=source_conn.get("schema"),
                additional_config=source_conn.get("additional_config", {})
            )
            
            target_connection = Connection(
                id=target_conn["id"],
                name=target_conn["name"],
                connection_type="target",
                database_type=target_conn["database_type"],
                host=target_conn["host"],
                port=target_conn["port"],
                database=target_conn["database"],
                username=target_conn["username"],
                password=target_conn["password"],
                schema=target_conn.get("schema"),
                additional_config=target_conn.get("additional_config", {})
            )
            
            source_config = source_connection.get_connection_config()
            target_config = target_connection.get_connection_config()
            
            source_connector = PostgreSQLConnector(source_config)
            target_connector = SQLServerConnector(target_config)
            
            transfer = DataTransfer(source_connector, target_connector)
            
            result = transfer.transfer_table(
                table_name="projects_simple",
                source_database=pipeline.get("source_database"),
                source_schema=pipeline.get("source_schema", "public"),
                target_database=pipeline.get("target_database"),
                target_schema=pipeline.get("target_schema", "dbo"),
                transfer_schema=False,
                transfer_data=True,
                batch_size=100
            )
            
            print_status(f"Transfer result: {result.get('rows_transferred', 0)} rows", 
                        "SUCCESS" if result.get('rows_transferred', 0) > 0 else "ERROR")
            
            if result.get("errors"):
                print_status("Errors:", "ERROR")
                for error in result.get("errors", []):
                    print(f"  - {error}")
            
            return 0 if result.get('rows_transferred', 0) > 0 else 1
            
        except Exception as e:
            print_status(f"Manual transfer failed: {e}", "ERROR")
            import traceback
            traceback.print_exc()
            return 1
    
    return 0

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except Exception as e:
        print_status(f"Error: {e}", "ERROR")
        import traceback
        traceback.print_exc()
        sys.exit(1)


import sys
import requests
import psycopg2
import pyodbc
from ingestion.connectors.postgresql import PostgreSQLConnector
from ingestion.connectors.sqlserver import SQLServerConnector
from ingestion.transfer import DataTransfer

# Configure encoding for Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

API_BASE_URL = "http://localhost:8000"

def print_status(message: str, status: str = "INFO"):
    """Print colored status message."""
    colors = {
        "INFO": "\033[94m", "SUCCESS": "\033[92m", "ERROR": "\033[91m", 
        "WARNING": "\033[93m", "RESET": "\033[0m"
    }
    symbol = {"INFO": "ℹ", "SUCCESS": "✓", "ERROR": "✗", "WARNING": "⚠"}
    print(f"{colors.get(status, '')}{symbol.get(status, '')} {message}{colors['RESET']}")

def main():
    """Get credentials and test transfer."""
    print("\n" + "="*60)
    print("DATA TRANSFER DIAGNOSTIC")
    print("="*60 + "\n")
    
    # Get pipeline
    try:
        response = requests.get(f"{API_BASE_URL}/api/pipelines")
        response.raise_for_status()
        pipelines = response.json()
        pipeline = next((p for p in pipelines if p.get("name") == "final_test"), None)
        if not pipeline:
            print_status("Pipeline not found", "ERROR")
            return 1
    except Exception as e:
        print_status(f"Failed to get pipeline: {e}", "ERROR")
        return 1
    
    # Get connections
    try:
        source_conn_id = pipeline.get("source_connection_id")
        target_conn_id = pipeline.get("target_connection_id")
        
        response = requests.get(f"{API_BASE_URL}/api/v1/connections/{source_conn_id}")
        source_conn = response.json()
        
        response = requests.get(f"{API_BASE_URL}/api/v1/connections/{target_conn_id}")
        target_conn = response.json()
        
        print_status("Got connection details from API", "SUCCESS")
    except Exception as e:
        print_status(f"Failed to get connections: {e}", "ERROR")
        return 1
    
    # Test PostgreSQL
    print_status("\n=== PostgreSQL Source ===", "INFO")
    try:
        pg_conn = psycopg2.connect(
            host=source_conn["host"],
            port=source_conn["port"],
            database=source_conn["database"],
            user=source_conn["username"],
            password=source_conn["password"],
            connect_timeout=10
        )
        cursor = pg_conn.cursor()
        cursor.execute(f"SELECT COUNT(*) FROM {pipeline.get('source_schema', 'public')}.projects_simple")
        pg_count = cursor.fetchone()[0]
        print_status(f"PostgreSQL has {pg_count} rows", "SUCCESS")
        cursor.close()
        pg_conn.close()
    except Exception as e:
        print_status(f"PostgreSQL check failed: {e}", "ERROR")
        return 1
    
    # Test SQL Server
    print_status("\n=== SQL Server Target ===", "INFO")
    try:
        sql_conn_str = (
            f"DRIVER={{ODBC Driver 17 for SQL Server}};"
            f"SERVER={target_conn['host']},{target_conn['port']};"
            f"DATABASE={target_conn['database']};"
            f"UID={target_conn['username']};"
            f"PWD={target_conn['password']};"
            f"TrustServerCertificate=yes;"
            f"Encrypt=no;"
        )
        
        sql_conn = pyodbc.connect(sql_conn_str, timeout=10)
        cursor = sql_conn.cursor()
        cursor.execute(f"SELECT COUNT(*) FROM [{pipeline.get('target_schema', 'dbo')}].[projects_simple]")
        sql_count = cursor.fetchone()[0]
        print_status(f"SQL Server has {sql_count} rows", "SUCCESS" if sql_count > 0 else "ERROR")
        cursor.close()
        sql_conn.close()
    except Exception as e:
        print_status(f"SQL Server check failed: {e}", "ERROR")
        print_status("This confirms the connection issue", "WARNING")
        return 1
    
    # Compare
    print_status("\n=== Comparison ===", "INFO")
    print(f"PostgreSQL: {pg_count} rows")
    print(f"SQL Server: {sql_count} rows")
    
    if pg_count > 0 and sql_count == 0:
        print_status("ISSUE CONFIRMED: Data not transferred!", "ERROR")
        
        # Try manual transfer
        print_status("\n=== Attempting Manual Transfer ===", "INFO")
        try:
            from ingestion.models import Connection
            
            source_connection = Connection(
                id=source_conn["id"],
                name=source_conn["name"],
                connection_type="source",
                database_type=source_conn["database_type"],
                host=source_conn["host"],
                port=source_conn["port"],
                database=source_conn["database"],
                username=source_conn["username"],
                password=source_conn["password"],
                schema=source_conn.get("schema"),
                additional_config=source_conn.get("additional_config", {})
            )
            
            target_connection = Connection(
                id=target_conn["id"],
                name=target_conn["name"],
                connection_type="target",
                database_type=target_conn["database_type"],
                host=target_conn["host"],
                port=target_conn["port"],
                database=target_conn["database"],
                username=target_conn["username"],
                password=target_conn["password"],
                schema=target_conn.get("schema"),
                additional_config=target_conn.get("additional_config", {})
            )
            
            source_config = source_connection.get_connection_config()
            target_config = target_connection.get_connection_config()
            
            source_connector = PostgreSQLConnector(source_config)
            target_connector = SQLServerConnector(target_config)
            
            transfer = DataTransfer(source_connector, target_connector)
            
            result = transfer.transfer_table(
                table_name="projects_simple",
                source_database=pipeline.get("source_database"),
                source_schema=pipeline.get("source_schema", "public"),
                target_database=pipeline.get("target_database"),
                target_schema=pipeline.get("target_schema", "dbo"),
                transfer_schema=False,
                transfer_data=True,
                batch_size=100
            )
            
            print_status(f"Transfer result: {result.get('rows_transferred', 0)} rows", 
                        "SUCCESS" if result.get('rows_transferred', 0) > 0 else "ERROR")
            
            if result.get("errors"):
                print_status("Errors:", "ERROR")
                for error in result.get("errors", []):
                    print(f"  - {error}")
            
            return 0 if result.get('rows_transferred', 0) > 0 else 1
            
        except Exception as e:
            print_status(f"Manual transfer failed: {e}", "ERROR")
            import traceback
            traceback.print_exc()
            return 1
    
    return 0

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except Exception as e:
        print_status(f"Error: {e}", "ERROR")
        import traceback
        traceback.print_exc()
        sys.exit(1)

