# CDC Troubleshooting Summary - Consumer Group DEAD Issue

## Current Status

✅ **All Setup Complete:**
- Debezium source connector: RUNNING
- Snowflake sink connector: RUNNING (but not consuming)
- Transforms configured: `extractPayload` → `extractAfter`
- Table exists in Snowflake
- Consumer group explicitly configured: `connect-sink-ps_sn_p-snowflake-public`

❌ **Issue:**
- Consumer group shows **DEAD state (0 members)**
- Connector reports RUNNING but not actually consuming messages
- No data flowing to Snowflake (0 rows)

## Root Cause Analysis

The connector task is in RUNNING state but the consumer group has 0 members, which means:
1. The connector task isn't actually subscribing to the Kafka topic
2. There's a Kafka Connect worker issue preventing task execution
3. The task might be failing silently during initialization

## What We've Tried

1. ✅ Configured transforms correctly (`extractPayload` → `extractAfter`)
2. ✅ Created Snowflake table
3. ✅ Set explicit consumer group ID
4. ✅ Restarted connector multiple times
5. ✅ Paused/resumed connector
6. ✅ Deleted and recreated connector

## Next Steps to Diagnose

### 1. Check Kafka Connect Worker Logs

On the Kafka Connect server (72.61.233.209), check the worker logs:

```bash
# If using Docker:
docker logs <kafka-connect-container> --tail 100

# Look for:
# - Connector task initialization errors
# - Consumer group subscription errors
# - Any exceptions during task startup
```

### 2. Verify Kafka Connect Worker Configuration

Check if the worker can connect to Kafka brokers:
- Worker configuration file
- Bootstrap servers configuration
- Network connectivity between worker and brokers

### 3. Check Consumer Group Status

In Kafka UI or using kafka-consumer-groups.sh:
```bash
kafka-consumer-groups.sh --bootstrap-server <broker> --group connect-sink-ps_sn_p-snowflake-public --describe
```

### 4. Verify Topic Has Messages

Check if messages exist in the topic:
- Kafka UI: http://72.61.233.209:8080/ui/cluster/topic/ps_sn_p.public.projects_simple
- Verify messages are at offsets the connector is trying to consume

### 5. Check Task Initialization

The connector task might be failing during initialization. Check:
- Task state transitions (should go: UNASSIGNED → RUNNING)
- Any errors during task assignment
- Worker capacity (might be at max tasks)

## Possible Solutions

### Solution 1: Restart Kafka Connect Worker

If the worker has issues, restart it:
```bash
docker restart <kafka-connect-container>
# or
systemctl restart kafka-connect
```

### Solution 2: Check Worker Task Capacity

The worker might be at max task capacity. Check worker configuration:
```
tasks.max configuration
worker capacity
```

### Solution 3: Verify Network Connectivity

Ensure Kafka Connect worker can reach:
- Kafka brokers
- Snowflake (for sink connector)
- Topic partitions

### Solution 4: Check for Silent Errors

The connector might be failing silently. Enable debug logging:
```
log4j.logger.org.apache.kafka.connect=DEBUG
```

### Solution 5: Try Different Connector Configuration

As a test, try creating a simple sink connector without transforms to see if the issue is transform-related.

## Current Configuration

**Connector Name:** `sink-ps_sn_p-snowflake-public`

**Key Configuration:**
- Topics: `ps_sn_p.public.projects_simple`
- Value Converter: `com.snowflake.kafka.connector.records.SnowflakeJsonConverter`
- Transforms: `extractPayload,extractAfter`
- Consumer Group: `connect-sink-ps_sn_p-snowflake-public`
- Database: `seg`
- Schema: `public`
- Table: `projects_simple`

## Expected Behavior

When working correctly:
1. Connector task subscribes to topic → Consumer group shows active members
2. Task consumes messages from topic
3. Transforms extract `payload.after` from Debezium envelope
4. SnowflakeJsonConverter processes the JSON
5. Data is written to Snowflake table

## Verification Commands

```bash
# Check connector status
curl http://72.61.233.209:8083/connectors/sink-ps_sn_p-snowflake-public/status

# Check consumer group
kafka-consumer-groups.sh --bootstrap-server <broker> --group connect-sink-ps_sn_p-snowflake-public --describe

# Check topic messages
kafka-console-consumer.sh --bootstrap-server <broker> --topic ps_sn_p.public.projects_simple --from-beginning
```

## Contact Points

- Kafka Connect API: http://72.61.233.209:8083
- Kafka UI: http://72.61.233.209:8080
- Connector: `sink-ps_sn_p-snowflake-public`
- Consumer Group: `connect-sink-ps_sn_p-snowflake-public`
- Topic: `ps_sn_p.public.projects_simple`

