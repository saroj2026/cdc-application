# What Are Offsets? - Complete Explanation

## Simple Definition

**Offset** = A unique number that identifies the position of a message in a Kafka topic partition.

Think of it like a **page number** in a book:
- Each message in a Kafka topic has an offset number
- Offsets start at 0 and increase sequentially
- They never decrease or repeat
- They're unique within a partition

## Visual Example

```
Kafka Topic Partition:
┌─────────────────────────────────────────┐
│ Partition 0                             │
├─────────────────────────────────────────┤
│ [0] [1] [2] [3] [4] [5] [6] [7] [8]... │
│  ↑   ↑   ↑   ↑   ↑   ↑   ↑   ↑   ↑      │
│ Offset numbers (like line numbers)      │
└─────────────────────────────────────────┘
```

**Example**:
- Message at offset 0: First message ever written
- Message at offset 5: Sixth message (0-indexed)
- Message at offset 100: 101st message

## How Offsets Work

### 1. Message Writing

When a message is written to Kafka:
```
Producer writes message → Kafka assigns offset → Message stored
```

**Example**:
```
Message: {"id": 1, "name": "Department A"}
→ Written to partition 0
→ Assigned offset: 12345
→ Stored at position 12345
```

### 2. Message Reading

When a consumer reads from Kafka:
```
Consumer requests messages → Kafka returns from offset X → Consumer processes
```

**Example**:
```
Consumer: "Give me messages starting from offset 12340"
Kafka: Returns messages at offsets 12340, 12341, 12342, 12343, 12344, 12345
Consumer: Processes them, then commits offset 12345
```

### 3. Offset Committing

After processing, consumer commits the offset:
```
Consumer processes message → Commits offset → Kafka remembers position
```

**Why This Matters**:
- If consumer crashes, it can resume from last committed offset
- No message loss or duplicate processing

## Types of Offsets

### 1. Current Offset (High Water Mark)

**What**: Last offset written to the partition

**Example**: If 1000 messages written, current offset = 999 (0-indexed)

**Query**:
```bash
kafka-run-class.sh kafka.tools.GetOffsetShell \
  --broker-list localhost:9092 \
  --topic my-topic --partitions 0
```

### 2. Consumer Offset (Committed Offset)

**What**: Last offset that consumer has committed (processed)

**Example**: Consumer processed up to offset 950, so committed offset = 950

**Stored**: In Kafka's `__consumer_offsets` topic

**Query**:
```bash
kafka-consumer-groups.sh --bootstrap-server localhost:9092 \
  --group my-consumer-group --describe
```

### 3. Lag (Offset Lag)

**What**: Difference between current offset and consumer offset

**Formula**: `Lag = Current Offset - Consumer Offset`

**Example**:
- Current offset: 1000
- Consumer offset: 950
- Lag: 50 messages (consumer is 50 messages behind)

## Offsets in CDC System

### 1. Debezium (Source Connector)

**Role**: Producer - writes messages to Kafka

**Offsets**:
- Debezium doesn't track offsets (it's a producer)
- It reads from PostgreSQL replication slot (LSN)
- Publishes changes to Kafka topics
- Kafka assigns offsets automatically

**Flow**:
```
PostgreSQL Change (LSN: 0/28ABE88)
  ↓
Debezium captures
  ↓
Publishes to Kafka
  ↓
Kafka assigns offset: 12345
```

### 2. Sink Connector (Consumer)

**Role**: Consumer - reads messages from Kafka

**Offsets**:
- Tracks which messages it has consumed
- Commits offset after successful write
- Can resume from last committed offset

**Flow**:
```
Kafka Topic (offset 12345 available)
  ↓
Sink Connector reads offset 12340
  ↓
Processes messages 12340-12345
  ↓
Writes to target database
  ↓
Commits offset 12345
```

### 3. Offset Storage

**Where Stored**:
1. **Kafka `__consumer_offsets` topic**: Primary storage
2. **Kafka Connect offset storage**: Connector state
3. **Application database** (optional): `pipeline_metrics.target_offset`

## Real-World Example

### Scenario: CDC Pipeline Processing

```
1. PostgreSQL Transaction
   INSERT INTO department (name) VALUES ('Sales')
   LSN: 0/298E958

2. Debezium Captures
   Reads from slot (LSN: 0/28ABE88)
   Publishes to Kafka topic
   Topic: PostgreSQL_to_S3_cdctest.public.department
   Partition: 0
   Offset: 12345 ← Kafka assigns this

3. Kafka Stores
   Message at offset 12345
   Current offset: 12345
   Consumer offset: 12340 (Sink connector hasn't processed yet)
   Lag: 5 messages

4. Sink Connector Consumes
   Reads offset 12340 (next to process)
   Processes messages 12340, 12341, 12342, 12343, 12344
   Writes to S3
   Commits offset 12344

5. Next Cycle
   Reads offset 12345
   Processes message
   Commits offset 12345
   Lag: 0 (caught up!)
```

## Offset Properties

### 1. Immutable

- Offsets never change once assigned
- They only increase
- Cannot delete or modify

### 2. Sequential

- Offsets are assigned in order
- No gaps (unless messages deleted with retention)
- Always increasing

### 3. Partition-Specific

- Each partition has its own offset sequence
- Partition 0: offsets 0, 1, 2, 3...
- Partition 1: offsets 0, 1, 2, 3... (separate sequence)

### 4. Persistent

- Stored in Kafka's log files
- Survives broker restarts
- Can be replayed from any offset

## How to Check Offsets

### Method 1: Kafka Consumer Groups

```bash
kafka-consumer-groups.sh \
  --bootstrap-server 72.61.233.209:9092 \
  --group sink-postgresql_to_s3_cdctest-s3-public \
  --describe
```

**Output**:
```
TOPIC                          PARTITION  CURRENT-OFFSET  LAG
PostgreSQL_to_S3_cdctest...    0          12345          0
```

**Fields**:
- `CURRENT-OFFSET`: Last offset in partition
- `LAG`: Messages not yet consumed

### Method 2: Get Topic Offsets

```bash
kafka-run-class.sh kafka.tools.GetOffsetShell \
  --broker-list 72.61.233.209:9092 \
  --topic PostgreSQL_to_S3_cdctest.public.department \
  --partitions 0
```

**Output**: `PostgreSQL_to_S3_cdctest.public.department:0:12345`

### Method 3: Kafka Connect API

```bash
curl "http://72.61.233.209:8083/connectors/sink-postgresql_to_s3_cdctest-s3-public/status"
```

**Returns**: Connector status including offset information

## Offset vs LSN Comparison

| Aspect | Offset | LSN |
|--------|--------|-----|
| **What** | Message position in Kafka | Transaction position in PostgreSQL WAL |
| **Format** | Integer (0, 1, 2, 3...) | Hexadecimal ("0/28ABE88") |
| **Scope** | Per topic/partition | Database-wide |
| **Stored** | Kafka `__consumer_offsets` | PostgreSQL replication slot |
| **Used By** | Kafka consumers | PostgreSQL replication |
| **Purpose** | Track message consumption | Track transaction processing |

## Common Offset Operations

### 1. Reset Offset (Start from Beginning)

```bash
kafka-consumer-groups.sh \
  --bootstrap-server localhost:9092 \
  --group my-group \
  --reset-offsets \
  --to-earliest \
  --topic my-topic \
  --execute
```

### 2. Reset Offset (Start from End)

```bash
kafka-consumer-groups.sh \
  --bootstrap-server localhost:9092 \
  --group my-group \
  --reset-offsets \
  --to-latest \
  --topic my-topic \
  --execute
```

### 3. Reset Offset (Specific Position)

```bash
kafka-consumer-groups.sh \
  --bootstrap-server localhost:9092 \
  --group my-group \
  --reset-offsets \
  --to-offset 1000 \
  --topic my-topic \
  --execute
```

## Why Offsets Matter

### 1. **Fault Tolerance**

If consumer crashes:
- Can resume from last committed offset
- No message loss
- No duplicate processing

### 2. **Scalability**

Multiple consumers can process different partitions:
- Partition 0: Consumer A (offset 1000)
- Partition 1: Consumer B (offset 2000)
- Parallel processing

### 3. **Monitoring**

Track processing progress:
- Lag = Current - Committed
- High lag = Consumer falling behind
- Low lag = Consumer keeping up

### 4. **Replay Capability**

Can reprocess messages:
- Reset offset to earlier position
- Replay from that point
- Useful for debugging or reprocessing

## Summary

**Offset** = A sequential number identifying message position in a Kafka topic partition.

**Key Points**:
- ✅ Integer number (0, 1, 2, 3...)
- ✅ Unique within a partition
- ✅ Always increasing
- ✅ Stored in Kafka `__consumer_offsets` topic
- ✅ Used to track consumer progress
- ✅ Enables fault tolerance and replay

**In CDC Context**:
- Debezium publishes messages → Kafka assigns offsets
- Sink connector consumes → Tracks offsets
- Offset lag = How far behind consumer is
- Committed offset = Last successfully processed message


