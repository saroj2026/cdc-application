"""Check if backend is running and restart if needed."""
import subprocess
import sys
import os

# Change to the application directory
app_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(app_dir)

print("=" * 70)
print("Backend Status Check")
print("=" * 70)

# Check if backend is running on port 8000
try:
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('localhost', 8000))
    sock.close()
    
    if result == 0:
        print("⚠️  Port 8000 is in use, but backend may be hung")
        print("   You may need to kill the process and restart")
    else:
        print("❌ Backend is NOT running on port 8000")
        print("   Starting backend...")
        
        # Start backend
        env = os.environ.copy()
        env['PYTHONPATH'] = '.'
        
        print("\n🚀 Starting backend server...")
        print("   Command: python -m uvicorn ingestion.api:app --host 0.0.0.0 --port 8000 --reload")
        print("\n   Press Ctrl+C to stop")
        print("=" * 70)
        
        subprocess.run([
            sys.executable, '-m', 'uvicorn',
            'ingestion.api:app',
            '--host', '0.0.0.0',
            '--port', '8000',
            '--reload'
        ], env=env)
        
except KeyboardInterrupt:
    print("\n\n✅ Backend stopped")
except Exception as e:
    print(f"\n❌ Error: {e}")
    print("\nTo start manually, run:")
    print("  cd seg-cdc-application")
    print("  $env:PYTHONPATH='.'")
    print("  python -m uvicorn ingestion.api:app --host 0.0.0.0 --port 8000 --reload")


