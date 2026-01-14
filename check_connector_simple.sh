#!/bin/bash
# Simple script to check connector status - run this on VPS

CONNECTOR="sink-as400-s3_p-s3-dbo"

echo "======================================================================"
echo "Connector Status: $CONNECTOR"
echo "======================================================================"
echo ""

# Get status
echo "1. Connector Status:"
docker exec kafka-connect-cdc curl -s http://localhost:8083/connectors/$CONNECTOR/status | python3 -m json.tool

echo ""
echo "2. Configuration:"
docker exec kafka-connect-cdc curl -s http://localhost:8083/connectors/$CONNECTOR/config | python3 -c "
import sys, json
config = json.load(sys.stdin)
print(f\"   aws.access.key.id: {config.get('aws.access.key.id', 'NOT SET')[:20]}...\")
print(f\"   aws.secret.access.key: {'SET' if config.get('aws.secret.access.key') else 'NOT SET'}\")
print(f\"   flush.size: {config.get('flush.size', 'NOT SET')}\")
print(f\"   s3.bucket.name: {config.get('s3.bucket.name', 'NOT SET')}\")
"



