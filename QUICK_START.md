# Quick Start Guide

## Create a CDC Pipeline in 3 Steps

### Step 1: Start Kafka Infrastructure

```bash
docker-compose up -d
```

Wait 30 seconds for services to start.

### Step 2: Provide Your Credentials

Create a script or use the provided example:

```python
from create_cdc_pipeline import create_pipeline_from_credentials

result = create_pipeline_from_credentials(
    # Your PostgreSQL (Source)
    source_host="your-postgres-host",
    source_port=5432,
    source_database="your_database",
    source_schema="public",
    source_user="your_user",
    source_password="your_password",
    source_tables=["table1", "table2"],  # Tables to replicate
    
    # Your SQL Server (Target)
    target_host="your-sqlserver-host",
    target_port=1433,
    target_database="target_database",
    target_schema="dbo",
    target_user="sa",
    target_password="your_password"
)
```

### Step 3: Verify It's Working

```bash
python check_realtime_cdc.py
```

**That's it!** Real-time CDC is now active.

## What Happens Automatically

1. ✅ **Connection Validation** - Tests both databases
2. ✅ **Pipeline Creation** - Creates pipeline object
3. ✅ **Debezium Config Generated** - All Kafka Connect configs created
4. ✅ **Sink Config Generated** - JDBC connector config created
5. ✅ **Connectors Deployed** - Created in Kafka Connect
6. ✅ **Replication Started** - Real-time CDC active

## No Manual Configuration Needed!

- ❌ No Kafka config files to write
- ❌ No Debezium configs to create
- ❌ No JDBC Sink configs to write
- ❌ No replication slots to manage
- ❌ No publications to configure

**Just provide credentials - we handle everything!**


