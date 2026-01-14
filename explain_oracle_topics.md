# Why There Are 2 Topics for Oracle Connector

## Summary

The Oracle Debezium connector creates **2 topics** - this is **NORMAL and EXPECTED** behavior:

1. **Table Data Topic**: `oracle_sf_p.CDC_USER.TEST`
   - Contains DML changes (INSERT, UPDATE, DELETE)
   - One topic per table being monitored
   - Format: `{topic.prefix}.{schema}.{table}`

2. **Schema Change Topic**: `oracle_sf_p`
   - Contains DDL changes (CREATE TABLE, ALTER TABLE, etc.)
   - Named after `topic.prefix` (which is `oracle_sf_p`)
   - Records structural changes to the database schema

## Details

### 1. Table Data Topic: `oracle_sf_p.CDC_USER.TEST`
- **Purpose**: Captures data changes (INSERT, UPDATE, DELETE)
- **Format**: `{topic.prefix}.{schema}.{table}`
- **Used by**: Sink connector to replicate data changes to Snowflake

### 2. Schema Change Topic: `oracle_sf_p`
- **Purpose**: Captures schema changes (CREATE TABLE, ALTER TABLE, DROP TABLE, etc.)
- **Format**: `{topic.prefix}` (just the prefix)
- **Used by**: Schema evolution, tracking structural changes
- **Note**: This is different from the schema history topic (`oracle_sf_p.schema.history.internal`)

## Is This a Problem?

**NO!** This is the **correct and expected** behavior according to Debezium documentation.

The schema change topic is used for:
- Tracking DDL changes
- Schema evolution
- Notifying consumers about structural changes
- Maintaining schema consistency

## Sink Connector Behavior

The Snowflake sink connector should be configured to consume from:
- **Primary topic**: `oracle_sf_p.CDC_USER.TEST` (data changes)
- **Schema topic**: `oracle_sf_p` (optional - for schema tracking)

In our case, the sink connector is configured to consume from the data topic, so the schema change topic is not used by the sink. It's created by Debezium for schema tracking purposes.

## Verification

You can verify both topics are working:
- Table topic (`oracle_sf_p.CDC_USER.TEST`): Should have messages from INSERT/UPDATE/DELETE operations
- Schema topic (`oracle_sf_p`): Should have messages from DDL operations (if any occurred)

## Conclusion

Having 2 topics is **NORMAL** - it's how Debezium Oracle connector works. The connector is functioning correctly!

