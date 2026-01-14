# Snowflake Integration Setup Guide

This guide explains how to set up Snowflake as a target database for CDC pipelines.

## Prerequisites

1. **Snowflake Account**: You need a Snowflake account with appropriate permissions
2. **Kafka Connect Snowflake Connector**: The Snowflake Kafka Connector JAR must be installed in your Kafka Connect instance
3. **Python Package**: Install `snowflake-connector-python` for the backend:
   ```bash
   pip install snowflake-connector-python
   ```

## Required Credentials

When creating a Snowflake connection in the CDC application, you need to provide the following:

### Required Fields

1. **Account** (`host` field or `additional_config.account`):
   - Your Snowflake account identifier
   - Format: `xy12345` or `xy12345.us-east-1` or full URL
   - Examples:
     - `xy12345`
     - `xy12345.us-east-1`
     - `https://xy12345.us-east-1.snowflakecomputing.com` (will be auto-stripped)

2. **Username** (`username` field):
   - Your Snowflake username
   - Example: `MY_USER`

3. **Password** (`password` field) OR **Private Key** (`additional_config.private_key`):
   - **Option 1**: Password authentication
     - Provide your Snowflake password in the `password` field
   - **Option 2**: Key pair authentication (more secure)
     - Generate a private key and provide it in `additional_config.private_key`
     - If the private key is encrypted, also provide `additional_config.private_key_passphrase`

4. **Database** (`database` field):
   - Target database name
   - Example: `MY_DATABASE`

5. **Schema** (`schema` field):
   - Target schema name (optional, defaults to `PUBLIC`)
   - Example: `MY_SCHEMA`

### Optional Fields (in `additional_config`)

1. **Warehouse** (`additional_config.warehouse`):
   - Snowflake warehouse name
   - Recommended for better performance
   - Example: `MY_WAREHOUSE`

2. **Role** (`additional_config.role`):
   - Snowflake role to use
   - Example: `MY_ROLE`

3. **Private Key** (`additional_config.private_key`):
   - PEM-encoded private key for key pair authentication
   - Alternative to password authentication
   - Example: `-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----`

4. **Private Key Passphrase** (`additional_config.private_key_passphrase`):
   - Passphrase for encrypted private key
   - Only needed if private key is encrypted

## Connection Configuration Example

### Using Password Authentication

```json
{
  "name": "Snowflake Production",
  "database_type": "snowflake",
  "host": "xy12345.us-east-1",
  "username": "MY_USER",
  "password": "my_password",
  "database": "MY_DATABASE",
  "schema": "MY_SCHEMA",
  "additional_config": {
    "warehouse": "MY_WAREHOUSE",
    "role": "MY_ROLE"
  }
}
```

### Using Key Pair Authentication

```json
{
  "name": "Snowflake Production",
  "database_type": "snowflake",
  "host": "xy12345.us-east-1",
  "username": "MY_USER",
  "password": "",  // Empty when using private key
  "database": "MY_DATABASE",
  "schema": "MY_SCHEMA",
  "additional_config": {
    "warehouse": "MY_WAREHOUSE",
    "role": "MY_ROLE",
    "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQC...\n-----END PRIVATE KEY-----",
    "private_key_passphrase": "optional_passphrase_if_encrypted"
  }
}
```

## Kafka Connect Snowflake Connector Setup

The Snowflake Kafka Connector must be installed in your Kafka Connect instance. 

### Installation Steps

1. **Download the Connector**:
   - Download the Snowflake Kafka Connector from: https://docs.snowflake.com/en/user-guide/kafka-connector-install.html
   - Or use Maven to get the JAR file

2. **Install in Kafka Connect**:
   ```bash
   # Copy the JAR to Kafka Connect plugins directory
   cp snowflake-kafka-connector-*.jar /path/to/kafka-connect/plugins/
   
   # Restart Kafka Connect
   docker restart kafka-connect-cdc
   ```

3. **Verify Installation**:
   ```bash
   # Check if connector is available
   curl http://localhost:8083/connector-plugins | grep -i snowflake
   ```

### Required Connector Class

The connector class used is: `com.snowflake.kafka.connector.SnowflakeSinkConnector`

## Pipeline Configuration

When creating a pipeline with Snowflake as the target:

1. **Source**: Any supported source (PostgreSQL, SQL Server, AS400, etc.)
2. **Target**: Select your Snowflake connection
3. **Target Database**: The Snowflake database name
4. **Target Schema**: The Snowflake schema name (will be created if it doesn't exist)
5. **Tables**: Select source tables to replicate

## Data Flow

1. **Full Load**: For Snowflake, the full load is handled by the Kafka Connect sink connector
2. **CDC**: Change data capture events are streamed to Kafka topics and then consumed by the Snowflake sink connector
3. **Table Creation**: Tables are automatically created in Snowflake based on the source schema
4. **Data Format**: Data is written in JSON format to Snowflake tables

## Table Name Mapping

- Kafka topics follow the format: `{pipeline_name}.{schema}.{table}`
- The Snowflake connector extracts the table name (last part after the last dot)
- Tables are created in the format: `{database}.{schema}.{table}`

## Buffer Configuration

The Snowflake sink connector uses the following buffer settings (configurable):

- `buffer.count.records`: Number of records to buffer before flushing (default: 10000)
- `buffer.flush.time`: Time in seconds to flush buffer (default: 60)
- `buffer.size.bytes`: Buffer size in bytes (default: 5000000 = 5MB)

## Error Handling

The connector is configured with:
- `errors.tolerance`: `all` - Continue processing even if some records fail
- `errors.log.enable`: `true` - Log errors
- `errors.log.include.messages`: `true` - Include error messages in logs

## Troubleshooting

### Connection Issues

1. **Check Account Format**: Ensure the account identifier is correct
2. **Verify Credentials**: Test connection using Snowflake web UI or CLI
3. **Check Network**: Ensure Kafka Connect can reach Snowflake (check firewall rules)

### Connector Not Found

1. **Verify JAR Installation**: Check that the Snowflake connector JAR is in the plugins directory
2. **Restart Kafka Connect**: Restart the Kafka Connect service after installing the connector
3. **Check Logs**: Review Kafka Connect logs for errors

### Data Not Appearing

1. **Check Connector Status**: Verify the sink connector is RUNNING
2. **Check Buffer Settings**: Data may be buffered - wait for flush time or reduce buffer size
3. **Check Snowflake Tables**: Verify tables exist and have correct schema
4. **Review Error Logs**: Check for any error messages in Kafka Connect logs

## Security Best Practices

1. **Use Key Pair Authentication**: Prefer private key authentication over passwords
2. **Restrict Warehouse Access**: Use appropriate warehouse sizes and auto-suspend settings
3. **Role-Based Access**: Use specific roles with minimal required permissions
4. **Network Security**: Use Snowflake network policies to restrict access
5. **Encrypt Private Keys**: If using private key authentication, encrypt the key file

## Additional Resources

- [Snowflake Kafka Connector Documentation](https://docs.snowflake.com/en/user-guide/kafka-connector.html)
- [Snowflake Connection Parameters](https://docs.snowflake.com/en/user-guide/python-connector-api.html#connect)
- [Snowflake Key Pair Authentication](https://docs.snowflake.com/en/user-guide/key-pair-auth.html)



