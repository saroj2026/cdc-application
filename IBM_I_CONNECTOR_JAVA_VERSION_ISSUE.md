# IBM i Connector Java Version Compatibility Issue

## Problem

The Debezium IBM i Connector 2.6.0.Final is not loading in Kafka Connect 7.4.0.

## Root Cause

**Java Version Incompatibility:**

- **Debezium 2.6.0.Final** was compiled with **Java 17** (class file version 61.0)
- **Kafka Connect 7.4.0** is running on **Java 11** (class file version 55.0)

Error message:
```
java.lang.UnsupportedClassVersionError: 
io/debezium/connector/db2as400/As400RpcConnector has been compiled by a more recent 
version of the Java Runtime (class file version 61.0), this version of the Java 
Runtime only recognizes class file versions up to 55.0
```

## Solution

Use **Debezium IBM i Connector 2.5.0.Final** which is compatible with Java 11.

### Steps to Fix

1. **Download Debezium 2.5.0.Final:**
   ```bash
   wget https://repo1.maven.org/maven2/io/debezium/debezium-connector-ibmi/2.5.0.Final/debezium-connector-ibmi-2.5.0.Final-plugin.tar.gz
   ```

2. **Extract the connector:**
   ```bash
   tar -xzf debezium-connector-ibmi-2.5.0.Final-plugin.tar.gz
   ```

3. **Remove the 2.6.0.Final version from the container:**
   ```bash
   docker exec kafka-connect-cdc rm -rf /usr/share/java/plugins/debezium-connector-ibmi
   ```

4. **Copy the 2.5.0.Final version to the container:**
   ```bash
   docker cp debezium-connector-ibmi-2.5.0.Final/debezium-connector-ibmi kafka-connect-cdc:/usr/share/java/plugins/
   ```

5. **Ensure jt400.jar is present:**
   ```bash
   docker exec kafka-connect-cdc sh -c 'cd /usr/share/java/plugins/debezium-connector-ibmi && ls -la jt400*'
   ```
   If `jt400.jar` is missing, copy it from the 2.6.0.Final version or download it separately.

6. **Restart Kafka Connect:**
   ```bash
   docker restart kafka-connect-cdc
   ```

7. **Verify the connector loads:**
   ```bash
   curl http://localhost:8083/connector-plugins | grep -i "As400RpcConnector"
   ```

## Alternative Solutions

### Option 1: Upgrade Kafka Connect to Java 17
- Requires changing the Docker image or Java version in the container
- More complex and may affect other connectors

### Option 2: Use Debezium 2.5.0.Final (Recommended)
- Simple drop-in replacement
- Maintains compatibility with existing setup
- No changes to Kafka Connect required

## Verification

After installing 2.5.0.Final, check the logs:
```bash
docker logs kafka-connect-cdc | grep -i "Added plugin.*As400RpcConnector"
```

You should see:
```
INFO Added plugin 'io.debezium.connector.db2as400.As400RpcConnector'
```

## Required JARs

The plugin directory must contain:
- `debezium-connector-ibmi-2.5.0.Final.jar`
- `debezium-api-2.5.0.Final.jar`
- `debezium-core-2.5.0.Final.jar`
- `ibmi-journal-parsing-2.5.0.Final.jar`
- `jt400.jar` (IBM Toolbox for Java) - **MANDATORY**
- `jt400-override-ccsid-2.5.0.Final.jar` (if available)

## Notes

- The `jt400.jar` file is mandatory for the connector to function
- Ensure all JARs are in the same directory: `/usr/share/java/plugins/debezium-connector-ibmi/`
- The service file `META-INF/services/org.apache.kafka.connect.source.SourceConnector` should list:
  - `io.debezium.connector.db2as400.As400JdbcConnector`
  - `io.debezium.connector.db2as400.As400RpcConnector`

