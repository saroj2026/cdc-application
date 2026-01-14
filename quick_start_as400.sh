#!/bin/bash
# Quick script to start AS400-S3_P pipeline

API_BASE="http://localhost:8000/api/v1"
PIPELINE_NAME="AS400-S3_P"

echo "🚀 Starting AS400-S3_P Pipeline"
echo ""

# Get pipeline ID
echo "Finding pipeline..."
PIPELINE_ID=$(curl -s "$API_BASE/pipelines" | python3 -c "
import sys, json
data = json.load(sys.stdin)
for p in data:
    if p.get('name') == '$PIPELINE_NAME':
        print(p.get('id'))
        break
")

if [ -z "$PIPELINE_ID" ]; then
    echo "❌ Pipeline '$PIPELINE_NAME' not found"
    echo ""
    echo "Available pipelines:"
    curl -s "$API_BASE/pipelines" | python3 -c "
import sys, json
data = json.load(sys.stdin)
for p in data:
    print(f\"  - {p.get('name')} (ID: {p.get('id')})\")
"
    exit 1
fi

echo "✅ Found pipeline: $PIPELINE_ID"
echo ""

# Start pipeline
echo "Starting pipeline..."
RESPONSE=$(curl -s -X POST "$API_BASE/pipelines/$PIPELINE_ID/start")

# Check if successful
if echo "$RESPONSE" | python3 -c "import sys, json; data=json.load(sys.stdin); exit(0 if 'message' in data or 'status' in data else 1)" 2>/dev/null; then
    echo "✅ Pipeline start requested!"
    echo ""
    echo "$RESPONSE" | python3 -m json.tool
else
    echo "❌ Failed to start pipeline:"
    echo "$RESPONSE"
    exit 1
fi

echo ""
echo "Check status with:"
echo "  curl $API_BASE/pipelines/$PIPELINE_ID/status"

