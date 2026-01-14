# Oracle Connection Details

## Connection Information

### Oracle XE Database
- **Host**: `72.61.233.209`
- **Port**: `1521`
- **Service Name/SID**: `XE`
- **Container**: `4125e9856bf9` (oracle-xe)

### CDC User Credentials
- **Username**: `c##cdc_user`
- **Password**: `cdc_pass`
- **Schema**: `c##cdc_user`
- **Purpose**: Read-only access for CDC operations

### Sys Admin Credentials
- **Username**: `sys`
- **Password**: `Oracle18`
- **Purpose**: Administrative operations

## Connection Strings

### For CDC User (Python/Application)
```python
config = {
    "host": "72.61.233.209",
    "port": 1521,
    "sid": "XE",
    "user": "c##cdc_user",
    "password": "cdc_pass",
    "schema": "c##cdc_user"
}
```

### For Sys Admin (SQL*Plus)
```
sqlplus sys/Oracle18@72.61.233.209:1521/XE as sysdba
```

### For CDC User (SQL*Plus)
```
sqlplus c##cdc_user/cdc_pass@72.61.233.209:1521/XE
```

## Testing Connection

### Python Test
```python
from ingestion.connectors.oracle import OracleConnector

config = {
    "host": "72.61.233.209",
    "port": 1521,
    "sid": "XE",
    "user": "c##cdc_user",
    "password": "cdc_pass"
}

connector = OracleConnector(config)
connector.test_connection()  # Should return True
```

### Command Line Test
```bash
# From Docker container
docker exec -it oracle-xe sqlplus c##cdc_user/cdc_pass@localhost:1521/XE

# From server
sqlplus c##cdc_user/cdc_pass@72.61.233.209:1521/XE
```

## Common Queries

### List All Tables
```sql
SELECT owner, table_name 
FROM all_tables 
WHERE owner NOT IN ('SYS', 'SYSTEM') 
ORDER BY owner, table_name;
```

### List User Tables
```sql
SELECT table_name 
FROM user_tables;
```

### Describe Table
```sql
DESCRIBE schema_name.table_name;
```

### Select Sample Data
```sql
SELECT * 
FROM schema_name.table_name 
WHERE ROWNUM <= 10;
```

## Debezium Configuration

When creating a Debezium Oracle connector, use:

```json
{
  "connector.class": "io.debezium.connector.oracle.OracleConnector",
  "database.hostname": "72.61.233.209",
  "database.port": "1521",
  "database.user": "c##cdc_user",
  "database.password": "cdc_pass",
  "database.dbname": "XE",
  "database.server.name": "oracle-xe",
  "table.include.list": "c##cdc_user.table1,c##cdc_user.table2"
}
```

## Permissions

### CDC User Permissions
The `c##cdc_user` has:
- ✅ SELECT privileges on tables
- ✅ LogMiner access (for CDC)
- ❌ INSERT/UPDATE/DELETE (read-only for CDC)

### Granting Additional Permissions (if needed)
```sql
-- Connect as sys
sqlplus sys/Oracle18@72.61.233.209:1521/XE as sysdba

-- Grant write permissions (if needed)
GRANT INSERT, UPDATE, DELETE ON schema_name.table_name TO c##cdc_user;
```

## Kafka Connect Plugin

✅ **Status**: Installed and verified
- **Plugin**: `io.debezium.connector.oracle.OracleConnector`
- **Version**: `2.5.0.Final`
- **Location**: `/usr/share/java/plugins/debezium-connector-oracle/`
- **JDBC Driver**: `ojdbc8.jar` installed
- **REST API**: http://72.61.233.209:8083

## Next Steps

1. ✅ **Oracle Connector Installed** - Complete
2. ✅ **Connection Tested** - Run `python test_oracle_connection.py`
3. **Create Oracle → Snowflake Pipeline**:
   - Source: Oracle (using credentials above)
   - Target: Snowflake
   - Select tables to replicate
   - Start pipeline

## Troubleshooting

### Connection Issues
- Verify Oracle container is running: `docker ps | grep oracle-xe`
- Check port accessibility: `telnet 72.61.233.209 1521`
- Verify credentials: Use SQL*Plus to test

### CDC Issues
- Ensure LogMiner is enabled
- Check SCN (System Change Number) is accessible
- Verify user has LogMiner privileges

### Debezium Connector Issues
- Check Kafka Connect logs: `docker logs 28b9a11e27bb`
- Verify plugin is loaded: `curl http://72.61.233.209:8083/connector-plugins | grep oracle`
- Check connector status: `curl http://72.61.233.209:8083/connectors`

## Summary

✅ **Oracle Database**: Running (container: oracle-xe)
✅ **CDC User**: Configured (c##cdc_user)
✅ **Debezium Connector**: Installed and verified
✅ **Python Driver**: Installed (oracledb 3.4.1)
✅ **Backend Code**: Complete

**Ready for Oracle → Snowflake CDC pipelines!** 🎉

