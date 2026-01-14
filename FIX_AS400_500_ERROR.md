# Fix Kafka Connect 500 Error for AS400 Pipeline

## Problem

When starting the AS400-S3_P pipeline, you get this error:
```
HTTPConnectionPool(host='72.61.233.209', port=8083): Max retries exceeded with url: /connectors 
(Caused by ResponseError('too many 500 error responses'))
```

## Root Cause

Kafka Connect is returning 500 errors because the AS400 connector plugin (`io.debezium.connector.db2as400.As400RpcConnector`) is not installed or not loaded in the Kafka Connect container.

## Solution

You need to install/verify the AS400 connector plugin in the Kafka Connect Docker container on the VPS server (72.61.233.209).

---

## Option 1: Quick Fix Script (Linux/Mac)

### Step 1: Copy script to server
```bash
scp fix_as400_500_quick.sh root@72.61.233.209:/tmp/
```

### Step 2: SSH to server and run
```bash
ssh root@72.61.233.209
# Password: segmbp@1100

chmod +x /tmp/fix_as400_500_quick.sh
/tmp/fix_as400_500_quick.sh
```

---

## Option 2: Manual Steps (Linux/Mac)

### SSH to the server
```bash
ssh root@72.61.233.209
# Password: segmbp@1100
```

### Step 1: Find Kafka Connect container
```bash
CONTAINER=$(docker ps | grep -i connect | awk '{print $1}' | head -1)
echo "Container: $CONTAINER"
```

### Step 2: Check if connector exists
```bash
docker exec $CONTAINER ls -la /usr/share/java/plugins
docker exec $CONTAINER find /usr/share/java/plugins -type d -name "*ibmi*" -o -name "*db2as400*"
```

### Step 3: If not found, copy from host
```bash
# Find connector on host
find /opt/cdc3/connect-plugins -type d -name "*ibmi*" -o -name "*db2as400*"

# Copy to container (replace with actual path)
CONNECTOR_PATH=$(find /opt/cdc3/connect-plugins -type d -name "*ibmi*" | head -1)
CONNECTOR_NAME=$(basename "$CONNECTOR_PATH")
docker cp "$CONNECTOR_PATH" "$CONTAINER:/usr/share/java/plugins/$CONNECTOR_NAME"
```

### Step 4: Restart container
```bash
docker restart $CONTAINER
sleep 30
```

### Step 5: Verify connector is loaded
```bash
curl -s http://localhost:8083/connector-plugins | grep -i "As400RpcConnector\|db2as400"
```

---

## Option 3: Using Plink (Windows)

### Step 1: Run the batch file
```cmd
fix_as400_500_plink.bat
```

Or manually with plink:

```cmd
REM Find container
plink root@72.61.233.209 -pw segmbp@1100 "docker ps | grep connect"

REM Check connector
plink root@72.61.233.209 -pw segmbp@1100 "docker exec CONTAINER_ID find /usr/share/java/plugins -type d -name '*ibmi*'"

REM Copy connector (if needed)
plink root@72.61.233.209 -pw segmbp@1100 "docker cp /opt/cdc3/connect-plugins/debezium-connector-ibmi CONTAINER_ID:/usr/share/java/plugins/"

REM Restart
plink root@72.61.233.209 -pw segmbp@1100 "docker restart CONTAINER_ID"
```

---

## Option 4: Interactive Fix Script

Run the interactive script on the server:
```bash
ssh root@72.61.233.209
scp fix_kafka_connect_500_as400.sh root@72.61.233.209:/tmp/
chmod +x /tmp/fix_kafka_connect_500_as400.sh
/tmp/fix_kafka_connect_500_as400.sh
```

This script provides an interactive menu to:
1. Check connector status
2. Copy connector from host to container
3. Restart Kafka Connect
4. Full fix (all of the above)

---

## Verification

After fixing, verify the connector is available:

```bash
# On the VPS server
curl -s http://localhost:8083/connector-plugins | python3 -m json.tool | grep -i "As400RpcConnector"
```

You should see:
```json
{
  "class": "io.debezium.connector.db2as400.As400RpcConnector",
  ...
}
```

---

## After Fixing

1. **Restart your backend** (if needed):
   ```bash
   # Press Ctrl+C in backend terminal, then:
   ./start_backend_simple.sh
   ```

2. **Start the pipeline again**:
   ```bash
   ./quick_start_as400.sh
   ```

3. **Check pipeline status**:
   ```bash
   python3 check_as400_pipeline_cdc.py
   ```

---

## Troubleshooting

### Connector not found on host
If the connector doesn't exist at `/opt/cdc3/connect-plugins`, you need to download it first:

```bash
# On VPS server
cd /opt/cdc3/connect-plugins
wget https://repo1.maven.org/maven2/io/debezium/debezium-connector-ibmi/2.6.0.Beta1/debezium-connector-ibmi-2.6.0.Beta1-plugin.tar.gz
tar -xzf debezium-connector-ibmi-2.6.0.Beta1-plugin.tar.gz
```

### Container path doesn't exist
If `/usr/share/java/plugins` doesn't exist in the container:

```bash
docker exec $CONTAINER mkdir -p /usr/share/java/plugins
```

### Connector copied but not loading
1. Check plugin path configuration:
   ```bash
   docker exec $CONTAINER env | grep PLUGIN_PATH
   ```

2. Restart Kafka Connect:
   ```bash
   docker restart $CONTAINER
   sleep 30
   ```

3. Check Kafka Connect logs:
   ```bash
   docker logs $CONTAINER | tail -50
   ```

---

## Files Created

- `fix_as400_500_quick.sh` - Quick fix script (run on VPS)
- `fix_kafka_connect_500_as400.sh` - Interactive fix script (run on VPS)
- `fix_as400_500_plink.bat` - Windows/plink version
- `FIX_AS400_500_ERROR.md` - This documentation

