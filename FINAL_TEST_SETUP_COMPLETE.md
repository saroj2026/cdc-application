# Final Test Pipeline - Setup Complete

## ✅ What's Been Set Up

### 1. Connections
- **PostgreSQL Connection:** `POSTGRE`
  - Host: 72.61.233.209
  - Port: 5432
  - Database: `cdctest`
  - Schema: `public`
  - Connection ID: `61e57610-f088-48ec-8938-d07cf3903643`

- **SQL Server Connection:** `MS-SQL`
  - Host: 72.61.233.209
  - Port: 1433
  - Database: `cdctest`
  - Schema: `dbo`
  - Password: `Sql@12345`
  - Connection ID: `b875c98a-0aed-40a6-88be-e1213efcf0b4`

### 2. Pipeline
- **Name:** `final_test`
- **Mode:** `full_load_and_cdc`
- **Source:** `cdctest.public.projects_simple`
- **Target:** `cdctest.dbo.projects_simple`
- **Auto-create target:** Enabled (will create table in SQL Server)

### 3. Source Table
The `public.projects_simple` table exists with 3 rows:
- Row 1: CDC Pipeline Setup (project_id: 1)
- Row 2: Kafka Optimization (project_id: 2)
- Row 3: Data Quality Audit (project_id: 3)

## Current Issue

**Kafka Connect 500 Error:**
- When starting the pipeline, Kafka Connect returns 500 errors
- However, direct testing shows Kafka Connect is accessible
- This might be an intermittent issue or related to connector creation

## What Will Happen When Pipeline Starts

1. **Full Load:**
   - Extract all 3 rows from PostgreSQL `public.projects_simple`
   - Create table `dbo.projects_simple` in SQL Server (if not exists)
   - Insert all 3 rows into SQL Server

2. **CDC Setup:**
   - Create Debezium connector to capture PostgreSQL changes
   - Create SQL Server sink connector to write changes to SQL Server
   - Start streaming changes

## Next Steps

1. **Try starting the pipeline again** - the error might be intermittent
2. **Check Kafka Connect logs** on VPS if error persists
3. **Verify the pipeline was created correctly:**
   ```bash
   python check_all_pipelines.py
   ```

## Test CDC After Pipeline Starts

Once the pipeline is running, test CDC by:

1. **Insert a new row in PostgreSQL:**
   ```sql
   INSERT INTO public.projects_simple 
   VALUES (4, 'New Project', 203, 104, '2024-06-01', NULL, 'ACTIVE');
   ```

2. **Verify in SQL Server:**
   ```sql
   SELECT * FROM cdctest.dbo.projects_simple;
   ```

3. **Update a row in PostgreSQL:**
   ```sql
   UPDATE public.projects_simple 
   SET status = 'COMPLETED' 
   WHERE project_id = 1;
   ```

4. **Verify update in SQL Server**

## Files Created

- `setup_final_test_pipeline.py` - Original setup script
- `create_and_start_final_test.py` - Complete setup and start script
- `check_projects_simple_table.py` - Verify source table
- `check_and_fix_connections.py` - Connection verification

## Pipeline ID

Current pipeline ID: Check with `python check_all_pipelines.py`


## ✅ What's Been Set Up

### 1. Connections
- **PostgreSQL Connection:** `POSTGRE`
  - Host: 72.61.233.209
  - Port: 5432
  - Database: `cdctest`
  - Schema: `public`
  - Connection ID: `61e57610-f088-48ec-8938-d07cf3903643`

- **SQL Server Connection:** `MS-SQL`
  - Host: 72.61.233.209
  - Port: 1433
  - Database: `cdctest`
  - Schema: `dbo`
  - Password: `Sql@12345`
  - Connection ID: `b875c98a-0aed-40a6-88be-e1213efcf0b4`

### 2. Pipeline
- **Name:** `final_test`
- **Mode:** `full_load_and_cdc`
- **Source:** `cdctest.public.projects_simple`
- **Target:** `cdctest.dbo.projects_simple`
- **Auto-create target:** Enabled (will create table in SQL Server)

### 3. Source Table
The `public.projects_simple` table exists with 3 rows:
- Row 1: CDC Pipeline Setup (project_id: 1)
- Row 2: Kafka Optimization (project_id: 2)
- Row 3: Data Quality Audit (project_id: 3)

## Current Issue

**Kafka Connect 500 Error:**
- When starting the pipeline, Kafka Connect returns 500 errors
- However, direct testing shows Kafka Connect is accessible
- This might be an intermittent issue or related to connector creation

## What Will Happen When Pipeline Starts

1. **Full Load:**
   - Extract all 3 rows from PostgreSQL `public.projects_simple`
   - Create table `dbo.projects_simple` in SQL Server (if not exists)
   - Insert all 3 rows into SQL Server

2. **CDC Setup:**
   - Create Debezium connector to capture PostgreSQL changes
   - Create SQL Server sink connector to write changes to SQL Server
   - Start streaming changes

## Next Steps

1. **Try starting the pipeline again** - the error might be intermittent
2. **Check Kafka Connect logs** on VPS if error persists
3. **Verify the pipeline was created correctly:**
   ```bash
   python check_all_pipelines.py
   ```

## Test CDC After Pipeline Starts

Once the pipeline is running, test CDC by:

1. **Insert a new row in PostgreSQL:**
   ```sql
   INSERT INTO public.projects_simple 
   VALUES (4, 'New Project', 203, 104, '2024-06-01', NULL, 'ACTIVE');
   ```

2. **Verify in SQL Server:**
   ```sql
   SELECT * FROM cdctest.dbo.projects_simple;
   ```

3. **Update a row in PostgreSQL:**
   ```sql
   UPDATE public.projects_simple 
   SET status = 'COMPLETED' 
   WHERE project_id = 1;
   ```

4. **Verify update in SQL Server**

## Files Created

- `setup_final_test_pipeline.py` - Original setup script
- `create_and_start_final_test.py` - Complete setup and start script
- `check_projects_simple_table.py` - Verify source table
- `check_and_fix_connections.py` - Connection verification

## Pipeline ID

Current pipeline ID: Check with `python check_all_pipelines.py`

