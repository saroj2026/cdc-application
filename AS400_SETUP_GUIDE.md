# AS400/IBM i CDC Setup Guide

This guide explains how to set up Change Data Capture (CDC) for AS400/IBM i systems.

## Overview

AS400/IBM i CDC support has been added to the CDC application. It uses:
- **Debezium Db2 Connector** for capturing changes
- **IBM i Journaling** for change tracking
- **ODBC** for database connectivity

## Prerequisites

### 1. IBM i Access Client Solutions

Install IBM i Access Client Solutions on the system where the CDC application runs:

**For macOS:**
```bash
# Download from IBM website
# https://www.ibm.com/support/pages/ibm-i-access-client-solutions
```

**For Linux:**
```bash
# Download and install IBM i Access Client Solutions for Linux
```

**For Windows:**
- Download and install from IBM website

### 2. Enable Journaling on AS400

Journaling must be enabled on the tables you want to replicate:

```sql
-- On AS400/IBM i, enable journaling for a table
STRJRNPF FILE(LIBRARY/TABLENAME) JRN(LIBRARY/JOURNALNAME)
```

### 3. Debezium Db2 Connector

Ensure the Debezium Db2 connector is installed in Kafka Connect:

```bash
# The connector JAR should be in Kafka Connect plugins directory
# Debezium Db2 connector: debezium-connector-db2-*.jar
```

## Database Migration

Run the migration to add AS400 to the database type enum:

```bash
cd cdcteam/seg-cdc-application
source venv/bin/activate
alembic upgrade head
```

## Connection Configuration

### Connection Parameters

When creating an AS400 connection, use these parameters:

- **Host/Server**: AS400 server hostname or IP
- **Port**: 446 (default AS400 port)
- **Database**: Library name (e.g., "MYLIB")
- **Schema**: Library name (same as database)
- **Username**: AS400 user
- **Password**: AS400 password

### Additional Configuration

In `additional_config`, you can specify:

```json
{
  "driver": "IBM i Access ODBC Driver",
  "journal_library": "QSYS",
  "docker_hostname": "as400-hostname"  // If Kafka Connect is in Docker
}
```

## Creating a Pipeline

### AS400 → PostgreSQL

1. Create AS400 source connection
2. Create PostgreSQL target connection
3. Create pipeline:
   - Source: AS400 connection
   - Target: PostgreSQL connection
   - Source Tables: List of tables to replicate
   - Mode: `full_load_and_cdc`

### AS400 → SQL Server

Same as above, but use SQL Server as target.

### AS400 → S3

1. Create AS400 source connection
2. Create S3 target connection
3. Create pipeline with S3 as target

## How It Works

1. **Full Load**: 
   - Reads all data from AS400 tables
   - Transfers to target database/S3
   - Captures journal position

2. **CDC**:
   - Debezium Db2 connector connects to AS400
   - Reads from journal entries
   - Publishes changes to Kafka
   - Sink connector writes to target

## Troubleshooting

### ODBC Driver Not Found

**Error**: `No ODBC driver found for AS400/IBM i`

**Solution**:
1. Install IBM i Access Client Solutions
2. Verify driver installation:
   ```bash
   # On Linux/macOS
   odbcinst -q -d
   
   # Should show "IBM i Access ODBC Driver"
   ```

### Journal Not Enabled

**Error**: `Journal not found` or CDC not capturing changes

**Solution**:
1. Enable journaling on tables:
   ```sql
   STRJRNPF FILE(LIBRARY/TABLENAME) JRN(LIBRARY/JOURNALNAME)
   ```

2. Verify journal is active:
   ```sql
   SELECT * FROM QSYS2.JOURNAL_INFO
   WHERE JOURNAL_LIBRARY = 'LIBRARY' AND JOURNAL_NAME = 'JOURNALNAME'
   ```

### Connection Failed

**Error**: `Failed to connect to AS400/IBM i`

**Solution**:
1. Verify network connectivity
2. Check firewall rules (port 446)
3. Verify credentials
4. Check AS400 user permissions

### Debezium Connector Not Found

**Error**: `Connector class io.debezium.connector.db2.Db2Connector not found`

**Solution**:
1. Download Debezium Db2 connector
2. Place JAR in Kafka Connect plugins directory
3. Restart Kafka Connect

## Example: Creating AS400 Connection via API

```python
import requests

connection_data = {
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
}

response = requests.post(
    "http://localhost:8000/api/v1/connections",
    json=connection_data
)
```

## Notes

- AS400 uses **journaling** instead of LSN (Log Sequence Number)
- The connector extracts journal information for tracking
- Tables must have journaling enabled for CDC to work
- The Debezium Db2 connector is used (compatible with AS400/IBM i)

## References

- [IBM i Access Client Solutions](https://www.ibm.com/support/pages/ibm-i-access-client-solutions)
- [Debezium Db2 Connector Documentation](https://debezium.io/documentation/reference/connectors/db2.html)
- [IBM i Journaling Guide](https://www.ibm.com/docs/en/i/7.4?topic=concepts-journaling)


