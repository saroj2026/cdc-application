# Java 17 Upgrade Solutions for Confluent Platform

## Problem
The Confluent Platform Docker image doesn't have `apt-get`, so we can't install Java 17 using package managers.

## Solution Options

### Option 1: Upgrade Docker Image (Recommended) ⭐

**Use Confluent Platform 7.5+ which includes Java 17 by default.**

**Steps:**
1. **Backup current configuration:**
   ```bash
   ssh root@72.61.233.209
   docker exec kafka-connect-cdc cat /etc/kafka-connect/kafka-connect.properties > /tmp/kafka-connect-backup.properties
   ```

2. **Stop current container:**
   ```bash
   docker stop kafka-connect-cdc
   ```

3. **Start new container with Java 17 image:**
   ```bash
   # Check current container configuration
   docker inspect kafka-connect-cdc > /tmp/container-config.json
   
   # Start with Confluent Platform 7.5+ (has Java 17)
   docker run -d \
     --name kafka-connect-cdc \
     --network <same-network> \
     -p 8083:8083 \
     -v <same-volumes> \
     -e CONNECT_BOOTSTRAP_SERVERS=<your-brokers> \
     confluentinc/cp-kafka-connect:7.5.0
   ```

4. **Copy connector plugins:**
   ```bash
   # Copy from old container or reinstall
   docker cp <old-container>:/usr/share/java/plugins /tmp/plugins
   docker cp /tmp/plugins kafka-connect-cdc:/usr/share/java/
   ```

### Option 2: Download Java 17 Manually

**Download and install Java 17 binary in the container:**

```bash
# 1. Download Java 17 on the VPS
ssh root@72.61.233.209
cd /tmp
wget https://download.java.net/java/GA/jdk17.0.2/dfd4a8d0985749f896bed50d7138ee7f/8/GPL/openjdk-17.0.2_linux-x64_bin.tar.gz

# 2. Copy to container
docker cp openjdk-17.0.2_linux-x64_bin.tar.gz kafka-connect-cdc:/tmp/

# 3. Extract in container
docker exec kafka-connect-cdc sh -c 'cd /tmp && tar -xzf openjdk-17.0.2_linux-x64_bin.tar.gz && mv jdk-17.0.2 /usr/lib/jvm/'

# 4. Set environment variables
docker exec kafka-connect-cdc sh -c 'export JAVA_HOME=/usr/lib/jvm/jdk-17.0.2 && export PATH=$JAVA_HOME/bin:$PATH'

# 5. Update startup script or use environment variables
# Check /etc/confluent/docker/run for where to set JAVA_HOME
```

### Option 3: Use Environment Variables (If Java 17 Exists)

**If Java 17 is already in the image somewhere:**

```bash
# Find Java 17
docker exec kafka-connect-cdc find /usr -name "java" -type f | grep -E "17|jdk-17"

# Set environment variable
docker exec kafka-connect-cdc sh -c 'export JAVA_HOME=/path/to/java17'
```

### Option 4: Custom Dockerfile

**Create a custom image with Java 17:**

```dockerfile
FROM confluentinc/cp-kafka-connect:7.4.0

# Install Java 17
USER root
RUN apt-get update && apt-get install -y openjdk-17-jdk-headless
RUN update-alternatives --install /usr/bin/java java /usr/lib/jvm/java-17-openjdk-amd64/bin/java 1
RUN update-alternatives --set java /usr/lib/jvm/java-17-openjdk-amd64/bin/java

USER appuser
```

Then build and use:
```bash
docker build -t kafka-connect-java17:7.4.0 .
docker run ... kafka-connect-java17:7.4.0
```

## Recommended Approach

**Use Option 1 (Upgrade Docker Image)** because:
- ✅ Cleanest solution
- ✅ Official support
- ✅ No manual Java installation
- ✅ Future-proof
- ✅ All features tested together

## Quick Check Commands

```bash
# Check current image
docker inspect kafka-connect-cdc | grep Image

# Check if Java 17 exists in image
docker exec kafka-connect-cdc find /usr -name "java*17*" 2>/dev/null

# Check available Java versions
docker exec kafka-connect-cdc ls -la /usr/lib/jvm/
```

## Next Steps

1. **Decide on approach** (recommend Option 1)
2. **Backup current setup**
3. **Execute chosen solution**
4. **Verify IBM i connector loads**
5. **Test all connectors**

