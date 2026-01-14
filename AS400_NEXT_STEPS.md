# AS400/IBM i CDC - Next Steps

This guide provides step-by-step instructions to implement and test AS400/IBM i CDC support.

## Step 1: Run Database Migration

Add AS400 to the database type enum:

```bash
cd /Users/kumargaurav/Desktop/CDCTEAM/cdcteam/seg-cdc-application
source venv/bin/activate
alembic upgrade head
```

**Expected Output:**
```
INFO  [alembic.runtime.migration] Running upgrade ... -> add_as400_enum, Add AS400 and IBM_I to DatabaseType enum
```

## Step 2: Install IBM i Access ODBC Driver

### For macOS:
1. Download IBM i Access Client Solutions from:
   https://www.ibm.com/support/pages/ibm-i-access-client-solutions
2. Install the package
3. Verify installation:
   ```bash
   odbcinst -q -d | grep -i ibm
   ```

### For Linux:
1. Download IBM i Access Client Solutions for Linux
2. Install using package manager
3. Verify:
   ```bash
   odbcinst -q -d
   ```

### For Windows:
1. Download and install IBM i Access Client Solutions
2. Verify in ODBC Data Source Administrator

## Step 3: Verify Backend is Running

```bash
cd /Users/kumargaurav/Desktop/CDCTEAM/cdcteam/seg-cdc-application
source venv/bin/activate
./start_backend.sh
```

Check if backend is accessible:
```bash
curl http://localhost:8000/api/v1/health
```

## Step 4: Create AS400 Connection

### Option A: Via Frontend UI

1. Open http://localhost:3000/connections
2. Click "Add Connection"
3. Fill in connection details:
   - **Name**: AS400 Production (or your name)
   - **Type**: Source
   - **Database Type**: AS400 (or IBM i)
   - **Host**: Your AS400 server IP/hostname
   - **Port**: 446 (default)
   - **Database**: Library name (e.g., "MYLIB")
   - **Schema**: Library name (same as database)
   - **Username**: AS400 user
   - **Password**: AS400 password
   - **Additional Config** (optional):
     ```json
     {
       "journal_library": "QSYS",
       "driver": "IBM i Access ODBC Driver"
     }
     ```
4. Click "Test Connection"
5. If successful, click "Save"

### Option B: Via API

```bash
curl -X POST http://localhost:8000/api/v1/connections \
  -H "Content-Type: application/json" \
  -d '{
    "name": "AS400 Production",
    "connection_type": "source",
    "database_type": "as400",
    "host": "as400.example.com",
    "port": 446,
    "database": "MYLIB",
    "schema": "MYLIB",
    "username": "myuser",
    "password": "mypassword",
    "additional_config": {
      "journal_library": "QSYS"
    }
  }'
```

## Step 5: Enable Journaling on AS400 Tables

**Important**: Journaling must be enabled on tables you want to replicate.

On AS400/IBM i, run:

```sql
-- Enable journaling for a table
STRJRNPF FILE(MYLIB/MYTABLE) JRN(MYLIB/MYJOURNAL)

-- Verify journal is active
SELECT * FROM QSYS2.JOURNAL_INFO
WHERE JOURNAL_LIBRARY = 'MYLIB' AND JOURNAL_NAME = 'MYJOURNAL'
```

## Step 6: Create Target Connection

Create a target connection (PostgreSQL, SQL Server, or S3) if you don't have one:

### PostgreSQL Target:
```json
{
  "name": "PostgreSQL Target",
  "connection_type": "target",
  "database_type": "postgresql",
  "host": "72.61.233.209",
  "port": 5432,
  "database": "cdctest",
  "schema": "public",
  "username": "cdc_user",
  "password": "cdc_pass"
}
```

### SQL Server Target:
```json
{
  "name": "SQL Server Target",
  "connection_type": "target",
  "database_type": "sqlserver",
  "host": "your-sql-server",
  "port": 1433,
  "database": "cdctest",
  "schema": "dbo",
  "username": "sa",
  "password": "your-password"
}
```

### S3 Target:
```json
{
  "name": "S3 Target",
  "connection_type": "target",
  "database_type": "s3",
  "host": "s3.amazonaws.com",
  "port": 443,
  "database": "mycdcbucket26",
  "schema": "public/",
  "username": "AWS_ACCESS_KEY_ID",
  "password": "AWS_SECRET_ACCESS_KEY",
  "additional_config": {
    "region_name": "us-east-1"
  }
}
```

## Step 7: Create Pipeline

### Via Frontend UI:

1. Go to http://localhost:3000/pipelines
2. Click "Create Pipeline"
3. Fill in pipeline details:
   - **Name**: AS400_to_PostgreSQL_Test
   - **Source Connection**: Select your AS400 connection
   - **Target Connection**: Select your target connection
   - **Source Database**: Library name
   - **Source Schema**: Library name
   - **Source Tables**: Select tables to replicate
   - **Mode**: Full Load and CDC
4. Click "Create"

### Via API:

```bash
curl -X POST http://localhost:8000/api/v1/pipelines \
  -H "Content-Type: application/json" \
  -d '{
    "name": "AS400_to_PostgreSQL_Test",
    "source_connection_id": "your-as400-connection-id",
    "target_connection_id": "your-target-connection-id",
    "source_database": "MYLIB",
    "source_schema": "MYLIB",
    "source_tables": ["MYTABLE1", "MYTABLE2"],
    "target_database": "cdctest",
    "target_schema": "public",
    "mode": "full_load_and_cdc"
  }'
```

## Step 8: Start Pipeline

### Via Frontend:
1. Find your pipeline in the list
2. Click "Run" button

### Via API:
```bash
curl -X POST http://localhost:8000/api/v1/pipelines/{pipeline_id}/start
```

## Step 9: Verify Data Flow

### Check Pipeline Status:
```bash
curl http://localhost:8000/api/v1/pipelines/{pipeline_id}
```

### Check Debezium Connector:
```bash
curl http://72.61.233.209:8083/connectors/cdc-{pipeline_name}-as400-{schema}/status
```

### Check Kafka Topics:
```bash
# List topics
kafka-topics --bootstrap-server 72.61.233.209:9092 --list | grep {pipeline_name}
```

### Check Target Database:
- For PostgreSQL: Query target tables
- For SQL Server: Query target tables
- For S3: Check S3 bucket for files

## Step 10: Test CDC

1. Add/update a record in AS400 table:
   ```sql
   INSERT INTO MYLIB.MYTABLE (COL1, COL2) VALUES ('Test', 'Data')
   ```

2. Wait a few seconds

3. Verify record appears in target:
   - PostgreSQL: `SELECT * FROM public.mytable WHERE col1 = 'Test'`
   - SQL Server: `SELECT * FROM dbo.mytable WHERE col1 = 'Test'`
   - S3: Check for new files in bucket

## Troubleshooting

### Connection Test Fails

**Error**: `No ODBC driver found`

**Solution**:
1. Verify IBM i Access is installed
2. Check driver name: `odbcinst -q -d`
3. Specify driver in additional_config:
   ```json
   {
     "driver": "IBM i Access ODBC Driver"
   }
   ```

### CDC Not Working

**Error**: No changes captured

**Solution**:
1. Verify journaling is enabled:
   ```sql
   SELECT * FROM QSYS2.JOURNAL_INFO
   WHERE JOURNAL_LIBRARY = 'MYLIB'
   ```
2. Check Debezium connector status
3. Check Kafka Connect logs

### Debezium Connector Fails

**Error**: `Connector class not found`

**Solution**:
1. Install Debezium Db2 connector in Kafka Connect
2. Restart Kafka Connect
3. Verify connector is in plugins directory

## Verification Checklist

- [ ] Database migration completed
- [ ] IBM i Access ODBC Driver installed
- [ ] AS400 connection created and tested
- [ ] Target connection created
- [ ] Journaling enabled on AS400 tables
- [ ] Pipeline created
- [ ] Pipeline started successfully
- [ ] Debezium connector running
- [ ] Sink connector running
- [ ] Data flowing to target
- [ ] CDC changes captured

## Quick Test Script

```python
# test_as400_connection.py
import requests

# Test connection
response = requests.post(
    "http://localhost:8000/api/v1/connections/{connection_id}/test"
)
print(f"Connection test: {response.json()}")

# Create pipeline
pipeline_data = {
    "name": "AS400_Test",
    "source_connection_id": "your-as400-connection-id",
    "target_connection_id": "your-target-connection-id",
    "source_database": "MYLIB",
    "source_schema": "MYLIB",
    "source_tables": ["MYTABLE"],
    "mode": "full_load_and_cdc"
}

response = requests.post(
    "http://localhost:8000/api/v1/pipelines",
    json=pipeline_data
)
print(f"Pipeline created: {response.json()}")

# Start pipeline
pipeline_id = response.json()["id"]
response = requests.post(
    f"http://localhost:8000/api/v1/pipelines/{pipeline_id}/start"
)
print(f"Pipeline started: {response.json()}")
```

## Support

For issues or questions:
1. Check `AS400_SETUP_GUIDE.md` for detailed documentation
2. Review backend logs: `tail -f logs/backend.log`
3. Check Kafka Connect logs on server
4. Verify AS400 journaling is active


