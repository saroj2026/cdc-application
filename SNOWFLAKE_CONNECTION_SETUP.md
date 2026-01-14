# Snowflake Connection Configuration

## Overview

The CDC application now supports creating Snowflake connections with all required fields: Account, User, Password, Database, Schema, Warehouse, and Role.

## Changes Made

### Backend Changes

1. **API Schema (`ingestion/api.py`)**:
   - Updated `ConnectionCreate` Pydantic model to make `host` and `port` optional (required for Snowflake/S3)
   - Added logic to handle Snowflake account in `host` field or `additional_config.account`
   - Default port set to 443 for Snowflake connections

2. **Connection Service (`ingestion/connection_service.py`)**:
   - Already supports Snowflake connector initialization
   - Maps Snowflake fields from connection model to connector config:
     - `host` or `additional_config.account` → `account`
     - `username` → `user`
     - `password` → `password`
     - `database` → `database`
     - `schema` → `schema` (default: "PUBLIC")
     - `additional_config.warehouse` → `warehouse`
     - `additional_config.role` → `role`

3. **Sink Config Generator (`ingestion/sink_config.py`)**:
   - Already implements `_generate_snowflake_sink_config` method
   - Generates proper Kafka Connect Snowflake Sink Connector configuration

### Frontend Changes

1. **Connection Modal (`frontend/components/connections/connection-modal.tsx`)**:
   - Added Snowflake-specific form fields:
     - **Account** (required) - replaces Host field for Snowflake
     - **Schema** (optional, default: PUBLIC)
     - **Warehouse** (optional)
     - **Role** (optional)
   - Conditional field display based on selected database type
   - Updated validation to handle Snowflake-specific requirements
   - Updated form data handling to store Snowflake fields in `additional_config`

2. **Connection Page (`frontend/app/connections/page.tsx`)**:
   - Updated payload building to handle Snowflake fields
   - Maps Snowflake account to `host` field and `additional_config.account`
   - Includes warehouse and role in `additional_config`

## How to Create a Snowflake Connection

### Step 1: Open Connection Modal
1. Navigate to **Connections** page
2. Click **"New Connection"** button

### Step 2: Select Snowflake
1. In the database selection screen, select **Snowflake**
2. Click to proceed to configuration

### Step 3: Fill in Connection Details

#### Required Fields:
- **Connection Name**: A descriptive name (e.g., "Production Snowflake")
- **Account**: Snowflake account identifier
  - Format: `xy12345.us-east-1` or `xy12345`
  - Example: `abc12345.us-east-2`
- **Database**: Target database name
  - Example: `PROD_DB`
- **Username**: Snowflake username
  - Example: `CDC_USER`
- **Password**: Snowflake password

#### Optional Fields:
- **Schema**: Schema name (default: `PUBLIC` if not specified)
  - Example: `PUBLIC`, `ANALYTICS`, `STAGING`
- **Warehouse**: Snowflake warehouse name (recommended for better performance)
  - Example: `COMPUTE_WH`, `ANALYTICS_WH`
- **Role**: Snowflake role name (uses default role if not specified)
  - Example: `ACCOUNTADMIN`, `SYSADMIN`, `PUBLIC`

### Step 4: Test Connection
1. Click **"Test Connection"** to verify credentials
2. Wait for success message

### Step 5: Save Connection
1. Click **"Save Connection"**
2. Connection will be created and stored in the database

## Connection Data Storage

Snowflake connection data is stored as follows:

```json
{
  "id": "uuid",
  "name": "Production Snowflake",
  "database_type": "snowflake",
  "host": "xy12345.us-east-1",  // Account identifier
  "port": 443,  // Default HTTPS port
  "database": "PROD_DB",
  "username": "CDC_USER",
  "password": "***",  // Encrypted
  "schema": "PUBLIC",
  "additional_config": {
    "account": "xy12345.us-east-1",  // Account (duplicate of host)
    "warehouse": "COMPUTE_WH",  // Optional
    "role": "SYSADMIN"  // Optional
  }
}
```

## Using Snowflake in Pipelines

### Creating a Pipeline with Snowflake Target

1. Navigate to **Pipelines** page
2. Click **"New Pipeline"**
3. Select:
   - **Source**: Any supported source (AS400, PostgreSQL, SQL Server, etc.)
   - **Target**: Your Snowflake connection
4. Select tables to replicate
5. Start the pipeline

### Pipeline Configuration

When a pipeline is created with Snowflake as target:
- The system automatically generates a Snowflake Kafka Sink Connector configuration
- Tables are created in Snowflake (if `auto_create_target` is enabled)
- Data is replicated from source to Snowflake via Kafka

## Snowflake Account Format

Snowflake account identifiers can be in several formats:
- `xy12345` - Simple format
- `xy12345.us-east-1` - With region
- `xy12345.us-east-1.snowflakecomputing.com` - Full URL (will be normalized)

The system automatically normalizes the account format for the Kafka connector.

## Authentication Methods

Currently supported:
- **Password Authentication**: Username + Password (most common)

Future support (code ready, UI pending):
- **Private Key Authentication**: Username + Private Key + Optional Passphrase

For private key authentication, you would need to:
1. Generate a key pair in Snowflake
2. Store the private key in `additional_config.private_key`
3. Store the passphrase (if encrypted) in `additional_config.private_key_passphrase`

## Troubleshooting

### Connection Test Fails

1. **Check Account Format**:
   - Ensure account identifier is correct
   - Format: `xy12345` or `xy12345.us-east-1`

2. **Verify Credentials**:
   - Username and password must be correct
   - User must have necessary permissions

3. **Check Network**:
   - Ensure firewall allows connections to Snowflake
   - Default port: 443 (HTTPS)

4. **Verify Database/Schema**:
   - Database must exist
   - Schema must exist or be accessible

### Pipeline Fails to Start

1. **Check Kafka Connect**:
   - Ensure Snowflake Kafka Connector is installed
   - Verify connector appears in `/connector-plugins` endpoint

2. **Check Credentials**:
   - Verify connection credentials are correct
   - Test connection separately

3. **Check Permissions**:
   - User must have CREATE TABLE permission
   - Warehouse must be accessible (if specified)

4. **Check Logs**:
   - Review Kafka Connect logs
   - Check connector status in Kafka UI

## Example Configuration

### Minimal Configuration
```json
{
  "name": "Snowflake Prod",
  "account": "abc12345.us-east-1",
  "database": "PROD_DB",
  "username": "cdc_user",
  "password": "secure_password"
}
```

### Full Configuration
```json
{
  "name": "Snowflake Analytics",
  "account": "xyz98765.us-west-2",
  "database": "ANALYTICS_DB",
  "username": "analytics_user",
  "password": "secure_password",
  "schema": "ANALYTICS",
  "warehouse": "ANALYTICS_WH",
  "role": "ANALYTICS_ROLE"
}
```

## Related Files

- Backend API: `ingestion/api.py`
- Connection Service: `ingestion/connection_service.py`
- Sink Config: `ingestion/sink_config.py`
- Snowflake Connector: `ingestion/connectors/snowflake.py`
- Frontend Modal: `frontend/components/connections/connection-modal.tsx`
- Frontend Page: `frontend/app/connections/page.tsx`

## Next Steps

1. Create a Snowflake connection using the UI
2. Test the connection
3. Create a pipeline with Snowflake as target
4. Monitor the pipeline to ensure data replication is working

---

**Status**: ✅ Complete  
**Date**: January 6, 2026


