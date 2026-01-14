# Oracle User Privileges Required for Debezium Connector

## Error
```
ORA-01031: insufficient privileges
SELECT "ID", "NAME", "CREATED_AT" FROM "CDC_USER"."TEST" AS OF SCN 17873301
```

## Problem
The Oracle user `c##cdc_user` doesn't have sufficient privileges to perform flashback queries (`AS OF SCN`) required by Debezium for snapshots.

## Solution

### Option 1: Grant Flashback Privileges (Recommended)
Grant the user privileges to use flashback queries:

```sql
-- Connect as SYSDBA (e.g., SYS)
sqlplus sys/password@XE as sysdba

-- Grant flashback privileges
GRANT FLASHBACK ANY TABLE TO c##cdc_user;

-- Or grant flashback on specific schema
GRANT FLASHBACK ON SCHEMA cdc_user TO c##cdc_user;
```

### Option 2: Grant Additional Privileges
The user might also need:

```sql
-- Grant SELECT privilege on the tables
GRANT SELECT ON cdc_user.test TO c##cdc_user;

-- Grant LOGMINER privileges (for CDC)
GRANT LOGMINING TO c##cdc_user;

-- Grant CREATE SESSION (if not already granted)
GRANT CREATE SESSION TO c##cdc_user;
```

### Option 3: Disable Snapshots (If Full Load Already Done)
If full load has already been completed, you can disable snapshots by using snapshot mode that skips data. However, Oracle connector requires `initial_only` for schema capture.

## Current Configuration
- Database user: `c##cdc_user`
- Schema: `cdc_user`
- Table: `TEST`
- Snapshot mode: `initial_only`
- Database connection adapter: `logminer`

## Next Steps
1. Grant `FLASHBACK ANY TABLE` privilege to `c##cdc_user`
2. Restart the connector
3. The connector should then be able to perform snapshots and create the topic

