#!/bin/bash
# Check for Debezium IBM i connector installation

echo "Checking Debezium IBM i connector installation..."
echo "================================================"

# Check in Kafka Connect container
echo ""
echo "1. Checking Kafka Connect container for Debezium IBM i connector:"
docker exec kafka-connect-cdc find /usr/share/java/plugins -name '*ibmi*' -o -name '*as400*' -o -name '*db2as400*' 2>/dev/null

echo ""
echo "2. Listing all Debezium connectors:"
docker exec kafka-connect-cdc ls -la /usr/share/java/plugins/ | grep -i debezium

echo ""
echo "3. Checking specific directory:"
docker exec kafka-connect-cdc ls -la /usr/share/java/plugins/debezium-connector-ibmi/ 2>/dev/null || echo "Directory not found"

echo ""
echo "4. Checking for JAR files:"
docker exec kafka-connect-cdc find /usr/share/java/plugins/debezium-connector-ibmi -name '*.jar' 2>/dev/null | head -10

echo ""
echo "================================================"
echo "Note: If Debezium AS400 connector is RUNNING in Kafka UI,"
echo "the connector is installed and working correctly."
echo "The current issue is with S3 sink connector AWS credentials."



