# S3 Sink Connector Setup Guide

## Overview

The Confluent S3 Sink connector has been integrated into the codebase. This guide explains how to install and configure it in your Kafka Connect environment.

## Prerequisites

✅ Confluent S3 Sink connector JAR files are in: `confluentinc-kafka-connect-s3-11.0.8/`

## Installation Steps

### Step 1: Copy Connector to Kafka Connect

You need to copy the connector JAR files to your Kafka Connect container on the VPS server (72.61.233.209).

**Option A: Copy via Docker**

```bash
# Copy the entire lib directory to Kafka Connect container
docker cp confluentinc-kafka-connect-s3-11.0.8/confluentinc-kafka-connect-s3-11.0.8/lib/. kafka-connect-cdc:/kafka/connect/

# Or copy specific JAR files
docker cp confluentinc-kafka-connect-s3-11.0.8/confluentinc-kafka-connect-s3-11.0.8/lib/kafka-connect-s3-11.0.8.jar kafka-connect-cdc:/kafka/connect/
```

**Option B: Mount Volume (Recommended)**

If using docker-compose, add volume mount:
```yaml
kafka-connect-cdc:
  volumes:
    - ./confluentinc-kafka-connect-s3-11.0.8/confluentinc-kafka-connect-s3-11.0.8/lib:/kafka/connect/s3-connector
```

**Option C: SSH and Copy**

```bash
# From your local machine
scp -r confluentinc-kafka-connect-s3-11.0.8/confluentinc-kafka-connect-s3-11.0.8/lib/* user@72.61.233.209:/path/to/kafka-connect/plugins/
```

### Step 2: Restart Kafka Connect

After copying the JAR files, restart the Kafka Connect container:

```bash
docker restart kafka-connect-cdc
```

### Step 3: Verify Installation

Check if the connector is available:

```bash
curl http://72.61.233.209:8083/connector-plugins | grep -i s3
```

You should see:
```json
{
  "class": "io.confluent.connect.s3.S3SinkConnector",
  "type": "sink",
  "version": "11.0.8"
}
```

## Configuration

The S3 sink connector is now integrated into the codebase. When you create a pipeline with:
- **Mode**: `full_load_and_cdc` or `cdc_only`
- **Target**: S3 connection

The system will automatically:
1. Generate S3 sink connector configuration
2. Create the connector in Kafka Connect
3. Start consuming from Kafka topics
4. Write changes to S3 bucket

## S3 Sink Configuration Details

The connector configuration includes:

- **Connector Class**: `io.confluent.connect.s3.S3SinkConnector`
- **Format**: JSON (configurable)
- **Storage**: S3 Storage
- **Partitioner**: Default (preserves Kafka partitioning)
- **AWS Credentials**: From connection configuration
- **Bucket**: From target connection database field
- **Prefix**: From target connection schema field
- **Region**: From connection additional_config

## Testing

### 1. Create CDC Pipeline

```python
pipeline_data = {
    "name": "PostgreSQL_to_S3_department_CDC",
    "source_connection_id": "<postgres_id>",
    "target_connection_id": "<s3_id>",
    "mode": "full_load_and_cdc",
    "source_tables": ["department"],
    ...
}
```

### 2. Start Pipeline

The pipeline will:
- Run full load
- Create Debezium connector
- Create S3 sink connector
- Start streaming changes to S3

### 3. Verify

- Check connector status: `GET /api/pipelines/{id}`
- Check S3 bucket for new files
- Make changes to PostgreSQL and verify they appear in S3

## Troubleshooting

### Connector Not Found

If you get "Connector class not found":
1. Verify JAR files are in the correct location
2. Check Kafka Connect logs: `docker logs kafka-connect-cdc`
3. Restart Kafka Connect container

### Permission Errors

If you get AWS permission errors:
1. Verify AWS credentials in connection
2. Check IAM permissions for S3 bucket
3. Verify bucket name and region

### No Data in S3

1. Check connector status: `GET /connectors/{connector_name}/status`
2. Check Kafka topics have data
3. Verify flush.size configuration
4. Check S3 bucket prefix/path

## File Structure in S3

The connector will create files like:
```
bucket/
  prefix/
    topic=department/
      partition=0/
        department+0+0000000000.json
        department+0+0000000003.json
```

## Next Steps

1. ✅ Copy connector JARs to Kafka Connect
2. ✅ Restart Kafka Connect
3. ✅ Verify connector is available
4. ✅ Create/start CDC pipeline
5. ✅ Test with real changes

## Code Changes Made

1. **`ingestion/sink_config.py`**:
   - Added `_generate_s3_sink_config()` method
   - Generates Confluent S3 Sink connector configuration

2. **`ingestion/cdc_manager.py`**:
   - Removed S3 skip logic
   - Now creates S3 sink connector for S3 targets

3. **Configuration**:
   - Uses AWS credentials from connection
   - Configures bucket, prefix, region
   - Sets JSON format and partitioning


## Overview

The Confluent S3 Sink connector has been integrated into the codebase. This guide explains how to install and configure it in your Kafka Connect environment.

## Prerequisites

✅ Confluent S3 Sink connector JAR files are in: `confluentinc-kafka-connect-s3-11.0.8/`

## Installation Steps

### Step 1: Copy Connector to Kafka Connect

You need to copy the connector JAR files to your Kafka Connect container on the VPS server (72.61.233.209).

**Option A: Copy via Docker**

```bash
# Copy the entire lib directory to Kafka Connect container
docker cp confluentinc-kafka-connect-s3-11.0.8/confluentinc-kafka-connect-s3-11.0.8/lib/. kafka-connect-cdc:/kafka/connect/

# Or copy specific JAR files
docker cp confluentinc-kafka-connect-s3-11.0.8/confluentinc-kafka-connect-s3-11.0.8/lib/kafka-connect-s3-11.0.8.jar kafka-connect-cdc:/kafka/connect/
```

**Option B: Mount Volume (Recommended)**

If using docker-compose, add volume mount:
```yaml
kafka-connect-cdc:
  volumes:
    - ./confluentinc-kafka-connect-s3-11.0.8/confluentinc-kafka-connect-s3-11.0.8/lib:/kafka/connect/s3-connector
```

**Option C: SSH and Copy**

```bash
# From your local machine
scp -r confluentinc-kafka-connect-s3-11.0.8/confluentinc-kafka-connect-s3-11.0.8/lib/* user@72.61.233.209:/path/to/kafka-connect/plugins/
```

### Step 2: Restart Kafka Connect

After copying the JAR files, restart the Kafka Connect container:

```bash
docker restart kafka-connect-cdc
```

### Step 3: Verify Installation

Check if the connector is available:

```bash
curl http://72.61.233.209:8083/connector-plugins | grep -i s3
```

You should see:
```json
{
  "class": "io.confluent.connect.s3.S3SinkConnector",
  "type": "sink",
  "version": "11.0.8"
}
```

## Configuration

The S3 sink connector is now integrated into the codebase. When you create a pipeline with:
- **Mode**: `full_load_and_cdc` or `cdc_only`
- **Target**: S3 connection

The system will automatically:
1. Generate S3 sink connector configuration
2. Create the connector in Kafka Connect
3. Start consuming from Kafka topics
4. Write changes to S3 bucket

## S3 Sink Configuration Details

The connector configuration includes:

- **Connector Class**: `io.confluent.connect.s3.S3SinkConnector`
- **Format**: JSON (configurable)
- **Storage**: S3 Storage
- **Partitioner**: Default (preserves Kafka partitioning)
- **AWS Credentials**: From connection configuration
- **Bucket**: From target connection database field
- **Prefix**: From target connection schema field
- **Region**: From connection additional_config

## Testing

### 1. Create CDC Pipeline

```python
pipeline_data = {
    "name": "PostgreSQL_to_S3_department_CDC",
    "source_connection_id": "<postgres_id>",
    "target_connection_id": "<s3_id>",
    "mode": "full_load_and_cdc",
    "source_tables": ["department"],
    ...
}
```

### 2. Start Pipeline

The pipeline will:
- Run full load
- Create Debezium connector
- Create S3 sink connector
- Start streaming changes to S3

### 3. Verify

- Check connector status: `GET /api/pipelines/{id}`
- Check S3 bucket for new files
- Make changes to PostgreSQL and verify they appear in S3

## Troubleshooting

### Connector Not Found

If you get "Connector class not found":
1. Verify JAR files are in the correct location
2. Check Kafka Connect logs: `docker logs kafka-connect-cdc`
3. Restart Kafka Connect container

### Permission Errors

If you get AWS permission errors:
1. Verify AWS credentials in connection
2. Check IAM permissions for S3 bucket
3. Verify bucket name and region

### No Data in S3

1. Check connector status: `GET /connectors/{connector_name}/status`
2. Check Kafka topics have data
3. Verify flush.size configuration
4. Check S3 bucket prefix/path

## File Structure in S3

The connector will create files like:
```
bucket/
  prefix/
    topic=department/
      partition=0/
        department+0+0000000000.json
        department+0+0000000003.json
```

## Next Steps

1. ✅ Copy connector JARs to Kafka Connect
2. ✅ Restart Kafka Connect
3. ✅ Verify connector is available
4. ✅ Create/start CDC pipeline
5. ✅ Test with real changes

## Code Changes Made

1. **`ingestion/sink_config.py`**:
   - Added `_generate_s3_sink_config()` method
   - Generates Confluent S3 Sink connector configuration

2. **`ingestion/cdc_manager.py`**:
   - Removed S3 skip logic
   - Now creates S3 sink connector for S3 targets

3. **Configuration**:
   - Uses AWS credentials from connection
   - Configures bucket, prefix, region
   - Sets JSON format and partitioning

