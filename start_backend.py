"""Start backend server with proper error handling."""
import sys
import os
import subprocess

# Change to the application directory
app_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(app_dir)

print("=" * 70)
print("Starting Backend Server")
print("=" * 70)
print(f"Working Directory: {os.getcwd()}")
print(f"Python: {sys.executable}")
print()

# Set PYTHONPATH
env = os.environ.copy()
env['PYTHONPATH'] = '.'

try:
    print("🚀 Starting uvicorn server...")
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
except subprocess.CalledProcessError as e:
    print(f"\n❌ Error starting backend: {e}")
    print("\nTrying to diagnose...")
    try:
        # Try importing the module to see if there's an import error
        import ingestion.api
        print("✅ Module imports successfully")
    except Exception as import_error:
        print(f"❌ Import error: {import_error}")
        import traceback
        traceback.print_exc()
except Exception as e:
    print(f"\n❌ Unexpected error: {e}")
    import traceback
    traceback.print_exc()


