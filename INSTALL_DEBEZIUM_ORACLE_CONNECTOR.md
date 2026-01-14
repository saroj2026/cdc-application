# Install Debezium Oracle Connector JAR

## Overview

The Debezium Oracle connector must be installed in the Kafka Connect plugins directory on the server where Kafka Connect is running.

**Server:** `72.61.233.209:8083` (Kafka Connect)

## Step 1: Download Debezium Oracle Connector

### Option A: Download from Debezium Releases

1. Go to [Debezium Releases](https://debezium.io/releases/)
2. Download the latest Oracle connector:
   - Example: `debezium-connector-oracle-2.5.0.Final-plugin.tar.gz`
   - Or download individual JAR files

### Option B: Use Confluent Hub

```bash
# SSH into the server
ssh root@72.61.233.209

# Install via Confluent Hub (if available)
confluent-hub install debezium/debezium-connector-oracle:latest
```

## Step 2: Find Kafka Connect Plugins Directory

The plugins directory is typically:
- `/usr/share/confluent-hub-components/`
- `/opt/kafka/plugins/`
- `/kafka/connect/plugins/`
- Or check Kafka Connect configuration

### Check Current Plugin Location

```bash
# SSH into server
ssh root@72.61.233.209

# Find Kafka Connect container
docker ps | grep connect

# Check plugin path in container
docker exec <container_id> env | grep PLUGIN
docker exec <container_id> ls -la /usr/share/confluent-hub-components/
```

## Step 3: Install the Connector

### Method 1: Copy to Container (Recommended)

```bash
# On your local machine, download the connector
# Then copy to server
scp debezium-connector-oracle-*.tar.gz root@72.61.233.209:/tmp/

# SSH into server
ssh root@72.61.233.209

# Extract the connector
cd /tmp
tar -xzf debezium-connector-oracle-*.tar.gz

# Find Kafka Connect container
CONTAINER_ID=$(docker ps | grep connect | awk '{print $1}')

# Copy to container's plugin directory
docker cp debezium-connector-oracle root@72.61.233.209:/tmp/
docker exec $CONTAINER_ID mkdir -p /usr/share/confluent-hub-components/debezium-connector-oracle
docker cp /tmp/debezium-connector-oracle/. $CONTAINER_ID:/usr/share/confluent-hub-components/debezium-connector-oracle/

# Restart Kafka Connect to load new connector
docker restart $CONTAINER_ID
```

### Method 2: Direct Installation in Container

```bash
# SSH into server
ssh root@72.61.233.209

# Find container
CONTAINER_ID=$(docker ps | grep connect | awk '{print $1}')

# Download directly in container (if wget/curl available)
docker exec $CONTAINER_ID bash -c "
  cd /tmp &&
  wget https://repo1.maven.org/maven2/io/debezium/debezium-connector-oracle/2.5.0.Final/debezium-connector-oracle-2.5.0.Final-plugin.tar.gz &&
  tar -xzf debezium-connector-oracle-2.5.0.Final-plugin.tar.gz &&
  cp -r debezium-connector-oracle /usr/share/confluent-hub-components/
"

# Restart container
docker restart $CONTAINER_ID
```

## Step 4: Verify Installation

### Check Plugin is Available

```bash
# SSH into server
ssh root@72.61.233.209

# Check connector plugins
curl http://localhost:8083/connector-plugins | grep -i oracle

# Or check in container
docker exec <container_id> curl -s http://localhost:8083/connector-plugins | python3 -m json.tool | grep -i oracle
```

### Expected Output

You should see:
```json
{
  "class": "io.debezium.connector.oracle.OracleConnector",
  "type": "source",
  "version": "2.5.0.Final"
}
```

## Step 5: Verify Oracle JDBC Driver

The Debezium Oracle connector requires the Oracle JDBC driver (`ojdbc8.jar` or `ojdbc11.jar`). It's usually included in the connector package, but verify:

```bash
# Check if ojdbc JAR is present
docker exec <container_id> ls -la /usr/share/confluent-hub-components/debezium-connector-oracle/ | grep ojdbc
```

If missing, download and add:
- `ojdbc8.jar` for Oracle 12c/18c/19c
- `ojdbc11.jar` for Oracle 21c+

## Required Files

The connector directory should contain:
- `debezium-connector-oracle-*.jar`
- `ojdbc*.jar` (Oracle JDBC driver)
- `debezium-core-*.jar`
- Other dependencies

## Troubleshooting

### Connector Not Appearing

1. **Check plugin path:**
   ```bash
   docker exec <container_id> env | grep PLUGIN
   ```

2. **Check logs:**
   ```bash
   docker logs <container_id> | grep -i oracle
   docker logs <container_id> | grep -i error
   ```

3. **Verify JAR files:**
   ```bash
   docker exec <container_id> ls -la /usr/share/confluent-hub-components/debezium-connector-oracle/
   ```

### Class Not Found Errors

- Ensure all JAR files are in the connector directory
- Check Oracle JDBC driver is present
- Verify Java version compatibility (Oracle connector requires Java 11+)

### Connection Errors

- Verify Oracle database is accessible from Kafka Connect container
- Check network connectivity
- Verify Oracle listener is running

## Quick Installation Script

Save this as `install_debezium_oracle.sh`:

```bash
#!/bin/bash
# Install Debezium Oracle Connector

CONTAINER_ID=$(docker ps | grep connect | awk '{print $1}')
PLUGIN_DIR="/usr/share/confluent-hub-components/debezium-connector-oracle"
VERSION="2.5.0.Final"

echo "Installing Debezium Oracle Connector $VERSION..."

# Download and extract
docker exec $CONTAINER_ID bash -c "
  cd /tmp &&
  wget -q https://repo1.maven.org/maven2/io/debezium/debezium-connector-oracle/$VERSION/debezium-connector-oracle-$VERSION-plugin.tar.gz &&
  tar -xzf debezium-connector-oracle-$VERSION-plugin.tar.gz &&
  mkdir -p $PLUGIN_DIR &&
  cp -r debezium-connector-oracle/* $PLUGIN_DIR/ &&
  rm -rf /tmp/debezium-connector-oracle*
"

# Restart container
echo "Restarting Kafka Connect..."
docker restart $CONTAINER_ID

# Wait for restart
sleep 10

# Verify
echo "Verifying installation..."
docker exec $CONTAINER_ID curl -s http://localhost:8083/connector-plugins | grep -i oracle

echo "Installation complete!"
```

Run it:
```bash
chmod +x install_debezium_oracle.sh
./install_debezium_oracle.sh
```

## Next Steps

After installation:
1. ✅ Verify connector appears in plugin list
2. ✅ Test Oracle connection from backend
3. ✅ Create Oracle → Snowflake pipeline
4. ✅ Verify CDC works

## References

- [Debezium Oracle Connector Documentation](https://debezium.io/documentation/reference/connectors/oracle.html)
- [Debezium Releases](https://debezium.io/releases/)
- [Oracle JDBC Driver Downloads](https://www.oracle.com/database/technologies/appdev/jdbc-downloads.html)

