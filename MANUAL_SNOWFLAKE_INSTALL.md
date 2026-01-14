# Manual Snowflake Connector Installation

The automated download is failing. Please follow these manual steps:

## Option 1: Download on Your Local Machine and Copy

### Step 1: Download on Your Computer

Download the connector JAR file:
- **Direct Link**: https://repo1.maven.org/maven2/com/snowflake/snowflake-kafka-connector/1.11.0/snowflake-kafka-connector-1.11.0.jar
- **Expected Size**: ~2-5 MB (if you get a file smaller than 1MB, the download failed)

### Step 2: Copy to VPS

```bash
# From your local machine
scp snowflake-kafka-connector-1.11.0.jar root@72.61.233.209:/tmp/
```

### Step 3: Copy to Container

```bash
# SSH into VPS
ssh root@72.61.233.209

# Copy to container
docker cp /tmp/snowflake-kafka-connector-1.11.0.jar kafka-connect-cdc:/usr/share/confluent-hub-components/snowflake-kafka-connector/

# Verify file size (should be > 1MB)
docker exec kafka-connect-cdc ls -lh /usr/share/confluent-hub-components/snowflake-kafka-connector/
```

### Step 4: Restart Kafka Connect

```bash
docker restart kafka-connect-cdc

# Wait 30 seconds
sleep 30

# Verify
docker exec kafka-connect-cdc curl -s http://localhost:8083/connector-plugins | grep -i snowflake
```

## Option 2: Download Directly on VPS Using Alternative Method

If wget/curl is failing, try:

```bash
# SSH into VPS
ssh root@72.61.233.209

# Try with different options
cd /tmp
curl -L -C - -o snowflake-kafka-connector-1.11.0.jar \
  "https://repo1.maven.org/maven2/com/snowflake/snowflake-kafka-connector/1.11.0/snowflake-kafka-connector-1.11.0.jar"

# Or try with wget
wget --no-check-certificate -O snowflake-kafka-connector-1.11.0.jar \
  "https://repo1.maven.org/maven2/com/snowflake/snowflake-kafka-connector/1.11.0/snowflake-kafka-connector-1.11.0.jar"

# Verify download (should be > 1MB)
ls -lh snowflake-kafka-connector-1.11.0.jar

# Copy to container
docker cp snowflake-kafka-connector-1.11.0.jar kafka-connect-cdc:/usr/share/confluent-hub-components/snowflake-kafka-connector/

# Restart
docker restart kafka-connect-cdc
```

## Option 3: Use Maven to Download

If you have Maven installed on VPS:

```bash
# SSH into VPS
ssh root@72.61.233.209

# Download using Maven
mvn dependency:get \
  -Dartifact=com.snowflake:snowflake-kafka-connector:1.11.0 \
  -Ddest=/tmp/snowflake-kafka-connector-1.11.0.jar

# Copy to container
docker cp /tmp/snowflake-kafka-connector-1.11.0.jar kafka-connect-cdc:/usr/share/confluent-hub-components/snowflake-kafka-connector/

# Restart
docker restart kafka-connect-cdc
```

## Verification

After installation, verify:

```bash
# Check file exists and size
docker exec kafka-connect-cdc ls -lh /usr/share/confluent-hub-components/snowflake-kafka-connector/

# Should show file size > 1MB, for example:
# -rw-r--r-- 1 root root 2.5M Jan  6 11:30 snowflake-kafka-connector-1.11.0.jar

# Check if connector is available (may not show until first use)
docker exec kafka-connect-cdc curl -s http://localhost:8083/connector-plugins | python3 -m json.tool | grep -i snowflake
```

## Current Status

✅ **Step 1**: Python package installed  
⚠️ **Step 2**: Directory created, but file download failed (only 554 bytes)  
📋 **Action Required**: Download file manually using one of the options above

## Alternative Download URLs

If the main URL doesn't work, try:

1. **Maven Central**: https://repo1.maven.org/maven2/com/snowflake/snowflake-kafka-connector/1.11.0/
2. **GitHub Releases**: Check Snowflake's GitHub repository for releases
3. **Snowflake Documentation**: https://docs.snowflake.com/en/user-guide/kafka-connector-install.html

## Troubleshooting

### File Size Too Small

If the file is less than 1MB, it's likely:
- An error page (HTML)
- A redirect that wasn't followed
- Network timeout

**Solution**: Download on your local machine where you have better network, then copy to VPS.

### Container Not Running

```bash
# Start container
docker start kafka-connect-cdc

# Wait for it to be ready
sleep 20

# Verify
docker ps | grep kafka-connect-cdc
```

### Permission Issues

```bash
# If you get permission errors, use root user
docker exec -u root kafka-connect-cdc mkdir -p /usr/share/confluent-hub-components/snowflake-kafka-connector
```



