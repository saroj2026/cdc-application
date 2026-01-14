# Quick Guide: Grant Oracle Permissions

## Current Setup
- **Oracle User**: `c##cdc_user`
- **Table**: `cdc_user.test`
- **Error**: `ORA-01031: insufficient privileges` (FLASHBACK privilege missing)

## Quick Solution

### On the VPS Server (terminal PID 2876), run:

```bash
# Option 1: Run all commands at once (easiest)
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

### Or use the bash script:

```bash
# Copy the script to VPS first, then:
bash grant_oracle_permissions.sh
```

### Or manually connect and run:

```bash
# 1. Connect to Oracle
docker exec -it oracle-xe sqlplus sys/oracle@XE as sysdba

# 2. Run these commands (copy/paste):
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

# 3. Exit
EXIT;
```

## After Granting Permissions

Restart the connector:

```bash
# Via API
curl -X POST http://localhost:8000/api/v1/pipelines/{pipeline_id}/stop
curl -X POST http://localhost:8000/api/v1/pipelines/{pipeline_id}/start
```

The connector should now start successfully and create the topic!

