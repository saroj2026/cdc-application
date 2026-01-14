# Oracle Permissions Setup for Debezium Connector

## User Information
- **Oracle User**: `c##cdc_user` (common user in CDB)
- **Schema/Table**: `cdc_user.test`
- **Current Error**: `ORA-01031: insufficient privileges` (FLASHBACK privilege missing)

## Required Permissions

The user `c##cdc_user` needs the following permissions for Debezium Oracle connector:

1. **FLASHBACK ANY TABLE** - Required for snapshots (AS OF SCN queries)
2. **LOGMINING** - Required for Oracle LogMiner-based CDC
3. **SELECT ANY DICTIONARY** - Needed for metadata queries
4. **SELECT_CATALOG_ROLE** - Provides access to data dictionary views
5. **SELECT on cdc_user.test** - Access to the table being replicated
6. **EXECUTE on DBMS_LOGMNR packages** - Required for LogMiner

## How to Grant Permissions

### Option 1: Using Docker (Recommended)

If Oracle is running in Docker container `oracle-xe`:

```bash
# Connect to Oracle as SYSDBA
docker exec -it oracle-xe sqlplus sys/oracle@XE as sysdba

# Then run these commands:
GRANT CREATE SESSION TO c##cdc_user;
GRANT CONNECT TO c##cdc_user;
GRANT RESOURCE TO c##cdc_user;
GRANT LOGMINING TO c##cdc_user;
GRANT SELECT ANY TRANSACTION TO c##cdc_user;
GRANT SELECT ANY DICTIONARY TO c##cdc_user;
GRANT FLASHBACK ANY TABLE TO c##cdc_user;
GRANT SELECT ON cdc_user.test TO c##cdc_user;
GRANT EXECUTE ON SYS.DBMS_LOGMNR TO c##cdc_user;
GRANT EXECUTE ON SYS.DBMS_LOGMNR_D TO c##cdc_user;
GRANT SELECT_CATALOG_ROLE TO c##cdc_user;

# Verify permissions
SELECT PRIVILEGE FROM DBA_SYS_PRIVS WHERE GRANTEE = 'C##CDC_USER';
```

### Option 2: Run SQL Script File

Copy the SQL file to the VPS and run it:

```bash
# Copy SQL file to VPS
scp grant_oracle_permissions_for_cdc_user.sql root@72.61.233.209:/tmp/

# SSH into VPS
ssh root@72.61.233.209

# Run SQL script
docker exec -i oracle-xe sqlplus sys/oracle@XE as sysdba < /tmp/grant_oracle_permissions_for_cdc_user.sql
```

### Option 3: Copy-Paste SQL Commands

1. Connect to Oracle:
   ```bash
   docker exec -it oracle-xe sqlplus sys/oracle@XE as sysdba
   ```

2. Copy and paste all SQL commands from `grant_oracle_permissions_for_cdc_user.sql`

## Quick Commands (All-in-One)

Run this single command to grant all permissions:

```bash
docker exec -i oracle-xe sqlplus sys/oracle@XE as sysdba <<EOF
GRANT CREATE SESSION TO c##cdc_user;
GRANT CONNECT TO c##cdc_user;
GRANT RESOURCE TO c##cdc_user;
GRANT LOGMINING TO c##cdc_user;
GRANT SELECT ANY TRANSACTION TO c##cdc_user;
GRANT SELECT ANY DICTIONARY TO c##cdc_user;
GRANT FLASHBACK ANY TABLE TO c##cdc_user;
GRANT SELECT ON cdc_user.test TO c##cdc_user;
GRANT EXECUTE ON SYS.DBMS_LOGMNR TO c##cdc_user;
GRANT EXECUTE ON SYS.DBMS_LOGMNR_D TO c##cdc_user;
GRANT SELECT_CATALOG_ROLE TO c##cdc_user;
EXIT;
EOF
```

## After Granting Permissions

1. **Restart the connector** to apply the new permissions:
   ```bash
   # Stop the connector
   curl -X POST http://72.61.233.209:8083/connectors/cdc-oracle_sf_p-ora-cdc_user/restart
   
   # Or restart the pipeline via API
   curl -X POST http://localhost:8000/api/v1/pipelines/{pipeline_id}/stop
   curl -X POST http://localhost:8000/api/v1/pipelines/{pipeline_id}/start
   ```

2. **Verify the connector status**:
   ```bash
   curl http://72.61.233.209:8083/connectors/cdc-oracle_sf_p-ora-cdc_user/status | python -m json.tool
   ```

3. **Check if topic is created**:
   ```bash
   curl http://72.61.233.209:8083/connectors/cdc-oracle_sf_p-ora-cdc_user/topics | python -m json.tool
   ```

## Verification

After granting permissions, verify they were granted correctly:

```sql
-- Connect as SYSDBA
sqlplus sys/oracle@XE as sysdba

-- Check system privileges
SELECT PRIVILEGE FROM DBA_SYS_PRIVS WHERE GRANTEE = 'C##CDC_USER';

-- Check table privileges
SELECT OWNER, TABLE_NAME, PRIVILEGE 
FROM DBA_TAB_PRIVS 
WHERE GRANTEE = 'C##CDC_USER';

-- Check roles
SELECT GRANTED_ROLE FROM DBA_ROLE_PRIVS WHERE GRANTEE = 'C##CDC_USER';
```

Expected privileges should include:
- CREATE SESSION
- CONNECT
- RESOURCE
- LOGMINING
- SELECT ANY TRANSACTION
- SELECT ANY DICTIONARY
- **FLASHBACK ANY TABLE** (most important!)
- SELECT_CATALOG_ROLE

