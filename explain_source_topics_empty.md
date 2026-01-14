# Why Source Connector Topics Column is Empty

## Summary

The Debezium Oracle source connector (`cdc-oracle_sf_p-ora-cdc_user`) is showing an empty topics list in the Kafka UI, even though the connector is **RUNNING**.

## Why This Happens

### 1. **Snapshot Mode: `initial_only`**
- The connector is configured with `snapshot.mode: initial_only`
- In this mode, the connector takes a **schema-only snapshot** (no data)
- Topics are created when the connector **first produces messages**
- Since `initial_only` doesn't produce data messages during snapshot, topics may not be created yet

### 2. **Topics Created on First Message**
- Kafka topics are created when the connector **first writes a message**
- The `/connectors/{connector}/topics` API only returns topics that have been **actively used** (messages written)
- If no messages have been written yet, the API returns an empty list

### 3. **This is Normal Behavior**
- For `initial_only` snapshot mode, topics are created when:
  - **CDC changes occur** (INSERT/UPDATE/DELETE after snapshot)
  - The connector captures the first change event
  - The connector writes the first message to the topic

## Current Status

✅ **Connector is RUNNING** - This is the most important status
✅ **Task is RUNNING** - The connector task is operational
✅ **No errors** - The connector is working correctly
⚠️ **Topics empty** - This is expected for `initial_only` mode until first CDC event

## When Topics Will Appear

Topics will appear in the API/UI when:
1. The connector captures the **first CDC change** (INSERT/UPDATE/DELETE)
2. The connector writes the **first message** to the topic
3. After that, topics will be visible in the `/connectors/{connector}/topics` API

## Verification

You can verify topics exist in Kafka even if the connector API doesn't report them:
- Check Kafka directly: Topics may exist but not be "active" yet
- Check after CDC events: Topics will appear after first change is captured

## Conclusion

**This is NORMAL and EXPECTED behavior** for `initial_only` snapshot mode. The connector is working correctly. Topics will appear when the first CDC change is captured.

