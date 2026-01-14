# Database Permissions and Setup Guide for CDC

This comprehensive guide outlines all the permissions, privileges, configuration requirements, and setup steps needed for each database type to enable Change Data Capture (CDC) functionality in our system.

---

## Table of Contents

1. [PostgreSQL](#postgresql)
2. [SQL Server](#sql-server)
3. [Oracle](#oracle)
4. [Snowflake](#snowflake)
5. [AS400/IBM i](#as400ibm-i)
6. [S3](#s3)
7. [Kafka Connect Requirements](#kafka-connect-requirements)
8. [Network and Firewall](#network-and-firewall)
9. [Quick Reference](#quick-reference)
10. [Troubleshooting](#troubleshooting)

---

## PostgreSQL

### Overview
PostgreSQL uses **Write-Ahead Logging (WAL)** and **logical replication** for CDC. Debezium PostgreSQL connector requires specific database-level and user-level permissions.

### Database-Level Configuration

#### 1. Enable Logical Replication (WAL Level)
**Required**: `wal_level = logical`

**How to Configure**:
```sql
-- Check current WAL level
SHOW wal_level;

-- If not 'logical', update postgresql.conf:
-- wal_level = logical

-- Restart PostgreSQL after changing
```

**Location**: `postgresql.conf` file

**Why Required**: Logical replication allows Debezium to read transaction log changes without requiring physical replication.

#### 2. Max Replication Slots
**Recommended**: `max_replication_slots >= 10` (or number of pipelines + buffer)

**How to Configure**:
```sql
-- Check current setting
SHOW max_replication_slots;

-- Update postgresql.conf:
-- max_replication_slots = 10

-- Restart PostgreSQL
```

**Why Required**: Each Debezium connector creates a replication slot. Ensure enough slots for all pipelines.

#### 3. Max WAL Senders
**Recommended**: `max_wal_senders >= 10`

**How to Configure**:
```sql
-- Check current setting
SHOW max_wal_senders;

-- Update postgresql.conf:
-- max_wal_senders = 10

-- Restart PostgreSQL
```

**Why Required**: WAL senders handle replication connections. Each Debezium connector needs one.

#### 4. PostgreSQL Configuration File Example
```conf
# postgresql.conf
wal_level = logical
max_replication_slots = 10
max_wal_senders = 10
```

### User-Level Permissions

#### Required Privileges for CDC User

```sql
-- Connect as superuser (postgres) or database owner
-- Replace 'cdc_user' with your actual CDC username

-- 1. REPLICATION privilege (CRITICAL for CDC)
ALTER USER cdc_user WITH REPLICATION;

-- 2. Connect to database
GRANT CONNECT ON DATABASE your_database TO cdc_user;

-- 3. Usage on schema (usually 'public')
GRANT USAGE ON SCHEMA public TO cdc_user;

-- 4. SELECT on tables to be replicated
GRANT SELECT ON ALL TABLES IN SCHEMA public TO cdc_user;

-- 5. SELECT on future tables (optional but recommended)
ALTER DEFAULT PRIVILEGES IN SCHEMA public 
    GRANT SELECT ON TABLES TO cdc_user;

-- 6. CREATE on schema (for creating publications - optional)
GRANT CREATE ON SCHEMA public TO cdc_user;
```

#### Complete Setup Script

```sql
-- Run as superuser (postgres)
-- Replace placeholders: cdc_user, your_database, public

-- Create user (if doesn't exist)
CREATE USER cdc_user WITH PASSWORD 'your_secure_password';

-- Grant REPLICATION privilege (MOST IMPORTANT)
ALTER USER cdc_user WITH REPLICATION;

-- Grant database access
GRANT CONNECT ON DATABASE your_database TO cdc_user;

-- Grant schema access
GRANT USAGE ON SCHEMA public TO cdc_user;
GRANT CREATE ON SCHEMA public TO cdc_user;

-- Grant table access
GRANT SELECT ON ALL TABLES IN SCHEMA public TO cdc_user;

-- Grant future table access
ALTER DEFAULT PRIVILEGES IN SCHEMA public 
    GRANT SELECT ON TABLES TO cdc_user;

-- Verify permissions
\du cdc_user
```

### What Debezium Does Automatically

1. **Creates Replication Slot**: Named `{pipeline_name}_slot`
2. **Creates Publication**: Named `{pipeline_name}_pub` (if auto-create enabled)
3. **Subscribes to Changes**: Reads from WAL via replication slot

### Verification Queries

```sql
-- Check WAL level
SHOW wal_level;
-- Expected: logical

-- Check replication slots
SELECT slot_name, plugin, slot_type, active 
FROM pg_replication_slots;

-- Check publications
SELECT * FROM pg_publication;

-- Check user privileges
SELECT rolname, rolreplication 
FROM pg_roles 
WHERE rolname = 'cdc_user';
-- Expected: rolreplication = true

-- Check table permissions
SELECT grantee, table_schema, table_name, privilege_type
FROM information_schema.table_privileges
WHERE grantee = 'cdc_user';
```

### Common Issues

**Issue**: `ERROR: replication slots can only be used if max_replication_slots > 0`
- **Solution**: Increase `max_replication_slots` in `postgresql.conf` and restart

**Issue**: `ERROR: permission denied to create replication slot`
- **Solution**: Grant `REPLICATION` privilege: `ALTER USER cdc_user WITH REPLICATION;`

**Issue**: `ERROR: could not access file "pg_wal"`
- **Solution**: Check PostgreSQL data directory permissions and WAL level

---

## SQL Server

### Overview
SQL Server CDC uses **Change Data Capture (CDC)** feature or **Change Tracking**. For Debezium, we use SQL Server's native CDC feature.

### Database-Level Configuration

#### 1. Enable CDC on Database
**Required**: CDC must be enabled on the database

```sql
-- Connect as sysadmin or db_owner
USE your_database;
GO

-- Enable CDC on database
EXEC sys.sp_cdc_enable_db;
GO

-- Verify CDC is enabled
SELECT is_cdc_enabled 
FROM sys.databases 
WHERE name = 'your_database';
-- Expected: 1 (enabled)
```

#### 2. Enable CDC on Tables
**Required**: CDC must be enabled on each table to be replicated

```sql
-- Enable CDC on a specific table
USE your_database;
GO

EXEC sys.sp_cdc_enable_table
    @source_schema = N'dbo',
    @source_name = N'your_table',
    @role_name = N'cdc_admin',
    @supports_net_changes = 1;
GO

-- Verify CDC is enabled on table
SELECT is_tracked_by_cdc 
FROM sys.tables 
WHERE name = 'your_table';
-- Expected: 1 (enabled)
```

### User-Level Permissions

#### Required Roles and Permissions

```sql
-- Connect as sysadmin or db_owner

-- 1. Create CDC user (if doesn't exist)
CREATE LOGIN cdc_user WITH PASSWORD = 'your_secure_password';
GO

-- 2. Create user in database
USE your_database;
GO
CREATE USER cdc_user FOR LOGIN cdc_user;
GO

-- 3. Grant db_datareader role (to read tables)
ALTER ROLE db_datareader ADD MEMBER cdc_user;
GO

-- 4. Grant db_owner role (for CDC operations - recommended)
-- OR grant specific CDC permissions:
ALTER ROLE db_owner ADD MEMBER cdc_user;
GO

-- Alternative: Grant CDC-specific permissions
-- Grant access to CDC tables
GRANT SELECT ON SCHEMA::cdc TO cdc_user;
GRANT SELECT ON SCHEMA::dbo TO cdc_user;

-- Grant access to CDC functions
GRANT VIEW DATABASE STATE TO cdc_user;
```

#### Complete Setup Script

```sql
-- Run as sysadmin
-- Replace placeholders: cdc_user, your_database, dbo, your_table

-- Step 1: Enable CDC on database
USE your_database;
GO
EXEC sys.sp_cdc_enable_db;
GO

-- Step 2: Create login and user
CREATE LOGIN cdc_user WITH PASSWORD = 'your_secure_password';
GO

USE your_database;
GO
CREATE USER cdc_user FOR LOGIN cdc_user;
GO

-- Step 3: Grant permissions
ALTER ROLE db_datareader ADD MEMBER cdc_user;
ALTER ROLE db_owner ADD MEMBER cdc_user;  -- Or use specific CDC permissions
GO

-- Step 4: Enable CDC on tables
EXEC sys.sp_cdc_enable_table
    @source_schema = N'dbo',
    @source_name = N'your_table',
    @role_name = N'cdc_admin',
    @supports_net_changes = 1;
GO

-- Verify
SELECT is_cdc_enabled FROM sys.databases WHERE name = 'your_database';
SELECT name, is_tracked_by_cdc FROM sys.tables WHERE is_tracked_by_cdc = 1;
```

### Target Database Permissions (Sink)

When SQL Server is used as a **target** (sink):

```sql
-- Connect as sysadmin or db_owner

-- 1. Create user
CREATE LOGIN sink_user WITH PASSWORD = 'your_secure_password';
GO

USE target_database;
GO
CREATE USER sink_user FOR LOGIN sink_user;
GO

-- 2. Grant table creation and modification permissions
ALTER ROLE db_ddladmin ADD MEMBER sink_user;  -- CREATE/ALTER tables
ALTER ROLE db_datawriter ADD MEMBER sink_user;  -- INSERT/UPDATE/DELETE
GO

-- Or grant specific permissions:
GRANT CREATE TABLE TO sink_user;
GRANT ALTER ON SCHEMA::dbo TO sink_user;
GRANT INSERT, UPDATE, DELETE ON SCHEMA::dbo TO sink_user;
```

### Network Configuration

- **Port**: 1433 (default SQL Server port)
- **Protocol**: TCP/IP must be enabled
- **Firewall**: Allow inbound connections on port 1433

### Verification Queries

```sql
-- Check CDC enabled on database
SELECT is_cdc_enabled 
FROM sys.databases 
WHERE name = 'your_database';

-- Check CDC enabled tables
SELECT 
    s.name AS schema_name,
    t.name AS table_name,
    t.is_tracked_by_cdc
FROM sys.tables t
INNER JOIN sys.schemas s ON t.schema_id = s.schema_id
WHERE t.is_tracked_by_cdc = 1;

-- Check user permissions
SELECT 
    dp.name AS principal_name,
    dp.type_desc AS principal_type,
    p.permission_name,
    p.state_desc
FROM sys.database_permissions p
INNER JOIN sys.database_principals dp ON p.grantee_principal_id = dp.principal_id
WHERE dp.name = 'cdc_user';
```

### Common Issues

**Issue**: `CDC is not enabled on database`
- **Solution**: Run `EXEC sys.sp_cdc_enable_db;` on the database

**Issue**: `Table is not enabled for CDC`
- **Solution**: Run `EXEC sys.sp_cdc_enable_table` for each table

**Issue**: `Permission denied to access CDC tables`
- **Solution**: Grant `SELECT` on `cdc` schema and `VIEW DATABASE STATE` permission

**Issue**: `Connection timeout` or `Cannot connect to SQL Server`
- **Solution**: Enable TCP/IP protocol in SQL Server Configuration Manager and check firewall rules

---

## Oracle

### Overview
Oracle CDC uses **Oracle LogMiner** to read redo logs. Requires specific system-level and object-level privileges, and the database must be in ARCHIVELOG mode.

### Database-Level Configuration

#### 1. Enable Archive Log Mode
**Required**: Database must be in `ARCHIVELOG` mode

```sql
-- Connect as SYSDBA
sqlplus sys/password@XE as sysdba

-- Check current log mode
SELECT log_mode FROM v$database;
-- Expected: ARCHIVELOG

-- If not ARCHIVELOG, enable it:
SHUTDOWN IMMEDIATE;
STARTUP MOUNT;
ALTER DATABASE ARCHIVELOG;
ALTER DATABASE OPEN;
```

#### 2. Enable Supplemental Logging
**Required**: Supplemental logging must be enabled

```sql
-- Connect as SYSDBA

-- Enable database-level supplemental logging
ALTER DATABASE ADD SUPPLEMENTAL LOG DATA;

-- Enable table-level supplemental logging (for each table)
ALTER TABLE schema.table_name ADD SUPPLEMENTAL LOG DATA (ALL) COLUMNS;
```

#### 3. Container Database (CDB) Considerations
If using Oracle 12c+ with Container Database (CDB):
- User must be a **common user** (starts with `c##`)
- Example: `c##cdc_user` instead of `cdc_user`

### User-Level Permissions

#### Required Privileges for CDC User

```sql
-- Connect as SYSDBA
-- Replace 'c##cdc_user' with your actual CDC username
-- Note: In CDB, user must start with c##

-- 1. Basic privileges
GRANT CREATE SESSION TO c##cdc_user;
GRANT CONNECT TO c##cdc_user;
GRANT RESOURCE TO c##cdc_user;

-- 2. LogMiner privileges (CRITICAL for CDC)
GRANT LOGMINING TO c##cdc_user;
GRANT SELECT ANY TRANSACTION TO c##cdc_user;
GRANT SELECT ANY DICTIONARY TO c##cdc_user;

-- 3. Flashback privileges (CRITICAL for snapshots)
GRANT FLASHBACK ANY TABLE TO c##cdc_user;

-- 4. Select privileges on tables to be replicated
GRANT SELECT ON schema.table_name TO c##cdc_user;

-- 5. Execute privileges on LogMiner packages
GRANT EXECUTE ON SYS.DBMS_LOGMNR TO c##cdc_user;
GRANT EXECUTE ON SYS.DBMS_LOGMNR_D TO c##cdc_user;

-- 6. Additional privileges for metadata access
GRANT SELECT_CATALOG_ROLE TO c##cdc_user;
```

#### Complete Setup Script

```sql
-- Run as SYSDBA
-- Replace placeholders: c##cdc_user, schema, table_name

-- Step 1: Create user (if doesn't exist)
-- Note: In CDB, user must start with c##
CREATE USER c##cdc_user IDENTIFIED BY your_password;

-- Step 2: Grant basic privileges
GRANT CREATE SESSION TO c##cdc_user;
GRANT CONNECT TO c##cdc_user;
GRANT RESOURCE TO c##cdc_user;

-- Step 3: Grant LogMiner privileges (REQUIRED for CDC)
GRANT LOGMINING TO c##cdc_user;
GRANT SELECT ANY TRANSACTION TO c##cdc_user;
GRANT SELECT ANY DICTIONARY TO c##cdc_user;

-- Step 4: Grant Flashback privileges (REQUIRED for snapshots)
GRANT FLASHBACK ANY TABLE TO c##cdc_user;

-- Step 5: Grant table access
GRANT SELECT ON schema.table_name TO c##cdc_user;

-- Step 6: Grant LogMiner package access
GRANT EXECUTE ON SYS.DBMS_LOGMNR TO c##cdc_user;
GRANT EXECUTE ON SYS.DBMS_LOGMNR_D TO c##cdc_user;

-- Step 7: Grant catalog role
GRANT SELECT_CATALOG_ROLE TO c##cdc_user;

-- Verify permissions
SELECT PRIVILEGE FROM DBA_SYS_PRIVS WHERE GRANTEE = 'C##CDC_USER';
SELECT OWNER, TABLE_NAME, PRIVILEGE FROM DBA_TAB_PRIVS WHERE GRANTEE = 'C##CDC_USER';
```

### Connection Configuration

#### Connection Parameters
- **Host**: Oracle server hostname or IP
- **Port**: 1521 (default) or custom port
- **Database**: SID or Service Name
- **Schema**: Schema name containing tables (e.g., `cdc_user`)
- **Username**: CDC user (e.g., `c##cdc_user`)
- **Password**: User password

#### Additional Config (in connection's `additional_config`):
```json
{
  "service_name": "XE",  // If using service name instead of SID
  "database": "XE",      // If using SID
  "mode": "normal"       // Connection mode
}
```

### Important Notes

1. **Container Database (CDB)**: If using Oracle 12c+ with CDB, user must start with `c##` (common user)
2. **Flashback**: Required for Debezium snapshots (AS OF SCN queries)
3. **LogMiner**: Required for reading redo logs for CDC
4. **Schema Access**: User accessing tables in different schema needs explicit `SELECT` grants
5. **Archive Logs**: Must be retained long enough for CDC to process (recommended: 7+ days)

### Verification Queries

```sql
-- Check archive log mode
SELECT log_mode FROM v$database;
-- Expected: ARCHIVELOG

-- Check supplemental logging
SELECT supplemental_log_data_min FROM v$database;
-- Expected: YES or IMPLICIT

-- Check user privileges
SELECT PRIVILEGE FROM DBA_SYS_PRIVS WHERE GRANTEE = 'C##CDC_USER';

-- Check table privileges
SELECT OWNER, TABLE_NAME, PRIVILEGE 
FROM DBA_TAB_PRIVS 
WHERE GRANTEE = 'C##CDC_USER';

-- Check LogMiner session (when CDC is running)
SELECT session_name, start_scn, end_scn 
FROM v$logmnr_session;
```

### Network Configuration

- **Port**: 1521 (default) or custom port
- **Protocol**: TCP/IP
- **Firewall**: Allow inbound connections on Oracle port
- **TNS**: Optional, can use direct connection with host:port

### Common Issues

**Issue**: `ORA-01031: insufficient privileges` - Missing FLASHBACK privilege
- **Solution**: `GRANT FLASHBACK ANY TABLE TO c##cdc_user;`

**Issue**: `ORA-01354: LogMiner session not found`
- **Solution**: Ensure `LOGMINING` privilege is granted and archive logs are available

**Issue**: `ORA-00904: invalid identifier` - Schema/table access
- **Solution**: Grant explicit `SELECT` on the table: `GRANT SELECT ON schema.table TO user;`

**Issue**: `ORA-44609: CONTINOUS_MINE is desupported`
- **Solution**: Set `log.mining.continuous.mine: false` in Debezium connector config

**Issue**: `ORA-01017: invalid username/password`
- **Solution**: Verify credentials, check if user exists in correct container (CDB vs PDB)

---

## Snowflake

### Overview
Snowflake is typically used as a **target** (sink) for CDC. Requires warehouse, database, schema, and role permissions. Supports both password and key-pair authentication.

### Database-Level Configuration

#### 1. Create Database and Schema (if needed)
```sql
-- Connect as ACCOUNTADMIN or SYSADMIN

-- Create database
CREATE DATABASE IF NOT EXISTS your_database;

-- Create schema
USE DATABASE your_database;
CREATE SCHEMA IF NOT EXISTS your_schema;
```

#### 2. Create Warehouse (if needed)
```sql
-- Create warehouse for CDC operations
CREATE WAREHOUSE IF NOT EXISTS cdc_warehouse
    WITH WAREHOUSE_SIZE = 'X-SMALL'
    AUTO_SUSPEND = 60
    AUTO_RESUME = TRUE;
```

### User-Level Permissions

#### Required Privileges for CDC User (Sink)

```sql
-- Connect as ACCOUNTADMIN or SYSADMIN
-- Replace placeholders: cdc_user, your_database, your_schema, cdc_warehouse

-- Step 1: Create user (if doesn't exist)
CREATE USER IF NOT EXISTS cdc_user
    PASSWORD = 'your_secure_password'
    DEFAULT_ROLE = 'CDC_ROLE'
    DEFAULT_WAREHOUSE = 'cdc_warehouse';

-- Step 2: Create role
CREATE ROLE IF NOT EXISTS CDC_ROLE;

-- Step 3: Grant warehouse usage
GRANT USAGE ON WAREHOUSE cdc_warehouse TO ROLE CDC_ROLE;

-- Step 4: Grant database access
GRANT USAGE ON DATABASE your_database TO ROLE CDC_ROLE;

-- Step 5: Grant schema access
GRANT USAGE ON SCHEMA your_database.your_schema TO ROLE CDC_ROLE;

-- Step 6: Grant table creation and modification
GRANT CREATE TABLE ON SCHEMA your_database.your_schema TO ROLE CDC_ROLE;
GRANT INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA your_database.your_schema TO ROLE CDC_ROLE;

-- Step 7: Grant future table permissions (optional but recommended)
GRANT INSERT, UPDATE, DELETE ON FUTURE TABLES IN SCHEMA your_database.your_schema TO ROLE CDC_ROLE;

-- Step 8: Assign role to user
GRANT ROLE CDC_ROLE TO USER cdc_user;

-- Step 9: Set default role
ALTER USER cdc_user SET DEFAULT_ROLE = 'CDC_ROLE';
```

#### Complete Setup Script

```sql
-- Run as ACCOUNTADMIN or SYSADMIN

-- Step 1: Create warehouse
CREATE WAREHOUSE IF NOT EXISTS cdc_warehouse
    WITH WAREHOUSE_SIZE = 'X-SMALL'
    AUTO_SUSPEND = 60
    AUTO_RESUME = TRUE;

-- Step 2: Create database and schema
CREATE DATABASE IF NOT EXISTS your_database;
USE DATABASE your_database;
CREATE SCHEMA IF NOT EXISTS your_schema;

-- Step 3: Create user
CREATE USER IF NOT EXISTS cdc_user
    PASSWORD = 'your_secure_password'
    DEFAULT_ROLE = 'CDC_ROLE'
    DEFAULT_WAREHOUSE = 'cdc_warehouse';

-- Step 4: Create and configure role
CREATE ROLE IF NOT EXISTS CDC_ROLE;

GRANT USAGE ON WAREHOUSE cdc_warehouse TO ROLE CDC_ROLE;
GRANT USAGE ON DATABASE your_database TO ROLE CDC_ROLE;
GRANT USAGE ON SCHEMA your_database.your_schema TO ROLE CDC_ROLE;
GRANT CREATE TABLE ON SCHEMA your_database.your_schema TO ROLE CDC_ROLE;
GRANT INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA your_database.your_schema TO ROLE CDC_ROLE;

GRANT ROLE CDC_ROLE TO USER cdc_user;
ALTER USER cdc_user SET DEFAULT_ROLE = 'CDC_ROLE';

-- Verify
SHOW GRANTS TO ROLE CDC_ROLE;
SHOW GRANTS TO USER cdc_user;
```

### Authentication Methods

#### Option 1: Password Authentication
```sql
-- User created with password (as shown above)
-- Connection uses: username + password
```

#### Option 2: Key Pair Authentication (Recommended for Production)
```bash
# Step 1: Generate RSA key pair (on client machine)
ssh-keygen -t rsa -b 2048 -f rsa_key.pem

# Step 2: Extract public key
openssl rsa -in rsa_key.pem -pubout -out rsa_key.pub

# Step 3: Associate public key with user in Snowflake
ALTER USER cdc_user SET RSA_PUBLIC_KEY='MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8A...';

# Step 4: Use private key in connection (stored in additional_config.private_key)
```

**Connection Configuration for Key Pair Auth**:
```json
{
  "account": "your_account",
  "user": "cdc_user",
  "database": "your_database",
  "schema": "your_schema",
  "warehouse": "cdc_warehouse",
  "private_key": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----",
  "private_key_passphrase": "optional_passphrase"
}
```

### Special Schema Requirements for CDC

When using Snowflake as a CDC target, tables are auto-created with special columns:

```sql
-- Tables are auto-created with:
CREATE TABLE your_schema.your_table (
    RECORD_CONTENT VARIANT,      -- Full Debezium message envelope
    RECORD_METADATA VARIANT,     -- Kafka metadata (topic, partition, offset)
    -- ... other columns from source
);
```

**Important**: 
- `RECORD_CONTENT` must be `VARIANT` type (not `OBJECT`)
- `RECORD_METADATA` must be `VARIANT` type (not `OBJECT`)
- These columns are automatically created by the system

### Connection Configuration

#### Required Fields:
- **Account**: Snowflake account identifier (e.g., `xy12345.us-east-1`)
- **User**: Snowflake username
- **Database**: Database name
- **Schema**: Schema name (default: `PUBLIC`)

#### Optional Fields:
- **Warehouse**: Warehouse name (recommended for performance)
- **Role**: Role name (defaults to user's default role)
- **Password**: For password authentication
- **Private Key**: For key-pair authentication (alternative to password)

#### Additional Config:
```json
{
  "warehouse": "cdc_warehouse",
  "role": "CDC_ROLE",
  "private_key": "...",  // If using key-pair auth
  "private_key_passphrase": "..."  // If key is encrypted
}
```

### Verification Queries

```sql
-- Check user roles
SHOW GRANTS TO USER cdc_user;

-- Check role privileges
SHOW GRANTS TO ROLE CDC_ROLE;

-- Check warehouse access
SHOW GRANTS ON WAREHOUSE cdc_warehouse;

-- Check schema access
SHOW GRANTS ON SCHEMA your_database.your_schema;

-- Check table permissions
SHOW GRANTS ON TABLE your_database.your_schema.your_table;

-- Check table structure (verify RECORD_CONTENT and RECORD_METADATA are VARIANT)
DESC TABLE your_database.your_schema.your_table;
```

### Common Issues

**Issue**: `Insufficient privileges to operate on warehouse`
- **Solution**: Grant `USAGE ON WAREHOUSE` to the role

**Issue**: `Object does not exist or not authorized`
- **Solution**: Grant `USAGE ON DATABASE` and `USAGE ON SCHEMA`

**Issue**: `Table doesn't have a compatible schema` (Snowflake sink connector error)
- **Solution**: Ensure table has `RECORD_CONTENT VARIANT` and `RECORD_METADATA VARIANT` columns

**Issue**: `Invalid key format` (key-pair authentication)
- **Solution**: Ensure private key is properly formatted with `-----BEGIN PRIVATE KEY-----` headers

**Issue**: `Connection timeout`
- **Solution**: Check network connectivity, firewall rules, and Snowflake account status

---

## AS400/IBM i

### Overview
AS400/IBM i CDC uses **journaling** to track changes. Requires journaling to be enabled on tables and appropriate user permissions. Uses Debezium Db2 connector.

### Database-Level Configuration

#### 1. Enable Journaling on Tables
**Required**: Journaling must be enabled on each table to be replicated

```sql
-- On AS400/IBM i, enable journaling for a table
STRJRNPF FILE(LIBRARY/TABLENAME) JRN(LIBRARY/JOURNALNAME)
```

**Example**:
```
STRJRNPF FILE(MYLIB/MYTABLE) JRN(MYLIB/MYJOURNAL)
```

#### 2. Create Journal (if doesn't exist)
```sql
-- Create journal receiver
CRTJRNRCV JRNRCV(LIBRARY/JOURNALRCV) THRESHOLD(5000000)

-- Create journal
CRTJRN JRN(LIBRARY/JOURNALNAME) JRNRCV(LIBRARY/JOURNALRCV)
```

### User-Level Permissions

#### Required Privileges for CDC User

```sql
-- Connect as system administrator or user with *ALLOBJ authority

-- 1. Object authority on tables
GRANT OBJ(*LIBL/MYTABLE) OBJTYPE(*FILE) TO USER CDCUSER
    AUT(*USE)  -- Read access

-- 2. Object authority on journal
GRANT OBJ(*LIBL/MYJOURNAL) OBJTYPE(*JRN) TO USER CDCUSER
    AUT(*USE)  -- Read journal entries

-- 3. Object authority on journal receiver
GRANT OBJ(*LIBL/JOURNALRCV) OBJTYPE(*JRNRCV) TO USER CDCUSER
    AUT(*USE)

-- 4. Library authority (if needed)
GRANT OBJ(*LIBL) OBJTYPE(*LIB) TO USER CDCUSER
    AUT(*USE)
```

#### Complete Setup Script

```sql
-- Run as system administrator
-- Replace placeholders: CDCUSER, MYLIB, MYTABLE, MYJOURNAL

-- Step 1: Enable journaling on table
STRJRNPF FILE(MYLIB/MYTABLE) JRN(MYLIB/MYJOURNAL)

-- Step 2: Grant table access
GRANT OBJ(MYLIB/MYTABLE) OBJTYPE(*FILE) TO USER CDCUSER AUT(*USE)

-- Step 3: Grant journal access
GRANT OBJ(MYLIB/MYJOURNAL) OBJTYPE(*JRN) TO USER CDCUSER AUT(*USE)

-- Step 4: Grant library access (if needed)
GRANT OBJ(MYLIB) OBJTYPE(*LIB) TO USER CDCUSER AUT(*USE)

-- Verify journaling
SELECT * FROM QSYS2.JOURNAL_INFO
WHERE JOURNAL_LIBRARY = 'MYLIB' AND JOURNAL_NAME = 'MYJOURNAL'
```

### Connection Configuration

#### Connection Parameters
- **Host**: AS400 server hostname or IP
- **Port**: 446 (default AS400 port)
- **Database**: Library name (e.g., "MYLIB")
- **Schema**: Library name (same as database)
- **Username**: AS400 user
- **Password**: AS400 password

#### Additional Config (in connection's `additional_config`):
```json
{
  "driver": "IBM i Access ODBC Driver",
  "journal_library": "MYLIB",
  "journal_name": "MYJOURNAL",
  "docker_hostname": "as400-hostname"  // If Kafka Connect is in Docker
}
```

### Prerequisites

#### 1. IBM i Access Client Solutions
Install IBM i Access Client Solutions on the system where Kafka Connect runs:

- **For macOS**: Download from [IBM website](https://www.ibm.com/support/pages/ibm-i-access-client-solutions)
- **For Linux**: Download and install IBM i Access Client Solutions for Linux
- **For Windows**: Download and install from IBM website

#### 2. ODBC Driver Verification
```bash
# On Linux/macOS
odbcinst -q -d

# Should show "IBM i Access ODBC Driver"
```

### Network Configuration

- **Port**: 446 (default AS400 port)
- **Protocol**: TCP/IP
- **Firewall**: Allow inbound connections on port 446

### Verification Queries

```sql
-- Check if journaling is enabled on table
SELECT * FROM QSYS2.JOURNAL_INFO
WHERE JOURNAL_LIBRARY = 'MYLIB' AND JOURNAL_NAME = 'MYJOURNAL'

-- Check table journaling status
SELECT * FROM QSYS2.TABLE_INFO
WHERE TABLE_SCHEMA = 'MYLIB' AND TABLE_NAME = 'MYTABLE'
```

### Common Issues

**Issue**: `Journal not found` or CDC not capturing changes
- **Solution**: Enable journaling: `STRJRNPF FILE(LIBRARY/TABLENAME) JRN(LIBRARY/JOURNALNAME)`

**Issue**: `ODBC driver not found`
- **Solution**: Install IBM i Access Client Solutions on the system running Kafka Connect

**Issue**: `Connection failed`
- **Solution**: Verify network connectivity, firewall rules (port 446), and credentials

---

## S3

### Overview
S3 is used as a **target** (sink) for full load and CDC. Requires AWS credentials and bucket permissions. Uses Confluent S3 Sink Connector.

### AWS Configuration

#### 1. Create S3 Bucket
```bash
# Using AWS CLI
aws s3 mb s3://your-cdc-bucket --region us-east-1
```

#### 2. Configure Bucket Policy
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AllowCDCWrite",
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::ACCOUNT_ID:user/cdc_user"
      },
      "Action": [
        "s3:PutObject",
        "s3:GetObject",
        "s3:DeleteObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::your-cdc-bucket",
        "arn:aws:s3:::your-cdc-bucket/*"
      ]
    }
  ]
}
```

### IAM User Permissions

#### Required IAM Policy for CDC User

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:PutObject",
        "s3:GetObject",
        "s3:DeleteObject",
        "s3:ListBucket",
        "s3:GetBucketLocation"
      ],
      "Resource": [
        "arn:aws:s3:::your-cdc-bucket",
        "arn:aws:s3:::your-cdc-bucket/*"
      ]
    }
  ]
}
```

#### Create IAM User

```bash
# Create IAM user
aws iam create-user --user-name cdc_user

# Create access key
aws iam create-access-key --user-name cdc_user

# Attach policy
aws iam put-user-policy \
    --user-name cdc_user \
    --policy-name S3CDCAccess \
    --policy-document file://s3-cdc-policy.json
```

### Connection Configuration

In the connection, provide:

```json
{
  "bucket": "your-cdc-bucket",
  "aws_access_key_id": "AKIAIOSFODNN7EXAMPLE",
  "aws_secret_access_key": "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY",
  "region_name": "us-east-1",
  "prefix": "cdc-data/"  // Optional: folder prefix
}
```

#### Connection Field Mapping:
- **Database**: Bucket name
- **Schema**: Prefix/folder path (optional)
- **Username**: AWS Access Key ID
- **Password**: AWS Secret Access Key
- **Host**: Not used (S3 doesn't use host)
- **Port**: Not used

#### Additional Config:
```json
{
  "region_name": "us-east-1",
  "prefix": "cdc-data/",
  "endpoint_url": "https://s3.amazonaws.com"  // Optional: for S3-compatible services
}
```

### Network Configuration

- **Protocol**: HTTPS (port 443)
- **Endpoint**: `s3.{region}.amazonaws.com` or custom endpoint
- **Firewall**: Allow outbound HTTPS connections

### Verification

```bash
# Test S3 access
aws s3 ls s3://your-cdc-bucket --profile cdc_user

# Test write access
echo "test" | aws s3 cp - s3://your-cdc-bucket/test.txt --profile cdc_user
```

### Common Issues

**Issue**: `Access Denied` when writing to S3
- **Solution**: Check IAM policy and bucket policy permissions

**Issue**: `Bucket does not exist`
- **Solution**: Create bucket or verify bucket name and region

**Issue**: `Invalid credentials`
- **Solution**: Verify AWS Access Key ID and Secret Access Key

---

## Kafka Connect Requirements

### Overview
Kafka Connect is the infrastructure that runs Debezium source connectors and sink connectors. It requires specific configuration and connector plugins.

### Required Connector Plugins

#### For Source Databases:
1. **PostgreSQL**: `debezium-connector-postgres`
2. **SQL Server**: `debezium-connector-sqlserver`
3. **Oracle**: `debezium-connector-oracle`
4. **AS400/IBM i**: `debezium-connector-db2`

#### For Target Databases:
1. **SQL Server**: `kafka-connect-jdbc` + `mssql-jdbc` driver
2. **Snowflake**: `snowflake-kafka-connector`
3. **S3**: `kafka-connect-s3`

### Installation

#### Install Debezium Connectors
```bash
# Download Debezium connector
cd /tmp
wget https://repo1.maven.org/maven2/io/debezium/debezium-connector-postgres/2.5.0.Final/debezium-connector-postgres-2.5.0.Final-plugin.tar.gz

# Extract
tar -xzf debezium-connector-postgres-2.5.0.Final-plugin.tar.gz

# Copy to Kafka Connect
docker cp debezium-connector-postgres-2.5.0.Final-plugin/. kafka-connect-cdc:/kafka/connect/

# Restart Kafka Connect
docker restart kafka-connect-cdc
```

#### Install JDBC Sink Connector (for SQL Server)
```bash
# Download JDBC connector
wget https://repo1.maven.org/maven2/io/confluent/kafka-connect-jdbc/10.7.4/kafka-connect-jdbc-10.7.4.jar

# Download SQL Server driver
wget https://repo1.maven.org/maven2/com/microsoft/sqlserver/mssql-jdbc/12.4.2.jre8/mssql-jdbc-12.4.2.jre8.jar

# Copy to container
docker cp kafka-connect-jdbc-10.7.4.jar kafka-connect-cdc:/kafka/connect/
docker cp mssql-jdbc-12.4.2.jre8.jar kafka-connect-cdc:/kafka/connect/

# Restart
docker restart kafka-connect-cdc
```

#### Install Snowflake Connector
```bash
# Download Snowflake connector
wget https://repo1.maven.org/maven2/com/snowflake/snowflake-kafka-connector/2.1.0/snowflake-kafka-connector-2.1.0.jar

# Copy to container
docker cp snowflake-kafka-connector-2.1.0.jar kafka-connect-cdc:/kafka/connect/

# Restart
docker restart kafka-connect-cdc
```

### Kafka Connect Configuration

#### Environment Variables
```bash
# Kafka Connect worker configuration
CONNECT_BOOTSTRAP_SERVERS=kafka:29092
CONNECT_REST_ADVERTISED_HOST_NAME=kafka-connect-cdc
CONNECT_REST_PORT=8083
CONNECT_PLUGIN_PATH=/kafka/connect
CONNECT_GROUP_ID=connect-cluster
CONNECT_CONFIG_STORAGE_TOPIC=connect-configs
CONNECT_OFFSET_STORAGE_TOPIC=connect-offsets
CONNECT_STATUS_STORAGE_TOPIC=connect-status
```

### Verification

```bash
# Check connector plugins
curl http://localhost:8083/connector-plugins | jq

# Should show installed connectors:
# - io.debezium.connector.postgresql.PostgresConnector
# - io.debezium.connector.sqlserver.SqlServerConnector
# - io.debezium.connector.oracle.OracleConnector
# - io.confluent.connect.jdbc.JdbcSinkConnector
# - com.snowflake.kafka.connector.SnowflakeSinkConnector
```

---

## Network and Firewall

### Port Requirements

| Service | Port | Protocol | Direction | Purpose |
|---------|------|----------|-----------|---------|
| **PostgreSQL** | 5432 | TCP | Inbound | Database connections |
| **SQL Server** | 1433 | TCP | Inbound | Database connections |
| **Oracle** | 1521 | TCP | Inbound | Database connections |
| **AS400/IBM i** | 446 | TCP | Inbound | Database connections |
| **Kafka** | 9092 | TCP | Both | Kafka broker |
| **Kafka Connect** | 8083 | HTTP | Inbound | REST API |
| **Zookeeper** | 2181 | TCP | Both | Zookeeper |
| **Snowflake** | 443 | HTTPS | Outbound | API connections |
| **S3** | 443 | HTTPS | Outbound | API connections |

### Firewall Rules

#### For Source Databases:
- Allow inbound connections from Kafka Connect server IP
- Allow connections on database port (5432, 1433, 1521, 446)

#### For Target Databases:
- Allow inbound connections from Kafka Connect server IP
- Allow connections on database port

#### For Kafka Connect:
- Allow outbound connections to source databases
- Allow outbound connections to target databases
- Allow outbound connections to Kafka broker
- Allow inbound connections on port 8083 (REST API)

### Network Connectivity Testing

```bash
# Test PostgreSQL connection
telnet postgres-host 5432

# Test SQL Server connection
telnet sqlserver-host 1433

# Test Oracle connection
telnet oracle-host 1521

# Test Kafka Connect API
curl http://kafka-connect-host:8083/connector-plugins
```

---

## Quick Reference

### Summary Table

| Database | Source CDC | Target Sink | Key Permission | Port |
|----------|-----------|-------------|----------------|------|
| **PostgreSQL** | ✅ WAL Logical Replication | ✅ JDBC Sink | `REPLICATION` privilege | 5432 |
| **SQL Server** | ✅ Native CDC | ✅ JDBC Sink | `db_owner` or CDC permissions | 1433 |
| **Oracle** | ✅ LogMiner | ✅ JDBC Sink | `FLASHBACK ANY TABLE`, `LOGMINING` | 1521 |
| **Snowflake** | ❌ Not supported | ✅ Snowflake Sink | `CREATE TABLE`, `INSERT/UPDATE/DELETE` | 443 |
| **AS400/IBM i** | ✅ Journaling | ✅ JDBC Sink | Journal read access | 446 |
| **S3** | ❌ Not supported | ✅ S3 Sink | `s3:PutObject`, `s3:GetObject` | 443 |

### Permission Checklist

#### For Source Databases (CDC):
- [ ] **PostgreSQL**: `REPLICATION` privilege, `wal_level = logical`, `max_replication_slots >= 10`
- [ ] **SQL Server**: CDC enabled on database and tables, `db_owner` or CDC permissions
- [ ] **Oracle**: `FLASHBACK ANY TABLE`, `LOGMINING`, archive log mode, supplemental logging
- [ ] **AS400**: Journaling enabled, journal read access

#### For Target Databases (Sink):
- [ ] **SQL Server**: `CREATE TABLE`, `INSERT/UPDATE/DELETE` permissions
- [ ] **Snowflake**: `CREATE TABLE`, `INSERT/UPDATE/DELETE` on schema, warehouse usage
- [ ] **S3**: IAM policy with `s3:PutObject`, `s3:GetObject`

### Testing Connection

After granting permissions, test the connection:

```python
# Example: Test PostgreSQL connection
from ingestion.connectors.postgresql import PostgreSQLConnector

connector = PostgreSQLConnector({
    "host": "localhost",
    "port": 5432,
    "database": "mydb",
    "user": "cdc_user",
    "password": "password"
})

# Test connection
if connector.test_connection():
    print("✅ Connection successful!")
    
    # Validate CDC setup
    validation = connector.validate_cdc_setup()
    if validation.get("errors"):
        print("❌ CDC setup issues:", validation["errors"])
    else:
        print("✅ CDC setup valid!")
```

---

## Troubleshooting

### Common Connection Issues

#### Issue: Connection Timeout
**Symptoms**: Cannot connect to database
**Solutions**:
1. Check network connectivity: `ping database-host`
2. Check firewall rules: Allow inbound connections on database port
3. Verify database is running: `systemctl status postgresql` (Linux)
4. Check database configuration: Ensure remote connections are allowed

#### Issue: Authentication Failed
**Symptoms**: `invalid username/password` or `authentication failed`
**Solutions**:
1. Verify credentials are correct
2. Check if user exists: `SELECT * FROM pg_user WHERE usename = 'cdc_user'` (PostgreSQL)
3. Check password expiration (SQL Server, Oracle)
4. Verify user is not locked

#### Issue: Permission Denied
**Symptoms**: `permission denied` or `insufficient privileges`
**Solutions**:
1. Review permission checklist for your database type
2. Grant required privileges (see database-specific sections)
3. Verify user has correct role/permissions
4. Check if permissions were granted to correct user/database

### Common CDC Issues

#### Issue: CDC Not Capturing Changes
**Symptoms**: No messages in Kafka topics, connector running but no data
**Solutions**:
1. **PostgreSQL**: Check replication slot is active, WAL level is `logical`
2. **SQL Server**: Verify CDC is enabled on database and tables
3. **Oracle**: Check archive log mode, LogMiner session status
4. **AS400**: Verify journaling is enabled on tables

#### Issue: Connector Task Failed
**Symptoms**: Connector status shows `FAILED`, task shows error
**Solutions**:
1. Check connector logs: `curl http://localhost:8083/connectors/{connector}/status`
2. Verify database permissions (see permission checklist)
3. Check database configuration (WAL level, CDC enabled, etc.)
4. Verify connector plugin is installed

#### Issue: Sink Connector Not Writing Data
**Symptoms**: Source connector working, but no data in target
**Solutions**:
1. Check sink connector status and logs
2. Verify target database permissions (CREATE TABLE, INSERT, etc.)
3. Check table schema compatibility (especially for Snowflake)
4. Verify Kafka topic has messages: `kafka-console-consumer --topic {topic}`

### Getting Help

1. **Check Logs**: Review Kafka Connect logs and database logs
2. **Verify Configuration**: Use verification queries in each database section
3. **Test Connection**: Use connection test scripts
4. **Review Permissions**: Go through permission checklist

---

## Additional Resources

- [PostgreSQL Logical Replication](https://www.postgresql.org/docs/current/logical-replication.html)
- [SQL Server Change Data Capture](https://docs.microsoft.com/en-us/sql/relational-databases/track-changes/about-change-data-capture-sql-server)
- [Oracle LogMiner](https://docs.oracle.com/en/database/oracle/oracle-database/19/sutil/oracle-logminer-utility.html)
- [Snowflake Access Control](https://docs.snowflake.com/en/user-guide/security-access-control.html)
- [IBM i Journaling](https://www.ibm.com/docs/en/i/7.4?topic=concepts-journaling)
- [AWS S3 IAM Policies](https://docs.aws.amazon.com/AmazonS3/latest/userguide/access-policy-language-overview.html)
- [Debezium Documentation](https://debezium.io/documentation/)
- [Kafka Connect Documentation](https://kafka.apache.org/documentation/#connect)

---

**Last Updated**: 2025-01-13  
**Version**: 1.0  
**Maintained By**: CDC Team

