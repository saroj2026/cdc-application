# Install SQL Server JDBC Sink Connector

## Why Needed

To write data from Kafka topics to SQL Server, you need:
1. **Confluent JDBC Sink Connector** - Generic JDBC sink connector
2. **SQL Server JDBC Driver** - Microsoft's JDBC driver for SQL Server

## Installation Steps

### On VPS Server (72.61.233.209)

```bash
# Step 1: Download JDBC Sink Connector
cd /tmp
wget https://repo1.maven.org/maven2/io/confluent/kafka-connect-jdbc/10.7.4/kafka-connect-jdbc-10.7.4.jar

# Step 2: Download SQL Server JDBC Driver
wget https://repo1.maven.org/maven2/com/microsoft/sqlserver/mssql-jdbc/12.4.2.jre8/mssql-jdbc-12.4.2.jre8.jar

# Step 3: Copy to Kafka Connect
docker cp kafka-connect-jdbc-10.7.4.jar kafka-connect-cdc:/kafka/connect/
docker cp mssql-jdbc-12.4.2.jre8.jar kafka-connect-cdc:/kafka/connect/

# Step 4: Restart
docker restart kafka-connect-cdc
sleep 60

# Step 5: Verify
curl http://localhost:8083/connector-plugins | grep -i jdbc
```

## Quick Install Script

Save as `install_sqlserver_sink.sh`:

```bash
#!/bin/bash
set -e

echo "Installing SQL Server JDBC Sink Connector..."

cd /tmp

# Download JDBC connector
wget https://repo1.maven.org/maven2/io/confluent/kafka-connect-jdbc/10.7.4/kafka-connect-jdbc-10.7.4.jar

# Download SQL Server driver
wget https://repo1.maven.org/maven2/com/microsoft/sqlserver/mssql-jdbc/12.4.2.jre8/mssql-jdbc-12.4.2.jre8.jar

# Copy to container
docker cp kafka-connect-jdbc-10.7.4.jar kafka-connect-cdc:/kafka/connect/
docker cp mssql-jdbc-12.4.2.jre8.jar kafka-connect-cdc:/kafka/connect/

# Restart
docker restart kafka-connect-cdc
sleep 60

# Verify
curl -s http://localhost:8083/connector-plugins | grep -i "JdbcSinkConnector" && echo "✅ JDBC Sink connector installed!" || echo "⚠️  Check installation"

echo "Done!"
```

## After Installation

The SQL Server sink connector will be available as:
- Class: `io.confluent.connect.jdbc.JdbcSinkConnector`
- Type: `sink`

Your pipeline will automatically use this when the target is SQL Server.


## Why Needed

To write data from Kafka topics to SQL Server, you need:
1. **Confluent JDBC Sink Connector** - Generic JDBC sink connector
2. **SQL Server JDBC Driver** - Microsoft's JDBC driver for SQL Server

## Installation Steps

### On VPS Server (72.61.233.209)

```bash
# Step 1: Download JDBC Sink Connector
cd /tmp
wget https://repo1.maven.org/maven2/io/confluent/kafka-connect-jdbc/10.7.4/kafka-connect-jdbc-10.7.4.jar

# Step 2: Download SQL Server JDBC Driver
wget https://repo1.maven.org/maven2/com/microsoft/sqlserver/mssql-jdbc/12.4.2.jre8/mssql-jdbc-12.4.2.jre8.jar

# Step 3: Copy to Kafka Connect
docker cp kafka-connect-jdbc-10.7.4.jar kafka-connect-cdc:/kafka/connect/
docker cp mssql-jdbc-12.4.2.jre8.jar kafka-connect-cdc:/kafka/connect/

# Step 4: Restart
docker restart kafka-connect-cdc
sleep 60

# Step 5: Verify
curl http://localhost:8083/connector-plugins | grep -i jdbc
```

## Quick Install Script

Save as `install_sqlserver_sink.sh`:

```bash
#!/bin/bash
set -e

echo "Installing SQL Server JDBC Sink Connector..."

cd /tmp

# Download JDBC connector
wget https://repo1.maven.org/maven2/io/confluent/kafka-connect-jdbc/10.7.4/kafka-connect-jdbc-10.7.4.jar

# Download SQL Server driver
wget https://repo1.maven.org/maven2/com/microsoft/sqlserver/mssql-jdbc/12.4.2.jre8/mssql-jdbc-12.4.2.jre8.jar

# Copy to container
docker cp kafka-connect-jdbc-10.7.4.jar kafka-connect-cdc:/kafka/connect/
docker cp mssql-jdbc-12.4.2.jre8.jar kafka-connect-cdc:/kafka/connect/

# Restart
docker restart kafka-connect-cdc
sleep 60

# Verify
curl -s http://localhost:8083/connector-plugins | grep -i "JdbcSinkConnector" && echo "✅ JDBC Sink connector installed!" || echo "⚠️  Check installation"

echo "Done!"
```

## After Installation

The SQL Server sink connector will be available as:
- Class: `io.confluent.connect.jdbc.JdbcSinkConnector`
- Type: `sink`

Your pipeline will automatically use this when the target is SQL Server.

