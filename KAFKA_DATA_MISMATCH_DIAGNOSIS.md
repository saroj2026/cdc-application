# Kafka Topic Data Mismatch Diagnosis

## Issue
Pipeline `pg_to_mssql_projects_simple` is configured to capture `projects_simple` table (with columns: `project_id`, `project_name`, `department_id`, `employee_id`, `start_date`, `end_date`, `status`), but the data in Kafka topics shows `id`, `name`, `location` (which matches the `department` table structure).

## Current Configuration Status

### ✅ Correct Configuration:
- **Pipeline Name**: `pg_to_mssql_projects_simple`
- **Source Table**: `projects_simple` ✅
- **Debezium Connector**: `cdc-pg_to_mssql_projects_simple-pg-public`
- **Table Include List**: `public.projects_simple` ✅
- **Expected Kafka Topic**: `pg_to_mssql_projects_simple.public.projects_simple`
- **Publication**: Only includes `projects_simple` (not all tables) ✅

### 📊 Table Structures:

**projects_simple** (expected):
- `project_id` (integer)
- `project_name` (varchar)
- `department_id` (integer)
- `employee_id` (integer)
- `start_date` (date)
- `end_date` (date)
- `status` (varchar)

**department** (what you're seeing):
- `id` (integer)
- `name` (varchar)
- `location` (varchar)

## Possible Causes

### 1. Wrong Kafka Topic Being Checked
**Most Likely**: You might be looking at a different Kafka topic.

**Check**:
- Verify you're looking at topic: `pg_to_mssql_projects_simple.public.projects_simple`
- Not: `pg_to_mssql_projects_simple.public.department` or any other topic

**Solution**:
```bash
# List all topics
kafka-topics --bootstrap-server 72.61.233.209:9092 --list

# Check specific topic
kafka-console-consumer --bootstrap-server 72.61.233.209:9092 \
  --topic pg_to_mssql_projects_simple.public.projects_simple \
  --from-beginning --max-messages 5
```

### 2. Another Connector Capturing Department
**Check**: Another Debezium connector might be capturing the `department` table.

**Solution**:
```bash
# Check all connectors
curl http://72.61.233.209:8083/connectors

# Check each connector's table.include.list
curl http://72.61.233.209:8083/connectors/{connector_name}/config | jq '.["table.include.list"]'
```

### 3. Publication Issue (Unlikely - Already Verified)
The publication is correctly configured to only include `projects_simple`.

### 4. Debezium Transform Issue
**Unlikely**: Debezium should capture all columns from the table as configured.

## Diagnostic Steps

### Step 1: Verify Kafka Topic Name
```bash
# List all topics
kafka-topics --bootstrap-server 72.61.233.209:9092 --list | grep pg_to_mssql
```

### Step 2: Check Actual Topic Content
```bash
# Check projects_simple topic
kafka-console-consumer --bootstrap-server 72.61.233.209:9092 \
  --topic pg_to_mssql_projects_simple.public.projects_simple \
  --from-beginning --max-messages 1 \
  --property print.key=true \
  --property print.value=true
```

### Step 3: Check for Department Topic
```bash
# Check if department topic exists
kafka-topics --bootstrap-server 72.61.233.209:9092 --list | grep department
```

### Step 4: Verify Connector Status
```bash
# Check connector status
curl http://72.61.233.209:8083/connectors/cdc-pg_to_mssql_projects_simple-pg-public/status | jq
```

## Solutions

### Solution 1: Verify Correct Topic
Make sure you're checking the correct topic:
- **Correct**: `pg_to_mssql_projects_simple.public.projects_simple`
- **Wrong**: Any other topic name

### Solution 2: Check Sink Connector
The sink connector might be consuming from the wrong topic:

```bash
# Check sink connector config
curl http://72.61.233.209:8083/connectors/sink-pg_to_mssql_projects_simple-mssql-dbo/config | jq '.["topics"]'
```

### Solution 3: Recreate Connector (If Needed)
If the connector is somehow capturing the wrong table:

1. Stop the pipeline
2. Delete the Debezium connector
3. Recreate the pipeline
4. Start the pipeline

## Expected Kafka Message Format

For `projects_simple` table, you should see messages like:

```json
{
  "schema": {...},
  "payload": {
    "before": null,
    "after": {
      "project_id": 1,
      "project_name": "CDC Pipeline Setup",
      "department_id": 200,
      "employee_id": 101,
      "start_date": 18993,
      "end_date": null,
      "status": "ACTIVE"
    },
    "source": {...},
    "op": "c",
    "ts_ms": 1234567890
  }
}
```

**NOT**:
```json
{
  "after": {
    "id": 1,
    "name": "Engineering",
    "location": "Bangalore"
  }
}
```

## Next Steps

1. **Verify the exact Kafka topic name** you're checking
2. **Check if there are multiple topics** (one for projects_simple, one for department)
3. **Verify the sink connector** is consuming from the correct topic
4. **Check if there's another pipeline** capturing the department table

## Quick Check Script

Run this to verify:
```bash
cd /Users/kumargaurav/Desktop/CDCTEAM/cdcteam/seg-cdc-application
source venv/bin/activate
python3 check_kafka_topic_data.py
```


