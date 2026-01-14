#!/bin/bash

# Move Java 17 from /tmp to /opt
sshpass -p 'segmbp@1100' ssh -o StrictHostKeyChecking=no root@72.61.233.209 "docker exec kafka-connect-cdc sh -c 'mv /tmp/jdk-17.0.2 /opt/'"

# Verify the move
echo "Verifying Java 17 location..."
sshpass -p 'segmbp@1100' ssh -o StrictHostKeyChecking=no root@72.61.233.209 "docker exec kafka-connect-cdc sh -c 'ls -la /opt/jdk-17.0.2/bin/java'"

# Test Java 17
echo "Testing Java 17..."
sshpass -p 'segmbp@1100' ssh -o StrictHostKeyChecking=no root@72.61.233.209 "docker exec kafka-connect-cdc /opt/jdk-17.0.2/bin/java -version"

echo "✅ Java 17 moved to /opt/"

