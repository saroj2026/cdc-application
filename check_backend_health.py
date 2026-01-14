"""Script to check backend health and diagnose timeout issues."""

import requests
import sys
import time

def check_backend_health():
    """Check backend API health and diagnose issues."""
    api_url = "http://localhost:8000"
    
    print(f"🔍 Checking backend API at {api_url}...\n")
    
    # Check health endpoint
    print("1. Checking /health endpoint...")
    try:
        start_time = time.time()
        response = requests.get(f"{api_url}/health", timeout=5)
        elapsed = time.time() - start_time
        if response.status_code == 200:
            health = response.json()
            print(f"   ✓ Health endpoint responded in {elapsed:.2f}s")
            print(f"   Database: {health.get('database', {}).get('status', 'unknown')}")
            kafka_status = health.get('kafka_connect', {})
            print(f"   Kafka Connect: {kafka_status.get('status', 'unknown')}")
            if kafka_status.get('status') == 'unreachable':
                print(f"      Error: {kafka_status.get('error', 'N/A')}")
        else:
            print(f"   ⚠️  Health endpoint returned status {response.status_code}")
    except requests.exceptions.Timeout:
        print(f"   ❌ Health endpoint timed out (>5s)")
    except requests.exceptions.ConnectionError:
        print(f"   ❌ Cannot connect to backend - is it running?")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Check connections endpoint with shorter timeout
    print("\n2. Checking /api/v1/connections endpoint...")
    try:
        start_time = time.time()
        response = requests.get(f"{api_url}/api/v1/connections", timeout=10)
        elapsed = time.time() - start_time
        if response.status_code == 200:
            connections = response.json()
            print(f"   ✓ Connections endpoint responded in {elapsed:.2f}s")
            if isinstance(connections, list):
                print(f"   Found {len(connections)} connections")
            elif isinstance(connections, dict):
                print(f"   Response: {connections}")
        else:
            print(f"   ⚠️  Connections endpoint returned status {response.status_code}")
            print(f"   Response: {response.text[:200]}")
    except requests.exceptions.Timeout:
        print(f"   ❌ Connections endpoint timed out (>10s)")
        print(f"   This is the issue - the endpoint is taking too long to respond")
    except requests.exceptions.ConnectionError:
        print(f"   ❌ Cannot connect to backend")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Check if backend process is running (Windows)
    print("\n3. Checking if backend process is running...")
    try:
        import subprocess
        # Check for Python processes running api.py or uvicorn
        result = subprocess.run(
            ["tasklist", "/FI", "IMAGENAME eq python.exe", "/FO", "CSV"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if "python.exe" in result.stdout:
            print(f"   ✓ Python processes are running")
            # Try to find uvicorn or api.py processes
            lines = result.stdout.split('\n')
            python_count = sum(1 for line in lines if 'python.exe' in line)
            print(f"   Found {python_count} Python process(es)")
        else:
            print(f"   ⚠️  No Python processes found")
    except Exception as e:
        print(f"   ⚠️  Could not check processes: {e}")
    
    print("\n💡 Recommendations:")
    print("   1. If backend is not running, start it:")
    print("      python -m uvicorn ingestion.api:app --reload --host 0.0.0.0 --port 8000")
    print("   2. If backend is running but timing out:")
    print("      - Check backend logs for errors")
    print("      - The connections endpoint might be hanging on database queries")
    print("      - Restart the backend")
    print("   3. Check database connection:")
    print("      - Ensure PostgreSQL is accessible")
    print("      - Check database credentials")

if __name__ == "__main__":
    check_backend_health()


