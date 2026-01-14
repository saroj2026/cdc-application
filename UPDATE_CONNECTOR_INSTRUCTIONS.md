# Update Kafka Connect Connector Configuration

## Credentials to Use
- **Access Key ID**: `AKIATLTXNANW2EV7QGV2`
- **Secret Access Key**: `kuJfl7aEDrwQfhPKC/qzGFf7I0tHu11d1U2RM4h2`
- **Connector**: `sink-as400-s3_p-s3-dbo`

## Method 1: Using curl commands on VPS (Recommended)

SSH into your VPS and run these commands:

```bash
# SSH into VPS
ssh root@72.61.233.209

# Step 1: Get current config and update credentials
docker exec kafka-connect-cdc curl -s http://localhost:8083/connectors/sink-as400-s3_p-s3-dbo/config > /tmp/connector_config.json

# Step 2: Update the JSON file with new credentials (using sed)
docker exec kafka-connect-cdc sh -c "cat /tmp/connector_config.json | sed 's/\"aws.access.key.id\":[^,}]*/\"aws.access.key.id\": \"AKIATLTXNANW2EV7QGV2\"/' | sed 's/\"aws.secret.access.key\":[^,}]*/\"aws.secret.access.key\": \"kuJfl7aEDrwQfhPKC\/qzGFf7I0tHu11d1U2RM4h2\"/' > /tmp/updated_config.json"

# Step 3: Update connector configuration
docker exec kafka-connect-cdc curl -X PUT \
  -H 'Content-Type: application/json' \
  -d @/tmp/updated_config.json \
  http://localhost:8083/connectors/sink-as400-s3_p-s3-dbo/config

# Step 4: Restart connector
docker exec kafka-connect-cdc curl -X POST \
  http://localhost:8083/connectors/sink-as400-s3_p-s3-dbo/restart

# Step 5: Check status (wait 30 seconds first)
sleep 30
docker exec kafka-connect-cdc curl -s http://localhost:8083/connectors/sink-as400-s3_p-s3-dbo/status | python3 -m json.tool
```

## Method 2: Using Python script on VPS

1. Copy `update_connector_on_vps.sh` to your VPS
2. Make it executable: `chmod +x update_connector_on_vps.sh`
3. Run it: `./update_connector_on_vps.sh`

## Method 3: Manual update via Kafka UI

1. Go to: http://72.61.233.209:8080/ui/clusters/local/connectors/sink-as400-s3_p-s3-dbo
2. Click "Edit Config"
3. Update:
   - `aws.access.key.id`: `AKIATLTXNANW2EV7QGV2`
   - `aws.secret.access.key`: `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`
4. Save
5. Click "Restart"
6. Wait 30-60 seconds
7. Verify status is `RUNNING`

## Verification

After updating, check:
- Connector status should be `RUNNING`
- Tasks should show `1 of 1` running
- No error messages in trace
- Data should start flowing to S3



