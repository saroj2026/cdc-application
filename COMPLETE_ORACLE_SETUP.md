# Complete Oracle Setup Instructions

## ✅ Completed Steps

### 1. Python Oracle Driver
- ✅ **Status**: Installed
- ✅ **Package**: `oracledb` version 3.4.1
- ✅ **Verification**: Can be imported

### 2. Database Migration
- ✅ **Status**: Code updated (Oracle in DatabaseType enum)
- ⚠️ **Note**: Database migration may need to be run when database is accessible
- **Command**: `alembic upgrade heads` (when database is running)

### 3. Backend Code
- ✅ Oracle connector created (`oracle.py`)
- ✅ Added to connection service
- ✅ Debezium config added
- ✅ All imports updated

## 📋 Remaining Steps

### Step 1: Install Debezium Oracle Connector JAR on Server

**Run this script on the server (72.61.233.209):**

```bash
# Copy script to server
scp install_oracle_connector_server.sh root@72.61.233.209:/tmp/

# SSH and run
ssh root@72.61.233.209
chmod +x /tmp/install_oracle_connector_server.sh
/tmp/install_oracle_connector_server.sh
```

**Or run manually on server:**

```bash
# SSH into server
ssh root@72.61.233.209

# Run installation
docker exec 28b9a11e27bb bash -c "
    cd /usr/share/confluent-hub-components && \
    mkdir -p debezium-connector-oracle && \
    cd debezium-connector-oracle && \
    wget -q https://repo1.maven.org/maven2/io/debezium/debezium-connector-oracle/2.5.0.Final/debezium-connector-oracle-2.5.0.Final-plugin.tar.gz && \
    tar -xzf debezium-connector-oracle-2.5.0.Final-plugin.tar.gz && \
    rm debezium-connector-oracle-2.5.0.Final-plugin.tar.gz && \
    echo 'Installation complete'
"

# Restart Kafka Connect
docker restart 28b9a11e27bb

# Wait 15 seconds, then verify
sleep 15
docker exec 28b9a11e27bb curl -s http://localhost:8083/connector-plugins | grep -i oracle
```

### Step 2: Run Database Migration (when database is accessible)

```bash
# When PostgreSQL management database is running
alembic upgrade heads

# Or if that fails due to multiple heads:
alembic upgrade add_oracle_enum
```

**Alternative: Add Oracle to enum directly in database:**

```sql
-- Connect to PostgreSQL management database
-- Then run:
ALTER TYPE database_type ADD VALUE IF NOT EXISTS 'oracle';
```

### Step 3: Verify Installation

Run the verification script:

```bash
python verify_oracle_setup.py
```

This will check:
- ✅ Python Oracle driver
- ✅ DatabaseType enum
- ✅ OracleConnector import
- ✅ Debezium config
- ✅ Kafka Connect connector availability

## Quick Reference

### Oracle Container (from your Docker list)
- **Container**: `4125e9856bf9` (oracle-xe)
- **Port**: `1521`
- **Default SID**: `XE`
- **Default Service Name**: `XEPDB1` (for PDB)

### Kafka Connect Container
- **Container**: `28b9a11e27bb` (kafka-connect-cdc)
- **Port**: `8083`
- **Plugins Directory**: `/usr/share/confluent-hub-components`

### Files Created
- ✅ `ingestion/connectors/oracle.py` - Oracle connector
- ✅ `install_oracle_connector_server.sh` - Installation script
- ✅ `verify_oracle_setup.py` - Verification script
- ✅ `ORACLE_INTEGRATION_GUIDE.md` - Complete guide
- ✅ `ORACLE_SETUP_COMPLETE.md` - Setup summary

## Next Steps After Installation

1. **Test Oracle Connection**
   ```python
   from ingestion.connectors.oracle import OracleConnector
   
   config = {
       "host": "72.61.233.209",
       "port": 1521,
       "database": "XE",
       "user": "SYSTEM",
       "password": "your_password"
   }
   
   connector = OracleConnector(config)
   connector.test_connection()  # Should return True
   ```

2. **Create Oracle → Snowflake Pipeline**
   - Use API or UI
   - Source: Oracle connection
   - Target: Snowflake connection
   - Select tables
   - Start pipeline

3. **Verify Data Flow**
   - Full load works
   - CDC works
   - Data appears in Snowflake

## Summary

✅ **Backend Code**: 100% Complete
✅ **Python Driver**: Installed
⚠️ **Database Migration**: Needs database to be running
⚠️ **Debezium JAR**: Needs to be installed on server

**Once the Debezium JAR is installed and migration is run, the system is ready!**

