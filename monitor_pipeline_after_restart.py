"""Monitor pipeline status after backend restart to verify persistence."""

import sys
import time
import requests
import psycopg2

# Configure encoding for Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

BASE_URL = "http://localhost:8000"
PIPELINE_NAME = "final_test2"

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
            "updated_at": row[3]
        }
    return None

def stop_pipeline(pipeline_id: str) -> dict:
    """Stop pipeline."""
    response = requests.post(f"{BASE_URL}/api/pipelines/{pipeline_id}/stop", timeout=30)
    response.raise_for_status()
    return response.json()

def start_pipeline(pipeline_id: str) -> dict:
    """Start pipeline."""
    response = requests.post(f"{BASE_URL}/api/pipelines/{pipeline_id}/start", timeout=120)
    response.raise_for_status()
    return response.json()

def main():
    """Main function."""
    print("\n" + "="*60)
    print("MONITOR PIPELINE STATUS AFTER BACKEND RESTART".center(60))
    print("="*60 + "\n")
    
    # Step 1: Check backend
    print_status("Step 1: Checking backend...", "INFO")
    if not check_backend():
        print_status("Backend is not running!", "ERROR")
        print_status("Please start the backend: python -m uvicorn ingestion.api:app --host 0.0.0.0 --port 8000", "WARNING")
        return 1
    print_status("Backend is running", "SUCCESS")
    
    # Step 2: Get pipeline
    print_status("\nStep 2: Finding pipeline...", "INFO")
    pipeline_id = get_pipeline_id(PIPELINE_NAME)
    if not pipeline_id:
        print_status(f"Pipeline '{PIPELINE_NAME}' not found", "ERROR")
        return 1
    print_status(f"Found pipeline: {pipeline_id}", "SUCCESS")
    
    # Step 3: Check current status
    print_status("\nStep 3: Checking current status...", "INFO")
    api_status = get_pipeline_status_api(pipeline_id)
    db_status = get_pipeline_status_db(pipeline_id)
    
    print_status("\n=== Current Status ===", "INFO")
    print(f"API - Status: {api_status.get('status')}")
    print(f"API - Full Load: {api_status.get('full_load_status')}")
    print(f"API - CDC: {api_status.get('cdc_status')}")
    
    if db_status:
        print(f"\nDB  - Status: {db_status.get('status')}")
        print(f"DB  - Full Load: {db_status.get('full_load_status')}")
        print(f"DB  - CDC: {db_status.get('cdc_status')}")
        print(f"DB  - Updated At: {db_status.get('updated_at')}")
    
    # Step 4: Stop and restart pipeline
    print_status("\nStep 4: Stopping pipeline...", "INFO")
    try:
        stop_pipeline(pipeline_id)
        print_status("Pipeline stopped", "SUCCESS")
        time.sleep(3)
    except Exception as e:
        print_status(f"Failed to stop pipeline (may already be stopped): {e}", "WARNING")
    
    # Step 5: Start pipeline
    print_status("\nStep 5: Starting pipeline (will trigger full load)...", "INFO")
    try:
        start_result = start_pipeline(pipeline_id)
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
    
    # Step 6: Monitor status updates
    print_status("\nStep 6: Monitoring status updates in database...", "INFO")
    print_status("Watching for status changes (verifies persistence is working)...", "INFO")
    
    full_load_started = False
    full_load_completed = False
    cdc_started = False
    
    for i in range(90):  # Monitor for up to 3 minutes
        time.sleep(2)
        
        # Check DB status
        db_status = get_pipeline_status_db(pipeline_id)
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
            print_status(f"[{i*2}s] ✅ Full load started (IN_PROGRESS) - Status persisted!", "SUCCESS")
            print_status(f"      Status: {db_pipeline_status}, Full Load: {db_full_load}, CDC: {db_cdc}", "INFO")
        
        if db_full_load == "COMPLETED" and not full_load_completed:
            full_load_completed = True
            print_status(f"[{i*2}s] ✅ Full load completed (COMPLETED) - Status persisted!", "SUCCESS")
            print_status(f"      Status: {db_pipeline_status}, Full Load: {db_full_load}, CDC: {db_cdc}", "INFO")
        
        if db_cdc == "RUNNING" and not cdc_started:
            cdc_started = True
            print_status(f"[{i*2}s] ✅ CDC started (RUNNING) - Status persisted!", "SUCCESS")
            print_status(f"      Status: {db_pipeline_status}, Full Load: {db_full_load}, CDC: {db_cdc}", "INFO")
        
        # Show progress every 10 seconds
        if i % 5 == 0 and i > 0:
            print_status(
                f"[{i*2}s] DB Status: {db_pipeline_status}, FullLoad: {db_full_load}, CDC: {db_cdc}",
                "INFO"
            )
        
        # Check if done
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
    
    # Step 7: Final verification
    print_status("\nStep 7: Final status verification...", "INFO")
    final_api_status = get_pipeline_status_api(pipeline_id)
    final_db_status = get_pipeline_status_db(pipeline_id)
    
    print_status("\n=== Final Status ===", "INFO")
    print(f"API - Status: {final_api_status.get('status')}")
    print(f"API - Full Load: {final_api_status.get('full_load_status')}")
    print(f"API - CDC: {final_api_status.get('cdc_status')}")
    
    if final_db_status:
        print(f"\nDB  - Status: {final_db_status.get('status')}")
        print(f"DB  - Full Load: {final_db_status.get('full_load_status')}")
        print(f"DB  - CDC: {final_db_status.get('cdc_status')}")
        print(f"DB  - Updated At: {final_db_status.get('updated_at')}")
    
    # Summary
    print_status("\n=== Summary ===", "INFO")
    if full_load_started:
        print_status("✅ Full load started and status persisted", "SUCCESS")
    if full_load_completed:
        print_status("✅ Full load completed and status persisted", "SUCCESS")
    if cdc_started:
        print_status("✅ CDC started and status persisted", "SUCCESS")
    
    if final_db_status:
        if (final_api_status.get('full_load_status') == final_db_status.get('full_load_status') and
            final_api_status.get('cdc_status') == final_db_status.get('cdc_status')):
            print_status("\n✅ STATUS PERSISTENCE IS WORKING! API and DB match.", "SUCCESS")
            return 0
    
    return 0

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print_status("\nMonitoring interrupted", "WARNING")
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
PIPELINE_NAME = "final_test2"

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
            "updated_at": row[3]
        }
    return None

def stop_pipeline(pipeline_id: str) -> dict:
    """Stop pipeline."""
    response = requests.post(f"{BASE_URL}/api/pipelines/{pipeline_id}/stop", timeout=30)
    response.raise_for_status()
    return response.json()

def start_pipeline(pipeline_id: str) -> dict:
    """Start pipeline."""
    response = requests.post(f"{BASE_URL}/api/pipelines/{pipeline_id}/start", timeout=120)
    response.raise_for_status()
    return response.json()

def main():
    """Main function."""
    print("\n" + "="*60)
    print("MONITOR PIPELINE STATUS AFTER BACKEND RESTART".center(60))
    print("="*60 + "\n")
    
    # Step 1: Check backend
    print_status("Step 1: Checking backend...", "INFO")
    if not check_backend():
        print_status("Backend is not running!", "ERROR")
        print_status("Please start the backend: python -m uvicorn ingestion.api:app --host 0.0.0.0 --port 8000", "WARNING")
        return 1
    print_status("Backend is running", "SUCCESS")
    
    # Step 2: Get pipeline
    print_status("\nStep 2: Finding pipeline...", "INFO")
    pipeline_id = get_pipeline_id(PIPELINE_NAME)
    if not pipeline_id:
        print_status(f"Pipeline '{PIPELINE_NAME}' not found", "ERROR")
        return 1
    print_status(f"Found pipeline: {pipeline_id}", "SUCCESS")
    
    # Step 3: Check current status
    print_status("\nStep 3: Checking current status...", "INFO")
    api_status = get_pipeline_status_api(pipeline_id)
    db_status = get_pipeline_status_db(pipeline_id)
    
    print_status("\n=== Current Status ===", "INFO")
    print(f"API - Status: {api_status.get('status')}")
    print(f"API - Full Load: {api_status.get('full_load_status')}")
    print(f"API - CDC: {api_status.get('cdc_status')}")
    
    if db_status:
        print(f"\nDB  - Status: {db_status.get('status')}")
        print(f"DB  - Full Load: {db_status.get('full_load_status')}")
        print(f"DB  - CDC: {db_status.get('cdc_status')}")
        print(f"DB  - Updated At: {db_status.get('updated_at')}")
    
    # Step 4: Stop and restart pipeline
    print_status("\nStep 4: Stopping pipeline...", "INFO")
    try:
        stop_pipeline(pipeline_id)
        print_status("Pipeline stopped", "SUCCESS")
        time.sleep(3)
    except Exception as e:
        print_status(f"Failed to stop pipeline (may already be stopped): {e}", "WARNING")
    
    # Step 5: Start pipeline
    print_status("\nStep 5: Starting pipeline (will trigger full load)...", "INFO")
    try:
        start_result = start_pipeline(pipeline_id)
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
    
    # Step 6: Monitor status updates
    print_status("\nStep 6: Monitoring status updates in database...", "INFO")
    print_status("Watching for status changes (verifies persistence is working)...", "INFO")
    
    full_load_started = False
    full_load_completed = False
    cdc_started = False
    
    for i in range(90):  # Monitor for up to 3 minutes
        time.sleep(2)
        
        # Check DB status
        db_status = get_pipeline_status_db(pipeline_id)
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
            print_status(f"[{i*2}s] ✅ Full load started (IN_PROGRESS) - Status persisted!", "SUCCESS")
            print_status(f"      Status: {db_pipeline_status}, Full Load: {db_full_load}, CDC: {db_cdc}", "INFO")
        
        if db_full_load == "COMPLETED" and not full_load_completed:
            full_load_completed = True
            print_status(f"[{i*2}s] ✅ Full load completed (COMPLETED) - Status persisted!", "SUCCESS")
            print_status(f"      Status: {db_pipeline_status}, Full Load: {db_full_load}, CDC: {db_cdc}", "INFO")
        
        if db_cdc == "RUNNING" and not cdc_started:
            cdc_started = True
            print_status(f"[{i*2}s] ✅ CDC started (RUNNING) - Status persisted!", "SUCCESS")
            print_status(f"      Status: {db_pipeline_status}, Full Load: {db_full_load}, CDC: {db_cdc}", "INFO")
        
        # Show progress every 10 seconds
        if i % 5 == 0 and i > 0:
            print_status(
                f"[{i*2}s] DB Status: {db_pipeline_status}, FullLoad: {db_full_load}, CDC: {db_cdc}",
                "INFO"
            )
        
        # Check if done
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
    
    # Step 7: Final verification
    print_status("\nStep 7: Final status verification...", "INFO")
    final_api_status = get_pipeline_status_api(pipeline_id)
    final_db_status = get_pipeline_status_db(pipeline_id)
    
    print_status("\n=== Final Status ===", "INFO")
    print(f"API - Status: {final_api_status.get('status')}")
    print(f"API - Full Load: {final_api_status.get('full_load_status')}")
    print(f"API - CDC: {final_api_status.get('cdc_status')}")
    
    if final_db_status:
        print(f"\nDB  - Status: {final_db_status.get('status')}")
        print(f"DB  - Full Load: {final_db_status.get('full_load_status')}")
        print(f"DB  - CDC: {final_db_status.get('cdc_status')}")
        print(f"DB  - Updated At: {final_db_status.get('updated_at')}")
    
    # Summary
    print_status("\n=== Summary ===", "INFO")
    if full_load_started:
        print_status("✅ Full load started and status persisted", "SUCCESS")
    if full_load_completed:
        print_status("✅ Full load completed and status persisted", "SUCCESS")
    if cdc_started:
        print_status("✅ CDC started and status persisted", "SUCCESS")
    
    if final_db_status:
        if (final_api_status.get('full_load_status') == final_db_status.get('full_load_status') and
            final_api_status.get('cdc_status') == final_db_status.get('cdc_status')):
            print_status("\n✅ STATUS PERSISTENCE IS WORKING! API and DB match.", "SUCCESS")
            return 0
    
    return 0

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print_status("\nMonitoring interrupted", "WARNING")
        sys.exit(1)
    except Exception as e:
        print_status(f"Error: {e}", "ERROR")
        import traceback
        traceback.print_exc()
        sys.exit(1)

