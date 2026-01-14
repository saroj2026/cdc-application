"""Script to restart the backend server."""

import subprocess
import sys
import os
import time
import signal

def find_backend_processes():
    """Find running backend processes."""
    try:
        # On Windows, use tasklist to find Python processes
        result = subprocess.run(
            ["tasklist", "/FI", "IMAGENAME eq python.exe", "/FO", "CSV"],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        processes = []
        lines = result.stdout.split('\n')
        for line in lines[1:]:  # Skip header
            if 'python.exe' in line:
                # Parse CSV line
                parts = line.split('","')
                if len(parts) >= 2:
                    pid = parts[1].strip('"')
                    processes.append(pid)
        
        return processes
    except Exception as e:
        print(f"⚠️  Could not list processes: {e}")
        return []

def kill_backend_processes():
    """Kill existing backend processes."""
    processes = find_backend_processes()
    if not processes:
        print("ℹ️  No Python processes found to kill")
        return True
    
    print(f"🔍 Found {len(processes)} Python process(es)")
    print("⚠️  Note: This will kill ALL Python processes. Make sure no other important Python scripts are running.")
    
    killed = 0
    for pid in processes:
        try:
            subprocess.run(["taskkill", "/F", "/PID", pid], 
                         capture_output=True, timeout=5)
            print(f"   ✓ Killed process {pid}")
            killed += 1
        except Exception as e:
            print(f"   ⚠️  Could not kill process {pid}: {e}")
    
    if killed > 0:
        print(f"✅ Killed {killed} process(es)")
        time.sleep(2)  # Wait a moment for processes to fully terminate
        return True
    return False

def start_backend():
    """Start the backend server."""
    print("\n🚀 Starting backend server...")
    print("   Command: python -m uvicorn ingestion.api:app --reload --host 0.0.0.0 --port 8000")
    print("\n   The backend will start in the background.")
    print("   Check the terminal output for any errors.")
    print("   Press Ctrl+C in that terminal to stop the backend.\n")
    
    try:
        # Start backend in a new process
        # On Windows, use CREATE_NEW_CONSOLE to open a new window
        subprocess.Popen(
            ["python", "-m", "uvicorn", "ingestion.api:app", "--reload", "--host", "0.0.0.0", "--port", "8000"],
            creationflags=subprocess.CREATE_NEW_CONSOLE if sys.platform == "win32" else 0
        )
        print("✅ Backend server started!")
        print("\n💡 The backend should be accessible at http://localhost:8000")
        print("   Wait a few seconds for it to fully start, then try the UI again.")
        return True
    except Exception as e:
        print(f"❌ Failed to start backend: {e}")
        return False

if __name__ == "__main__":
    print("🔄 Restarting backend server...\n")
    
    # Kill existing processes
    print("1. Stopping existing backend processes...")
    kill_backend_processes()
    
    # Wait a moment
    time.sleep(1)
    
    # Start backend
    print("\n2. Starting new backend process...")
    if start_backend():
        print("\n✅ Backend restart initiated!")
        print("\n📝 Next steps:")
        print("   1. Wait 5-10 seconds for the backend to start")
        print("   2. Check http://localhost:8000/health to verify it's running")
        print("   3. Try the UI again - the connections endpoint should work now")
    else:
        print("\n❌ Failed to restart backend")
        print("   Please start it manually:")
        print("   python -m uvicorn ingestion.api:app --reload --host 0.0.0.0 --port 8000")
        sys.exit(1)


