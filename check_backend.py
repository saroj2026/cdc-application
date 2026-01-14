"""Check if backend is running."""

import requests
import sys

try:
    r = requests.get('http://localhost:8000/health', timeout=5)
    print(f'✅ Backend Status: {r.status_code}')
    print(f'Response: {r.text[:300]}')
    sys.exit(0)
except requests.exceptions.ConnectionError:
    print('❌ Backend is not running (connection refused)')
    sys.exit(1)
except requests.exceptions.Timeout:
    print('⚠️  Backend is not responding (timeout)')
    sys.exit(1)
except Exception as e:
    print(f'⚠️  Error: {type(e).__name__}: {e}')
    sys.exit(1)


