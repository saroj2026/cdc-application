# Manual Backend Start Instructions

If the backend is not starting automatically, follow these steps:

## Option 1: Using the Script (Recommended)

```bash
cd /Users/kumargaurav/Desktop/CDCTEAM/cdcteam/seg-cdc-application
chmod +x start_backend_simple.sh
./start_backend_simple.sh
```

## Option 2: Manual Start (Step by Step)

### Step 1: Navigate to project directory
```bash
cd /Users/kumargaurav/Desktop/CDCTEAM/cdcteam/seg-cdc-application
```

### Step 2: Activate virtual environment
```bash
source venv/bin/activate
```

You should see `(venv)` in your terminal prompt.

### Step 3: Set environment variables
```bash
export KAFKA_CONNECT_URL=http://72.61.233.209:8083
export KAFKA_BOOTSTRAP_SERVERS=72.61.233.209:9092
export DATABASE_URL=postgresql://cdc_user:cdc_pass@72.61.233.209:5432/cdctest
export API_HOST=0.0.0.0
export API_PORT=8000
```

### Step 4: Start the backend

**Option A: Using uvicorn directly (Recommended)**
```bash
uvicorn ingestion.api:app --host 0.0.0.0 --port 8000
```

**Option B: Using Python module**
```bash
python -m ingestion.api
```

**Option C: Using Python directly**
```bash
python -m uvicorn ingestion.api:app --host 0.0.0.0 --port 8000
```

## Verify Backend is Running

Open a new terminal and run:
```bash
curl http://localhost:8000/docs
```

Or open in browser:
```
http://localhost:8000/docs
```

## Troubleshooting

### If you see "ModuleNotFoundError"
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### If you see "Port already in use"
```bash
# Find and kill the process
lsof -ti:8000 | xargs kill -9

# Or
pkill -f "uvicorn"
pkill -f "python.*api"
```

### If you see database connection errors
Check that:
- The database is accessible at `72.61.233.209:5432`
- Credentials are correct: `cdc_user:cdc_pass`
- Database `cdctest` exists

### If you see Kafka connection errors
Check that:
- Kafka Connect is running at `http://72.61.233.209:8083`
- Kafka is accessible at `72.61.233.209:9092`

## Expected Output

When the backend starts successfully, you should see:
```
INFO:     Started server process [PID]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

## Stop the Backend

Press `Ctrl+C` in the terminal where it's running.

Or kill it:
```bash
pkill -f "uvicorn"
pkill -f "python.*api"
```

