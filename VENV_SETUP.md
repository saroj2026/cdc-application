# Virtual Environment Setup

## ✅ Virtual Environment Created

A Python virtual environment has been created and all requirements have been installed.

**Location**: `/Users/kumargaurav/Desktop/CDCTEAM/cdcteam/seg-cdc-application/venv`

## Installed Packages

All packages from `requirements.txt` have been successfully installed:
- ✅ FastAPI
- ✅ Uvicorn
- ✅ SQLAlchemy
- ✅ psycopg2-binary
- ✅ Alembic
- ✅ Requests
- ✅ Redis
- ✅ And all other dependencies

## Using the Virtual Environment

### Activate the Virtual Environment

```bash
cd /Users/kumargaurav/Desktop/CDCTEAM/cdcteam/seg-cdc-application
source venv/bin/activate
```

You'll see `(venv)` in your terminal prompt when activated.

### Start Backend (with venv)

The `start_backend.sh` script has been updated to automatically use the virtual environment:

```bash
./start_backend.sh
```

Or manually:
```bash
source venv/bin/activate
export KAFKA_CONNECT_URL=http://72.61.233.209:8083
export KAFKA_BOOTSTRAP_SERVERS=72.61.233.209:9092
export DATABASE_URL=postgresql://cdc_user:cdc_password@localhost:5434/cdc_management
python -m ingestion.api
```

### Deactivate Virtual Environment

When you're done:
```bash
deactivate
```

## Verify Installation

Test that all dependencies are available:
```bash
source venv/bin/activate
python -c "import fastapi, uvicorn, sqlalchemy, psycopg2; print('✅ All dependencies available')"
```

## Benefits of Using venv

1. **Isolated Dependencies**: No conflicts with system Python packages
2. **Reproducible Environment**: Same packages across different machines
3. **Easy Cleanup**: Just delete the `venv` folder to remove everything
4. **Version Control**: Can be recreated from `requirements.txt`

## Troubleshooting

### If venv is not found
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### If packages are missing
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### Check installed packages
```bash
source venv/bin/activate
pip list
```



