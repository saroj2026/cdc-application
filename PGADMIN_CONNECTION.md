# pgAdmin Connection Guide for CDC Database

## ✅ pgAdmin Installed Successfully!

pgAdmin 4 has been installed to `/Applications/pgAdmin 4.app`

## How to Connect to Your CDC Database

### Step 1: Launch pgAdmin
- Open **Applications** folder
- Double-click **pgAdmin 4**
- Or use Spotlight: Press `Cmd + Space`, type "pgAdmin", press Enter

### Step 2: Set Master Password (First Time Only)
- When pgAdmin opens, it will ask for a **master password**
- This password encrypts your stored server passwords
- Choose a strong password and remember it

### Step 3: Add Your CDC Server

1. **Right-click "Servers"** in the left panel
2. Select **Create** → **Server...**

3. **General Tab**:
   - **Name**: `CDC PostgreSQL Server` (or any name you prefer)

4. **Connection Tab**:
   - **Host name/address**: `72.61.233.209`
   - **Port**: `5432`
   - **Maintenance database**: `cdctest`
   - **Username**: `cdc_user`
   - **Password**: `cdc_pass`
   - ✅ **Save password** (check this box)

5. **Click "Save"**

### Step 4: Explore Your Database

Once connected, you can:

1. **Browse Tables**:
   - Expand: `Servers` → `CDC PostgreSQL Server` → `Databases` → `cdctest` → `Schemas` → `public` → `Tables`
   - View: `pipelines`, `connections`, `pipeline_metrics`, `pipeline_runs`, etc.

2. **Run SQL Queries**:
   - Right-click `cdctest` → **Query Tool**
   - Write and execute SQL queries

## Useful SQL Queries for CDC

### 1. Check All Pipelines
```sql
SELECT id, name, status, cdc_status, full_load_status, full_load_lsn
FROM pipelines
ORDER BY created_at DESC;
```

### 2. Check Replication Slots (CDC LSN)
```sql
SELECT 
    slot_name,
    confirmed_flush_lsn AS cdc_lsn,
    pg_wal_lsn_diff(pg_current_wal_lsn(), confirmed_flush_lsn) AS lag_bytes,
    pg_size_pretty(pg_wal_lsn_diff(pg_current_wal_lsn(), confirmed_flush_lsn)) AS lag_size,
    active
FROM pg_replication_slots
ORDER BY slot_name;
```

### 3. Check Current WAL LSN
```sql
SELECT 
    pg_current_wal_lsn() AS current_lsn,
    pg_current_wal_insert_lsn() AS insert_lsn;
```

### 4. View Recent Pipeline Metrics
```sql
SELECT 
    pipeline_id,
    timestamp,
    throughput_events_per_sec,
    lag_seconds,
    error_count,
    source_offset,
    target_offset
FROM pipeline_metrics
ORDER BY timestamp DESC
LIMIT 20;
```

### 5. View Recent Pipeline Runs (CDC Events)
```sql
SELECT 
    id,
    pipeline_id,
    run_type,
    status,
    started_at,
    rows_processed,
    run_metadata
FROM pipeline_runs
ORDER BY started_at DESC
LIMIT 20;
```

### 6. Check Full Load LSN for All Pipelines
```sql
SELECT 
    name,
    full_load_lsn,
    full_load_status,
    full_load_completed_at,
    cdc_status
FROM pipelines
WHERE full_load_lsn IS NOT NULL
ORDER BY full_load_completed_at DESC;
```

### 7. Compare Source LSN vs Full Load LSN
```sql
SELECT 
    p.name,
    p.full_load_lsn,
    pg_current_wal_lsn() AS current_wal_lsn,
    pg_wal_lsn_diff(pg_current_wal_lsn(), p.full_load_lsn) AS bytes_since_full_load
FROM pipelines p
WHERE p.full_load_lsn IS NOT NULL;
```

## Quick Access Tips

- **Query Tool**: Right-click database → Query Tool
- **View Table Data**: Right-click table → View/Edit Data → All Rows
- **Refresh**: Right-click → Refresh (to see latest data)
- **New Query**: Click "Query Tool" icon in toolbar

## Connection Details Summary

```
Host: 72.61.233.209
Port: 5432
Database: cdctest
Username: cdc_user
Password: cdc_pass
```

## Troubleshooting

### Can't Connect?
1. Check if PostgreSQL is accessible: `ping 72.61.233.209`
2. Verify port 5432 is open
3. Check firewall settings

### Connection Timeout?
- The database is on a remote server (72.61.233.209)
- Make sure you have network access to that IP

### Authentication Failed?
- Double-check username: `cdc_user`
- Double-check password: `cdc_pass`
- Verify database name: `cdctest`


