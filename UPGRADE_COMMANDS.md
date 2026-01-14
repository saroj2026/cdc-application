# Java 17 Upgrade - Direct Commands

If you get "permission denied", run these commands directly:

## Option 1: Fix permissions and run script

```bash
cd /Users/kumargaurav/Desktop/CDCTEAM/cdcteam/seg-cdc-application
chmod +x upgrade_kafka_connect_to_java17.sh
./upgrade_kafka_connect_to_java17.sh
```

## Option 2: Run with bash directly

```bash
cd /Users/kumargaurav/Desktop/CDCTEAM/cdcteam/seg-cdc-application
bash upgrade_kafka_connect_to_java17.sh
```

## Option 3: Run commands manually

Copy and paste these commands one by one:

```bash
# 1. Check current Java version
sshpass -p 'segmbp@1100' ssh -o StrictHostKeyChecking=no root@72.61.233.209 "docker exec kafka-connect-cdc java -version"

# 2. Install Java 17
sshpass -p 'segmbp@1100' ssh -o StrictHostKeyChecking=no root@72.61.233.209 "docker exec kafka-connect-cdc sh -c 'apt-get update && apt-get install -y openjdk-17-jdk-headless'"

# 3. Set Java 17 as default
sshpass -p 'segmbp@1100' ssh -o StrictHostKeyChecking=no root@72.61.233.209 "docker exec kafka-connect-cdc sh -c 'update-alternatives --install /usr/bin/java java /usr/lib/jvm/java-17-openjdk-amd64/bin/java 1 && update-alternatives --set java /usr/lib/jvm/java-17-openjdk-amd64/bin/java'"

# 4. Configure JAVA_HOME
sshpass -p 'segmbp@1100' ssh -o StrictHostKeyChecking=no root@72.61.233.209 "docker exec kafka-connect-cdc sh -c 'echo \"export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64\" >> /etc/profile && echo \"export PATH=\$JAVA_HOME/bin:\$PATH\" >> /etc/profile'"

# 5. Verify Java 17
sshpass -p 'segmbp@1100' ssh -o StrictHostKeyChecking=no root@72.61.233.209 "docker exec kafka-connect-cdc java -version"

# 6. Restart Kafka Connect
sshpass -p 'segmbp@1100' ssh -o StrictHostKeyChecking=no root@72.61.233.209 "docker restart kafka-connect-cdc"

# 7. Wait 70 seconds
sleep 70

# 8. Verify Java 17 is active
sshpass -p 'segmbp@1100' ssh -o StrictHostKeyChecking=no root@72.61.233.209 "docker exec kafka-connect-cdc java -version"

# 9. Check if IBM i connector loads
sshpass -p 'segmbp@1100' ssh -o StrictHostKeyChecking=no root@72.61.233.209 "docker logs kafka-connect-cdc 2>&1 | grep -i 'Added plugin.*As400RpcConnector' | tail -1"

# 10. Verify via API
sshpass -p 'segmbp@1100' ssh -o StrictHostKeyChecking=no root@72.61.233.209 "curl -s http://localhost:8083/connector-plugins | python3 -c \"import sys, json; plugins = json.load(sys.stdin); as400 = [p for p in plugins if 'As400RpcConnector' in p.get('class', '')]; print('SUCCESS: IBM i connector loaded!' if as400 else 'Not found'); [print(f'  {p.get(\"class\")} v{p.get(\"version\")}') for p in as400]\""
```

## Quick Fix for Permission Denied

```bash
chmod +x /Users/kumargaurav/Desktop/CDCTEAM/cdcteam/seg-cdc-application/upgrade_kafka_connect_to_java17.sh
```

Then run:
```bash
bash /Users/kumargaurav/Desktop/CDCTEAM/cdcteam/seg-cdc-application/upgrade_kafka_connect_to_java17.sh
```

