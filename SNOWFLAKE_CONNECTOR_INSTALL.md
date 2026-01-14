# Snowflake Kafka Connector Installation Guide

## Step 1: Python Package ✅ COMPLETED

The Python package `snowflake-connector-python` has been successfully installed.

## Step 2: Kafka Connect Connector Installation

### Option A: Automated Installation (Recommended)

Run the installation script on your VPS:

```bash
# SSH into your VPS
ssh root@72.61.233.209

# First, find the correct plugins directory
docker exec kafka-connect-cdc find /usr -name '*s3*connector*.jar' 2>/dev/null | head -1

# This will show you where connectors are installed, for example:
# /usr/share/confluent-hub-components/confluentinc-kafka-connect-s3/lib/kafka-connect-s3-10.0.0.jar
# The plugins directory would be: /usr/share/confluent-hub-components

# Then download and install Snowflake connector
CONNECTOR_VERSION="1.11.0"
PLUGINS_DIR="/usr/share/confluent-hub-components"  # Use the directory found above

# Create directory for Snowflake connector
docker exec kafka-connect-cdc mkdir -p ${PLUGINS_DIR}/snowflake-kafka-connector

# Download the connector
docker exec kafka-connect-cdc wget -O ${PLUGINS_DIR}/snowflake-kafka-connector/snowflake-kafka-connector-${CONNECTOR_VERSION}.jar \
  https://repo1.maven.org/maven2/com/snowflake/snowflake-kafka-connector/${CONNECTOR_VERSION}/snowflake-kafka-connector-${CONNECTOR_VERSION}.jar

# Verify download
docker exec kafka-connect-cdc ls -lh ${PLUGINS_DIR}/snowflake-kafka-connector/

# Restart Kafka Connect
docker restart kafka-connect-cdc

# Wait for restart (30 seconds)
sleep 30

# Verify installation
docker exec kafka-connect-cdc curl -s http://localhost:8083/connector-plugins | grep -i snowflake
```

### Option B: Manual Installation

1. **Download the Connector JAR**:
   ```bash
   # On your local machine or VPS
   wget https://repo1.maven.org/maven2/com/snowflake/snowflake-kafka-connector/1.11.0/snowflake-kafka-connector-1.11.0.jar
   ```

2. **Find the Plugins Directory**:
   ```bash
   # SSH into VPS
   ssh root@72.61.233.209
   
   # Find where existing connectors are installed
   docker exec kafka-connect-cdc find /usr -name '*s3*connector*.jar' 2>/dev/null
   
   # Common locations:
   # - /usr/share/confluent-hub-components/
   # - /usr/share/java/plugins/
   # - /usr/local/share/kafka/plugins/
   ```

3. **Copy JAR to Container**:
   ```bash
   # If you downloaded on local machine, copy to VPS first
   scp snowflake-kafka-connector-1.11.0.jar root@72.61.233.209:/tmp/
   
   # Then copy into container (replace PLUGINS_DIR with actual directory)
   docker cp /tmp/snowflake-kafka-connector-1.11.0.jar kafka-connect-cdc:/usr/share/confluent-hub-components/snowflake-kafka-connector/
   ```

4. **Restart Kafka Connect**:
   ```bash
   docker restart kafka-connect-cdc
   ```

5. **Verify Installation**:
   ```bash
   # Wait 30 seconds for restart
   sleep 30
   
   # Check if connector is available
   docker exec kafka-connect-cdc curl -s http://localhost:8083/connector-plugins | grep -i snowflake
   ```

### Option C: Using Confluent Hub (if available)

If your Kafka Connect has Confluent Hub installed:

```bash
docker exec kafka-connect-cdc confluent-hub install snowflakeinc/snowflake-kafka-connector:latest
docker restart kafka-connect-cdc
```

## Verification

After installation, verify the connector is available:

```bash
# Check connector plugins
docker exec kafka-connect-cdc curl -s http://localhost:8083/connector-plugins | jq '.[] | select(.class | contains("Snowflake"))'

# Or using grep
docker exec kafka-connect-cdc curl -s http://localhost:8083/connector-plugins | grep -i snowflake
```

You should see output like:
```json
{
  "class": "com.snowflake.kafka.connector.SnowflakeSinkConnector",
  "type": "sink",
  "version": "1.11.0"
}
```

## Troubleshooting

### Connector Not Found

1. **Check Logs**:
   ```bash
   docker logs kafka-connect-cdc | tail -100 | grep -i snowflake
   ```

2. **Verify JAR Location**:
   ```bash
   docker exec kafka-connect-cdc find /usr -name 'snowflake-kafka-connector*.jar'
   ```

3. **Check Plugin Path**:
   ```bash
   docker exec kafka-connect-cdc env | grep -i plugin
   ```

### Permission Denied

If you get permission errors, try:
```bash
# Check container user
docker exec kafka-connect-cdc whoami

# Try with root user
docker exec -u root kafka-connect-cdc mkdir -p /path/to/plugins
```

### Download Fails

If wget fails inside container:
1. Download on VPS host
2. Copy into container using `docker cp`

## Next Steps

Once the connector is installed:

1. ✅ Python package installed
2. ✅ Kafka Connect connector installed
3. Create Snowflake connection in the CDC application UI
4. Create a pipeline with Snowflake as target
5. Start the pipeline and verify data flow

## Connector Information

- **Connector Class**: `com.snowflake.kafka.connector.SnowflakeSinkConnector`
- **Latest Version**: 1.11.0
- **Download URL**: https://repo1.maven.org/maven2/com/snowflake/snowflake-kafka-connector/1.11.0/snowflake-kafka-connector-1.11.0.jar
- **Documentation**: https://docs.snowflake.com/en/user-guide/kafka-connector.html



