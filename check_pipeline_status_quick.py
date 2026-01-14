"""Quick check of pipeline status."""

import sys
import requests
import psycopg2

BASE_URL = "http://localhost:8000"
PIPELINE_NAME = "final_test2"

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

if __name__ == "__main__":
    pipeline_id = get_pipeline_id(PIPELINE_NAME)
    if not pipeline_id:
        print(f"Pipeline '{PIPELINE_NAME}' not found")
        sys.exit(1)
    
    print(f"Pipeline ID: {pipeline_id}\n")
    
    api_status = get_pipeline_status_api(pipeline_id)
    db_status = get_pipeline_status_db(pipeline_id)
    
    print("API Status:")
    print(f"  Status: {api_status.get('status')}")
    print(f"  Full Load: {api_status.get('full_load_status')}")
    print(f"  CDC: {api_status.get('cdc_status')}")
    
    print("\nDB Status:")
    if db_status:
        print(f"  Status: {db_status.get('status')}")
        print(f"  Full Load: {db_status.get('full_load_status')}")
        print(f"  CDC: {db_status.get('cdc_status')}")
        print(f"  Updated At: {db_status.get('updated_at')}")
    else:
        print("  Not found in database")


import sys
import requests
import psycopg2

BASE_URL = "http://localhost:8000"
PIPELINE_NAME = "final_test2"

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

if __name__ == "__main__":
    pipeline_id = get_pipeline_id(PIPELINE_NAME)
    if not pipeline_id:
        print(f"Pipeline '{PIPELINE_NAME}' not found")
        sys.exit(1)
    
    print(f"Pipeline ID: {pipeline_id}\n")
    
    api_status = get_pipeline_status_api(pipeline_id)
    db_status = get_pipeline_status_db(pipeline_id)
    
    print("API Status:")
    print(f"  Status: {api_status.get('status')}")
    print(f"  Full Load: {api_status.get('full_load_status')}")
    print(f"  CDC: {api_status.get('cdc_status')}")
    
    print("\nDB Status:")
    if db_status:
        print(f"  Status: {db_status.get('status')}")
        print(f"  Full Load: {db_status.get('full_load_status')}")
        print(f"  CDC: {db_status.get('cdc_status')}")
        print(f"  Updated At: {db_status.get('updated_at')}")
    else:
        print("  Not found in database")

