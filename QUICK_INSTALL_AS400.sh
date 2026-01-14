#!/bin/bash
# Quick install script - run this on the server (72.61.233.209)
# SSH: ssh root@72.61.233.209

CONTAINER=$(docker ps | grep -i connect | awk '{print $1}' | head -1)
echo "Found container: $CONTAINER"

cd /tmp
wget -q https://repo1.maven.org/maven2/io/debezium/debezium-connector-ibmi/2.6.0.Beta1/debezium-connector-ibmi-2.6.0.Beta1-plugin.tar.gz
tar -xzf debezium-connector-ibmi-2.6.0.Beta1-plugin.tar.gz
docker cp debezium-connector-ibmi-2.6.0.Beta1-plugin $CONTAINER:/kafka/connect/debezium-connector-ibmi
docker restart $CONTAINER
echo "Waiting 30 seconds for restart..."
sleep 30
echo "Verifying..."
curl -s http://localhost:8083/connector-plugins | grep -i As400RpcConnector && echo "✅ AS400 Connector installed!" || echo "⚠️  Check manually"

