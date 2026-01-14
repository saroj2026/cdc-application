# AS400 Required Files - Complete List

This document lists all AS400/IBM i related files that are required for the CDC pipeline to work.

## Core Implementation Files

### Backend Connector
- **`ingestion/connectors/as400.py`** ⭐ CRITICAL
  - AS400 connector implementation
  - Implements: `extract_schema()`, `extract_data()`, `full_load()`, `extract_lsn_offset()`
  - Handles ODBC connection to AS400/IBM i
  - Captures journal offset for CDC

### Configuration Files
- **`ingestion/debezium_config.py`** ⭐ CRITICAL
  - Contains `_generate_as400_config()` method
  - Generates Debezium connector configuration for AS400
  - Handles snapshot mode logic based on offset availability
  - Configures: `io.debezium.connector.db2as400.As400RpcConnector`

- **`ingestion/cdc_manager.py`** ⭐ CRITICAL
  - Contains AS400 full load logic in `_run_full_load_to_s3()`
  - Captures LSN/offset after full load
  - Handles offset extraction and storage
  - Manages pipeline lifecycle for AS400

### Connection Service
- **`ingestion/connection_service.py`** ⭐ CRITICAL
  - Instantiates `AS400Connector` for AS400 connections
  - Maps connection config (host → server, library → database)

### Discovery Service
- **`ingestion/discovery_service.py`** ⭐ CRITICAL
  - Handles table discovery for AS400
  - Works with `AS400Connector.list_tables()`

## Frontend Files

### Database Icons & Configuration
- **`frontend/lib/database-icons.tsx`**
  - Contains AS400 and IBM i entries in `DATABASE_SERVICES`
  - Maps connection types: "as400", "ibm_i", "ibmi", "iseries"

- **`frontend/lib/database-logo-loader.tsx`**
  - Contains AS400 logo mappings
  - Exports `DatabaseLogo` component

- **`frontend/app/connections/page.tsx`**
  - Connection type map includes AS400 aliases
  - Handles AS400 connection creation

### Connection Modal
- **`frontend/components/connections/connection-modal.tsx`** ⭐ CRITICAL
  - AS400-specific fields: Journal Library, Library, Table Name
  - Makes Database field optional for AS400
  - Stores AS400 config in `additional_config`

## Database Migration
- **`alembic/versions/add_as400_to_database_type_enum.py`**
  - Adds "as400" and "ibm_i" to DatabaseType enum in PostgreSQL

## Utility Scripts

### Pipeline Management
- **`restart_as400_pipeline.py`** ⭐ USEFUL
  - Restarts AS400-S3_P pipeline
  - Stops and starts pipeline via API

- **`start_as400_pipeline.py`**
  - Starts AS400-S3_P pipeline

- **`quick_start_as400.sh`**
  - Quick script to start AS400 pipeline

### Status & Verification
- **`check_as400_pipeline_status.py`** ⭐ USEFUL
  - Comprehensive status check for AS400 pipeline
  - Checks pipeline, connectors, events, metrics

- **`verify_as400_offset_capture.py`** ⭐ USEFUL
  - Verifies if offset was captured after full load
  - Checks connector configuration

- **`check_as400_pipeline_cdc.py`**
  - Checks CDC status for AS400 pipeline

- **`check_as400_plugin.py`**
  - Checks if AS400 connector plugin is available

### Connector Configuration
- **`fix_as400_connector_schema.py`** ⭐ USEFUL
  - Fixes missing database.schema in connector config
  - Updates snapshot.mode based on offset availability

- **`fix_as400_cdc_offset.py`**
  - Fixes CDC to use offset from full load

### Installation Scripts
- **`install_as400_connector_remote.sh`**
  - Installs AS400 connector on remote Kafka Connect

- **`install_as400_connector_on_vps.sh`**
  - Installs connector on VPS

- **`QUICK_INSTALL_AS400.sh`**
  - Quick installation script

### Testing & Diagnostics
- **`test_as400_offset_extraction.py`**
  - Tests AS400 offset extraction

- **`check_as400_in_docker.sh`**
  - Checks connector in Docker container

- **`check_as400_connector_installation.sh`**
  - Verifies connector installation

## Documentation Files

- **`AS400_FILES_SUMMARY.md`**
  - Summary of all AS400 files

- **`AS400_SETUP_GUIDE.md`**
  - Setup guide for AS400

- **`START_AS400_PIPELINE.md`**
  - Instructions for starting AS400 pipeline

- **`FIX_AS400_500_ERROR.md`**
  - Troubleshooting guide for Kafka Connect 500 errors

- **`AS400_NEXT_STEPS.md`**
  - Next steps documentation

- **`INSTALL_IBM_I_ACCESS.md`**
  - IBM i Access ODBC Driver installation guide

- **`INSTALL_IBM_I_ACCESS_MANUAL.sh`**
  - Manual installation script

## Key Features Implemented

### 1. Connection Configuration
- ✅ AS400 connection type support
- ✅ Journal Library field
- ✅ Library field (replaces Database)
- ✅ Table Name field
- ✅ Database field optional for AS400

### 2. Full Load
- ✅ Schema extraction from QSYS2.SYSTABLES
- ✅ Data extraction with pagination
- ✅ LSN/offset capture after full load
- ✅ Fallback LSN creation if extraction fails

### 3. CDC Integration
- ✅ Debezium AS400 connector configuration
- ✅ Snapshot mode logic (never/initial based on offset)
- ✅ Journal offset handling
- ✅ Database schema configuration

### 4. Offset Capture
- ✅ Extracts journal information
- ✅ Creates LSN format: `JOURNAL:{library}:{timestamp}`
- ✅ Stores in `pipeline.full_load_lsn`
- ✅ CDC uses offset to start from correct point

## Critical Files Summary

**MUST HAVE:**
1. `ingestion/connectors/as400.py` - Core connector
2. `ingestion/debezium_config.py` - Debezium config
3. `ingestion/cdc_manager.py` - Full load + CDC logic
4. `frontend/components/connections/connection-modal.tsx` - UI
5. `alembic/versions/add_as400_to_database_type_enum.py` - DB enum

**VERY USEFUL:**
1. `restart_as400_pipeline.py` - Pipeline management
2. `check_as400_pipeline_status.py` - Status monitoring
3. `verify_as400_offset_capture.py` - Offset verification
4. `fix_as400_connector_schema.py` - Connector fixes

## File Status

All files are saved and ready for use. The AS400 integration is complete and operational.

