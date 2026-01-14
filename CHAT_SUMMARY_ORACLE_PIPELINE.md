# Oracle to Snowflake Pipeline Setup - Summary

## What We've Accomplished

### 1. ✅ Created Oracle Test Table
- **Table**: `c##cdc_user.test` in Oracle XE
- **Location**: 72.61.233.209:1521
- **Data**: 5 test records inserted
- **Structure**: id (NUMBER PK), name, email, created_date, updated_date, status

### 2. ✅ Added Oracle Support to Backend
- **Database Enum**: Added 'oracle' to PostgreSQL `databasetype` enum
- **Oracle Connector**: Created `ingestion/connectors/oracle.py` with full support
- **Connection Service**: Added Oracle support in `connection_service.py`
- **Schema Service**: Added Oracle support in `schema_service.py`
- **Debezium Config**: Added Oracle Debezium connector configuration
- **Fixed SQL Queries**: Changed from bind variables to string formatting to fix ORA-01745 errors

### 3. ✅ Created Pipeline
- **Name**: `oracle_sf_p`
- **Source**: Oracle XE - `c##cdc_user.test`
- **Target**: Snowflake - `seg.public.test`
- **Mode**: `full_load_only` (for initial load)
- **Auto-create**: Enabled

### 4. ✅ Fixed Configuration Issues
- **Target Schema**: Changed from `PUBLIC` to `public` (lowercase) to match working `ps_sn_p` pipeline
- **Oracle SQL**: Fixed all queries to use `ALL_TAB_COLUMNS` and `ALL_TABLES` instead of `USER_*` views
- **Bind Variables**: Replaced with string formatting to avoid ORA-01745 errors
- **Connection Config**: Properly configured SID/service_name handling

### 5. ✅ Snowflake Table Structure
Based on the working `ps_sn_p` pipeline, Snowflake tables are auto-created with:
- **RECORD_CONTENT** (VARIANT): Contains the actual data from Oracle
- **RECORD_METADATA** (VARIANT): Contains Kafka metadata (CreateTime, offset, partition, topic)

This structure is automatically created by the Snowflake Kafka Connector when using:
- `JsonConverter` with `schemas.enable=true`
- `ExtractNewRecordState` transform
- Auto-create tables enabled

## Key Files Modified

1. **`ingestion/connectors/oracle.py`**: Complete Oracle connector implementation
2. **`ingestion/connection_service.py`**: Added Oracle support in `_get_connector` method
3. **`ingestion/schema_service.py`**: Added Oracle support for schema/table creation
4. **`ingestion/debezium_config.py`**: Added `_generate_oracle_config` method
5. **`ingestion/database/models_db.py`**: Added `ORACLE = "oracle"` to DatabaseType enum
6. **`ingestion/connectors/__init__.py`**: Exported OracleConnector

## Backend Restart Command

The backend is started with:
```powershell
$env:KAFKA_CONNECT_URL="http://72.61.233.209:8083"
$env:KAFKA_BOOTSTRAP_SERVERS="72.61.233.209:9092"
$env:DATABASE_URL="postgresql://cdc_user:cdc_pass@72.61.233.209:5432/cdctest"
$env:API_HOST="0.0.0.0"
$env:API_PORT="8000"
python -m uvicorn ingestion.api:app --host 0.0.0.0 --port 8000
```

## Pipeline Configuration

- **Pipeline ID**: `3b06bbae-2bbc-4526-ad6f-4e5d12c14f04`
- **Source Connection**: `oracle-xe` (18983f2b-3d93-43ca-a790-1571bf2f4bcb)
- **Target Connection**: `snowflake-s` (0221d59a-6bd8-4c53-99fa-069fbaadf4ae)
- **Target Schema**: `public` (lowercase, matches ps_sn_p)

## Next Steps

1. ✅ Backend restarted with all Oracle fixes
2. ⏳ Start pipeline with full load
3. ⏳ Verify data appears in Snowflake `seg.public.test` table
4. ⏳ After full load completes, switch to `full_load_and_cdc` mode for ongoing replication

## How to Start Full Load

After backend is running:
```python
import requests
API_BASE_URL = "http://localhost:8000/api/v1"
pipeline_id = "3b06bbae-2bbc-4526-ad6f-4e5d12c14f04"

# Update to full_load_only
requests.put(f"{API_BASE_URL}/pipelines/{pipeline_id}", json={"mode": "full_load_only"})

# Start pipeline
requests.post(f"{API_BASE_URL}/pipelines/{pipeline_id}/start")
```

## Troubleshooting

- **ORA-01745 Error**: Fixed by using string formatting instead of bind variables
- **Schema Case Sensitivity**: Fixed by using lowercase 'public' instead of 'PUBLIC'
- **Connection Issues**: Oracle connector properly handles SID vs service_name
- **Table Structure**: Snowflake auto-creates RECORD_CONTENT and RECORD_METADATA columns

