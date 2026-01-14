# IBM i Connector - Solution Options

## Problem Summary

- **Debezium IBM i Connector 2.6.0.Final** requires **Java 17**
- **Kafka Connect 7.4.0** runs on **Java 11**
- **Result:** Class version incompatibility (61.0 vs 55.0)

## Discovery

The IBM i connector (`debezium-connector-ibmi`) was **NOT released in Debezium 2.5.x versions**. 

Available versions on Maven Central:
- 2.6.0.Beta1
- 2.6.0.CR1
- 2.6.0.Final
- 2.6.1.Final
- 2.6.2.Final
- 2.7.0.Alpha1+
- 2.7.0.Final

**All require Java 17+**

## Solution Options

### Option 1: Upgrade Kafka Connect to Java 17 (Recommended)

**Pros:**
- Uses the latest stable version (2.6.0.Final)
- Future-proof
- Full feature support

**Cons:**
- Requires Docker image change or Java upgrade
- May affect other connectors (verify compatibility)

**Steps:**
1. Use a Kafka Connect Docker image with Java 17
2. Or modify the existing container to use Java 17
3. Install debezium-connector-ibmi-2.6.0.Final
4. Verify connector loads

### Option 2: Try Debezium 2.6.0.Beta1 (May work with Java 11)

**Pros:**
- Might be compiled with Java 11
- No infrastructure changes needed

**Cons:**
- Beta version (less stable)
- May still require Java 17
- Not recommended for production

**Steps:**
1. Download debezium-connector-ibmi-2.6.0.Beta1
2. Test if it loads with Java 11
3. If successful, use it (with caution)

### Option 3: Use Alternative Connector (If Available)

Check if there's an older IBM i connector or alternative solution.

### Option 4: Build from Source (Advanced)

**Pros:**
- Can compile with Java 11
- Full control

**Cons:**
- Complex
- Requires build environment
- Maintenance burden

## Recommended Action

**Upgrade Kafka Connect to Java 17** is the best long-term solution.

### Quick Implementation

1. **Check current Docker image:**
   ```bash
   docker inspect kafka-connect-cdc | grep Image
   ```

2. **Use Java 17-based image:**
   - Confluent Platform 7.5+ includes Java 17
   - Or use `confluentinc/cp-kafka-connect:latest`

3. **Alternative: Modify existing container:**
   ```bash
   # Install Java 17 in container
   docker exec kafka-connect-cdc apt-get update
   docker exec kafka-connect-cdc apt-get install -y openjdk-17-jdk
   # Update JAVA_HOME and PATH
   ```

## Current Status

- ✅ Connector files installed: `/usr/share/java/plugins/debezium-connector-ibmi/`
- ✅ jt400.jar present
- ✅ Service file correct
- ❌ Java version mismatch prevents loading

## Next Steps

1. **Decide on solution approach**
2. **If upgrading to Java 17:**
   - Backup current setup
   - Upgrade Kafka Connect container
   - Reinstall connector
   - Test thoroughly
3. **If trying Beta1:**
   - Download and test
   - Monitor for stability issues

## Verification Commands

After implementing solution:
```bash
# Check Java version
docker exec kafka-connect-cdc java -version

# Check connector loads
curl http://localhost:8083/connector-plugins | grep As400RpcConnector

# Check logs
docker logs kafka-connect-cdc | grep "Added plugin.*As400RpcConnector"
```

