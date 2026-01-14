"""Check pipeline status in database directly."""

import sys
import requests
import psycopg2

# Configure encoding for Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

def print_status(message: str, status: str = "INFO"):
    """Print colored status message."""
    colors = {
        "INFO": "\033[94m", "SUCCESS": "\033[92m", "ERROR": "\033[91m", 
        "WARNING": "\033[93m", "RESET": "\033[0m"
    }
    symbol = {"INFO": "ℹ", "SUCCESS": "✓", "ERROR": "✗", "WARNING": "⚠"}
    print(f"{colors.get(status, '')}{symbol.get(status, '')} {message}{colors['RESET']}")

def main():
    """Check pipeline status in database."""
    print("\n" + "="*60)
    print("CHECK PIPELINE STATUS IN DATABASE")
    print("="*60 + "\n")
    
    # Get pipeline from API
    try:
        response = requests.get("http://localhost:8000/api/pipelines")
        response.raise_for_status()
        pipelines = response.json()
        pipeline = next((p for p in pipelines if p.get("name") == "final_test"), None)
        
        if not pipeline:
            print_status("Pipeline not found", "ERROR")
            return 1
        
        pipeline_id = pipeline.get("id")
        print_status(f"Pipeline ID: {pipeline_id}", "INFO")
    except Exception as e:
        print_status(f"Failed to get pipeline: {e}", "ERROR")
        return 1
    
    # Check database directly
    try:
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
                id,
                name,
                status,
                full_load_status,
                cdc_status,
                full_load_lsn,
                updated_at
            FROM pipelines
            WHERE id = %s
        """, (pipeline_id,))
        
        row = cursor.fetchone()
        if row:
            print_status("\n=== Database Status ===", "INFO")
            print(f"ID: {row[0]}")
            print(f"Name: {row[1]}")
            print(f"Status: {row[2]}")
            print(f"Full Load Status: {row[3]}")
            print(f"CDC Status: {row[4]}")
            print(f"Full Load LSN: {row[5]}")
            print(f"Updated At: {row[6]}")
            
            # Compare with API
            print_status("\n=== API Status ===", "INFO")
            print(f"Status: {pipeline.get('status')}")
            print(f"Full Load Status: {pipeline.get('full_load_status')}")
            print(f"CDC Status: {pipeline.get('cdc_status')}")
            
            # Check if they match
            if row[2] != pipeline.get('status'):
                print_status("Status mismatch!", "WARNING")
            if row[3] != pipeline.get('full_load_status'):
                print_status(f"Full Load Status mismatch! DB: {row[3]}, API: {pipeline.get('full_load_status')}", "ERROR")
            if row[4] != pipeline.get('cdc_status'):
                print_status("CDC Status mismatch!", "WARNING")
        else:
            print_status("Pipeline not found in database", "ERROR")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print_status(f"Database check failed: {e}", "ERROR")
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

# Configure encoding for Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

def print_status(message: str, status: str = "INFO"):
    """Print colored status message."""
    colors = {
        "INFO": "\033[94m", "SUCCESS": "\033[92m", "ERROR": "\033[91m", 
        "WARNING": "\033[93m", "RESET": "\033[0m"
    }
    symbol = {"INFO": "ℹ", "SUCCESS": "✓", "ERROR": "✗", "WARNING": "⚠"}
    print(f"{colors.get(status, '')}{symbol.get(status, '')} {message}{colors['RESET']}")

def main():
    """Check pipeline status in database."""
    print("\n" + "="*60)
    print("CHECK PIPELINE STATUS IN DATABASE")
    print("="*60 + "\n")
    
    # Get pipeline from API
    try:
        response = requests.get("http://localhost:8000/api/pipelines")
        response.raise_for_status()
        pipelines = response.json()
        pipeline = next((p for p in pipelines if p.get("name") == "final_test"), None)
        
        if not pipeline:
            print_status("Pipeline not found", "ERROR")
            return 1
        
        pipeline_id = pipeline.get("id")
        print_status(f"Pipeline ID: {pipeline_id}", "INFO")
    except Exception as e:
        print_status(f"Failed to get pipeline: {e}", "ERROR")
        return 1
    
    # Check database directly
    try:
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
                id,
                name,
                status,
                full_load_status,
                cdc_status,
                full_load_lsn,
                updated_at
            FROM pipelines
            WHERE id = %s
        """, (pipeline_id,))
        
        row = cursor.fetchone()
        if row:
            print_status("\n=== Database Status ===", "INFO")
            print(f"ID: {row[0]}")
            print(f"Name: {row[1]}")
            print(f"Status: {row[2]}")
            print(f"Full Load Status: {row[3]}")
            print(f"CDC Status: {row[4]}")
            print(f"Full Load LSN: {row[5]}")
            print(f"Updated At: {row[6]}")
            
            # Compare with API
            print_status("\n=== API Status ===", "INFO")
            print(f"Status: {pipeline.get('status')}")
            print(f"Full Load Status: {pipeline.get('full_load_status')}")
            print(f"CDC Status: {pipeline.get('cdc_status')}")
            
            # Check if they match
            if row[2] != pipeline.get('status'):
                print_status("Status mismatch!", "WARNING")
            if row[3] != pipeline.get('full_load_status'):
                print_status(f"Full Load Status mismatch! DB: {row[3]}, API: {pipeline.get('full_load_status')}", "ERROR")
            if row[4] != pipeline.get('cdc_status'):
                print_status("CDC Status mismatch!", "WARNING")
        else:
            print_status("Pipeline not found in database", "ERROR")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print_status(f"Database check failed: {e}", "ERROR")
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
