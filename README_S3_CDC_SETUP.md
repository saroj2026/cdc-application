# S3 CDC Setup - Complete Guide

## ✅ What's Been Done

### Code Implementation
1. ✅ **S3 Sink Configuration Generator** (`ingestion/sink_config.py`)
   - Added `_generate_s3_sink_config()` method
   - Generates Confluent S3 Sink connector configuration
   - Handles AWS credentials, bucket, prefix, region

2. ✅ **CDC Manager Updated** (`ingestion/cdc_manager.py`)
   - Removed S3 skip logic
   - Now creates S3 sink connector for S3 targets
   - Full CDC flow: Debezium → Kafka → S3 Sink

3. ✅ **Kafka Configuration** (`ingestion/api.py`)
   - Configured to use remote Kafka: `http://72.61.233.209:8083`

## 📦 What You Need to Do

### Step 1: Install S3 Connector to Kafka Connect

**Copy the connector JAR files to your Kafka Connect container on the VPS:**

```bash
# From your local machine (if you have Docker access to VPS)
docker cp confluentinc-kafka-connect-s3-11.0.8/confluentinc-kafka-connect-s3-11.0.8/lib/. kafka-connect-cdc:/kafka/connect/

# Or if you need to copy via SSH first, then:
# 1. Copy files to VPS
scp -r confluentinc-kafka-connect-s3-11.0.8 user@72.61.233.209:/tmp/

# 2. SSH to VPS and copy to container
ssh user@72.61.233.209
docker cp /tmp/confluentinc-kafka-connect-s3-11.0.8/confluentinc-kafka-connect-s3-11.0.8/lib/. kafka-connect-cdc:/kafka/connect/
```

### Step 2: Restart Kafka Connect

```bash
docker restart kafka-connect-cdc
```

Wait 30-60 seconds for it to fully restart.

### Step 3: Verify Installation

```bash
curl http://72.61.233.209:8083/connector-plugins | grep -i "S3SinkConnector"
```

You should see:
```json
{
  "class": "io.confluent.connect.s3.S3SinkConnector",
  "type": "sink",
  "version": "11.0.8"
}
```

## 🚀 How CDC Will Work

### Complete Flow

```
PostgreSQL → Debezium Connector → Kafka Topics → S3 Sink Connector → S3 Bucket
```

1. **Debezium**: Captures changes from PostgreSQL WAL
2. **Kafka**: Stores change events in topics
3. **S3 Sink**: Consumes from Kafka and writes to S3
4. **S3**: Files created with change data

### File Format in S3

```
mycdcbucket26/
  department/
    topic=department/
      partition=0/
        department+0+0000000000.json
        department+0+0000000003.json
```

## 📝 Configuration Details

The S3 sink connector will be configured with:

- **Connector Class**: `io.confluent.connect.s3.S3SinkConnector`
- **Format**: JSON
- **Bucket**: From S3 connection `database` field
- **Prefix**: From S3 connection `schema` field
- **Region**: From connection `additional_config.region_name`
- **AWS Credentials**: From connection `username` and `password`
- **Flush Size**: Configurable (default from batch_size)

## ✅ Testing After Installation

1. **Create CDC Pipeline**:
   ```python
   {
     "mode": "full_load_and_cdc",
     "source_tables": ["department"],
     "target_connection_id": "<s3_conn_id>"
   }
   ```

2. **Start Pipeline**: Will create both Debezium and S3 sink connectors

3. **Make Changes**: Add/update records in PostgreSQL `department` table

4. **Verify**: Check S3 bucket for new files with change data

## 📚 Documentation Files Created

- `S3_SINK_SETUP.md` - Detailed setup guide
- `INSTALL_S3_CONNECTOR.md` - Quick installation steps
- `SETUP_SUMMARY.md` - Summary of changes
- `install_s3_connector.sh` - Installation script

## ⚠️ Important Notes

1. **All JAR files** from the `lib/` directory must be copied
2. **Kafka Connect must be restarted** after copying
3. **AWS credentials** must be correct in S3 connection
4. **Bucket permissions** must allow writes

## 🎯 Status

- ✅ Code implementation: **Complete**
- ✅ Configuration: **Ready**
- ⏳ Connector installation: **Needs to be done on VPS**
- ⏳ Testing: **After installation**

Once you install the connector JARs to Kafka Connect, the complete CDC flow will work!


## ✅ What's Been Done

### Code Implementation
1. ✅ **S3 Sink Configuration Generator** (`ingestion/sink_config.py`)
   - Added `_generate_s3_sink_config()` method
   - Generates Confluent S3 Sink connector configuration
   - Handles AWS credentials, bucket, prefix, region

2. ✅ **CDC Manager Updated** (`ingestion/cdc_manager.py`)
   - Removed S3 skip logic
   - Now creates S3 sink connector for S3 targets
   - Full CDC flow: Debezium → Kafka → S3 Sink

3. ✅ **Kafka Configuration** (`ingestion/api.py`)
   - Configured to use remote Kafka: `http://72.61.233.209:8083`

## 📦 What You Need to Do

### Step 1: Install S3 Connector to Kafka Connect

**Copy the connector JAR files to your Kafka Connect container on the VPS:**

```bash
# From your local machine (if you have Docker access to VPS)
docker cp confluentinc-kafka-connect-s3-11.0.8/confluentinc-kafka-connect-s3-11.0.8/lib/. kafka-connect-cdc:/kafka/connect/

# Or if you need to copy via SSH first, then:
# 1. Copy files to VPS
scp -r confluentinc-kafka-connect-s3-11.0.8 user@72.61.233.209:/tmp/

# 2. SSH to VPS and copy to container
ssh user@72.61.233.209
docker cp /tmp/confluentinc-kafka-connect-s3-11.0.8/confluentinc-kafka-connect-s3-11.0.8/lib/. kafka-connect-cdc:/kafka/connect/
```

### Step 2: Restart Kafka Connect

```bash
docker restart kafka-connect-cdc
```

Wait 30-60 seconds for it to fully restart.

### Step 3: Verify Installation

```bash
curl http://72.61.233.209:8083/connector-plugins | grep -i "S3SinkConnector"
```

You should see:
```json
{
  "class": "io.confluent.connect.s3.S3SinkConnector",
  "type": "sink",
  "version": "11.0.8"
}
```

## 🚀 How CDC Will Work

### Complete Flow

```
PostgreSQL → Debezium Connector → Kafka Topics → S3 Sink Connector → S3 Bucket
```

1. **Debezium**: Captures changes from PostgreSQL WAL
2. **Kafka**: Stores change events in topics
3. **S3 Sink**: Consumes from Kafka and writes to S3
4. **S3**: Files created with change data

### File Format in S3

```
mycdcbucket26/
  department/
    topic=department/
      partition=0/
        department+0+0000000000.json
        department+0+0000000003.json
```

## 📝 Configuration Details

The S3 sink connector will be configured with:

- **Connector Class**: `io.confluent.connect.s3.S3SinkConnector`
- **Format**: JSON
- **Bucket**: From S3 connection `database` field
- **Prefix**: From S3 connection `schema` field
- **Region**: From connection `additional_config.region_name`
- **AWS Credentials**: From connection `username` and `password`
- **Flush Size**: Configurable (default from batch_size)

## ✅ Testing After Installation

1. **Create CDC Pipeline**:
   ```python
   {
     "mode": "full_load_and_cdc",
     "source_tables": ["department"],
     "target_connection_id": "<s3_conn_id>"
   }
   ```

2. **Start Pipeline**: Will create both Debezium and S3 sink connectors

3. **Make Changes**: Add/update records in PostgreSQL `department` table

4. **Verify**: Check S3 bucket for new files with change data

## 📚 Documentation Files Created

- `S3_SINK_SETUP.md` - Detailed setup guide
- `INSTALL_S3_CONNECTOR.md` - Quick installation steps
- `SETUP_SUMMARY.md` - Summary of changes
- `install_s3_connector.sh` - Installation script

## ⚠️ Important Notes

1. **All JAR files** from the `lib/` directory must be copied
2. **Kafka Connect must be restarted** after copying
3. **AWS credentials** must be correct in S3 connection
4. **Bucket permissions** must allow writes

## 🎯 Status

- ✅ Code implementation: **Complete**
- ✅ Configuration: **Ready**
- ⏳ Connector installation: **Needs to be done on VPS**
- ⏳ Testing: **After installation**

Once you install the connector JARs to Kafka Connect, the complete CDC flow will work!

