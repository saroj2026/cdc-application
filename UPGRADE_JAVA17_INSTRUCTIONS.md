# Upgrade Kafka Connect to Java 17 - Instructions

## Quick Start

Run the upgrade script:
```bash
cd /Users/kumargaurav/Desktop/CDCTEAM/cdcteam/seg-cdc-application
./upgrade_kafka_connect_to_java17.sh
```

## Manual Steps (if script doesn't work)

### 1. Connect to VPS
```bash
ssh root@72.61.233.209
# Password: segmbp@1100
```

### 2. Install Java 17
```bash
docker exec kafka-connect-cdc apt-get update
docker exec kafka-connect-cdc apt-get install -y openjdk-17-jdk-headless
```

### 3. Set Java 17 as Default
```bash
docker exec kafka-connect-cdc update-alternatives --install /usr/bin/java java /usr/lib/jvm/java-17-openjdk-amd64/bin/java 1
docker exec kafka-connect-cdc update-alternatives --set java /usr/lib/jvm/java-17-openjdk-amd64/bin/java
```

### 4. Configure JAVA_HOME
```bash
docker exec kafka-connect-cdc sh -c 'echo "export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64" >> /etc/profile'
docker exec kafka-connect-cdc sh -c 'echo "export PATH=$JAVA_HOME/bin:$PATH" >> /etc/profile'
```

### 5. Verify Java 17
```bash
docker exec kafka-connect-cdc java -version
# Should show: openjdk version "17.x.x"
```

### 6. Restart Kafka Connect
```bash
docker restart kafka-connect-cdc
```

### 7. Wait and Verify
```bash
# Wait 70 seconds
sleep 70

# Check Java version
docker exec kafka-connect-cdc java -version

# Check if IBM i connector loads
docker logs kafka-connect-cdc | grep "Added plugin.*As400RpcConnector"

# Check via API
curl http://localhost:8083/connector-plugins | grep -i "As400RpcConnector"
```

## Verification Checklist

After upgrade, verify:

- [ ] Java 17 is active: `docker exec kafka-connect-cdc java -version`
- [ ] Kafka Connect is running: `docker ps | grep kafka-connect-cdc`
- [ ] IBM i connector loads: Check logs for "Added plugin.*As400RpcConnector"
- [ ] Existing connectors still work:
  - DB2 connector
  - PostgreSQL connector
  - SQL Server connector
  - JDBC sink
  - S3 sink
- [ ] No errors in logs: `docker logs kafka-connect-cdc | grep -i error`

## Rollback (if needed)

If issues occur:

```bash
# Revert to Java 11
docker exec kafka-connect-cdc update-alternatives --set java /usr/lib/jvm/zulu11-ca-amd64/bin/java

# Restart
docker restart kafka-connect-cdc
```

## Expected Results

✅ **Java 17 active**
✅ **IBM i connector (As400RpcConnector) loads successfully**
✅ **All existing connectors continue to work**
✅ **No errors in logs**

## Troubleshooting

### Issue: Java 17 not active after restart
**Solution:** The container may reset. Check if JAVA_HOME is set in the startup script.

### Issue: Connectors not loading
**Solution:** Check logs for specific errors. Verify all JAR files are present.

### Issue: Existing connectors broken
**Solution:** Rollback to Java 11 (see Rollback section above).

## Support

If you encounter issues:
1. Check Kafka Connect logs: `docker logs kafka-connect-cdc`
2. Verify connector files: `docker exec kafka-connect-cdc ls -la /usr/share/java/plugins/debezium-connector-ibmi/`
3. Check Java version: `docker exec kafka-connect-cdc java -version`

