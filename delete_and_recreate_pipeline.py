"""Delete final_test pipeline and create final_test2 with same config, then monitor."""

import sys
import time
import requests
import psycopg2

# Configure encoding for Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

BASE_URL = "http://localhost:8000"
OLD_PIPELINE_NAME = "final_test"
NEW_PIPELINE_NAME = "final_test2"

def print_status(message: str, status: str = "INFO"):
    """Print colored status message."""
    colors = {
        "INFO": "\033[94m", "SUCCESS": "\033[92m", "ERROR": "\033[91m", 
        "WARNING": "\033[93m", "RESET": "\033[0m"
    }
    symbol = {"INFO": "ℹ", "SUCCESS": "✓", "ERROR": "✗", "WARNING": "⚠"}
    print(f"{colors.get(status, '')}{symbol.get(status, '')} {message}{colors['RESET']}")

def check_backend():
    """Check if backend is running."""
    try:
        response = requests.get(f"{BASE_URL}/api/v1/connections", timeout=5)
        return response.status_code == 200
    except:
        return False

def get_pipeline_id(pipeline_name: str) -> str:
    """Get pipeline ID by name."""
    response = requests.get(f"{BASE_URL}/api/pipelines", timeout=10)
    response.raise_for_status()
    pipelines = response.json()
    for p in pipelines:
        if p.get("name") == pipeline_name:
            return p["id"]
    return None

def get_pipeline_details(pipeline_id: str) -> dict:
    """Get pipeline details."""
    response = requests.get(f"{BASE_URL}/api/pipelines/{pipeline_id}", timeout=10)
    response.raise_for_status()
    return response.json()

def delete_pipeline(pipeline_id: str, hard_delete: bool = True) -> dict:
    """Delete pipeline."""
    response = requests.delete(
        f"{BASE_URL}/api/pipelines/{pipeline_id}",
        params={"hard_delete": hard_delete},
        timeout=30
    )
    response.raise_for_status()
    return response.json()

def create_pipeline(pipeline_data: dict) -> dict:
    """Create new pipeline."""
    response = requests.post(
        f"{BASE_URL}/api/pipelines",
        json=pipeline_data,
        timeout=30
    )
    response.raise_for_status()
    return response.json()

def start_pipeline(pipeline_id: str) -> dict:
    """Start pipeline."""
    response = requests.post(f"{BASE_URL}/api/pipelines/{pipeline_id}/start", timeout=120)
    response.raise_for_status()
    return response.json()

def get_pipeline_status_api(pipeline_id: str) -> dict:
    """Get pipeline status from API."""
    response = requests.get(f"{BASE_URL}/api/pipelines/{pipeline_id}", timeout=10)
    response.raise_for_status()
    return response.json()

def get_pipeline_status_db(pipeline_id: str) -> dict:
    """Get pipeline status from database."""
    conn = psycopg2.connect(
        host="72.61.233.209",
        port=5432,
        database="cdctest",
        user="cdc_user",
        password="cdc_pass",
        connect_timeout=10
    )
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT 
            status,
            full_load_status,
            cdc_status,
            full_load_lsn,
            updated_at
        FROM pipelines
        WHERE id = %s
    """, (pipeline_id,))
    
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    
    if row:
        return {
            "status": row[0],
            "full_load_status": row[1],
            "cdc_status": row[2],
            "full_load_lsn": row[3],
            "updated_at": row[4]
        }
    return None

def main():
    """Main function."""
    print("\n" + "="*60)
    print("DELETE AND RECREATE PIPELINE".center(60))
    print("="*60 + "\n")
    
    # Step 1: Check backend
    print_status("Step 1: Checking backend...", "INFO")
    if not check_backend():
        print_status("Backend is not running!", "ERROR")
        print_status("Please start the backend: python -m uvicorn ingestion.api:app --host 0.0.0.0 --port 8000", "WARNING")
        return 1
    print_status("Backend is running", "SUCCESS")
    
    # Step 2: Find and get old pipeline details
    print_status(f"\nStep 2: Finding pipeline '{OLD_PIPELINE_NAME}'...", "INFO")
    old_pipeline_id = get_pipeline_id(OLD_PIPELINE_NAME)
    
    if not old_pipeline_id:
        print_status(f"Pipeline '{OLD_PIPELINE_NAME}' not found", "WARNING")
        print_status("Proceeding to create new pipeline...", "INFO")
        old_pipeline_details = None
    else:
        print_status(f"Found pipeline: {old_pipeline_id}", "SUCCESS")
        old_pipeline_details = get_pipeline_details(old_pipeline_id)
        print_status("\n=== Old Pipeline Configuration ===", "INFO")
        print(f"Source: {old_pipeline_details.get('source_database')}.{old_pipeline_details.get('source_schema')}")
        print(f"Target: {old_pipeline_details.get('target_database')}.{old_pipeline_details.get('target_schema')}")
        print(f"Tables: {old_pipeline_details.get('source_tables')}")
        print(f"Mode: {old_pipeline_details.get('mode')}")
    
    # Step 3: Delete old pipeline
    if old_pipeline_id:
        print_status(f"\nStep 3: Deleting pipeline '{OLD_PIPELINE_NAME}'...", "INFO")
        try:
            delete_result = delete_pipeline(old_pipeline_id, hard_delete=True)
            print_status("Pipeline deleted successfully", "SUCCESS")
            time.sleep(2)  # Wait for deletion to complete
        except Exception as e:
            print_status(f"Failed to delete pipeline: {e}", "ERROR")
            return 1
    else:
        print_status(f"\nStep 3: No pipeline to delete", "INFO")
    
    # Step 4: Check if new pipeline already exists
    print_status(f"\nStep 4: Checking if '{NEW_PIPELINE_NAME}' already exists...", "INFO")
    existing_new_pipeline_id = get_pipeline_id(NEW_PIPELINE_NAME)
    if existing_new_pipeline_id:
        print_status(f"Pipeline '{NEW_PIPELINE_NAME}' already exists, deleting it...", "WARNING")
        try:
            delete_pipeline(existing_new_pipeline_id, hard_delete=True)
            print_status("Existing pipeline deleted", "SUCCESS")
            time.sleep(2)
        except Exception as e:
            print_status(f"Failed to delete existing pipeline: {e}", "ERROR")
            return 1
    
    # Step 5: Create new pipeline
    print_status(f"\nStep 5: Creating new pipeline '{NEW_PIPELINE_NAME}'...", "INFO")
    
    # Get connections first
    print_status("Getting connection details...", "INFO")
    try:
        connections_response = requests.get(f"{BASE_URL}/api/v1/connections", timeout=10)
        connections_response.raise_for_status()
        connections = connections_response.json()
        
        # Find PostgreSQL and SQL Server connections
        pg_connection = None
        sql_connection = None
        
        for conn in connections:
            db_type = conn.get("database_type", "").lower()
            if db_type == "postgresql":
                pg_connection = conn
            elif db_type in ["sqlserver", "mssql"]:
                sql_connection = conn
        
        if not pg_connection:
            print_status("PostgreSQL connection not found!", "ERROR")
            return 1
        if not sql_connection:
            print_status("SQL Server connection not found!", "ERROR")
            return 1
        
        print_status(f"Found PostgreSQL connection: {pg_connection.get('name')} ({pg_connection.get('id')})", "SUCCESS")
        print_status(f"Found SQL Server connection: {sql_connection.get('name')} ({sql_connection.get('id')})", "SUCCESS")
        
    except Exception as e:
        print_status(f"Failed to get connections: {e}", "ERROR")
        return 1
    
    # Use configuration from old pipeline if available, otherwise use defaults
    if old_pipeline_details and old_pipeline_details.get("source_connection_id"):
        source_conn_id = old_pipeline_details.get("source_connection_id")
        target_conn_id = old_pipeline_details.get("target_connection_id")
        source_db = old_pipeline_details.get("source_database") or "cdctest"
        source_schema = old_pipeline_details.get("source_schema") or "public"
        source_tables = old_pipeline_details.get("source_tables") or ["projects_simple"]
        target_db = old_pipeline_details.get("target_database") or "cdctest"
        target_schema = old_pipeline_details.get("target_schema") or "dbo"
        mode = old_pipeline_details.get("mode") or "full_load_and_cdc"
    else:
        # Use the connections we found
        source_conn_id = pg_connection.get("id")
        target_conn_id = sql_connection.get("id")
        source_db = "cdctest"
        source_schema = "public"
        source_tables = ["projects_simple"]
        target_db = "cdctest"
        target_schema = "dbo"
        mode = "full_load_and_cdc"
    
    pipeline_data = {
        "name": NEW_PIPELINE_NAME,
        "source_connection_id": source_conn_id,
        "target_connection_id": target_conn_id,
        "source_database": source_db,
        "source_schema": source_schema,
        "source_tables": source_tables,
        "target_database": target_db,
        "target_schema": target_schema,
        "mode": mode,
        "auto_create_target": True
    }
    
    print_status("\n=== Pipeline Configuration ===", "INFO")
    print(f"Name: {NEW_PIPELINE_NAME}")
    print(f"Source Connection: {source_conn_id}")
    print(f"Target Connection: {target_conn_id}")
    print(f"Source: {source_db}.{source_schema}")
    print(f"Target: {target_db}.{target_schema}")
    print(f"Tables: {source_tables}")
    print(f"Mode: {mode}")
    
    try:
        new_pipeline = create_pipeline(pipeline_data)
        new_pipeline_id = new_pipeline.get("id")
        print_status(f"Pipeline created: {new_pipeline_id}", "SUCCESS")
        print_status("\n=== New Pipeline Configuration ===", "INFO")
        print(f"Name: {new_pipeline.get('name')}")
        print(f"Source: {new_pipeline.get('source_database')}.{new_pipeline.get('source_schema')}")
        print(f"Target: {new_pipeline.get('target_database')}.{new_pipeline.get('target_schema')}")
        print(f"Tables: {new_pipeline.get('source_tables')}")
        print(f"Mode: {new_pipeline.get('mode')}")
    except Exception as e:
        print_status(f"Failed to create pipeline: {e}", "ERROR")
        if hasattr(e, 'response') and e.response:
            try:
                error_detail = e.response.json()
                print_status(f"Error details: {error_detail}", "ERROR")
            except:
                print_status(f"Response: {e.response.text}", "ERROR")
        return 1
    
    # Step 6: Start pipeline
    print_status(f"\nStep 6: Starting pipeline '{NEW_PIPELINE_NAME}'...", "INFO")
    try:
        start_result = start_pipeline(new_pipeline_id)
        print_status("Pipeline start request sent", "SUCCESS")
        
        if start_result.get('full_load'):
            fl_info = start_result['full_load']
            print(f"  - Tables: {fl_info.get('tables_transferred', 'N/A')}")
            print(f"  - Rows: {fl_info.get('total_rows', 'N/A')}")
    except Exception as e:
        print_status(f"Failed to start pipeline: {e}", "ERROR")
        if hasattr(e, 'response') and e.response:
            print_status(f"Response: {e.response.text}", "ERROR")
        return 1
    
    # Step 7: Monitor full load -> CDC transition
    print_status("\nStep 7: Monitoring full load -> CDC transition...", "INFO")
    print_status("Watching for status changes in database...", "INFO")
    
    full_load_started = False
    full_load_completed = False
    cdc_started = False
    
    for i in range(90):  # Monitor for up to 3 minutes
        time.sleep(2)
        
        # Check DB status (this is what we care about)
        db_status = get_pipeline_status_db(new_pipeline_id)
        if not db_status:
            if i % 5 == 0:
                print_status(f"[{i*2}s] Waiting for pipeline status in database...", "INFO")
            continue
        
        db_full_load = db_status.get('full_load_status')
        db_cdc = db_status.get('cdc_status')
        db_pipeline_status = db_status.get('status')
        
        # Track milestones
        if db_full_load == "IN_PROGRESS" and not full_load_started:
            full_load_started = True
            print_status(f"[{i*2}s] ✅ Full load started (IN_PROGRESS)", "SUCCESS")
            print_status(f"      Status: {db_pipeline_status}, Full Load: {db_full_load}, CDC: {db_cdc}", "INFO")
        
        if db_full_load == "COMPLETED" and not full_load_completed:
            full_load_completed = True
            print_status(f"[{i*2}s] ✅ Full load completed (COMPLETED)", "SUCCESS")
            print_status(f"      Status: {db_pipeline_status}, Full Load: {db_full_load}, CDC: {db_cdc}", "INFO")
            if db_status.get('full_load_lsn'):
                print_status(f"      Full Load LSN: {db_status.get('full_load_lsn')}", "INFO")
        
        if db_cdc == "RUNNING" and not cdc_started:
            cdc_started = True
            print_status(f"[{i*2}s] ✅ CDC started (RUNNING)", "SUCCESS")
            print_status(f"      Status: {db_pipeline_status}, Full Load: {db_full_load}, CDC: {db_cdc}", "INFO")
        
        # Show progress every 10 seconds
        if i % 5 == 0 and i > 0:
            print_status(
                f"[{i*2}s] Status: {db_pipeline_status}, FullLoad: {db_full_load}, CDC: {db_cdc}",
                "INFO"
            )
        
        # Check if we're done
        if full_load_completed and cdc_started:
            print_status(f"\n[{i*2}s] ✅ Pipeline fully operational!", "SUCCESS")
            break
        
        # Check for errors
        if db_full_load == "FAILED":
            print_status(f"[{i*2}s] ❌ Full load failed!", "ERROR")
            break
        
        if db_cdc == "ERROR":
            print_status(f"[{i*2}s] ❌ CDC error!", "ERROR")
            break
    
    # Step 8: Final status check
    print_status("\nStep 8: Final status check...", "INFO")
    final_api_status = get_pipeline_status_api(new_pipeline_id)
    final_db_status = get_pipeline_status_db(new_pipeline_id)
    
    print_status("\n=== Final Status ===", "INFO")
    print(f"Pipeline ID: {new_pipeline_id}")
    print(f"Pipeline Name: {NEW_PIPELINE_NAME}")
    print(f"\nAPI - Status: {final_api_status.get('status')}")
    print(f"API - Full Load: {final_api_status.get('full_load_status')}")
    print(f"API - CDC: {final_api_status.get('cdc_status')}")
    
    if final_db_status:
        print(f"\nDB  - Status: {final_db_status.get('status')}")
        print(f"DB  - Full Load: {final_db_status.get('full_load_status')}")
        print(f"DB  - CDC: {final_db_status.get('cdc_status')}")
        print(f"DB  - Full Load LSN: {final_db_status.get('full_load_lsn')}")
        print(f"DB  - Updated At: {final_db_status.get('updated_at')}")
    
    # Summary
    print_status("\n=== Summary ===", "INFO")
    if full_load_started:
        print_status("✅ Full load started", "SUCCESS")
    else:
        print_status("⚠ Full load did not start", "WARNING")
    
    if full_load_completed:
        print_status("✅ Full load completed", "SUCCESS")
    else:
        print_status("⚠ Full load did not complete", "WARNING")
    
    if cdc_started:
        print_status("✅ CDC started", "SUCCESS")
    else:
        print_status("⚠ CDC did not start", "WARNING")
    
    # Verify status persistence
    if final_db_status:
        if (final_api_status.get('full_load_status') == final_db_status.get('full_load_status') and
            final_api_status.get('cdc_status') == final_db_status.get('cdc_status')):
            print_status("\n✅ Status persistence is working! API and DB match.", "SUCCESS")
            return 0
        else:
            print_status(
                f"\n⚠ Status mismatch: API FullLoad={final_api_status.get('full_load_status')}, DB FullLoad={final_db_status.get('full_load_status')}",
                "WARNING"
            )
            return 1
    
    return 0

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print_status("\nTest interrupted", "WARNING")
        sys.exit(1)
    except Exception as e:
        print_status(f"Error: {e}", "ERROR")
        import traceback
        traceback.print_exc()
        sys.exit(1)


import sys
import time
import requests
import psycopg2

# Configure encoding for Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

BASE_URL = "http://localhost:8000"
OLD_PIPELINE_NAME = "final_test"
NEW_PIPELINE_NAME = "final_test2"

def print_status(message: str, status: str = "INFO"):
    """Print colored status message."""
    colors = {
        "INFO": "\033[94m", "SUCCESS": "\033[92m", "ERROR": "\033[91m", 
        "WARNING": "\033[93m", "RESET": "\033[0m"
    }
    symbol = {"INFO": "ℹ", "SUCCESS": "✓", "ERROR": "✗", "WARNING": "⚠"}
    print(f"{colors.get(status, '')}{symbol.get(status, '')} {message}{colors['RESET']}")

def check_backend():
    """Check if backend is running."""
    try:
        response = requests.get(f"{BASE_URL}/api/v1/connections", timeout=5)
        return response.status_code == 200
    except:
        return False

def get_pipeline_id(pipeline_name: str) -> str:
    """Get pipeline ID by name."""
    response = requests.get(f"{BASE_URL}/api/pipelines", timeout=10)
    response.raise_for_status()
    pipelines = response.json()
    for p in pipelines:
        if p.get("name") == pipeline_name:
            return p["id"]
    return None

def get_pipeline_details(pipeline_id: str) -> dict:
    """Get pipeline details."""
    response = requests.get(f"{BASE_URL}/api/pipelines/{pipeline_id}", timeout=10)
    response.raise_for_status()
    return response.json()

def delete_pipeline(pipeline_id: str, hard_delete: bool = True) -> dict:
    """Delete pipeline."""
    response = requests.delete(
        f"{BASE_URL}/api/pipelines/{pipeline_id}",
        params={"hard_delete": hard_delete},
        timeout=30
    )
    response.raise_for_status()
    return response.json()

def create_pipeline(pipeline_data: dict) -> dict:
    """Create new pipeline."""
    response = requests.post(
        f"{BASE_URL}/api/pipelines",
        json=pipeline_data,
        timeout=30
    )
    response.raise_for_status()
    return response.json()

def start_pipeline(pipeline_id: str) -> dict:
    """Start pipeline."""
    response = requests.post(f"{BASE_URL}/api/pipelines/{pipeline_id}/start", timeout=120)
    response.raise_for_status()
    return response.json()

def get_pipeline_status_api(pipeline_id: str) -> dict:
    """Get pipeline status from API."""
    response = requests.get(f"{BASE_URL}/api/pipelines/{pipeline_id}", timeout=10)
    response.raise_for_status()
    return response.json()

def get_pipeline_status_db(pipeline_id: str) -> dict:
    """Get pipeline status from database."""
    conn = psycopg2.connect(
        host="72.61.233.209",
        port=5432,
        database="cdctest",
        user="cdc_user",
        password="cdc_pass",
        connect_timeout=10
    )
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT 
            status,
            full_load_status,
            cdc_status,
            full_load_lsn,
            updated_at
        FROM pipelines
        WHERE id = %s
    """, (pipeline_id,))
    
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    
    if row:
        return {
            "status": row[0],
            "full_load_status": row[1],
            "cdc_status": row[2],
            "full_load_lsn": row[3],
            "updated_at": row[4]
        }
    return None

def main():
    """Main function."""
    print("\n" + "="*60)
    print("DELETE AND RECREATE PIPELINE".center(60))
    print("="*60 + "\n")
    
    # Step 1: Check backend
    print_status("Step 1: Checking backend...", "INFO")
    if not check_backend():
        print_status("Backend is not running!", "ERROR")
        print_status("Please start the backend: python -m uvicorn ingestion.api:app --host 0.0.0.0 --port 8000", "WARNING")
        return 1
    print_status("Backend is running", "SUCCESS")
    
    # Step 2: Find and get old pipeline details
    print_status(f"\nStep 2: Finding pipeline '{OLD_PIPELINE_NAME}'...", "INFO")
    old_pipeline_id = get_pipeline_id(OLD_PIPELINE_NAME)
    
    if not old_pipeline_id:
        print_status(f"Pipeline '{OLD_PIPELINE_NAME}' not found", "WARNING")
        print_status("Proceeding to create new pipeline...", "INFO")
        old_pipeline_details = None
    else:
        print_status(f"Found pipeline: {old_pipeline_id}", "SUCCESS")
        old_pipeline_details = get_pipeline_details(old_pipeline_id)
        print_status("\n=== Old Pipeline Configuration ===", "INFO")
        print(f"Source: {old_pipeline_details.get('source_database')}.{old_pipeline_details.get('source_schema')}")
        print(f"Target: {old_pipeline_details.get('target_database')}.{old_pipeline_details.get('target_schema')}")
        print(f"Tables: {old_pipeline_details.get('source_tables')}")
        print(f"Mode: {old_pipeline_details.get('mode')}")
    
    # Step 3: Delete old pipeline
    if old_pipeline_id:
        print_status(f"\nStep 3: Deleting pipeline '{OLD_PIPELINE_NAME}'...", "INFO")
        try:
            delete_result = delete_pipeline(old_pipeline_id, hard_delete=True)
            print_status("Pipeline deleted successfully", "SUCCESS")
            time.sleep(2)  # Wait for deletion to complete
        except Exception as e:
            print_status(f"Failed to delete pipeline: {e}", "ERROR")
            return 1
    else:
        print_status(f"\nStep 3: No pipeline to delete", "INFO")
    
    # Step 4: Check if new pipeline already exists
    print_status(f"\nStep 4: Checking if '{NEW_PIPELINE_NAME}' already exists...", "INFO")
    existing_new_pipeline_id = get_pipeline_id(NEW_PIPELINE_NAME)
    if existing_new_pipeline_id:
        print_status(f"Pipeline '{NEW_PIPELINE_NAME}' already exists, deleting it...", "WARNING")
        try:
            delete_pipeline(existing_new_pipeline_id, hard_delete=True)
            print_status("Existing pipeline deleted", "SUCCESS")
            time.sleep(2)
        except Exception as e:
            print_status(f"Failed to delete existing pipeline: {e}", "ERROR")
            return 1
    
    # Step 5: Create new pipeline
    print_status(f"\nStep 5: Creating new pipeline '{NEW_PIPELINE_NAME}'...", "INFO")
    
    # Get connections first
    print_status("Getting connection details...", "INFO")
    try:
        connections_response = requests.get(f"{BASE_URL}/api/v1/connections", timeout=10)
        connections_response.raise_for_status()
        connections = connections_response.json()
        
        # Find PostgreSQL and SQL Server connections
        pg_connection = None
        sql_connection = None
        
        for conn in connections:
            db_type = conn.get("database_type", "").lower()
            if db_type == "postgresql":
                pg_connection = conn
            elif db_type in ["sqlserver", "mssql"]:
                sql_connection = conn
        
        if not pg_connection:
            print_status("PostgreSQL connection not found!", "ERROR")
            return 1
        if not sql_connection:
            print_status("SQL Server connection not found!", "ERROR")
            return 1
        
        print_status(f"Found PostgreSQL connection: {pg_connection.get('name')} ({pg_connection.get('id')})", "SUCCESS")
        print_status(f"Found SQL Server connection: {sql_connection.get('name')} ({sql_connection.get('id')})", "SUCCESS")
        
    except Exception as e:
        print_status(f"Failed to get connections: {e}", "ERROR")
        return 1
    
    # Use configuration from old pipeline if available, otherwise use defaults
    if old_pipeline_details and old_pipeline_details.get("source_connection_id"):
        source_conn_id = old_pipeline_details.get("source_connection_id")
        target_conn_id = old_pipeline_details.get("target_connection_id")
        source_db = old_pipeline_details.get("source_database") or "cdctest"
        source_schema = old_pipeline_details.get("source_schema") or "public"
        source_tables = old_pipeline_details.get("source_tables") or ["projects_simple"]
        target_db = old_pipeline_details.get("target_database") or "cdctest"
        target_schema = old_pipeline_details.get("target_schema") or "dbo"
        mode = old_pipeline_details.get("mode") or "full_load_and_cdc"
    else:
        # Use the connections we found
        source_conn_id = pg_connection.get("id")
        target_conn_id = sql_connection.get("id")
        source_db = "cdctest"
        source_schema = "public"
        source_tables = ["projects_simple"]
        target_db = "cdctest"
        target_schema = "dbo"
        mode = "full_load_and_cdc"
    
    pipeline_data = {
        "name": NEW_PIPELINE_NAME,
        "source_connection_id": source_conn_id,
        "target_connection_id": target_conn_id,
        "source_database": source_db,
        "source_schema": source_schema,
        "source_tables": source_tables,
        "target_database": target_db,
        "target_schema": target_schema,
        "mode": mode,
        "auto_create_target": True
    }
    
    print_status("\n=== Pipeline Configuration ===", "INFO")
    print(f"Name: {NEW_PIPELINE_NAME}")
    print(f"Source Connection: {source_conn_id}")
    print(f"Target Connection: {target_conn_id}")
    print(f"Source: {source_db}.{source_schema}")
    print(f"Target: {target_db}.{target_schema}")
    print(f"Tables: {source_tables}")
    print(f"Mode: {mode}")
    
    try:
        new_pipeline = create_pipeline(pipeline_data)
        new_pipeline_id = new_pipeline.get("id")
        print_status(f"Pipeline created: {new_pipeline_id}", "SUCCESS")
        print_status("\n=== New Pipeline Configuration ===", "INFO")
        print(f"Name: {new_pipeline.get('name')}")
        print(f"Source: {new_pipeline.get('source_database')}.{new_pipeline.get('source_schema')}")
        print(f"Target: {new_pipeline.get('target_database')}.{new_pipeline.get('target_schema')}")
        print(f"Tables: {new_pipeline.get('source_tables')}")
        print(f"Mode: {new_pipeline.get('mode')}")
    except Exception as e:
        print_status(f"Failed to create pipeline: {e}", "ERROR")
        if hasattr(e, 'response') and e.response:
            try:
                error_detail = e.response.json()
                print_status(f"Error details: {error_detail}", "ERROR")
            except:
                print_status(f"Response: {e.response.text}", "ERROR")
        return 1
    
    # Step 6: Start pipeline
    print_status(f"\nStep 6: Starting pipeline '{NEW_PIPELINE_NAME}'...", "INFO")
    try:
        start_result = start_pipeline(new_pipeline_id)
        print_status("Pipeline start request sent", "SUCCESS")
        
        if start_result.get('full_load'):
            fl_info = start_result['full_load']
            print(f"  - Tables: {fl_info.get('tables_transferred', 'N/A')}")
            print(f"  - Rows: {fl_info.get('total_rows', 'N/A')}")
    except Exception as e:
        print_status(f"Failed to start pipeline: {e}", "ERROR")
        if hasattr(e, 'response') and e.response:
            print_status(f"Response: {e.response.text}", "ERROR")
        return 1
    
    # Step 7: Monitor full load -> CDC transition
    print_status("\nStep 7: Monitoring full load -> CDC transition...", "INFO")
    print_status("Watching for status changes in database...", "INFO")
    
    full_load_started = False
    full_load_completed = False
    cdc_started = False
    
    for i in range(90):  # Monitor for up to 3 minutes
        time.sleep(2)
        
        # Check DB status (this is what we care about)
        db_status = get_pipeline_status_db(new_pipeline_id)
        if not db_status:
            if i % 5 == 0:
                print_status(f"[{i*2}s] Waiting for pipeline status in database...", "INFO")
            continue
        
        db_full_load = db_status.get('full_load_status')
        db_cdc = db_status.get('cdc_status')
        db_pipeline_status = db_status.get('status')
        
        # Track milestones
        if db_full_load == "IN_PROGRESS" and not full_load_started:
            full_load_started = True
            print_status(f"[{i*2}s] ✅ Full load started (IN_PROGRESS)", "SUCCESS")
            print_status(f"      Status: {db_pipeline_status}, Full Load: {db_full_load}, CDC: {db_cdc}", "INFO")
        
        if db_full_load == "COMPLETED" and not full_load_completed:
            full_load_completed = True
            print_status(f"[{i*2}s] ✅ Full load completed (COMPLETED)", "SUCCESS")
            print_status(f"      Status: {db_pipeline_status}, Full Load: {db_full_load}, CDC: {db_cdc}", "INFO")
            if db_status.get('full_load_lsn'):
                print_status(f"      Full Load LSN: {db_status.get('full_load_lsn')}", "INFO")
        
        if db_cdc == "RUNNING" and not cdc_started:
            cdc_started = True
            print_status(f"[{i*2}s] ✅ CDC started (RUNNING)", "SUCCESS")
            print_status(f"      Status: {db_pipeline_status}, Full Load: {db_full_load}, CDC: {db_cdc}", "INFO")
        
        # Show progress every 10 seconds
        if i % 5 == 0 and i > 0:
            print_status(
                f"[{i*2}s] Status: {db_pipeline_status}, FullLoad: {db_full_load}, CDC: {db_cdc}",
                "INFO"
            )
        
        # Check if we're done
        if full_load_completed and cdc_started:
            print_status(f"\n[{i*2}s] ✅ Pipeline fully operational!", "SUCCESS")
            break
        
        # Check for errors
        if db_full_load == "FAILED":
            print_status(f"[{i*2}s] ❌ Full load failed!", "ERROR")
            break
        
        if db_cdc == "ERROR":
            print_status(f"[{i*2}s] ❌ CDC error!", "ERROR")
            break
    
    # Step 8: Final status check
    print_status("\nStep 8: Final status check...", "INFO")
    final_api_status = get_pipeline_status_api(new_pipeline_id)
    final_db_status = get_pipeline_status_db(new_pipeline_id)
    
    print_status("\n=== Final Status ===", "INFO")
    print(f"Pipeline ID: {new_pipeline_id}")
    print(f"Pipeline Name: {NEW_PIPELINE_NAME}")
    print(f"\nAPI - Status: {final_api_status.get('status')}")
    print(f"API - Full Load: {final_api_status.get('full_load_status')}")
    print(f"API - CDC: {final_api_status.get('cdc_status')}")
    
    if final_db_status:
        print(f"\nDB  - Status: {final_db_status.get('status')}")
        print(f"DB  - Full Load: {final_db_status.get('full_load_status')}")
        print(f"DB  - CDC: {final_db_status.get('cdc_status')}")
        print(f"DB  - Full Load LSN: {final_db_status.get('full_load_lsn')}")
        print(f"DB  - Updated At: {final_db_status.get('updated_at')}")
    
    # Summary
    print_status("\n=== Summary ===", "INFO")
    if full_load_started:
        print_status("✅ Full load started", "SUCCESS")
    else:
        print_status("⚠ Full load did not start", "WARNING")
    
    if full_load_completed:
        print_status("✅ Full load completed", "SUCCESS")
    else:
        print_status("⚠ Full load did not complete", "WARNING")
    
    if cdc_started:
        print_status("✅ CDC started", "SUCCESS")
    else:
        print_status("⚠ CDC did not start", "WARNING")
    
    # Verify status persistence
    if final_db_status:
        if (final_api_status.get('full_load_status') == final_db_status.get('full_load_status') and
            final_api_status.get('cdc_status') == final_db_status.get('cdc_status')):
            print_status("\n✅ Status persistence is working! API and DB match.", "SUCCESS")
            return 0
        else:
            print_status(
                f"\n⚠ Status mismatch: API FullLoad={final_api_status.get('full_load_status')}, DB FullLoad={final_db_status.get('full_load_status')}",
                "WARNING"
            )
            return 1
    
    return 0

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print_status("\nTest interrupted", "WARNING")
        sys.exit(1)
    except Exception as e:
        print_status(f"Error: {e}", "ERROR")
        import traceback
        traceback.print_exc()
        sys.exit(1)

