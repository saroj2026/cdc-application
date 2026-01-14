# Installing Debezium AS400/IBM i Connector

## Overview
**Important:** Debezium has a **specific AS400/IBM i connector** (`io.debezium.connector.db2as400.As400RpcConnector`) for IBM i/AS400 systems. This is different from the generic Db2 connector.

This guide explains how to install the Debezium AS400 connector in your Kafka Connect Docker container for AS400/IBM i CDC.

## Prerequisites
- Access to the Kafka Connect Docker container
- SSH access to the server (72.61.233.209)
- Docker installed on the server

## Installation Steps

### Option 1: Using Docker Exec (Recommended)

1. **SSH into the server:**
   ```bash
   ssh root@72.61.233.209
   # Password: segmbp@1100
   ```

2. **Find the Kafka Connect container:**
   ```bash
   docker ps | grep connect
   # Note the container name/ID
   ```

3. **Download Debezium Db2 Connector:**
   ```bash
   # Create a directory for the connector
   mkdir -p /tmp/debezium-db2-connector
   cd /tmp/debezium-db2-connector
   
   # Download the connector (latest version)
   wget https://repo1.maven.org/maven2/io/debezium/debezium-connector-db2/2.5.0.Final/debezium-connector-db2-2.5.0.Final-plugin.tar.gz
   
   # Extract
   tar -xzf debezium-connector-db2-2.5.0.Final-plugin.tar.gz
   ```

4. **Copy connector to Kafka Connect container:**
   ```bash
   # Replace CONTAINER_NAME with your Kafka Connect container name
   CONTAINER_NAME=$(docker ps | grep connect | awk '{print $1}' | head -1)
   
   # Copy the connector plugin directory
   docker cp debezium-connector-db2-2.5.0.Final-plugin $CONTAINER_NAME:/kafka/connect/debezium-connector-db2
   ```

5. **Restart Kafka Connect container:**
   ```bash
   docker restart $CONTAINER_NAME
   ```

6. **Verify installation:**
   ```bash
   # Wait a few seconds for Kafka Connect to start
   sleep 10
   
   # Check if the connector plugin is available
   curl http://localhost:8083/connector-plugins | grep -i db2
   ```

### Option 2: Using Docker Compose (If Using docker-compose.yml)

If your Kafka Connect is managed via docker-compose:

1. **Edit docker-compose.yml:**
   ```yaml
   kafka-connect:
     image: confluentinc/cp-kafka-connect:latest
     volumes:
       - ./connectors:/usr/share/confluent-hub-components
       - debezium-connector-db2:/usr/share/confluent-hub-components/debezium-connector-db2
     environment:
       CONNECT_PLUGIN_PATH: "/usr/share/java,/usr/share/confluent-hub-components"
   ```

2. **Download and extract connector:**
   ```bash
   mkdir -p connectors/debezium-connector-db2
   cd connectors/debezium-connector-db2
   wget https://repo1.maven.org/maven2/io/debezium/debezium-connector-db2/2.5.0.Final/debezium-connector-db2-2.5.0.Final-plugin.tar.gz
   tar -xzf debezium-connector-db2-2.5.0.Final-plugin.tar.gz
   mv debezium-connector-db2-2.5.0.Final-plugin/* .
   rm -rf debezium-connector-db2-2.5.0.Final-plugin
   ```

3. **Restart services:**
   ```bash
   docker-compose restart kafka-connect
   ```

### Option 3: Using Confluent Hub (If Available)

If Confluent Hub is installed:

```bash
# SSH into server
ssh user@72.61.233.209

# Find Kafka Connect container
CONTAINER_NAME=$(docker ps | grep connect | awk '{print $1}' | head -1)

# Install via Confluent Hub
docker exec -it $CONTAINER_NAME confluent-hub install debezium/debezium-connector-db2:latest

# Restart container
docker restart $CONTAINER_NAME
```

## Verification

After installation, verify the connector is available:

```bash
# Check connector plugins
curl http://72.61.233.209:8083/connector-plugins | python3 -m json.tool | grep -i db2

# Should show:
# "class": "io.debezium.connector.db2.Db2Connector"
```

## Required JARs

The Debezium Db2 connector (used for IBM i/AS400) requires:
- `debezium-connector-db2-*.jar` - Main connector JAR (this is the connector for IBM i)
- `debezium-core-*.jar` - Core Debezium library
- `db2jcc4.jar` - IBM Db2 JDBC driver (for IBM i)
- Other dependencies (automatically included in plugin package)

**Note:** The connector class `io.debezium.connector.db2.Db2Connector` is the correct connector for IBM i systems. It is configured with IBM i-specific parameters like `database.journal.library` to work with AS400.

## Troubleshooting

### Issue: Connector plugin not found

**Solution:**
1. Verify the plugin directory is in the correct location
2. Check `CONNECT_PLUGIN_PATH` environment variable
3. Ensure JARs are in the plugin directory (not nested)
4. Restart Kafka Connect

### Issue: ClassNotFoundException

**Solution:**
1. Ensure all required JARs are present
2. Check that the Db2 JDBC driver is included
3. Verify plugin path configuration

### Issue: Connection errors

**Solution:**
1. Verify AS400 connection details
2. Check network connectivity
3. Ensure journaling is enabled on AS400
4. Verify user permissions

## Quick Installation Script

Save this as `install_debezium_db2.sh`:

```bash
#!/bin/bash

echo "Installing Debezium Db2 Connector..."

# Find Kafka Connect container
CONTAINER_NAME=$(docker ps | grep connect | awk '{print $1}' | head -1)

if [ -z "$CONTAINER_NAME" ]; then
    echo "❌ Kafka Connect container not found"
    exit 1
fi

echo "Found container: $CONTAINER_NAME"

# Download connector
cd /tmp
wget -q https://repo1.maven.org/maven2/io/debezium/debezium-connector-db2/2.5.0.Final/debezium-connector-db2-2.5.0.Final-plugin.tar.gz
tar -xzf debezium-connector-db2-2.5.0.Final-plugin.tar.gz

# Copy to container
docker cp debezium-connector-db2-2.5.0.Final-plugin $CONTAINER_NAME:/kafka/connect/debezium-connector-db2

# Restart container
echo "Restarting Kafka Connect..."
docker restart $CONTAINER_NAME

echo "✅ Installation complete!"
echo "Waiting for Kafka Connect to start..."
sleep 15

# Verify
echo "Verifying installation..."
curl -s http://localhost:8083/connector-plugins | grep -i db2 && echo "✅ Db2 connector found!" || echo "❌ Db2 connector not found"
```

Make it executable and run:
```bash
chmod +x install_debezium_db2.sh
./install_debezium_db2.sh
```

## Alternative: Manual JAR Installation

If the plugin package doesn't work, you can manually install JARs:

1. **Download required JARs:**
   ```bash
   mkdir -p /tmp/db2-connector
   cd /tmp/db2-connector
   
   # Download Debezium Db2 connector
   wget https://repo1.maven.org/maven2/io/debezium/debezium-connector-db2/2.5.0.Final/debezium-connector-db2-2.5.0.Final.jar
   
   # Download Debezium core
   wget https://repo1.maven.org/maven2/io/debezium/debezium-core/2.5.0.Final/debezium-core-2.5.0.Final.jar
   
   # Download Db2 JDBC driver (you may need to get this from IBM)
   # Or use the one from your AS400 installation
   ```

2. **Copy to container:**
   ```bash
   CONTAINER_NAME=$(docker ps | grep connect | awk '{print $1}' | head -1)
   docker cp debezium-connector-db2-2.5.0.Final.jar $CONTAINER_NAME:/usr/share/confluent-hub-components/
   docker cp debezium-core-2.5.0.Final.jar $CONTAINER_NAME:/usr/share/confluent-hub-components/
   docker restart $CONTAINER_NAME
   ```

## Notes

- The connector version should match your Debezium version (if using other Debezium connectors)
- Latest stable version: 2.5.0.Final (as of this writing)
- Check for newer versions at: https://repo1.maven.org/maven2/io/debezium/debezium-connector-db2/
- After installation, restart Kafka Connect to load the new plugin

## Important Notes for IBM i/AS400

**The Db2 connector IS the connector for IBM i:**
- Connector class: `io.debezium.connector.db2.Db2Connector`
- This same connector works for both Db2 on z/OS and IBM i (AS400)
- IBM i-specific configuration is done via connection parameters:
  - `database.journal.library` - Journal library name
  - `database.dbname` - Library name
  - `database.hostname` - AS400 hostname
  - `database.port` - AS400 port (default: 446)

**There is no separate "IBM i connector"** - the Db2 connector handles both.

## References

- Debezium Db2 Connector Documentation: https://debezium.io/documentation/reference/stable/connectors/db2.html
- IBM i Configuration: https://debezium.io/documentation/reference/stable/connectors/db2.html#db2-connector-configuration-properties
- Maven Repository: https://repo1.maven.org/maven2/io/debezium/debezium-connector-db2/
- Installation Guide: https://debezium.io/documentation/reference/stable/install.html

