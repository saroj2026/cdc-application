# Fix Oracle SYSDBA Password Issue

## Problem
Getting `ORA-01017: invalid username/password; logon denied` when trying to connect as SYSDBA.

## Solution Options

### Option 1: Try Common Oracle XE Default Passwords

Oracle XE default passwords vary. Try these common ones:

```bash
# Try common passwords
docker exec -it oracle-xe sqlplus sys/oracle@XE as sysdba
docker exec -it oracle-xe sqlplus sys/Oracle123@XE as sysdba
docker exec -it oracle-xe sqlplus sys/Oradoc_db1@XE as sysdba
docker exec -it oracle-xe sqlplus sys/manager@XE as sysdba
```

### Option 2: Check Oracle Container Environment

Check if password is set in environment variables:

```bash
docker inspect oracle-xe --format '{{range .Config.Env}}{{println .}}{{end}}' | grep -i password
```

### Option 3: Reset SYSDBA Password

If you know the container setup, you might need to reset the password:

```bash
# Connect to container and reset password (if possible)
docker exec -it oracle-xe bash
# Then inside container, try:
# sqlplus / as sysdba
# ALTER USER sys IDENTIFIED BY newpassword;
```

### Option 4: Use Alternative Authentication (OS Authentication)

Try connecting without password (OS authentication):

```bash
# Connect as oracle user inside container
docker exec -it oracle-xe bash
su - oracle
sqlplus / as sysdba
```

### Option 5: Check Oracle Documentation

Oracle XE passwords are typically set during installation. If this is a Docker image, check:
- Docker image documentation
- Environment variables used when starting the container
- Any setup scripts that created the container

### Option 6: Grant Permissions via Regular User (If c##cdc_user has privileges)

If `c##cdc_user` has DBA privileges or can grant privileges, you might be able to grant them directly:

```bash
# Connect as c##cdc_user (if it has DBA role)
docker exec -it oracle-xe sqlplus c##cdc_user/<password>@XE

# Then try to grant (might not work if user doesn't have DBA)
GRANT FLASHBACK ANY TABLE TO c##cdc_user;
```

## Recommended Approach

1. **First, check what password was used during Oracle setup**
2. **If password is unknown, try common defaults:**
   - `oracle`
   - `Oracle123`
   - `Oradoc_db1`
3. **If still failing, check Docker container logs or setup scripts**
4. **As last resort, reset the password using OS authentication**

## After Getting Correct Password

Once you have the correct password, use the grant script:

```bash
# Set password
export ORACLE_SYS_PASSWORD=your_password

# Run grant script
bash grant_oracle_permissions_with_password.sh
```

Or run the SQL commands directly:

```bash
docker exec -i oracle-xe sqlplus sys/your_password@XE as sysdba <<EOF
GRANT FLASHBACK ANY TABLE TO c##cdc_user;
GRANT LOGMINING TO c##cdc_user;
GRANT SELECT_CATALOG_ROLE TO c##cdc_user;
-- ... (other grants)
EXIT;
EOF
```

