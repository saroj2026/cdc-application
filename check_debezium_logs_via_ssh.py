#!/usr/bin/env python3
"""Check Debezium connector logs via SSH to see if there are any errors."""

import subprocess

print("=" * 70)
print("CHECKING DEBEZIUM CONNECTOR LOGS")
print("=" * 70)

print("\nTo check Debezium connector logs, run this on the server:")
print("\n1. SSH to server:")
print("   ssh root@72.61.233.209")
print("   Password: segmbp@1100")
print("\n2. Find Kafka Connect container:")
print("   docker ps --filter 'name=kafka-connect' --format '{{.Names}}'")
print("\n3. Check connector logs:")
print("   docker logs KAFKA_CONNECT_CONTAINER 2>&1 | grep -i 'oracle\\|cdc\\|error\\|exception' | tail -50")
print("\n4. Or check connector status via API:")
print("   curl http://localhost:8083/connectors/cdc-oracle_sf_p-ora-cdc_user/status")
print("\n5. Check for LogMiner errors:")
print("   docker logs KAFKA_CONNECT_CONTAINER 2>&1 | grep -i 'logminer\\|archive\\|scn' | tail -30")
print("\n" + "=" * 70)
print("Common issues:")
print("  - LogMiner not reading archive logs")
print("  - SCN (System Change Number) not advancing")
print("  - Archive log destination full")
print("  - LogMiner session not started")
print("=" * 70)

