# Permanent Solution for CDC Stuck Issues

## Overview

This document describes the permanent solution implemented to prevent and automatically recover from CDC replication slot lag issues.

## Problem

CDC pipelines can get stuck when:
- Debezium connector stops reading from replication slot (shows RUNNING but doesn't process changes)
- Replication slot lag accumulates (changes waiting in WAL but not processed)
- Network issues or connector errors cause CDC to stall

## Solution Components

### 1. CDC Health Monitor (`ingestion/cdc_health_monitor.py`)

**Features:**
- **Replication Slot Lag Monitoring**: Continuously checks lag between CDC LSN and current WAL LSN
- **Automatic Recovery**: Automatically recovers from stuck states
- **Health Status Classification**: 
  - `healthy`: Lag < 100 KB
  - `warning`: Lag 100-500 KB
  - `critical`: Lag 500-1000 KB
  - `stuck`: Lag > 1000 KB

**Recovery Strategies:**
1. **Restart Connector** (for moderate lag < 1 MB):
   - Pauses and resumes Debezium connector
   - Forces reconnection to PostgreSQL
   - Processes pending changes

2. **Recreate Replication Slot** (for severe lag >= 500 KB):
   - Pauses connector
   - Deletes stuck replication slot
   - Resumes connector (automatically recreates slot)
   - Starts fresh from current position

**Safety Features:**
- **Recovery Cooldown**: 5 minutes between recovery attempts
- **Max Attempts**: 3 attempts before requiring manual intervention
- **Error Handling**: Graceful failure with detailed logging

### 2. Background Monitoring Service (`ingestion/background_monitor.py`)

**Features:**
- **Automatic Periodic Checks**: Monitors all running pipelines every 60 seconds (configurable)
- **Background Thread**: Runs independently without blocking API
- **Auto-Recovery**: Automatically attempts recovery for unhealthy pipelines
- **Logging**: Logs warnings for unhealthy pipelines and successful recoveries

**Configuration:**
- Check interval: Set via `CDC_MONITOR_INTERVAL_SECONDS` environment variable (default: 60 seconds)
- Starts automatically when backend starts

### 3. API Endpoints

**New/Enhanced Endpoints:**

1. **`GET /api/v1/pipelines/{pipeline_id}/health`**
   - Comprehensive health check with replication slot lag
   - Optional `auto_recover` parameter to trigger recovery
   - Returns detailed health status including:
     - Overall status (healthy/unhealthy)
     - Replication slot lag (bytes, KB, status)
     - Debezium connector health
     - Sink connector health
     - Issues list
     - Recovery attempt results

2. **`GET /api/v1/pipelines/{pipeline_id}/health/legacy`**
   - Original health check endpoint (for backward compatibility)

## How It Works

### Automatic Monitoring Flow

```
1. Background Monitor starts (every 60 seconds)
   ↓
2. Get all running pipelines from database
   ↓
3. For each pipeline:
   a. Check replication slot lag
   b. Check connector health
   c. Determine overall health status
   ↓
4. If unhealthy (lag > 500 KB):
   a. Check recovery cooldown
   b. Attempt recovery (restart connector or recreate slot)
   c. Log results
   ↓
5. Wait 60 seconds, repeat
```

### Manual Health Check

```bash
# Check health (no auto-recovery)
curl http://localhost:8000/api/v1/pipelines/{pipeline_id}/health

# Check health with auto-recovery
curl "http://localhost:8000/api/v1/pipelines/{pipeline_id}/health?auto_recover=true"
```

## Configuration

### Environment Variables

```bash
# Kafka Connect URL
KAFKA_CONNECT_URL=http://72.61.233.209:8083

# Background monitor check interval (seconds)
CDC_MONITOR_INTERVAL_SECONDS=60
```

### Thresholds (in `cdc_health_monitor.py`)

```python
LAG_WARNING_THRESHOLD_KB = 100      # 100 KB - warning level
LAG_CRITICAL_THRESHOLD_KB = 500     # 500 KB - critical, trigger recovery
LAG_MAX_THRESHOLD_KB = 1000         # 1 MB - maximum before forced recovery

MAX_RECOVERY_ATTEMPTS = 3           # Max recovery attempts
RECOVERY_COOLDOWN_SECONDS = 300     # 5 minutes between attempts
```

## Benefits

### ✅ Automatic Prevention
- Continuously monitors all pipelines
- Detects issues before they become critical
- Prevents data loss by catching lag early

### ✅ Automatic Recovery
- No manual intervention needed for most cases
- Recovers from stuck states automatically
- Multiple recovery strategies (restart vs recreate slot)

### ✅ Safety Features
- Cooldown periods prevent excessive recovery attempts
- Max attempts limit prevents infinite loops
- Detailed logging for troubleshooting

### ✅ Visibility
- Health check API provides detailed status
- Background monitor logs warnings and recoveries
- Easy to monitor via API or logs

## Usage Examples

### Check Pipeline Health

```python
import requests

# Check health
response = requests.get(
    "http://localhost:8000/api/v1/pipelines/{pipeline_id}/health"
)
health = response.json()

print(f"Status: {health['status']}")
print(f"Lag: {health['lag_info']['lag_kb']:.2f} KB")
print(f"Issues: {health['issues']}")
```

### Monitor All Pipelines

The background monitor automatically checks all running pipelines. To see results:

1. **Check Logs**:
   ```bash
   # Backend logs will show:
   # - Unhealthy pipelines
   # - Recovery attempts
   # - Recovery results
   ```

2. **Use API**:
   ```bash
   # Check specific pipeline
   curl http://localhost:8000/api/v1/pipelines/{pipeline_id}/health
   ```

## Troubleshooting

### If Recovery Fails

1. **Check Logs**: Look for error messages in backend logs
2. **Manual Recovery**: Use the manual recovery steps from `fix_stuck_cdc.py`
3. **Check Connector Status**: Verify connectors are accessible
4. **Check PostgreSQL**: Verify replication slot exists and is active

### If Background Monitor Not Working

1. **Check Environment Variable**: `CDC_MONITOR_INTERVAL_SECONDS` should be set
2. **Check Logs**: Look for "Background CDC monitor started" message
3. **Restart Backend**: Background monitor starts on backend startup

### Adjusting Thresholds

Edit `ingestion/cdc_health_monitor.py`:

```python
# Make recovery more aggressive (lower thresholds)
LAG_WARNING_THRESHOLD_KB = 50
LAG_CRITICAL_THRESHOLD_KB = 200
LAG_MAX_THRESHOLD_KB = 500

# Or make recovery less aggressive (higher thresholds)
LAG_WARNING_THRESHOLD_KB = 200
LAG_CRITICAL_THRESHOLD_KB = 1000
LAG_MAX_THRESHOLD_KB = 2000
```

## Monitoring Recommendations

### 1. Set Up Alerts

Monitor backend logs for:
- `"Unhealthy pipeline"` warnings
- `"recovered"` messages
- `"Max recovery attempts reached"` errors

### 2. Regular Health Checks

Use the health API in your monitoring system:
```bash
# Check all pipelines periodically
for pipeline_id in $(get_pipeline_ids); do
    health=$(curl -s "http://localhost:8000/api/v1/pipelines/$pipeline_id/health")
    if [ "$(echo $health | jq -r '.status')" != "healthy" ]; then
        send_alert "Pipeline $pipeline_id is unhealthy"
    fi
done
```

### 3. Dashboard Integration

Add health status to your dashboard:
- Overall pipeline health
- Replication slot lag metrics
- Recovery attempt history

## Summary

This permanent solution provides:

1. ✅ **Automatic Monitoring**: Background service checks all pipelines every 60 seconds
2. ✅ **Automatic Recovery**: Recovers from stuck states without manual intervention
3. ✅ **Safety Features**: Cooldowns and limits prevent excessive recovery attempts
4. ✅ **Visibility**: API endpoints and logging provide full visibility
5. ✅ **Configurability**: Thresholds and intervals can be adjusted

**Result**: CDC pipelines will automatically recover from stuck states, preventing data loss and reducing manual intervention to near zero.

