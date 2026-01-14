# Install Oracle Connector - Quick Guide

## Current Status

✅ **Backend Code**: Complete
✅ **Python Driver**: Installed (oracledb 3.4.1)
✅ **Database Enum**: Oracle added
❌ **Kafka Connect Plugin**: **NOT INSTALLED** (needs to be done on server)

## Installation Required

The Oracle connector is **NOT** in the plugin list at http://72.61.233.209:8083/connector-plugins

You need to install it on the server.

## Quick Installation (Run on Server)

**SSH into the server and run this ONE command:**

```bash
docker exec 28b9a11e27bb bash -c "
    cd /usr/share/confluent-hub-components && \
    mkdir -p debezium-connector-oracle && \
    cd debezium-connector-oracle && \
    wget -q https://repo1.maven.org/maven2/io/debezium/debezium-connector-oracle/2.5.0.Final/debezium-connector-oracle-2.5.0.Final-plugin.tar.gz && \
    tar -xzf debezium-connector-oracle-2.5.0.Final-plugin.tar.gz && \
    rm debezium-connector-oracle-2.5.0.Final-plugin.tar.gz && \
    echo 'Installation complete'
" && docker restart 28b9a11e27bb
```

**Wait 30 seconds, then verify:**

```bash
sleep 30
curl http://72.61.233.209:8083/connector-plugins | grep -i oracle
```

## Alternative: Use Installation Script

1. **Copy script to server:**
   ```bash
   scp install_oracle_connector_direct.sh root@72.61.233.209:/tmp/
   ```

2. **SSH and run:**
   ```bash
   ssh root@72.61.233.209
   chmod +x /tmp/install_oracle_connector_direct.sh
   /tmp/install_oracle_connector_direct.sh
   ```

## Verification

After installation, check:

```bash
curl http://72.61.233.209:8083/connector-plugins | python3 -m json.tool | grep -i oracle
```

**Expected output:**
```json
{
  "class": "io.debezium.connector.oracle.OracleConnector",
  "type": "source",
  "version": "2.5.0.Final"
}
```

## Troubleshooting

If Oracle connector doesn't appear:

1. **Check if JAR files are present:**
   ```bash
   docker exec 28b9a11e27bb ls -la /usr/share/confluent-hub-components/debezium-connector-oracle/
   ```

2. **Check Kafka Connect logs:**
   ```bash
   docker logs 28b9a11e27bb | grep -i oracle | tail -20
   docker logs 28b9a11e27bb | grep -i error | tail -20
   ```

3. **Verify plugin path:**
   ```bash
   docker exec 28b9a11e27bb env | grep PLUGIN
   ```

4. **Restart container again:**
   ```bash
   docker restart 28b9a11e27bb
   sleep 30
   ```

## Current Plugin List

From http://72.61.233.209:8083/connector-plugins:

**Debezium Connectors Available:**
- ✅ `io.debezium.connector.postgresql.PostgresConnector` (2.5.0.Final)
- ✅ `io.debezium.connector.sqlserver.SqlServerConnector` (2.5.0.Final)
- ✅ `io.debezium.connector.db2.Db2Connector` (2.5.0.Final)
- ✅ `io.debezium.connector.db2as400.As400RpcConnector` (2.6.0.Final)
- ❌ `io.debezium.connector.oracle.OracleConnector` - **MISSING**

**After installation, Oracle connector should appear in this list.**

## Summary

**Action Required:** Install Debezium Oracle Connector JAR on server
**Command:** See "Quick Installation" above
**Time:** ~2-3 minutes (download + restart)
**Verification:** Check connector-plugins endpoint

Once installed, Oracle → Snowflake pipelines will work! 🎉

