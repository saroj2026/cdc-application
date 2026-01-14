# Install Debezium PostgreSQL Connector

## Problem

Kafka Connect is missing the Debezium PostgreSQL connector. The error shows:
```
Failed to find any class that implements Connector and which name matches 
io.debezium.connector.postgresql.PostgresConnector
```

## Solution: Install Debezium PostgreSQL Connector

### Step 1: Download Debezium PostgreSQL Connector

On your VPS server (72.61.233.209), download the Debezium PostgreSQL connector:

```bash
# SSH to VPS
ssh root@72.61.233.209

# Navigate to where you want to store connectors
cd /opt/cdc3

# Download Debezium PostgreSQL connector (version 2.5 - matches your Debezium Connect version)
wget https://repo1.maven.org/maven2/io/debezium/debezium-connector-postgres/2.5.0.Final/debezium-connector-postgres-2.5.0.Final-plugin.tar.gz

# Extract it
tar -xzf debezium-connector-postgres-2.5.0.Final-plugin.tar.gz
```

### Step 2: Copy to Kafka Connect Container

```bash
# Copy the connector JARs to Kafka Connect
docker cp debezium-connector-postgres-2.5.0.Final-plugin/. kafka-connect-cdc:/kafka/connect/

# Or if you have a specific plugin path, use that:
# docker cp debezium-connector-postgres-2.5.0.Final-plugin/. kafka-connect-cdc:/usr/share/confluent-hub-components/
```

### Step 3: Restart Kafka Connect

```bash
docker restart kafka-connect-cdc

# Wait for it to start (30-60 seconds)
sleep 60
```

### Step 4: Verify Installation

```bash
# Check if connector is available
curl http://localhost:8083/connector-plugins | grep -i debezium

# Or check from your local machine:
curl http://72.61.233.209:8083/connector-plugins | python3 -m json.tool | grep -i postgres
```

You should see:
```json
{
  "class": "io.debezium.connector.postgresql.PostgresConnector",
  "type": "source",
  "version": "2.5.0.Final"
}
```

## Alternative: Using Confluent Hub (if available)

If your Kafka Connect has Confluent Hub installed:

```bash
# Enter the container
docker exec -it kafka-connect-cdc bash

# Install via Confluent Hub
confluent-hub install debezium/debezium-connector-postgresql:2.5.0

# Exit and restart
exit
docker restart kafka-connect-cdc
```

## Also Check: SQL Server Sink Connector

For writing to SQL Server, you may also need the JDBC Sink Connector:

```bash
# Download Confluent JDBC Sink Connector
wget https://repo1.maven.org/maven2/io/confluent/kafka-connect-jdbc/10.7.4/kafka-connect-jdbc-10.7.4.jar

# Copy to Kafka Connect
docker cp kafka-connect-jdbc-10.7.4.jar kafka-connect-cdc:/kafka/connect/

# Also need SQL Server JDBC driver
wget https://repo1.maven.org/maven2/com/microsoft/sqlserver/mssql-jdbc/12.4.2.jre8/mssql-jdbc-12.4.2.jre8.jar
docker cp mssql-jdbc-12.4.2.jre8.jar kafka-connect-cdc:/kafka/connect/

# Restart
docker restart kafka-connect-cdc
```

## Quick Install Script

Save this as `install_debezium_postgres.sh` on your VPS:

```bash
#!/bin/bash
set -e

echo "Installing Debezium PostgreSQL Connector..."

# Download
cd /tmp
wget https://repo1.maven.org/maven2/io/debezium/debezium-connector-postgres/2.5.0.Final/debezium-connector-postgres-2.5.0.Final-plugin.tar.gz
tar -xzf debezium-connector-postgres-2.5.0.Final-plugin.tar.gz

# Copy to container
docker cp debezium-connector-postgres-2.5.0.Final-plugin/. kafka-connect-cdc:/kafka/connect/

# Restart
echo "Restarting Kafka Connect..."
docker restart kafka-connect-cdc

echo "Waiting 60 seconds for Kafka Connect to start..."
sleep 60

# Verify
echo "Verifying installation..."
curl -s http://localhost:8083/connector-plugins | grep -i "PostgresConnector" && echo "✅ Debezium PostgreSQL connector installed!" || echo "❌ Installation may have failed"

echo "Done!"
```

Run it:
```bash
chmod +x install_debezium_postgres.sh
./install_debezium_postgres.sh
```

## After Installation

Once Debezium PostgreSQL connector is installed, retry starting the pipeline:

```bash
python create_and_start_final_test.py
```

The pipeline should now be able to:
1. ✅ Run full load (PostgreSQL → SQL Server)
2. ✅ Create Debezium connector (capture PostgreSQL changes)
3. ✅ Create SQL Server sink connector (write changes to SQL Server)
4. ✅ Start CDC streaming


## Problem

Kafka Connect is missing the Debezium PostgreSQL connector. The error shows:
```
Failed to find any class that implements Connector and which name matches 
io.debezium.connector.postgresql.PostgresConnector
```

## Solution: Install Debezium PostgreSQL Connector

### Step 1: Download Debezium PostgreSQL Connector

On your VPS server (72.61.233.209), download the Debezium PostgreSQL connector:

```bash
# SSH to VPS
ssh root@72.61.233.209

# Navigate to where you want to store connectors
cd /opt/cdc3

# Download Debezium PostgreSQL connector (version 2.5 - matches your Debezium Connect version)
wget https://repo1.maven.org/maven2/io/debezium/debezium-connector-postgres/2.5.0.Final/debezium-connector-postgres-2.5.0.Final-plugin.tar.gz

# Extract it
tar -xzf debezium-connector-postgres-2.5.0.Final-plugin.tar.gz
```

### Step 2: Copy to Kafka Connect Container

```bash
# Copy the connector JARs to Kafka Connect
docker cp debezium-connector-postgres-2.5.0.Final-plugin/. kafka-connect-cdc:/kafka/connect/

# Or if you have a specific plugin path, use that:
# docker cp debezium-connector-postgres-2.5.0.Final-plugin/. kafka-connect-cdc:/usr/share/confluent-hub-components/
```

### Step 3: Restart Kafka Connect

```bash
docker restart kafka-connect-cdc

# Wait for it to start (30-60 seconds)
sleep 60
```

### Step 4: Verify Installation

```bash
# Check if connector is available
curl http://localhost:8083/connector-plugins | grep -i debezium

# Or check from your local machine:
curl http://72.61.233.209:8083/connector-plugins | python3 -m json.tool | grep -i postgres
```

You should see:
```json
{
  "class": "io.debezium.connector.postgresql.PostgresConnector",
  "type": "source",
  "version": "2.5.0.Final"
}
```

## Alternative: Using Confluent Hub (if available)

If your Kafka Connect has Confluent Hub installed:

```bash
# Enter the container
docker exec -it kafka-connect-cdc bash

# Install via Confluent Hub
confluent-hub install debezium/debezium-connector-postgresql:2.5.0

# Exit and restart
exit
docker restart kafka-connect-cdc
```

## Also Check: SQL Server Sink Connector

For writing to SQL Server, you may also need the JDBC Sink Connector:

```bash
# Download Confluent JDBC Sink Connector
wget https://repo1.maven.org/maven2/io/confluent/kafka-connect-jdbc/10.7.4/kafka-connect-jdbc-10.7.4.jar

# Copy to Kafka Connect
docker cp kafka-connect-jdbc-10.7.4.jar kafka-connect-cdc:/kafka/connect/

# Also need SQL Server JDBC driver
wget https://repo1.maven.org/maven2/com/microsoft/sqlserver/mssql-jdbc/12.4.2.jre8/mssql-jdbc-12.4.2.jre8.jar
docker cp mssql-jdbc-12.4.2.jre8.jar kafka-connect-cdc:/kafka/connect/

# Restart
docker restart kafka-connect-cdc
```

## Quick Install Script

Save this as `install_debezium_postgres.sh` on your VPS:

```bash
#!/bin/bash
set -e

echo "Installing Debezium PostgreSQL Connector..."

# Download
cd /tmp
wget https://repo1.maven.org/maven2/io/debezium/debezium-connector-postgres/2.5.0.Final/debezium-connector-postgres-2.5.0.Final-plugin.tar.gz
tar -xzf debezium-connector-postgres-2.5.0.Final-plugin.tar.gz

# Copy to container
docker cp debezium-connector-postgres-2.5.0.Final-plugin/. kafka-connect-cdc:/kafka/connect/

# Restart
echo "Restarting Kafka Connect..."
docker restart kafka-connect-cdc

echo "Waiting 60 seconds for Kafka Connect to start..."
sleep 60

# Verify
echo "Verifying installation..."
curl -s http://localhost:8083/connector-plugins | grep -i "PostgresConnector" && echo "✅ Debezium PostgreSQL connector installed!" || echo "❌ Installation may have failed"

echo "Done!"
```

Run it:
```bash
chmod +x install_debezium_postgres.sh
./install_debezium_postgres.sh
```

## After Installation

Once Debezium PostgreSQL connector is installed, retry starting the pipeline:

```bash
python create_and_start_final_test.py
```

The pipeline should now be able to:
1. ✅ Run full load (PostgreSQL → SQL Server)
2. ✅ Create Debezium connector (capture PostgreSQL changes)
3. ✅ Create SQL Server sink connector (write changes to SQL Server)
4. ✅ Start CDC streaming

