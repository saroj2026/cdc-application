# PostgreSQL to S3 Pipeline - Full Load Only

## ✅ Pipeline Created Successfully

### Pipeline Details

- **Pipeline ID**: `b2937ed9-ab57-4965-9726-3e89b7ca0646`
- **Name**: `PostgreSQL_to_S3_cdctest`
- **Mode**: `full_load_only`
- **Status**: `STOPPED`
- **Created At**: 2025-12-31T12:40:58

### Source Connection (PostgreSQL)

- **Connection ID**: `61e57610-f088-48ec-8938-d07cf3903643`
- **Name**: `POSTGRE`
- **Database**: `cdctest`
- **Schema**: `public`

### Target Connection (S3)

- **Connection ID**: `d9d0175d-45e9-49c8-a926-2accb5114783`
- **Name**: `My CDC S3 Bucket - mycdcbucket26`
- **Bucket**: `mycdcbucket26`
- **Region**: `us-east-1`
- **Schema/Prefix**: (empty - root of bucket)

### Tables to Replicate

The pipeline will perform a full load of the following 5 tables:

1. `alembic_version`
2. `alert_history`
3. `alert_rules`
4. `audit_logs`
5. `connection_tests`

### Pipeline Configuration

- **Full Load Enabled**: `true`
- **Auto Create Target**: `true`
- **Full Load Status**: `NOT_STARTED`
- **CDC Status**: `NOT_STARTED` (not applicable for full_load_only mode)

## 🚀 How to Start the Pipeline

### Using API

```bash
POST http://localhost:8000/api/pipelines/b2937ed9-ab57-4965-9726-3e89b7ca0646/start
```

### Using cURL

```bash
curl -X POST http://localhost:8000/api/pipelines/b2937ed9-ab57-4965-9726-3e89b7ca0646/start
```

### Using Python

```python
import requests

response = requests.post(
    "http://localhost:8000/api/pipelines/b2937ed9-ab57-4965-9726-3e89b7ca0646/start"
)
print(response.json())
```

## 📊 Monitor Pipeline Status

### Get Pipeline Status

```bash
GET http://localhost:8000/api/pipelines/b2937ed9-ab57-4965-9726-3e89b7ca0646
```

### List All Pipelines

```bash
GET http://localhost:8000/api/pipelines
```

## 📝 What Happens During Full Load

1. **Schema Extraction**: The pipeline will extract schema from PostgreSQL tables
2. **Data Extraction**: Full data will be read from each source table
3. **Data Transformation**: Data will be formatted for S3 storage (JSON/CSV)
4. **S3 Upload**: Data will be uploaded to S3 bucket `mycdcbucket26` with appropriate prefixes
5. **Completion**: Pipeline status will change to `COMPLETED` when done

## 🔍 Expected S3 Structure

After the full load completes, you should see files in your S3 bucket like:

```
mycdcbucket26/
├── alembic_version/
│   └── full_load_<timestamp>.json
├── alert_history/
│   └── full_load_<timestamp>.json
├── alert_rules/
│   └── full_load_<timestamp>.json
├── audit_logs/
│   └── full_load_<timestamp>.json
└── connection_tests/
    └── full_load_<timestamp>.json
```

## ⚠️ Notes

- This pipeline is configured for **full load only** - it will not perform CDC (Change Data Capture)
- The pipeline will extract all data from the specified tables at the time of execution
- Data will be stored in JSON format in S3
- The pipeline can be run multiple times to refresh the data in S3

## 🛑 Stop Pipeline

If needed, you can stop the pipeline:

```bash
POST http://localhost:8000/api/pipelines/b2937ed9-ab57-4965-9726-3e89b7ca0646/stop
```

