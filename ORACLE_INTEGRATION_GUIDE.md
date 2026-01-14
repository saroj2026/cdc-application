# Oracle to Snowflake CDC Integration Guide

## Overview

This guide explains how to set up Oracle as a source database with Snowflake as the target for Change Data Capture (CDC) pipelines.

## Prerequisites

### 1. Oracle Database Requirements

- **Oracle Database 11g or later** (12c+ recommended for better CDC support)
- **Oracle LogMiner enabled** (required for CDC)
- **Archive log mode enabled** (required for LogMiner)
- **User with appropriate permissions**:
  - `SELECT` on tables to replicate
  - `SELECT` on `V$DATABASE`, `V$LOG`, `V$ARCHIVED_LOG`
  - `SELECT` on `DBA_LOGMNR_CONTENTS` (for LogMiner)
  - `EXECUTE` on `DBMS_LOGMNR` package

### 2. Debezium Oracle Connector JAR

The Debezium Oracle connector JAR must be installed in Kafka Connect:

```bash
# Download from Debezium releases
# https://debezium.io/releases/
# debezium-connector-oracle-*.jar

# Place in Kafka Connect plugins directory
# Example: /usr/share/confluent-hub-components/debezium-connector-oracle
```

**Required JAR files:**
- `debezium-connector-oracle-*.jar`
- `ojdbc8.jar` (Oracle JDBC driver) - usually included with connector

### 3. Python Dependencies

Install Oracle Python driver:

```bash
# Option 1: cx_Oracle (Oracle DB driver v1.x)
pip install cx_Oracle

# Option 2: oracledb (Oracle DB driver v2.0+) - Recommended
pip install oracledb
```

**Note:** The connector supports both `cx_Oracle` and `oracledb` (v2.0+).

## Database Migration

Run the migration to add Oracle to the database type enum:

```bash
cd seg-cdc-application
source venv/bin/activate  # or activate your virtual environment
alembic upgrade head
```

## Connection Configuration

### Oracle Source Connection

When creating an Oracle connection, use these parameters:

**Required Fields:**
- **Host/Server**: Oracle server hostname or IP
- **Port**: 1521 (default Oracle port)
- **Database**: Database SID or service name
- **Username**: Oracle user with CDC permissions
- **Password**: Oracle user password
- **Schema**: Schema name (user) - defaults to username if not provided

**Additional Configuration** (in `additional_config` JSON):

```json
{
  "service_name": "ORCLPDB1",  // Use service name instead of SID (for PDBs)
  "docker_hostname": "oracle-hostname",  // If Kafka Connect is in Docker
  "mode": "normal"  // Connection mode: normal, sysdba, sysoper
}
```

**Example Connection:**
```json
{
  "name": "oracle-source",
  "connection_type": "source",
  "database_type": "oracle",
  "host": "oracle-server.example.com",
  "port": 1521,
  "database": "ORCL",  // SID
  "username": "CDC_USER",
  "password": "password123",
  "schema": "CDC_USER",
  "additional_config": {
    "service_name": "ORCLPDB1"  // Optional: use service name for PDB
  }
}
```

### Snowflake Target Connection

Configure Snowflake connection as documented in `SNOWFLAKE_AUTO_CONFIGURATION.md`:

- Account URL or identifier
- Username
- Private key (recommended) or password
- Database and schema
- Optional: Warehouse and role

## Oracle-Specific Setup

### 1. Enable Archive Logging

Oracle must be in ARCHIVELOG mode for CDC:

```sql
-- Check current mode
SELECT log_mode FROM v$database;

-- Enable archive logging (requires DBA privileges)
SHUTDOWN IMMEDIATE;
STARTUP MOUNT;
ALTER DATABASE ARCHIVELOG;
ALTER DATABASE OPEN;
```

### 2. Configure LogMiner

Debezium Oracle connector uses LogMiner for CDC. Ensure LogMiner is properly configured:

```sql
-- Check if LogMiner is available
SELECT * FROM v$logmnr_parameters;

-- Grant necessary permissions to CDC user
GRANT SELECT ON v_$database TO CDC_USER;
GRANT SELECT ON v_$log TO CDC_USER;
GRANT SELECT ON v_$archived_log TO CDC_USER;
GRANT SELECT ON v_$logfile TO CDC_USER;
GRANT SELECT ON v_$logmnr_contents TO CDC_USER;
GRANT EXECUTE ON dbms_logmnr TO CDC_USER;
```

### 3. Grant Table Permissions

Grant SELECT on tables to replicate:

```sql
-- Grant SELECT on specific tables
GRANT SELECT ON schema_name.table_name TO CDC_USER;

-- Or grant SELECT on all tables in schema
GRANT SELECT ANY TABLE TO CDC_USER;  -- Use with caution
```

## Creating a Pipeline

### Oracle → Snowflake Pipeline

1. **Create Oracle Source Connection**
   - Use connection parameters above
   - Test connection to verify connectivity

2. **Create Snowflake Target Connection**
   - Configure with private key or password
   - Test connection

3. **Create Pipeline**
   - Select Oracle as source
   - Select Snowflake as target
   - Choose tables to replicate
   - Select mode:
     - `full_load_only`: Initial data load only
     - `cdc_only`: CDC only (requires existing data)
     - `full_load_and_cdc`: Full load + CDC (recommended)

4. **Start Pipeline**
   - System automatically:
     - Creates Debezium Oracle connector
     - Creates Kafka topics
     - Creates Snowflake sink connector with ExtractNewRecordState transform
     - Auto-creates Snowflake tables with RECORD_CONTENT column
     - Starts data replication

## How It Works

### 1. Source (Oracle + Debezium)

The system automatically configures:
- **Debezium Oracle Connector** using LogMiner
- Captures changes from Oracle redo logs
- Sends to Kafka in Debezium envelope format

**Key Configuration:**
- `log.mining.strategy`: `online_catalog` (uses online catalog for schema)
- `log.mining.continuous.mine`: `true` (continuous mining)
- Uses SCN (System Change Number) for tracking changes

### 2. Kafka

Messages are in Debezium format:
```json
{
  "schema": {...},
  "payload": {
    "before": {...},
    "after": {...},
    "op": "c/u/d",
    "source": {
      "connector": "oracle",
      "scn": "1234567890",
      ...
    }
  }
}
```

### 3. Sink (Snowflake Connector)

The system automatically configures:
- **ExtractNewRecordState transform** - extracts `after` field
- **JsonConverter** - works with transforms
- **Auto-creates tables** with `RECORD_CONTENT` and `RECORD_METADATA` columns

### 4. Snowflake Table

Auto-created with:
- `RECORD_CONTENT` (VARIANT) - Contains the actual data
- `RECORD_METADATA` (VARIANT) - Contains Kafka metadata

## Querying Data in Snowflake

Since data is stored in `RECORD_CONTENT` as JSON, use JSON path syntax:

```sql
-- Query specific record
SELECT 
    RECORD_CONTENT:column1::STRING as column1,
    RECORD_CONTENT:column2::NUMBER as column2,
    RECORD_CONTENT:column3::TIMESTAMP_NTZ as column3
FROM table_name 
WHERE RECORD_CONTENT:primary_key = 'value';

-- Get all records
SELECT * FROM table_name;

-- Check Oracle SCN in metadata
SELECT 
    RECORD_CONTENT:column1::STRING as column1,
    RECORD_METADATA:offset::NUMBER as kafka_offset
FROM table_name;
```

## SCN (System Change Number) vs LSN

Oracle uses **SCN** (System Change Number) instead of LSN:

- **LSN** (Log Sequence Number): Used by PostgreSQL, SQL Server
- **SCN** (System Change Number): Used by Oracle

The system handles this automatically:
- Full load extracts SCN: `{"lsn": "SCN:1234567890", "scn": 1234567890}`
- CDC resumes from the last SCN
- Debezium Oracle connector tracks SCN automatically

## Troubleshooting

### 1. Connection Issues

**Error: "ORA-12541: TNS:no listener"**
- Check Oracle listener is running
- Verify host and port are correct
- Check firewall rules

**Error: "ORA-01017: invalid username/password"**
- Verify username and password
- Check if user account is locked

### 2. CDC Issues

**Error: "LogMiner session not found"**
- Ensure archive logging is enabled
- Grant LogMiner permissions to user
- Check Oracle version compatibility

**Error: "No changes captured"**
- Verify tables have changes
- Check LogMiner is mining the correct logs
- Verify archive logs are accessible

### 3. Schema Issues

**Error: "Table not found"**
- Verify schema name is correct (case-sensitive in Oracle)
- Check user has SELECT permission
- Ensure table exists in the specified schema

### 4. Snowflake Issues

Refer to `SNOWFLAKE_AUTO_CONFIGURATION.md` for Snowflake-specific troubleshooting.

## Frontend Changes Needed

The frontend may need updates to support Oracle:

1. **Database Type Dropdown**
   - Add "Oracle" to database type options
   - Add Oracle icon/logo if available

2. **Connection Form**
   - Add Oracle-specific fields:
     - Service Name (optional, alternative to SID)
     - Connection Mode (normal, sysdba, sysoper)

3. **Table Discovery**
   - Ensure Oracle schema/table discovery works
   - Handle Oracle-specific naming (uppercase by default)

4. **Pipeline Creation**
   - Verify Oracle → Snowflake pipeline creation works
   - Test full load and CDC modes

## Backend Changes Summary

✅ **Completed:**
1. Created `oracle.py` connector file
2. Added `ORACLE` to `DatabaseType` enum
3. Added Oracle support in `connection_service.py`
4. Added Oracle Debezium config in `debezium_config.py`
5. Updated `connectors/__init__.py` to export `OracleConnector`
6. Snowflake sink automatically configured with ExtractNewRecordState transform

## Testing Checklist

- [ ] Oracle connection test works
- [ ] Table discovery works for Oracle
- [ ] Schema extraction works
- [ ] Full load works (Oracle → Snowflake)
- [ ] CDC works (Oracle → Snowflake)
- [ ] SCN tracking works correctly
- [ ] Data appears correctly in Snowflake RECORD_CONTENT
- [ ] Frontend displays Oracle as database type option

## Next Steps

1. **Install Debezium Oracle Connector JAR** in Kafka Connect
2. **Test Oracle connection** using the connection service
3. **Create test pipeline** (Oracle → Snowflake)
4. **Verify data flow** end-to-end
5. **Update frontend** if needed (add Oracle to UI)

## References

- [Debezium Oracle Connector Documentation](https://debezium.io/documentation/reference/connectors/oracle.html)
- [Oracle LogMiner Documentation](https://docs.oracle.com/en/database/oracle/oracle-database/19/sutil/oracle-logminer-utility.html)
- [Snowflake Kafka Connector Documentation](https://docs.snowflake.com/en/user-guide/kafka-connector-overview.html)

