"""Fix and test data transfer with correct credentials."""

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
    """Test and fix data transfer."""
    print("\n" + "="*60)
    print("FIX AND TEST DATA TRANSFER")
    print("="*60 + "\n")
    
    # Get pipeline and connections from API
    try:
        response = requests.get(f"{API_BASE_URL}/api/pipelines")
        pipelines = response.json()
        pipeline = next((p for p in pipelines if p.get("name") == "final_test"), None)
        if not pipeline:
            print_status("Pipeline not found", "ERROR")
            return 1
        
        source_conn_id = pipeline.get("source_connection_id")
        target_conn_id = pipeline.get("target_connection_id")
        
        response = requests.get(f"{API_BASE_URL}/api/v1/connections/{source_conn_id}")
        source_conn = response.json()
        
        response = requests.get(f"{API_BASE_URL}/api/v1/connections/{target_conn_id}")
        target_conn = response.json()
        
        print_status("Got connection details from API", "SUCCESS")
        print_status(f"SQL Server Host: {target_conn.get('host')}", "INFO")
        print_status(f"SQL Server Port: {target_conn.get('port')}", "INFO")
    except Exception as e:
        print_status(f"Failed to get connections: {e}", "ERROR")
        return 1
    
    # Use provided credentials
    pg_config = {
        "host": "72.61.233.209",
        "port": 5432,
        "database": "cdctest",
        "user": "cdc_user",
        "password": "cdc_pass",
        "schema": "public"
    }
    
    sql_config = {
        "server": target_conn.get("host", "localhost"),  # Use from API
        "port": 1433,
        "database": "cdctest",
        "user": "sa",
        "password": "Sql@12345",
        "schema": "dbo",
        "trust_server_certificate": True,
        "encrypt": False
    }
    
    table_name = "projects_simple"
    
    # Test PostgreSQL
    print_status("\n=== Testing PostgreSQL ===", "INFO")
    try:
        pg_conn = psycopg2.connect(
            host=pg_config["host"],
            port=pg_config["port"],
            database=pg_config["database"],
            user=pg_config["user"],
            password=pg_config["password"],
            connect_timeout=10
        )
        cursor = pg_conn.cursor()
        cursor.execute(f"SELECT COUNT(*) FROM {pg_config['schema']}.{table_name}")
        pg_count = cursor.fetchone()[0]
        print_status(f"PostgreSQL: {pg_count} rows", "SUCCESS")
        cursor.close()
        pg_conn.close()
    except Exception as e:
        print_status(f"PostgreSQL failed: {e}", "ERROR")
        return 1
    
    # Test SQL Server connection
    print_status(f"\n=== Testing SQL Server ({sql_config['server']}:{sql_config['port']}) ===", "INFO")
    try:
        sql_conn_str = (
            f"DRIVER={{ODBC Driver 17 for SQL Server}};"
            f"SERVER={sql_config['server']},{sql_config['port']};"
            f"DATABASE={sql_config['database']};"
            f"UID={sql_config['user']};"
            f"PWD={sql_config['password']};"
            f"TrustServerCertificate=yes;"
            f"Encrypt=no;"
        )
        
        sql_conn = pyodbc.connect(sql_conn_str, timeout=10)
        cursor = sql_conn.cursor()
        cursor.execute(f"SELECT COUNT(*) FROM [{sql_config['schema']}].[{table_name}]")
        sql_count = cursor.fetchone()[0]
        print_status(f"SQL Server: {sql_count} rows", "SUCCESS" if sql_count > 0 else "WARNING")
        cursor.close()
        sql_conn.close()
    except Exception as e:
        print_status(f"SQL Server connection failed: {e}", "ERROR")
        print_status(f"Trying to connect to: {sql_config['server']}:{sql_config['port']}", "INFO")
        print_status("Please verify SQL Server host and credentials", "WARNING")
        return 1
    
    # Compare
    print_status(f"\n=== Comparison ===", "INFO")
    print(f"PostgreSQL: {pg_count} rows")
    print(f"SQL Server: {sql_count} rows")
    
    if pg_count > 0 and sql_count == 0:
        print_status("Data not transferred - attempting transfer...", "INFO")
        
        try:
            source_connector = PostgreSQLConnector(pg_config)
            target_connector = SQLServerConnector(sql_config)
            
            print_status("Extracting source data...", "INFO")
            source_data = source_connector.extract_data(
                database=pg_config["database"],
                schema=pg_config["schema"],
                table_name=table_name,
                limit=10,
                offset=0
            )
            
            total_rows = source_data.get("total_rows", 0)
            rows = source_data.get("rows", [])
            print_status(f"Source: {total_rows} total rows, {len(rows)} extracted", "SUCCESS")
            
            if not rows:
                print_status("No data extracted!", "ERROR")
                return 1
            
            print_status("Transferring data...", "INFO")
            transfer = DataTransfer(source_connector, target_connector)
            
            result = transfer.transfer_table(
                table_name=table_name,
                source_database=pg_config["database"],
                source_schema=pg_config["schema"],
                target_database=sql_config["database"],
                target_schema=sql_config["schema"],
                transfer_schema=False,
                transfer_data=True,
                batch_size=100
            )
            
            rows_transferred = result.get("rows_transferred", 0)
            errors = result.get("errors", [])
            
            print_status(f"Transfer result: {rows_transferred} rows", 
                        "SUCCESS" if rows_transferred > 0 else "ERROR")
            
            if errors:
                print_status("Errors:", "ERROR")
                for error in errors:
                    print(f"  - {error}")
            
            if rows_transferred == 0:
                print_status("CRITICAL: 0 rows transferred!", "ERROR")
                print_status("Check error messages above for details", "WARNING")
                return 1
            
            # Verify
            sql_conn = pyodbc.connect(sql_conn_str, timeout=10)
            cursor = sql_conn.cursor()
            cursor.execute(f"SELECT COUNT(*) FROM [{sql_config['schema']}].[{table_name}]")
            final_count = cursor.fetchone()[0]
            cursor.close()
            sql_conn.close()
            
            print_status(f"Final SQL Server count: {final_count} rows", 
                        "SUCCESS" if final_count > 0 else "ERROR")
            
            if final_count > 0:
                print_status("Data transfer successful!", "SUCCESS")
                print_status("\nNext: Restart the pipeline to use the new validation", "INFO")
                return 0
            else:
                return 1
                
        except Exception as e:
            print_status(f"Transfer failed: {e}", "ERROR")
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
    """Test and fix data transfer."""
    print("\n" + "="*60)
    print("FIX AND TEST DATA TRANSFER")
    print("="*60 + "\n")
    
    # Get pipeline and connections from API
    try:
        response = requests.get(f"{API_BASE_URL}/api/pipelines")
        pipelines = response.json()
        pipeline = next((p for p in pipelines if p.get("name") == "final_test"), None)
        if not pipeline:
            print_status("Pipeline not found", "ERROR")
            return 1
        
        source_conn_id = pipeline.get("source_connection_id")
        target_conn_id = pipeline.get("target_connection_id")
        
        response = requests.get(f"{API_BASE_URL}/api/v1/connections/{source_conn_id}")
        source_conn = response.json()
        
        response = requests.get(f"{API_BASE_URL}/api/v1/connections/{target_conn_id}")
        target_conn = response.json()
        
        print_status("Got connection details from API", "SUCCESS")
        print_status(f"SQL Server Host: {target_conn.get('host')}", "INFO")
        print_status(f"SQL Server Port: {target_conn.get('port')}", "INFO")
    except Exception as e:
        print_status(f"Failed to get connections: {e}", "ERROR")
        return 1
    
    # Use provided credentials
    pg_config = {
        "host": "72.61.233.209",
        "port": 5432,
        "database": "cdctest",
        "user": "cdc_user",
        "password": "cdc_pass",
        "schema": "public"
    }
    
    sql_config = {
        "server": target_conn.get("host", "localhost"),  # Use from API
        "port": 1433,
        "database": "cdctest",
        "user": "sa",
        "password": "Sql@12345",
        "schema": "dbo",
        "trust_server_certificate": True,
        "encrypt": False
    }
    
    table_name = "projects_simple"
    
    # Test PostgreSQL
    print_status("\n=== Testing PostgreSQL ===", "INFO")
    try:
        pg_conn = psycopg2.connect(
            host=pg_config["host"],
            port=pg_config["port"],
            database=pg_config["database"],
            user=pg_config["user"],
            password=pg_config["password"],
            connect_timeout=10
        )
        cursor = pg_conn.cursor()
        cursor.execute(f"SELECT COUNT(*) FROM {pg_config['schema']}.{table_name}")
        pg_count = cursor.fetchone()[0]
        print_status(f"PostgreSQL: {pg_count} rows", "SUCCESS")
        cursor.close()
        pg_conn.close()
    except Exception as e:
        print_status(f"PostgreSQL failed: {e}", "ERROR")
        return 1
    
    # Test SQL Server connection
    print_status(f"\n=== Testing SQL Server ({sql_config['server']}:{sql_config['port']}) ===", "INFO")
    try:
        sql_conn_str = (
            f"DRIVER={{ODBC Driver 17 for SQL Server}};"
            f"SERVER={sql_config['server']},{sql_config['port']};"
            f"DATABASE={sql_config['database']};"
            f"UID={sql_config['user']};"
            f"PWD={sql_config['password']};"
            f"TrustServerCertificate=yes;"
            f"Encrypt=no;"
        )
        
        sql_conn = pyodbc.connect(sql_conn_str, timeout=10)
        cursor = sql_conn.cursor()
        cursor.execute(f"SELECT COUNT(*) FROM [{sql_config['schema']}].[{table_name}]")
        sql_count = cursor.fetchone()[0]
        print_status(f"SQL Server: {sql_count} rows", "SUCCESS" if sql_count > 0 else "WARNING")
        cursor.close()
        sql_conn.close()
    except Exception as e:
        print_status(f"SQL Server connection failed: {e}", "ERROR")
        print_status(f"Trying to connect to: {sql_config['server']}:{sql_config['port']}", "INFO")
        print_status("Please verify SQL Server host and credentials", "WARNING")
        return 1
    
    # Compare
    print_status(f"\n=== Comparison ===", "INFO")
    print(f"PostgreSQL: {pg_count} rows")
    print(f"SQL Server: {sql_count} rows")
    
    if pg_count > 0 and sql_count == 0:
        print_status("Data not transferred - attempting transfer...", "INFO")
        
        try:
            source_connector = PostgreSQLConnector(pg_config)
            target_connector = SQLServerConnector(sql_config)
            
            print_status("Extracting source data...", "INFO")
            source_data = source_connector.extract_data(
                database=pg_config["database"],
                schema=pg_config["schema"],
                table_name=table_name,
                limit=10,
                offset=0
            )
            
            total_rows = source_data.get("total_rows", 0)
            rows = source_data.get("rows", [])
            print_status(f"Source: {total_rows} total rows, {len(rows)} extracted", "SUCCESS")
            
            if not rows:
                print_status("No data extracted!", "ERROR")
                return 1
            
            print_status("Transferring data...", "INFO")
            transfer = DataTransfer(source_connector, target_connector)
            
            result = transfer.transfer_table(
                table_name=table_name,
                source_database=pg_config["database"],
                source_schema=pg_config["schema"],
                target_database=sql_config["database"],
                target_schema=sql_config["schema"],
                transfer_schema=False,
                transfer_data=True,
                batch_size=100
            )
            
            rows_transferred = result.get("rows_transferred", 0)
            errors = result.get("errors", [])
            
            print_status(f"Transfer result: {rows_transferred} rows", 
                        "SUCCESS" if rows_transferred > 0 else "ERROR")
            
            if errors:
                print_status("Errors:", "ERROR")
                for error in errors:
                    print(f"  - {error}")
            
            if rows_transferred == 0:
                print_status("CRITICAL: 0 rows transferred!", "ERROR")
                print_status("Check error messages above for details", "WARNING")
                return 1
            
            # Verify
            sql_conn = pyodbc.connect(sql_conn_str, timeout=10)
            cursor = sql_conn.cursor()
            cursor.execute(f"SELECT COUNT(*) FROM [{sql_config['schema']}].[{table_name}]")
            final_count = cursor.fetchone()[0]
            cursor.close()
            sql_conn.close()
            
            print_status(f"Final SQL Server count: {final_count} rows", 
                        "SUCCESS" if final_count > 0 else "ERROR")
            
            if final_count > 0:
                print_status("Data transfer successful!", "SUCCESS")
                print_status("\nNext: Restart the pipeline to use the new validation", "INFO")
                return 0
            else:
                return 1
                
        except Exception as e:
            print_status(f"Transfer failed: {e}", "ERROR")
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

