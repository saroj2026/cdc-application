# Installing S3 Sink Connector in Kafka Connect

## Problem

The S3 Sink Connector plugin (`io.confluent.connect.s3.S3SinkConnector`) is not installed in your Kafka Connect instance at `72.61.233.209:8083`. This is why you're getting 400 Bad Request errors when trying to create S3 sink connectors.

## Solution: Install Confluent S3 Sink Connector

### Option 1: Install via Confluent Hub (Recommended)

If you have SSH access to the Kafka Connect server:

```bash
# SSH into the Kafka Connect server
ssh root@72.61.233.209
# Password: segmbp@1100

# Navigate to Kafka Connect plugins directory
cd /path/to/kafka-connect/plugins  # Usually in /usr/share/confluent-hub-components or similar

# Install S3 Sink Connector via Confluent Hub
confluent-hub install confluentinc/kafka-connect-s3:latest

# Or download and install manually
# Download from: https://www.confluent.io/hub/confluentinc/kafka-connect-s3
```

### Option 2: Manual Installation

1. **Download the connector:**
   ```bash
   # Download from Confluent Hub
   wget https://d1i4a15mxbxib1.cloudfront.net/api/plugins/confluentinc/kafka-connect-s3/versions/latest/confluentinc-kafka-connect-s3-latest.tar.gz
   ```

2. **Extract and install:**
   ```bash
   tar -xzf confluentinc-kafka-connect-s3-latest.tar.gz
   # Copy to Kafka Connect plugins directory
   cp -r confluentinc-kafka-connect-s3-*/lib/* /path/to/kafka-connect/plugins/
   ```

3. **Restart Kafka Connect:**
   ```bash
   # Restart the Kafka Connect service
   systemctl restart kafka-connect
   # Or if using Docker:
   docker restart kafka-connect
   ```

### Option 3: Docker Installation

If Kafka Connect is running in Docker:

```bash
# SSH into the server
ssh root@72.61.233.209

# Find the Kafka Connect container
docker ps | grep connect

# Install connector in the container
docker exec -it <container-name> bash
cd /usr/share/confluent-hub-components
confluent-hub install confluentinc/kafka-connect-s3:latest

# Restart the container
docker restart <container-name>
```

## Verify Installation

After installation, verify the connector is available:

```bash
curl -s "http://72.61.233.209:8083/connector-plugins" | python3 -m json.tool | grep -i s3
```

You should see:
```json
{
  "class": "io.confluent.connect.s3.S3SinkConnector",
  "type": "sink",
  "version": "..."
}
```

## Alternative: Use Different Sink Method

If you cannot install the S3 Sink Connector, you have these alternatives:

1. **Use JDBC Sink to write to a database, then export to S3** (not ideal)
2. **Use a custom sink connector** (requires development)
3. **Use Kafka Streams to write to S3** (requires additional setup)
4. **Use AWS Kinesis Firehose** (if using AWS)

## After Installation

Once the S3 Sink Connector is installed:

1. Restart the backend (if needed)
2. Try starting the pipeline again:
   ```bash
   python3 start_specific_pipeline.py
   ```

The pipeline should now be able to create the S3 sink connector successfully.

## Required Dependencies

The S3 Sink Connector requires:
- AWS SDK for Java (included in the connector)
- Proper AWS credentials (access key and secret key)
- S3 bucket with appropriate permissions

Make sure your S3 connection in the CDC application has:
- Valid AWS Access Key ID
- Valid AWS Secret Access Key
- Correct S3 bucket name
- Appropriate IAM permissions (read/write to the bucket)


