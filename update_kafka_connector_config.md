# Update Kafka Connect S3 Sink Connector Configuration

## New AWS Credentials

- **Access Key ID**: `AKIATLTXNANW2JU6WWAH`
- **Secret Access Key**: `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`
- **Bucket**: `mycdcbucket26`
- **Region**: `us-east-1`

## Steps to Update Connector

### 1. Go to Kafka Connect UI
- URL: http://72.61.233.209:8080/ui/clusters/local/connectors
- Find connector: `sink-as400-s3_p-s3-dbo`

### 2. Edit Configuration
- Click on the connector name
- Click "Edit Config" or "Configuration" button
- Update these fields:

```json
{
  "aws.access.key.id": "AKIATLTXNANW2JU6WWAH",
  "aws.secret.access.key": "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"
}
```

### 3. Save Configuration
- Click "Save" or "Apply"
- Wait for configuration to be saved

### 4. Restart Connector
- Click "Restart" button
- Wait 30-60 seconds
- Check status - should change from `TASK_FAILED` to `RUNNING`

### 5. Verify
- Status should be: `RUNNING`
- Tasks should show: `1 of 1` running
- No error messages in trace

## Expected Result

After updating and restarting:
- ✅ Connector status: `RUNNING`
- ✅ Tasks: `1 of 1` running
- ✅ Data will start flowing to S3 bucket `mycdcbucket26`
- ✅ Your record (id=333, name=KISHOR) should appear in S3

## Full Configuration Reference

The complete configuration should include:

```json
{
  "connector.class": "io.confluent.connect.s3.S3SinkConnector",
  "topics": "AS400-S3_P.SEGMETRIQ1.MYTABLE",
  "s3.bucket.name": "mycdcbucket26",
  "s3.region": "us-east-1",
  "s3.prefix": "dbo/",
  "flush.size": "1",
  "aws.access.key.id": "AKIATLTXNANW2JU6WWAH",
  "aws.secret.access.key": "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",
  "format.class": "io.confluent.connect.s3.format.json.JsonFormat",
  "storage.class": "io.confluent.connect.s3.storage.S3Storage",
  "partitioner.class": "io.confluent.connect.storage.partitioner.DefaultPartitioner",
  "schema.compatibility": "NONE",
  "tasks.max": "1"
}
```



