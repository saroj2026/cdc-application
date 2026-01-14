# How to Run Oracle GRANT Commands

## Important: You Must Run These Commands Inside SQL*Plus, NOT in Bash!

The GRANT commands are SQL commands, not bash commands. You need to:
1. First connect to SQL*Plus
2. Then run the GRANT commands inside SQL*Plus

## Step-by-Step Instructions

### If You're Already Inside the Oracle Container (bash-4.4$)

1. **Exit the bash shell** (you're currently in bash, not SQL*Plus):
   ```bash
   exit
   ```

2. **Connect to SQL*Plus from Docker** (from the VPS host):
   ```bash
   docker exec -it oracle-xe sqlplus / as sysdba
   ```
   (This uses OS authentication - no password needed)

   OR if you need to specify username/password:
   ```bash
   docker exec -it oracle-xe sqlplus sys/password@XE as sysdba
   ```

3. **Once you're in SQL*Plus**, you'll see `SQL>` prompt, then run:
   ```sql
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
   ```

4. **Verify permissions**:
   ```sql
   SELECT PRIVILEGE FROM DBA_SYS_PRIVS WHERE GRANTEE = 'C##CDC_USER' ORDER BY PRIVILEGE;
   ```

5. **Exit SQL*Plus**:
   ```sql
   EXIT;
   ```

## Alternative: Run All Commands at Once

From the VPS host (not inside the container), run:

```bash
docker exec -i oracle-xe sqlplus / as sysdba <<EOF
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

## Key Points

- **SQL*Plus prompt looks like**: `SQL>`
- **Bash prompt looks like**: `bash-4.4$` or `root@hostname:~#`
- **GRANT commands ONLY work in SQL*Plus**, not in bash
- **If you see "command not found"**, you're in bash, not SQL*Plus

## Current Situation

You're in bash-4.4$ (Oracle container's bash shell). You need to:
1. Exit bash (type `exit`)
2. Connect to SQL*Plus
3. Then run the GRANT commands

