# Quick S3 Connector Installation Guide

## For VPS Server (72.61.233.209)

### Step 1: Upload Connector to VPS

If you haven't already, you need to get the connector files to the VPS:

**Option A: If connector is on your local machine:**
```bash
# From your local machine
scp -r confluentinc-kafka-connect-s3-11.0.8 user@72.61.233.209:/opt/cdc3/
```

**Option B: If connector is already on VPS:**
The connector should be in `/opt/cdc3/confluentinc-kafka-connect-s3-11.0.8/`

### Step 2: Run Installation Script

**On the VPS server:**

```bash
# Navigate to project directory
cd /opt/cdc3

# Make script executable
chmod +x install_s3_connector_vps.sh

# Run installation
./install_s3_connector_vps.sh
```

**Or manually:**

```bash
# Copy JAR files
docker cp confluentinc-kafka-connect-s3-11.0.8/confluentinc-kafka-connect-s3-11.0.8/lib/. kafka-connect-cdc:/kafka/connect/

# Restart
docker restart kafka-connect-cdc

# Wait 60 seconds
sleep 60

# Verify
curl http://localhost:8083/connector-plugins | grep -i "S3SinkConnector"
```

### Step 3: Verify Installation

```bash
curl http://72.61.233.209:8083/connector-plugins | python3 -m json.tool | grep -i s3
```

Should show:
```json
{
  "class": "io.confluent.connect.s3.S3SinkConnector",
  "type": "sink",
  "version": "11.0.8"
}
```

### Step 4: Test CDC Pipeline

Once installed, create and start a CDC pipeline - the S3 sink will be created automatically!

## Troubleshooting

### If connector not found:

1. **Check container logs:**
   ```bash
   docker logs kafka-connect-cdc | tail -100
   ```

2. **Verify files are in container:**
   ```bash
   docker exec kafka-connect-cdc ls -la /kafka/connect/ | grep s3
   ```

3. **Check plugin path:**
   ```bash
   docker exec kafka-connect-cdc env | grep PLUGIN
   ```

4. **Restart again and wait longer:**
   ```bash
   docker restart kafka-connect-cdc
   sleep 90
   ```

## What Happens After Installation

✅ Code is ready - S3 sink will be created automatically
✅ When you start a CDC pipeline with S3 target:
   - Debezium connector captures changes
   - S3 sink connector writes to S3
   - Changes appear in S3 bucket as JSON files


## For VPS Server (72.61.233.209)

### Step 1: Upload Connector to VPS

If you haven't already, you need to get the connector files to the VPS:

**Option A: If connector is on your local machine:**
```bash
# From your local machine
scp -r confluentinc-kafka-connect-s3-11.0.8 user@72.61.233.209:/opt/cdc3/
```

**Option B: If connector is already on VPS:**
The connector should be in `/opt/cdc3/confluentinc-kafka-connect-s3-11.0.8/`

### Step 2: Run Installation Script

**On the VPS server:**

```bash
# Navigate to project directory
cd /opt/cdc3

# Make script executable
chmod +x install_s3_connector_vps.sh

# Run installation
./install_s3_connector_vps.sh
```

**Or manually:**

```bash
# Copy JAR files
docker cp confluentinc-kafka-connect-s3-11.0.8/confluentinc-kafka-connect-s3-11.0.8/lib/. kafka-connect-cdc:/kafka/connect/

# Restart
docker restart kafka-connect-cdc

# Wait 60 seconds
sleep 60

# Verify
curl http://localhost:8083/connector-plugins | grep -i "S3SinkConnector"
```

### Step 3: Verify Installation

```bash
curl http://72.61.233.209:8083/connector-plugins | python3 -m json.tool | grep -i s3
```

Should show:
```json
{
  "class": "io.confluent.connect.s3.S3SinkConnector",
  "type": "sink",
  "version": "11.0.8"
}
```

### Step 4: Test CDC Pipeline

Once installed, create and start a CDC pipeline - the S3 sink will be created automatically!

## Troubleshooting

### If connector not found:

1. **Check container logs:**
   ```bash
   docker logs kafka-connect-cdc | tail -100
   ```

2. **Verify files are in container:**
   ```bash
   docker exec kafka-connect-cdc ls -la /kafka/connect/ | grep s3
   ```

3. **Check plugin path:**
   ```bash
   docker exec kafka-connect-cdc env | grep PLUGIN
   ```

4. **Restart again and wait longer:**
   ```bash
   docker restart kafka-connect-cdc
   sleep 90
   ```

## What Happens After Installation

✅ Code is ready - S3 sink will be created automatically
✅ When you start a CDC pipeline with S3 target:
   - Debezium connector captures changes
   - S3 sink connector writes to S3
   - Changes appear in S3 bucket as JSON files

