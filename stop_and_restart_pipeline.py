"""Stop pipeline, then restart for fresh full load."""

import sys
import time
import requests
import psycopg2

# Configure encoding for Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

BASE_URL = "http://localhost:8000"
PIPELINE_NAME = "final_test"

def print_status(message: str, status: str = "INFO"):
    """Print colored status message."""
    colors = {
        "INFO": "\033[94m", "SUCCESS": "\033[92m", "ERROR": "\033[91m", 
        "WARNING": "\033[93m", "RESET": "\033[0m"
    }
    symbol = {"INFO": "ℹ", "SUCCESS": "✓", "ERROR": "✗", "WARNING": "⚠"}
    print(f"{colors.get(status, '')}{symbol.get(status, '')} {message}{colors['RESET']}")

def get_pipeline_id(pipeline_name: str) -> str:
    """Get pipeline ID by name."""
    response = requests.get(f"{BASE_URL}/api/pipelines", timeout=10)
    response.raise_for_status()
    pipelines = response.json()
    for p in pipelines:
        if p.get("name") == pipeline_name:
            return p["id"]
    raise ValueError(f"Pipeline '{pipeline_name}' not found")

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
    print("STOP AND RESTART PIPELINE FOR FRESH FULL LOAD".center(60))
    print("="*60 + "\n")
    
    # Step 1: Get pipeline
    print_status("Step 1: Finding pipeline...", "INFO")
    try:
        pipeline_id = get_pipeline_id(PIPELINE_NAME)
        print_status(f"Found pipeline: {pipeline_id}", "SUCCESS")
    except Exception as e:
        print_status(f"Pipeline not found: {e}", "ERROR")
        return 1
    
    # Step 2: Check current status
    print_status("\nStep 2: Checking current status...", "INFO")
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
    
    # Step 3: Stop pipeline
    print_status("\nStep 3: Stopping pipeline...", "INFO")
    try:
        stop_result = stop_pipeline(pipeline_id)
        print_status("Pipeline stop request sent", "SUCCESS")
        time.sleep(3)  # Wait for stop to complete
    except Exception as e:
        print_status(f"Failed to stop pipeline (may already be stopped): {e}", "WARNING")
    
    # Step 4: Verify stopped
    print_status("\nStep 4: Verifying pipeline is stopped...", "INFO")
    time.sleep(2)
    api_status = get_pipeline_status_api(pipeline_id)
    db_status = get_pipeline_status_db(pipeline_id)
    
    print(f"API Status: {api_status.get('status')}")
    if db_status:
        print(f"DB Status: {db_status.get('status')}")
    
    # Step 5: Start pipeline (fresh full load)
    print_status("\nStep 5: Starting pipeline (will trigger fresh full load)...", "INFO")
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
    
    # Step 6: Monitor full load -> CDC transition
    print_status("\nStep 6: Monitoring full load -> CDC transition...", "INFO")
    print_status("Watching for status changes in database...", "INFO")
    
    full_load_started = False
    full_load_completed = False
    cdc_started = False
    
    for i in range(90):  # Monitor for up to 3 minutes
        time.sleep(2)
        
        # Check DB status (this is what we care about)
        db_status = get_pipeline_status_db(pipeline_id)
        if not db_status:
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
    
    # Step 7: Final status check
    print_status("\nStep 7: Final status check...", "INFO")
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
PIPELINE_NAME = "final_test"

def print_status(message: str, status: str = "INFO"):
    """Print colored status message."""
    colors = {
        "INFO": "\033[94m", "SUCCESS": "\033[92m", "ERROR": "\033[91m", 
        "WARNING": "\033[93m", "RESET": "\033[0m"
    }
    symbol = {"INFO": "ℹ", "SUCCESS": "✓", "ERROR": "✗", "WARNING": "⚠"}
    print(f"{colors.get(status, '')}{symbol.get(status, '')} {message}{colors['RESET']}")

def get_pipeline_id(pipeline_name: str) -> str:
    """Get pipeline ID by name."""
    response = requests.get(f"{BASE_URL}/api/pipelines", timeout=10)
    response.raise_for_status()
    pipelines = response.json()
    for p in pipelines:
        if p.get("name") == pipeline_name:
            return p["id"]
    raise ValueError(f"Pipeline '{pipeline_name}' not found")

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
    print("STOP AND RESTART PIPELINE FOR FRESH FULL LOAD".center(60))
    print("="*60 + "\n")
    
    # Step 1: Get pipeline
    print_status("Step 1: Finding pipeline...", "INFO")
    try:
        pipeline_id = get_pipeline_id(PIPELINE_NAME)
        print_status(f"Found pipeline: {pipeline_id}", "SUCCESS")
    except Exception as e:
        print_status(f"Pipeline not found: {e}", "ERROR")
        return 1
    
    # Step 2: Check current status
    print_status("\nStep 2: Checking current status...", "INFO")
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
    
    # Step 3: Stop pipeline
    print_status("\nStep 3: Stopping pipeline...", "INFO")
    try:
        stop_result = stop_pipeline(pipeline_id)
        print_status("Pipeline stop request sent", "SUCCESS")
        time.sleep(3)  # Wait for stop to complete
    except Exception as e:
        print_status(f"Failed to stop pipeline (may already be stopped): {e}", "WARNING")
    
    # Step 4: Verify stopped
    print_status("\nStep 4: Verifying pipeline is stopped...", "INFO")
    time.sleep(2)
    api_status = get_pipeline_status_api(pipeline_id)
    db_status = get_pipeline_status_db(pipeline_id)
    
    print(f"API Status: {api_status.get('status')}")
    if db_status:
        print(f"DB Status: {db_status.get('status')}")
    
    # Step 5: Start pipeline (fresh full load)
    print_status("\nStep 5: Starting pipeline (will trigger fresh full load)...", "INFO")
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
    
    # Step 6: Monitor full load -> CDC transition
    print_status("\nStep 6: Monitoring full load -> CDC transition...", "INFO")
    print_status("Watching for status changes in database...", "INFO")
    
    full_load_started = False
    full_load_completed = False
    cdc_started = False
    
    for i in range(90):  # Monitor for up to 3 minutes
        time.sleep(2)
        
        # Check DB status (this is what we care about)
        db_status = get_pipeline_status_db(pipeline_id)
        if not db_status:
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
    
    # Step 7: Final status check
    print_status("\nStep 7: Final status check...", "INFO")
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

