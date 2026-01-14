# Final Java 17 Installation Steps

## Current Status
- ✅ Java 17 downloaded and extracted in `/tmp/jdk-17.0.2`
- ⏳ Needs to be moved to `/opt/` and configured
- ⏳ Startup script needs JAVA_HOME update
- ⏳ Kafka Connect needs restart

## Commands to Run (Copy & Paste)

Run these commands **one by one** in your terminal:

### Step 1: Move Java 17 to /opt
```bash
sshpass -p 'segmbp@1100' ssh -o StrictHostKeyChecking=no root@72.61.233.209 "docker exec kafka-connect-cdc sh -c 'mv /tmp/jdk-17.0.2 /opt/'"
```

### Step 2: Verify Java 17
```bash
sshpass -p 'segmbp@1100' ssh -o StrictHostKeyChecking=no root@72.61.233.209 "docker exec kafka-connect-cdc /opt/jdk-17.0.2/bin/java -version"
```

### Step 3: Create Java 17 symlink
```bash
sshpass -p 'segmbp@1100' ssh -o StrictHostKeyChecking=no root@72.61.233.209 "docker exec kafka-connect-cdc sh -c 'cp /opt/jdk-17.0.2/bin/java /usr/bin/java17 && chmod +x /usr/bin/java17'"
```

### Step 4: Update startup script with JAVA_HOME
```bash
sshpass -p 'segmbp@1100' ssh -o StrictHostKeyChecking=no root@72.61.233.209 "docker exec kafka-connect-cdc sh -c 'sed -i \"1a export JAVA_HOME=/opt/jdk-17.0.2\" /etc/confluent/docker/run && sed -i \"1a export PATH=\$JAVA_HOME/bin:\$PATH\" /etc/confluent/docker/run'"
```

### Step 5: Verify startup script
```bash
sshpass -p 'segmbp@1100' ssh -o StrictHostKeyChecking=no root@72.61.233.209 "docker exec kafka-connect-cdc sh -c 'head -5 /etc/confluent/docker/run'"
```

### Step 6: Restart Kafka Connect
```bash
sshpass -p 'segmbp@1100' ssh -o StrictHostKeyChecking=no root@72.61.233.209 "docker restart kafka-connect-cdc"
```

### Step 7: Wait for startup
```bash
sleep 70
```

### Step 8: Verify Java 17 is active
```bash
sshpass -p 'segmbp@1100' ssh -o StrictHostKeyChecking=no root@72.61.233.209 "docker exec kafka-connect-cdc java -version"
```
**Expected:** Should show `openjdk version "17.x.x"`

### Step 9: Check if IBM i connector loads
```bash
sshpass -p 'segmbp@1100' ssh -o StrictHostKeyChecking=no root@72.61.233.209 "docker logs kafka-connect-cdc 2>&1 | grep -i 'Added plugin.*As400RpcConnector' | tail -1"
```
**Expected:** Should show `INFO Added plugin 'io.debezium.connector.db2as400.As400RpcConnector'`

### Step 10: Verify via API
```bash
sshpass -p 'segmbp@1100' ssh -o StrictHostKeyChecking=no root@72.61.233.209 "curl -s http://localhost:8083/connector-plugins | python3 -c \"import sys, json; plugins = json.load(sys.stdin); as400 = [p for p in plugins if 'As400RpcConnector' in p.get('class', '')]; print('✅ SUCCESS!' if as400 else '❌ Not found'); [print(f'{p.get(\"class\")} v{p.get(\"version\")}') for p in as400]\""
```

## Success Indicators

✅ **Java 17 active:** `java -version` shows version 17.x  
✅ **Connector loaded:** Log shows "Added plugin.*As400RpcConnector"  
✅ **API verification:** Connector appears in `/connector-plugins` endpoint  

## Next Steps After Installation

Once Java 17 is active and the connector loads:
1. Start the AS400-S3_P pipeline
2. Monitor logs for any issues
3. Verify data flow to S3

## Troubleshooting

If Java 17 doesn't activate after restart:
- Check startup script: `docker exec kafka-connect-cdc head -10 /etc/confluent/docker/run`
- Verify Java 17 location: `docker exec kafka-connect-cdc ls -la /opt/jdk-17.0.2/bin/java`
- Check logs: `docker logs kafka-connect-cdc | tail -50`

