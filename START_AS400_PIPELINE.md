# Start AS400-S3_P Pipeline

## Prerequisites

1. **Backend must be running** on http://localhost:8000
2. **Pipeline must exist** with name "AS400-S3_P"

## Quick Start

### Option 1: Using the Script (Recommended)

```bash
cd /Users/kumargaurav/Desktop/CDCTEAM/cdcteam/seg-cdc-application
python3 start_as400_pipeline.py
```

### Option 2: Using API Directly

```bash
# 1. Find the pipeline ID
curl http://localhost:8000/api/v1/pipelines | jq '.[] | select(.name=="AS400-S3_P")'

# 2. Start the pipeline (replace PIPELINE_ID)
curl -X POST http://localhost:8000/api/v1/pipelines/PIPELINE_ID/start
```

### Option 3: Using Python Script

```python
import requests

API_BASE_URL = "http://localhost:8000"
PIPELINE_NAME = "AS400-S3_P"

# Get all pipelines
response = requests.get(f"{API_BASE_URL}/api/v1/pipelines")
pipelines = response.json()

# Find AS400-S3_P pipeline
pipeline = next((p for p in pipelines if p.get("name") == PIPELINE_NAME), None)

if pipeline:
    pipeline_id = pipeline.get("id")
    print(f"Starting pipeline: {pipeline_id}")
    
    # Start pipeline
    response = requests.post(f"{API_BASE_URL}/api/v1/pipelines/{pipeline_id}/start")
    
    if response.status_code == 200:
        print("✅ Pipeline started successfully!")
        print(response.json())
    else:
        print(f"❌ Failed: {response.status_code}")
        print(response.text)
else:
    print(f"Pipeline '{PIPELINE_NAME}' not found")
```

## If Backend is Not Running

Start the backend first:

```bash
cd /Users/kumargaurav/Desktop/CDCTEAM/cdcteam/seg-cdc-application
./start_backend_simple.sh
```

Or manually:

```bash
cd /Users/kumargaurav/Desktop/CDCTEAM/cdcteam/seg-cdc-application
source venv/bin/activate
export KAFKA_CONNECT_URL=http://72.61.233.209:8083
export KAFKA_BOOTSTRAP_SERVERS=72.61.233.209:9092
export DATABASE_URL=postgresql://cdc_user:cdc_pass@72.61.233.209:5432/cdctest
uvicorn ingestion.api:app --host 0.0.0.0 --port 8000
```

## Check Pipeline Status

After starting, check the status:

```bash
# Using the script
python3 check_as400_pipeline_cdc.py

# Or using API
curl http://localhost:8000/api/v1/pipelines | jq '.[] | select(.name=="AS400-S3_P")'
```

## Monitor Pipeline

1. **Frontend UI**: http://localhost:3000/pipelines
2. **API Status**: `GET /api/v1/pipelines/{pipeline_id}/status`
3. **CDC Status**: `python check_as400_pipeline_cdc.py`
4. **S3 Data Flow**: `python check_s3_sink_data.py`

## Troubleshooting

### Backend Connection Error
- Make sure backend is running: `curl http://localhost:8000/api/v1/health`
- Check if port 8000 is in use: `lsof -i :8000`

### Pipeline Not Found
- List all pipelines: `curl http://localhost:8000/api/v1/pipelines`
- Check pipeline name spelling (case-sensitive)

### Pipeline Start Fails
- Check backend logs for errors
- Verify Kafka Connect is running: `curl http://72.61.233.209:8083/connector-plugins`
- Verify AS400 connector is installed
- Check database connections are valid

