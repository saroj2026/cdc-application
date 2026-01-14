# Kafka Offsets vs LSN - How CDC Tracks Progress

## Quick Answer

**Kafka stores OFFSETS, not LSN directly.**

- **Kafka**: Stores consumer offsets (partition + offset number)
- **PostgreSQL**: Stores LSN (Log Sequence Number)
- **Relationship**: Kafka offsets track which messages have been consumed, while LSN tracks the source database position

## What Kafka Stores

### 1. Consumer Offsets

**Location**: Kafka internal topic `__consumer_offsets`

**Format**: 
- Topic name
- Partition number
- Offset number (byte position in partition)

**Example**:
```
Topic: PostgreSQL_to_S3_cdctest.public.department
Partition: 0
Offset: 12345
```

**What This Means**:
- Consumer has processed up to message #12345 in partition 0
- Next message to read: offset 12346

### 2. How Offsets Work

```
Kafka Topic Partition:
[0] [1] [2] [3] [4] [5] [6] [7] [8] [9] ...
                    ↑
              Current Offset = 5
              (Next to read: 6)
```

## What PostgreSQL Stores

### LSN (Log Sequence Number)

**Location**: PostgreSQL WAL (Write-Ahead Log)

**Format**: `0/28ABE88` (hexadecimal)

**What This Means**:
- Position in PostgreSQL transaction log
- Exact byte position in WAL file

## How They Work Together in CDC

### The Flow

```
1. POSTGRESQL (Source)
   └─ LSN: 0/298E958 (current WAL position)
      └─ New transaction written here
      
2. DEBEZIUM (CDC Connector)
   └─ Reads from replication slot
   └─ Slot LSN: 0/28ABE88 (CDC position)
   └─ Publishes to Kafka topic
      └─ Topic: PostgreSQL_to_S3_cdctest.public.department
      └─ Partition: 0
      └─ Offset: 12345 (last published)
      
3. KAFKA
   └─ Stores messages with offsets
   └─ Consumer offset: 12340 (last consumed)
   └─ Gap: 5 messages (12345 - 12340)
   
4. SINK CONNECTOR (Consumer)
   └─ Reads from Kafka
   └─ Current offset: 12340
   └─ Commits offset after processing
```

## Where Offsets Are Stored in This System

### 1. Kafka Internal Topic: `__consumer_offsets`

**Location**: Kafka cluster (not in application database)

**What's Stored**:
- Consumer group ID
- Topic name
- Partition number
- Offset number
- Timestamp

**How to Check**:
```bash
# Connect to Kafka
kafka-consumer-groups.sh --bootstrap-server 72.61.233.209:9092 \
  --group {connector_group} --describe
```

### 2. Pipeline Metrics (Optional Tracking)

**Location**: `pipeline_metrics` table in application database

**Fields**:
- `source_offset`: Source LSN at time of measurement
- `target_offset`: Kafka offset or processed position

**Code**: `ingestion/database/models_db.py` line 195-196

```python
source_offset = Column(Text, nullable=True)  # Source LSN
target_offset = Column(Text, nullable=True)  # Kafka offset or target LSN
```

### 3. Debezium Connector State

**Location**: Kafka Connect internal storage

**What's Stored**:
- Connector configuration
- Last processed offset per partition
- Connector state (RUNNING, FAILED, etc.)

**How to Check**:
```bash
curl "http://72.61.233.209:8083/connectors/{connector_name}/status"
```

## Key Differences

| Aspect | Kafka Offset | PostgreSQL LSN |
|--------|-------------|----------------|
| **What It Tracks** | Message position in Kafka topic | Transaction position in WAL |
| **Format** | Integer (0, 1, 2, 3...) | Hexadecimal string ("0/28ABE88") |
| **Scope** | Per topic/partition | Database-wide |
| **Stored Where** | Kafka `__consumer_offsets` topic | PostgreSQL replication slot |
| **Used By** | Kafka consumers | PostgreSQL replication |
| **Purpose** | Track consumed messages | Track processed transactions |

## How CDC Uses Both

### 1. Source Side (Debezium)

**LSN Tracking**:
- Debezium reads from PostgreSQL replication slot
- Slot maintains `confirmed_flush_lsn` (CDC LSN)
- This is the source database position

**Kafka Publishing**:
- Debezium publishes changes to Kafka topics
- Each message gets a Kafka offset
- Offset is independent of LSN

### 2. Sink Side (Sink Connector)

**Kafka Offset Tracking**:
- Sink connector consumes from Kafka
- Tracks offset per partition
- Commits offset after successful write

**Target Database**:
- Writes changes to target database
- Target database may have its own LSN (if PostgreSQL)

## Example Flow

```
1. PostgreSQL Transaction
   LSN: 0/298E958
   INSERT INTO department (name) VALUES ('Sales')
   
2. Debezium Captures
   Reads from slot (LSN: 0/28ABE88)
   Publishes to Kafka
   Topic: PostgreSQL_to_S3_cdctest.public.department
   Partition: 0
   Offset: 12345
   
3. Kafka Stores
   Message at offset 12345
   Consumer offset: 12340 (5 messages behind)
   
4. Sink Connector Consumes
   Reads offset 12345
   Writes to S3
   Commits offset 12345
   
5. Next Cycle
   Consumer offset advances to 12346
   Source LSN advances to 0/298E959
```

## Monitoring Both

### Check Kafka Offsets

**API Endpoint**: (Not directly exposed, but can be calculated from metrics)

**Kafka Consumer Groups**:
```bash
kafka-consumer-groups.sh --bootstrap-server 72.61.233.209:9092 \
  --group sink-postgresql_to_s3_cdctest-s3-public \
  --describe
```

**Output**:
```
TOPIC                          PARTITION  CURRENT-OFFSET  LAG
PostgreSQL_to_S3_cdctest...    0          12345          0
```

### Check LSN

**API Endpoint**: `GET /api/v1/monitoring/pipelines/{pipeline_id}/lag`

**Returns**:
```json
{
  "source_lsn": "0/298E958",      // PostgreSQL WAL position
  "processed_lsn": "0/28ABE88",   // CDC LSN (from replication slot)
  "lag_bytes": 928464
}
```

## Summary

**Kafka stores OFFSETS** (not LSN):
- Offsets track message consumption in Kafka topics
- Stored in Kafka's `__consumer_offsets` topic
- Format: Integer (0, 1, 2, 3...)
- Per topic/partition

**PostgreSQL stores LSN**:
- LSN tracks transaction position in WAL
- Stored in replication slots
- Format: Hexadecimal ("0/28ABE88")
- Database-wide

**Both are used together**:
- LSN: Tracks source database position (Debezium side)
- Offset: Tracks Kafka message consumption (Sink connector side)
- Together they provide end-to-end tracking of CDC progress


