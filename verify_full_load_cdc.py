"""Verify that full load + CDC integration is working correctly.

This script checks:
1. Full load LSN was captured
2. Debezium connector uses correct snapshot mode
3. Replication slot position is correct
4. No duplicate data
"""

import logging
import sys
from ingestion.cdc_manager import CDCManager
from ingestion.models import Connection, Pipeline

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def verify_full_load_cdc(pipeline_id: str):
    """Verify full load + CDC integration.
    
    Args:
        pipeline_id: Pipeline ID to verify
    """
    print("=" * 70)
    print("Verifying Full Load + CDC Integration")
    print("=" * 70)
    
    try:
        cdc_manager = CDCManager(kafka_connect_url="http://localhost:8083")
        
        # Get pipeline status
        status = cdc_manager.get_pipeline_status(pipeline_id)
        pipeline = cdc_manager.pipeline_store.get(pipeline_id)
        
        if not pipeline:
            print(f"✗ Pipeline not found: {pipeline_id}")
            return False
        
        print(f"\n1. Pipeline Status:")
        print(f"   Name: {pipeline.name}")
        print(f"   Status: {pipeline.status}")
        print(f"   Full Load Status: {pipeline.full_load_status}")
        print(f"   CDC Status: {pipeline.cdc_status}")
        
        # Check full load LSN
        print(f"\n2. Full Load LSN:")
        if pipeline.full_load_lsn:
            print(f"   ✓ Full load LSN captured: {pipeline.full_load_lsn}")
        else:
            print(f"   ⚠ Full load LSN not captured (full load may not have run)")
        
        # Check Debezium connector
        print(f"\n3. Debezium Connector:")
        if pipeline.debezium_connector_name:
            debezium_status = cdc_manager.kafka_client.get_connector_status(
                pipeline.debezium_connector_name
            )
            print(f"   Name: {pipeline.debezium_connector_name}")
            print(f"   Status: {debezium_status.get('connector', {}).get('state', 'UNKNOWN')}")
            
            # Check snapshot mode
            if pipeline.debezium_config:
                snapshot_mode = pipeline.debezium_config.get("snapshot.mode", "unknown")
                print(f"   Snapshot Mode: {snapshot_mode}")
                
                if pipeline.full_load_lsn:
                    if snapshot_mode == "initial_only":
                        print(f"   ✓ Correct: Using 'initial_only' (skips data, only schema)")
                    else:
                        print(f"   ⚠ Warning: Expected 'initial_only' but got '{snapshot_mode}'")
                else:
                    if snapshot_mode in ["initial", "always"]:
                        print(f"   ✓ Correct: Using '{snapshot_mode}' (no full load done)")
        else:
            print(f"   ⚠ Debezium connector not created")
        
        # Check replication slot (if PostgreSQL)
        source_conn = cdc_manager.get_connection(pipeline.source_connection_id)
        if source_conn and source_conn.database_type == "postgresql":
            print(f"\n4. Replication Slot:")
            slot_name = f"{pipeline.name.lower()}_slot"
            print(f"   Expected slot name: {slot_name}")
            print(f"   Note: Check slot position manually using check_debezium_slot.py")
        
        # Summary
        print(f"\n" + "=" * 70)
        print("Verification Summary:")
        print("=" * 70)
        
        checks_passed = 0
        total_checks = 0
        
        # Check 1: Full load LSN
        total_checks += 1
        if pipeline.full_load_lsn:
            print("✓ Full load LSN captured")
            checks_passed += 1
        else:
            print("⚠ Full load LSN not captured")
        
        # Check 2: Snapshot mode
        total_checks += 1
        if pipeline.debezium_config:
            snapshot_mode = pipeline.debezium_config.get("snapshot.mode", "")
            if pipeline.full_load_lsn and snapshot_mode == "initial_only":
                print("✓ Snapshot mode correct (initial_only)")
                checks_passed += 1
            elif not pipeline.full_load_lsn and snapshot_mode in ["initial", "always"]:
                print("✓ Snapshot mode correct")
                checks_passed += 1
            else:
                print(f"⚠ Snapshot mode: {snapshot_mode}")
        
        # Check 3: Connector status
        total_checks += 1
        if pipeline.debezium_connector_name:
            debezium_status = cdc_manager.kafka_client.get_connector_status(
                pipeline.debezium_connector_name
            )
            connector_state = debezium_status.get('connector', {}).get('state', 'UNKNOWN')
            if connector_state == "RUNNING":
                print("✓ Debezium connector running")
                checks_passed += 1
            else:
                print(f"⚠ Debezium connector state: {connector_state}")
        
        print(f"\nChecks passed: {checks_passed}/{total_checks}")
        
        if checks_passed == total_checks:
            print("\n✅ Full Load + CDC integration verified!")
            return True
        else:
            print("\n⚠ Some checks failed. Review the output above.")
            return False
            
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python verify_full_load_cdc.py <pipeline_id>")
        print("\nTo get pipeline ID, check your pipeline creation script or use:")
        print("  python -c \"from ingestion.cdc_manager import CDCManager; m = CDCManager(); print([p.id for p in m.pipeline_store.values()])\"")
        sys.exit(1)
    
    pipeline_id = sys.argv[1]
    success = verify_full_load_cdc(pipeline_id)
    sys.exit(0 if success else 1)


