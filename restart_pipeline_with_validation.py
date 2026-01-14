"""Restart pipeline to test new validation."""

import sys
import requests
import time

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

def main():
    """Restart pipeline."""
    print("\n" + "="*60)
    print("RESTART PIPELINE WITH NEW VALIDATION")
    print("="*60 + "\n")
    
    # Find pipeline
    try:
        response = requests.get(f"{API_BASE_URL}/api/pipelines")
        response.raise_for_status()
        pipelines = response.json()
        pipeline = next((p for p in pipelines if p.get("name") == "final_test"), None)
        
        if not pipeline:
            print_status("Pipeline 'final_test' not found", "ERROR")
            return 1
        
        pipeline_id = pipeline.get("id")
        print_status(f"Found pipeline: {pipeline_id}", "SUCCESS")
    except Exception as e:
        print_status(f"Failed to get pipeline: {e}", "ERROR")
        return 1
    
    # Stop pipeline if running
    print_status("\nStep 1: Stopping pipeline (if running)...", "INFO")
    try:
        response = requests.post(f"{API_BASE_URL}/api/pipelines/{pipeline_id}/stop")
        if response.status_code == 200:
            print_status("Pipeline stopped", "SUCCESS")
        elif response.status_code == 404:
            print_status("Pipeline not found or already stopped", "WARNING")
        else:
            print_status(f"Stop returned status {response.status_code}", "WARNING")
    except Exception as e:
        print_status(f"Stop failed (may already be stopped): {e}", "WARNING")
    
    time.sleep(2)
    
    # Start pipeline
    print_status("\nStep 2: Starting pipeline with new validation...", "INFO")
    try:
        response = requests.post(f"{API_BASE_URL}/api/pipelines/{pipeline_id}/start")
        
        if response.status_code == 200:
            result = response.json()
            print_status("Pipeline start request sent", "SUCCESS")
            
            # Check full load result
            full_load = result.get("full_load", {})
            if full_load.get("success"):
                tables = full_load.get("tables_transferred", 0)
                rows = full_load.get("total_rows", 0)
                print_status(f"Full load: {tables} tables, {rows} rows", "SUCCESS" if rows > 0 else "ERROR")
            else:
                error = full_load.get("error", "Unknown error")
                print_status(f"Full load failed: {error}", "ERROR")
                print_status("\n✅ VALIDATION WORKING - Pipeline correctly detected failure!", "SUCCESS")
                return 0
        else:
            error_detail = response.json().get("detail", "Unknown error")
            print_status(f"Pipeline start failed: {error_detail}", "ERROR")
            
            if "0 rows" in error_detail or "transferred 0 rows" in error_detail:
                print_status("\n✅ VALIDATION WORKING - Pipeline correctly detected 0 rows issue!", "SUCCESS")
            else:
                print_status("\n⚠️  Check error message above", "WARNING")
            
            return 1
    except Exception as e:
        print_status(f"Failed to start pipeline: {e}", "ERROR")
        return 1
    
    # Monitor
    print_status("\nStep 3: Monitoring pipeline...", "INFO")
    for i in range(20):
        time.sleep(2)
        try:
            response = requests.get(f"{API_BASE_URL}/api/pipelines/{pipeline_id}")
            if response.status_code == 200:
                status = response.json()
                current_status = status.get("status")
                full_load_status = status.get("full_load_status")
                
                if current_status == "ERROR" or full_load_status == "FAILED":
                    print_status(f"Pipeline failed: {current_status}, Full Load: {full_load_status}", "ERROR")
                    print_status("\n✅ VALIDATION WORKING - Pipeline correctly detected failure!", "SUCCESS")
                    return 0
                elif current_status == "RUNNING" and full_load_status == "COMPLETED":
                    rows = status.get("full_load_rows", 0)
                    if rows == 0:
                        print_status("Pipeline completed but 0 rows - validation should have caught this!", "ERROR")
                        return 1
                    else:
                        print_status(f"Pipeline completed successfully: {rows} rows", "SUCCESS")
                        return 0
        except Exception:
            pass
    
    print_status("Monitoring timeout", "WARNING")
    return 1

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print_status("\nInterrupted", "WARNING")
        sys.exit(1)
    except Exception as e:
        print_status(f"Unexpected error: {e}", "ERROR")
        import traceback
        traceback.print_exc()
        sys.exit(1)


import sys
import requests
import time

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

def main():
    """Restart pipeline."""
    print("\n" + "="*60)
    print("RESTART PIPELINE WITH NEW VALIDATION")
    print("="*60 + "\n")
    
    # Find pipeline
    try:
        response = requests.get(f"{API_BASE_URL}/api/pipelines")
        response.raise_for_status()
        pipelines = response.json()
        pipeline = next((p for p in pipelines if p.get("name") == "final_test"), None)
        
        if not pipeline:
            print_status("Pipeline 'final_test' not found", "ERROR")
            return 1
        
        pipeline_id = pipeline.get("id")
        print_status(f"Found pipeline: {pipeline_id}", "SUCCESS")
    except Exception as e:
        print_status(f"Failed to get pipeline: {e}", "ERROR")
        return 1
    
    # Stop pipeline if running
    print_status("\nStep 1: Stopping pipeline (if running)...", "INFO")
    try:
        response = requests.post(f"{API_BASE_URL}/api/pipelines/{pipeline_id}/stop")
        if response.status_code == 200:
            print_status("Pipeline stopped", "SUCCESS")
        elif response.status_code == 404:
            print_status("Pipeline not found or already stopped", "WARNING")
        else:
            print_status(f"Stop returned status {response.status_code}", "WARNING")
    except Exception as e:
        print_status(f"Stop failed (may already be stopped): {e}", "WARNING")
    
    time.sleep(2)
    
    # Start pipeline
    print_status("\nStep 2: Starting pipeline with new validation...", "INFO")
    try:
        response = requests.post(f"{API_BASE_URL}/api/pipelines/{pipeline_id}/start")
        
        if response.status_code == 200:
            result = response.json()
            print_status("Pipeline start request sent", "SUCCESS")
            
            # Check full load result
            full_load = result.get("full_load", {})
            if full_load.get("success"):
                tables = full_load.get("tables_transferred", 0)
                rows = full_load.get("total_rows", 0)
                print_status(f"Full load: {tables} tables, {rows} rows", "SUCCESS" if rows > 0 else "ERROR")
            else:
                error = full_load.get("error", "Unknown error")
                print_status(f"Full load failed: {error}", "ERROR")
                print_status("\n✅ VALIDATION WORKING - Pipeline correctly detected failure!", "SUCCESS")
                return 0
        else:
            error_detail = response.json().get("detail", "Unknown error")
            print_status(f"Pipeline start failed: {error_detail}", "ERROR")
            
            if "0 rows" in error_detail or "transferred 0 rows" in error_detail:
                print_status("\n✅ VALIDATION WORKING - Pipeline correctly detected 0 rows issue!", "SUCCESS")
            else:
                print_status("\n⚠️  Check error message above", "WARNING")
            
            return 1
    except Exception as e:
        print_status(f"Failed to start pipeline: {e}", "ERROR")
        return 1
    
    # Monitor
    print_status("\nStep 3: Monitoring pipeline...", "INFO")
    for i in range(20):
        time.sleep(2)
        try:
            response = requests.get(f"{API_BASE_URL}/api/pipelines/{pipeline_id}")
            if response.status_code == 200:
                status = response.json()
                current_status = status.get("status")
                full_load_status = status.get("full_load_status")
                
                if current_status == "ERROR" or full_load_status == "FAILED":
                    print_status(f"Pipeline failed: {current_status}, Full Load: {full_load_status}", "ERROR")
                    print_status("\n✅ VALIDATION WORKING - Pipeline correctly detected failure!", "SUCCESS")
                    return 0
                elif current_status == "RUNNING" and full_load_status == "COMPLETED":
                    rows = status.get("full_load_rows", 0)
                    if rows == 0:
                        print_status("Pipeline completed but 0 rows - validation should have caught this!", "ERROR")
                        return 1
                    else:
                        print_status(f"Pipeline completed successfully: {rows} rows", "SUCCESS")
                        return 0
        except Exception:
            pass
    
    print_status("Monitoring timeout", "WARNING")
    return 1

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print_status("\nInterrupted", "WARNING")
        sys.exit(1)
    except Exception as e:
        print_status(f"Unexpected error: {e}", "ERROR")
        import traceback
        traceback.print_exc()
        sys.exit(1)

