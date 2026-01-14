"""Start backend server."""
import sys
import os
import subprocess

# Change to the application directory
app_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(app_dir)

# Set PYTHONPATH
env = os.environ.copy()
env['PYTHONPATH'] = '.'

print("=" * 70)
print("Starting Backend Server")
print("=" * 70)
print(f"Working Directory: {os.getcwd()}")
print(f"Python: {sys.executable}")
print()

try:
    print("🚀 Starting uvicorn server on http://0.0.0.0:8000")
    print("   Press Ctrl+C to stop")
    print("=" * 70)
    print()
    
    # Start uvicorn
    subprocess.run([
        sys.executable, '-m', 'uvicorn',
        'ingestion.api:app',
        '--host', '0.0.0.0',
        '--port', '8000',
        '--reload'
    ], env=env, check=True)
    
except KeyboardInterrupt:
    print("\n\n✅ Backend stopped by user")
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()


