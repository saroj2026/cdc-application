# Grant Permissions to c##cdc_user for CDC Testing

## Summary

The connector is now configured correctly to use `cdc_user.test` (without `##`), but we need to grant INSERT/UPDATE/DELETE permissions to `c##cdc_user` on the `cdc_user.test` table for CDC testing.

## Steps to Grant Permissions

1. **Connect to the server via SSH:**
   ```bash
   ssh root@72.61.233.209
   Password: segmbp@1100
   ```

2. **Find the Oracle container:**
   ```bash
   docker ps --filter "name=oracle" --format "{{.Names}}" | head -1
   ```

3. **Connect to Oracle as SYSDBA and grant permissions:**
   ```bash
   # Replace ORACLE_CONTAINER with the actual container name from step 2
   docker exec -it ORACLE_CONTAINER sqlplus sys/segmbp@1100@XE as sysdba
   ```

4. **Run these SQL commands:**
   ```sql
   GRANT SELECT, INSERT, UPDATE, DELETE ON cdc_user.test TO c##cdc_user;
   
   -- Verify permissions
   SELECT grantee, table_name, privilege
   FROM dba_tab_privs
   WHERE owner = 'CDC_USER'
   AND table_name = 'TEST'
   AND grantee = 'C##CDC_USER'
   ORDER BY privilege;
   
   EXIT;
   ```

## One-Line Command

If you prefer to do it all in one command:

```bash
ssh root@72.61.233.209
# Then run:
ORACLE_CONTAINER=$(docker ps --filter "name=oracle" --format "{{.Names}}" | head -1) && \
docker exec -i $ORACLE_CONTAINER sqlplus -s sys/segmbp@1100@XE as sysdba <<EOF
GRANT SELECT, INSERT, UPDATE, DELETE ON cdc_user.test TO c##cdc_user;
SELECT grantee, table_name, privilege
FROM dba_tab_privs
WHERE owner = 'CDC_USER'
AND table_name = 'TEST'
AND grantee = 'C##CDC_USER'
ORDER BY privilege;
EXIT;
EOF
```

## After Granting Permissions

After permissions are granted:

1. **Test CDC operations:**
   ```bash
   python test_cdc_with_correct_table.py
   ```

2. **Wait 20-30 seconds for CDC to process**

3. **Check Kafka topic for new messages:**
   ```bash
   python check_kafka_topic_messages.py
   ```

4. **Check Snowflake for CDC events:**
   ```bash
   python check_cdc_changes.py
   ```

## Current Status

✅ **Connector Configuration:**
- Table: `cdc_user.test` (without `##`)
- Connector: `cdc-oracle_sf_p-ora-cdc_user`
- Status: RUNNING
- Topic: `oracle_sf_p.CDC_USER.TEST`

✅ **Permissions Already Granted:**
- SELECT on `cdc_user.test` ✓
- LOGMINING privilege ✓

⏳ **Permissions Needed:**
- INSERT on `cdc_user.test` (for testing)
- UPDATE on `cdc_user.test` (for testing)
- DELETE on `cdc_user.test` (for testing)

**Note:** These INSERT/UPDATE/DELETE permissions are only needed for testing CDC. Debezium only needs SELECT and LOGMINING to capture changes from archive logs.

