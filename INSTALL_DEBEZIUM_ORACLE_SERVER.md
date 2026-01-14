# Install Debezium Oracle Connector on Kafka Connect Server

## Server Details
- **Host**: 72.61.233.209
- **Port**: 8083 (Kafka Connect REST API)
- **Container ID**: 28b9a11e27bb (from previous checks)

## Installation Steps

### Option 1: Using the Installation Script (Recommended)

1. **Copy script to server:**
   ```bash
   scp install_debezium_oracle_connector.sh root@72.61.233.209:/tmp/
   ```

2. **SSH and run:**
   ```bash
   ssh root@72.61.233.209
   chmod +x /tmp/install_debezium_oracle_connector.sh
   /tmp/install_debezium_oracle_connector.sh
   ```

3. **Restart Kafka Connect:**
   ```bash
   docker restart 28b9a11e27bb
   ```

### Option 2: Manual Installation via Docker

1. **SSH into server:**
   ```bash
   ssh root@72.61.233.209
   ```

2. **Find Kafka Connect plugins directory:**
   ```bash
   docker exec 28b9a11e27bb ls -la /usr/share/confluent-hub-components
   # Or check other common locations:
   docker exec 28b9a11e27bb find / -name "debezium-connector-postgresql*" 2>/dev/null | head -1
   ```

3. **Download and install connector:**
   ```bash
   # Get into container
   docker exec -it 28b9a11e27bb bash
   
   # Inside container:
   cd /usr/share/confluent-hub-components
   mkdir -p debezium-connector-oracle
   cd debezium-connector-oracle
   
   # Download (version 2.5.0.Final)
   wget https://repo1.maven.org/maven2/io/debezium/debezium-connector-oracle/2.5.0.Final/debezium-connector-oracle-2.5.0.Final-plugin.tar.gz
   
   # Extract
   tar -xzf debezium-connector-oracle-2.5.0.Final-plugin.tar.gz
   rm debezium-connector-oracle-2.5.0.Final-plugin.tar.gz
   
   # Verify
   ls -la
   exit
   ```

4. **Restart container:**
   ```bash
   docker restart 28b9a11e27bb
   ```

### Option 3: Copy from Local (if you have the JAR)

1. **Download connector locally:**
   - Visit: https://repo1.maven.org/maven2/io/debezium/debezium-connector-oracle/2.5.0.Final/
   - Download: `debezium-connector-oracle-2.5.0.Final-plugin.tar.gz`

2. **Copy to server:**
   ```bash
   scp debezium-connector-oracle-2.5.0.Final-plugin.tar.gz root@72.61.233.209:/tmp/
   ```

3. **SSH and extract:**
   ```bash
   ssh root@72.61.233.209
   
   # Find plugins directory
   PLUGINS_DIR=$(docker exec 28b9a11e27bb find / -name "debezium-connector-postgresql*" 2>/dev/null | head -1 | xargs dirname)
   echo "Plugins directory: $PLUGINS_DIR"
   
   # Create connector directory
   docker exec 28b9a11e27bb mkdir -p $PLUGINS_DIR/debezium-connector-oracle
   
   # Copy and extract
   docker cp /tmp/debezium-connector-oracle-2.5.0.Final-plugin.tar.gz 28b9a11e27bb:/tmp/
   docker exec 28b9a11e27bb bash -c "cd $PLUGINS_DIR/debezium-connector-oracle && tar -xzf /tmp/debezium-connector-oracle-2.5.0.Final-plugin.tar.gz && rm /tmp/debezium-connector-oracle-2.5.0.Final-plugin.tar.gz"
   
   # Restart
   docker restart 28b9a11e27bb
   ```

## Verification

After installation, verify the connector is available:

```bash
# Check connector plugins
curl http://72.61.233.209:8083/connector-plugins | python3 -m json.tool | grep -i oracle

# Should return:
# {
#   "class": "io.debezium.connector.oracle.OracleConnector",
#   "type": "source",
#   "version": "2.5.0.Final"
# }
```

Or check via Python:

```python
import requests
response = requests.get("http://72.61.233.209:8083/connector-plugins")
plugins = response.json()
oracle_plugins = [p for p in plugins if 'oracle' in p.get('class', '').lower()]
print("Oracle connectors:", oracle_plugins)
```

## Troubleshooting

### Connector Not Found

1. **Check if JAR is in plugins directory:**
   ```bash
   docker exec 28b9a11e27bb find /usr/share/confluent-hub-components -name "*oracle*.jar"
   ```

2. **Check Kafka Connect logs:**
   ```bash
   docker logs 28b9a11e27bb | grep -i oracle
   docker logs 28b9a11e27bb | grep -i error | tail -20
   ```

3. **Verify plugins directory is correct:**
   ```bash
   docker exec 28b9a11e27bb env | grep PLUGIN
   ```

### Missing Oracle JDBC Driver

The connector package should include `ojdbc8.jar` or `ojdbc11.jar`. If missing:

1. Download from Oracle: https://www.oracle.com/database/technologies/appdev/jdbc-downloads.html
2. Copy to connector directory:
   ```bash
   docker cp ojdbc8.jar 28b9a11e27bb:/usr/share/confluent-hub-components/debezium-connector-oracle/
   docker restart 28b9a11e27bb
   ```

## Quick Installation Command

```bash
# One-liner to install (run on server)
docker exec 28b9a11e27bb bash -c "cd /usr/share/confluent-hub-components && mkdir -p debezium-connector-oracle && cd debezium-connector-oracle && wget -q https://repo1.maven.org/maven2/io/debezium/debezium-connector-oracle/2.5.0.Final/debezium-connector-oracle-2.5.0.Final-plugin.tar.gz && tar -xzf debezium-connector-oracle-2.5.0.Final-plugin.tar.gz && rm debezium-connector-oracle-2.5.0.Final-plugin.tar.gz && echo 'Installation complete' && docker restart 28b9a11e27bb"
```

