# Install S3 Connector - Quick Guide

## Quick Installation

### Option 1: Using Docker Copy (Recommended)

```bash
# From the project root directory
docker cp confluentinc-kafka-connect-s3-11.0.8/confluentinc-kafka-connect-s3-11.0.8/lib/. kafka-connect-cdc:/kafka/connect/

# Restart Kafka Connect
docker restart kafka-connect-cdc

# Wait 30 seconds, then verify
curl http://72.61.233.209:8083/connector-plugins | grep -i s3
```

### Option 2: Using the Script

```bash
# Make script executable (if on Linux/Mac)
chmod +x install_s3_connector.sh

# Run the script
./install_s3_connector.sh
```

### Option 3: Manual Steps

1. **SSH to VPS server** (if you have access):
   ```bash
   ssh user@72.61.233.209
   ```

2. **Copy connector files**:
   ```bash
   # On VPS, copy the lib directory to Kafka Connect
   docker cp /path/to/confluentinc-kafka-connect-s3-11.0.8/confluentinc-kafka-connect-s3-11.0.8/lib/. kafka-connect-cdc:/kafka/connect/
   ```

3. **Restart container**:
   ```bash
   docker restart kafka-connect-cdc
   ```

4. **Verify**:
   ```bash
   curl http://localhost:8083/connector-plugins | grep -i s3
   ```

## What Files Need to be Copied?

**All JAR files** from:
```
confluentinc-kafka-connect-s3-11.0.8/confluentinc-kafka-connect-s3-11.0.8/lib/
```

**Key files include:**
- `kafka-connect-s3-11.0.8.jar` (main connector)
- `kafka-connect-storage-*.jar` (storage libraries)
- AWS SDK JARs
- Other dependencies

## Verification

After installation, verify the connector is available:

```bash
curl http://72.61.233.209:8083/connector-plugins
```

Look for:
```json
{
  "class": "io.confluent.connect.s3.S3SinkConnector",
  "type": "sink",
  "version": "11.0.8"
}
```

## Troubleshooting

### If connector is not found:

1. **Check container logs**:
   ```bash
   docker logs kafka-connect-cdc | tail -50
   ```

2. **Verify JAR files are in the container**:
   ```bash
   docker exec kafka-connect-cdc ls -la /kafka/connect/ | grep s3
   ```

3. **Check plugin path configuration**:
   ```bash
   docker exec kafka-connect-cdc env | grep PLUGIN
   ```

4. **Restart container again**:
   ```bash
   docker restart kafka-connect-cdc
   sleep 60  # Wait longer
   ```

### Common Issues

- **Permission denied**: Make sure Docker has permission to copy files
- **Container not found**: Verify container name is `kafka-connect-cdc`
- **Connector not loading**: Check Kafka Connect logs for errors
- **Class not found**: Ensure all JAR dependencies are copied

## After Installation

Once the connector is installed:

1. ✅ The code is already updated to use S3 sink
2. ✅ Create a pipeline with `mode: "full_load_and_cdc"`
3. ✅ Start the pipeline
4. ✅ Changes will automatically flow to S3!

## Need Help?

If you encounter issues:
1. Check `S3_SINK_SETUP.md` for detailed documentation
2. Review Kafka Connect logs
3. Verify AWS credentials in your S3 connection
4. Test connector manually via Kafka Connect API


## Quick Installation

### Option 1: Using Docker Copy (Recommended)

```bash
# From the project root directory
docker cp confluentinc-kafka-connect-s3-11.0.8/confluentinc-kafka-connect-s3-11.0.8/lib/. kafka-connect-cdc:/kafka/connect/

# Restart Kafka Connect
docker restart kafka-connect-cdc

# Wait 30 seconds, then verify
curl http://72.61.233.209:8083/connector-plugins | grep -i s3
```

### Option 2: Using the Script

```bash
# Make script executable (if on Linux/Mac)
chmod +x install_s3_connector.sh

# Run the script
./install_s3_connector.sh
```

### Option 3: Manual Steps

1. **SSH to VPS server** (if you have access):
   ```bash
   ssh user@72.61.233.209
   ```

2. **Copy connector files**:
   ```bash
   # On VPS, copy the lib directory to Kafka Connect
   docker cp /path/to/confluentinc-kafka-connect-s3-11.0.8/confluentinc-kafka-connect-s3-11.0.8/lib/. kafka-connect-cdc:/kafka/connect/
   ```

3. **Restart container**:
   ```bash
   docker restart kafka-connect-cdc
   ```

4. **Verify**:
   ```bash
   curl http://localhost:8083/connector-plugins | grep -i s3
   ```

## What Files Need to be Copied?

**All JAR files** from:
```
confluentinc-kafka-connect-s3-11.0.8/confluentinc-kafka-connect-s3-11.0.8/lib/
```

**Key files include:**
- `kafka-connect-s3-11.0.8.jar` (main connector)
- `kafka-connect-storage-*.jar` (storage libraries)
- AWS SDK JARs
- Other dependencies

## Verification

After installation, verify the connector is available:

```bash
curl http://72.61.233.209:8083/connector-plugins
```

Look for:
```json
{
  "class": "io.confluent.connect.s3.S3SinkConnector",
  "type": "sink",
  "version": "11.0.8"
}
```

## Troubleshooting

### If connector is not found:

1. **Check container logs**:
   ```bash
   docker logs kafka-connect-cdc | tail -50
   ```

2. **Verify JAR files are in the container**:
   ```bash
   docker exec kafka-connect-cdc ls -la /kafka/connect/ | grep s3
   ```

3. **Check plugin path configuration**:
   ```bash
   docker exec kafka-connect-cdc env | grep PLUGIN
   ```

4. **Restart container again**:
   ```bash
   docker restart kafka-connect-cdc
   sleep 60  # Wait longer
   ```

### Common Issues

- **Permission denied**: Make sure Docker has permission to copy files
- **Container not found**: Verify container name is `kafka-connect-cdc`
- **Connector not loading**: Check Kafka Connect logs for errors
- **Class not found**: Ensure all JAR dependencies are copied

## After Installation

Once the connector is installed:

1. ✅ The code is already updated to use S3 sink
2. ✅ Create a pipeline with `mode: "full_load_and_cdc"`
3. ✅ Start the pipeline
4. ✅ Changes will automatically flow to S3!

## Need Help?

If you encounter issues:
1. Check `S3_SINK_SETUP.md` for detailed documentation
2. Review Kafka Connect logs
3. Verify AWS credentials in your S3 connection
4. Test connector manually via Kafka Connect API

