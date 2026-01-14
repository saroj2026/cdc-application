# Installing Debezium Oracle Connector

## Step 1: Install Python Oracle Driver ✅

Already completed:
```bash
pip install oracledb
```

## Step 2: Run Database Migration ✅

Already completed:
```bash
alembic upgrade head
```

## Step 3: Install Debezium Oracle Connector JAR

The Debezium Oracle Connector JAR needs to be installed on the Kafka Connect server (72.61.233.209).

### Option A: Using the Installation Script

1. **Copy the script to the server:**
   ```bash
   scp install_debezium_oracle_connector.sh root@72.61.233.209:/tmp/
   ```

2. **SSH into the server and run:**
   ```bash
   ssh root@72.61.233.209
   chmod +x /tmp/install_debezium_oracle_connector.sh
   /tmp/install_debezium_oracle_connector.sh
   ```

3. **Restart Kafka Connect:**
   ```bash
   # If Kafka Connect is in Docker:
   docker restart <kafka-connect-container-id>
   
   # Or find the container:
   docker ps | grep kafka-connect
   docker restart <container-id>
   ```

### Option B: Manual Installation

1. **SSH into the Kafka Connect server:**
   ```bash
   ssh root@72.61.233.209
   ```

2. **Find Kafka Connect plugins directory:**
   ```bash
   # Common locations:
   # /usr/share/confluent-hub-components
   # /opt/kafka/plugins
   # /var/lib/kafka-connect/plugins
   
   # Check Docker container:
   docker exec <kafka-connect-container> ls -la /usr/share/confluent-hub-components
   ```

3. **Download Debezium Oracle Connector:**
   ```bash
   cd /usr/share/confluent-hub-components
   mkdir -p debezium-connector-oracle
   cd debezium-connector-oracle
   
   # Download version 2.5.0.Final (or latest)
   wget https://repo1.maven.org/maven2/io/debezium/debezium-connector-oracle/2.5.0.Final/debezium-connector-oracle-2.5.0.Final-plugin.tar.gz
   
   # Extract
   tar -xzf debezium-connector-oracle-2.5.0.Final-plugin.tar.gz
   rm debezium-connector-oracle-2.5.0.Final-plugin.tar.gz
   ```

4. **Verify installation:**
   ```bash
   ls -la /usr/share/confluent-hub-components/debezium-connector-oracle/
   # Should see: debezium-connector-oracle-*.jar and other files
   ```

5. **Restart Kafka Connect:**
   ```bash
   docker restart <kafka-connect-container-id>
   ```

6. **Verify connector is available:**
   ```bash
   curl http://localhost:8083/connector-plugins | grep -i oracle
   # Should return: "io.debezium.connector.oracle.OracleConnector"
   ```

### Option C: Using Confluent Hub (if available)

```bash
# If Confluent Hub CLI is installed:
confluent-hub install debezium/debezium-connector-oracle:2.5.0
```

## Verification

After installation, verify the connector is available:

```bash
# Check connector plugins
curl http://72.61.233.209:8083/connector-plugins | python3 -m json.tool | grep -i oracle

# Should see:
# {
#   "class": "io.debezium.connector.oracle.OracleConnector",
#   "type": "source",
#   "version": "2.5.0.Final"
# }
```

## Troubleshooting

### Connector Not Found

If the connector doesn't appear:

1. **Check plugins directory:**
   ```bash
   docker exec <container> ls -la /usr/share/confluent-hub-components/
   ```

2. **Check Kafka Connect logs:**
   ```bash
   docker logs <kafka-connect-container> | grep -i oracle
   docker logs <kafka-connect-container> | grep -i error
   ```

3. **Verify JAR files are present:**
   ```bash
   docker exec <container> find /usr/share/confluent-hub-components -name "*oracle*.jar"
   ```

### Missing Oracle JDBC Driver

The connector package should include the Oracle JDBC driver, but if it's missing:

1. **Download Oracle JDBC driver:**
   - Visit: https://www.oracle.com/database/technologies/appdev/jdbc-downloads.html
   - Download `ojdbc8.jar` or `ojdbc11.jar` (depending on Oracle version)

2. **Place in connector directory:**
   ```bash
   # Copy to connector directory
   cp ojdbc8.jar /usr/share/confluent-hub-components/debezium-connector-oracle/
   ```

3. **Restart Kafka Connect**

## Next Steps

After installation:

1. ✅ Test Oracle connection using the backend API
2. ✅ Create Oracle → Snowflake pipeline
3. ✅ Verify full load works
4. ✅ Verify CDC works

## Quick Reference

**Kafka Connect Server:** 72.61.233.209:8083
**Connector Class:** `io.debezium.connector.oracle.OracleConnector`
**Required JAR:** `debezium-connector-oracle-*.jar`
**JDBC Driver:** `ojdbc8.jar` or `ojdbc11.jar` (usually included)

