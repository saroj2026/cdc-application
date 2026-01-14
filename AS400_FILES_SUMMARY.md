# AS400 Connector - All Files Created

## Summary
All files have been created and saved in: `/Users/kumargaurav/Desktop/CDCTEAM/cdcteam/seg-cdc-application/`

---

## AS400 Connector Installation & Checking

### Installation Scripts
1. **install_as400_connector_remote.sh**
   - Install AS400 connector on remote Kafka Connect server
   - Downloads and installs debezium-connector-ibmi

2. **complete_as400_installation.sh**
   - Complete installation from already downloaded connector
   - Copies connector from local directory to container

3. **install_debezium_db2.sh**
   - Updated to install AS400 connector (debezium-connector-ibmi)
   - Downloads version 2.6.0.Beta1

### Checking Scripts
4. **check_as400_in_docker.sh**
   - Check connector in Kafka Connect Docker container
   - Verifies directory, JARs, and plugin loading

5. **check_as400_plugin.py**
   - Check if AS400 plugin is available via Kafka Connect API
   - Python script with detailed output

6. **check_as400_connector_installation.sh**
   - Comprehensive connector installation check
   - Checks directory, JARs, API availability

7. **check_debezium_at_opt.sh**
   - Check connector at `/opt/cdc3/connect-plugins` (host path)
   - Verifies if accessible from container

8. **check_debezium_container_path.sh**
   - Check connector at `/usr/share/java/plugins` (container path)
   - Verifies plugin loading

9. **copy_debezium_to_container_path.sh**
   - Copy connector from `/opt/cdc3/connect-plugins` to `/usr/share/java/plugins`
   - Automates the copy and restart process

---

## Pipeline Management

10. **restart_as400_pipeline.py**
    - Restart AS400-S3_P pipeline
    - Stops and starts the pipeline

11. **start_as400_pipeline.py**
    - Start AS400-S3_P pipeline
    - Checks status and shows connector information

12. **check_as400_pipeline_cdc.py**
    - Check CDC status for AS400-S3_P pipeline
    - Shows pipeline, connector, and event status

13. **check_s3_sink_data.py**
    - Check if data is flowing to S3 sink
    - Verifies sink connector and replication events

---

## Kafka Connect Troubleshooting

14. **diagnose_kafka_connect_500.py**
    - Diagnose 500 errors from Kafka Connect
    - Tests connectivity and identifies issues

15. **fix_kafka_connect_500.sh**
    - Quick fix for Kafka Connect 500 errors
    - Restarts container and verifies

16. **check_kafka_connect.sh**
    - Check Kafka Connect status
    - Verifies container, port mapping, and API

---

## Windows/Plink Support

17. **check_connector_plink.bat**
    - Check connector using plink (Windows)
    - Batch file for Windows users

18. **copy_connector_plink.bat**
    - Copy connector using plink (Windows)
    - Batch file for Windows users

---

## Backend Management

19. **restart_backend.sh**
    - Restart backend application
    - Stops and starts FastAPI backend

---

## Other Utilities

20. **ssh_and_check_as400.sh**
    - SSH and check AS400 connector
    - Automated SSH check script

21. **QUICK_INSTALL_AS400.sh**
    - Quick installation script
    - Minimal commands for fast setup

---

## Code Changes

### Backend Code
- **ingestion/debezium_config.py** - Updated to use `io.debezium.connector.db2as400.As400RpcConnector`
- **ingestion/connectors/as400.py** - AS400 connector implementation
- **ingestion/connection_service.py** - AS400 connection handling
- **ingestion/cdc_manager.py** - AS400 full load support
- **ingestion/models.py** - AS400 connection config
- **ingestion/database/models_db.py** - AS400 enum values

### Frontend Code
- **frontend/lib/database-icons.tsx** - AS400 database icons
- **frontend/components/connections/connection-modal.tsx** - AS400 connection fields
- **frontend/app/connections/page.tsx** - AS400 connection type mapping

---

## Quick Reference

### Most Important Files for Current Issue:

1. **check_debezium_container_path.sh** - Check connector at `/usr/share/java/plugins`
2. **copy_debezium_to_container_path.sh** - Copy connector to container path
3. **check_as400_plugin.py** - Verify plugin is loaded
4. **start_as400_pipeline.py** - Start the pipeline

---

## Usage

### Check Connector (Linux/Mac):
```bash
scp check_debezium_container_path.sh root@72.61.233.209:/tmp/
ssh root@72.61.233.209
chmod +x /tmp/check_debezium_container_path.sh
/tmp/check_debezium_container_path.sh
```

### Check Connector (Windows with plink):
```bash
check_connector_plink.bat
```

### Copy Connector (if needed):
```bash
scp copy_debezium_to_container_path.sh root@72.61.233.209:/tmp/
ssh root@72.61.233.209
chmod +x /tmp/copy_debezium_to_container_path.sh
/tmp/copy_debezium_to_container_path.sh
```

### Start Pipeline:
```bash
cd /Users/kumargaurav/Desktop/CDCTEAM/cdcteam/seg-cdc-application
source venv/bin/activate
python start_as400_pipeline.py
```

---

All files are saved and ready to use!


