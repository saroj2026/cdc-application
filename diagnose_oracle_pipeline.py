#!/usr/bin/env python3
"""Diagnose Oracle pipeline CDC connector creation issues."""

import requests
import json
import sys

PIPELINE_ID = "3b06bbae-2bbc-4526-ad6f-4e5d12c14f04"
BACKEND_URL = "http://localhost:8000"
KAFKA_CONNECT_URL = "http://72.61.233.209:8083"

def check_kafka_connect():
    """Check Kafka Connect accessibility."""
    print("=" * 70)
    print("1. Checking Kafka Connect Accessibility")
    print("=" * 70)
    try:
        r = requests.get(f"{KAFKA_CONNECT_URL}/connectors", timeout=5)
        if r.status_code == 200:
            connectors = r.json()
            print(f"✓ Kafka Connect is accessible")
            print(f"  Total connectors: {len(connectors)}")
            oracle_conns = [c for c in connectors if 'oracle' in c.lower()]
            print(f"  Oracle connectors: {len(oracle_conns)}")
            if oracle_conns:
                print(f"  Oracle connector names: {oracle_conns}")
            return True
        else:
            print(f"✗ Kafka Connect returned {r.status_code}")
            return False
    except Exception as e:
        print(f"✗ Kafka Connect not accessible: {e}")
        return False

def check_pipeline_status():
    """Check pipeline status from backend."""
    print("\n" + "=" * 70)
    print("2. Checking Pipeline Status from Backend")
    print("=" * 70)
    try:
        r = requests.get(f"{BACKEND_URL}/api/v1/pipelines/{PIPELINE_ID}")
        if r.status_code == 200:
            p = r.json()
            print(f"✓ Pipeline found: {p.get('name')}")
            print(f"  Status: {p.get('status')}")
            print(f"  Full Load Status: {p.get('full_load_status')}")
            print(f"  CDC Status: {p.get('cdc_status')}")
            print(f"  Mode: {p.get('mode')}")
            print(f"  Debezium Connector: {p.get('debezium_connector_name')}")
            print(f"  Sink Connector: {p.get('sink_connector_name')}")
            print(f"  Kafka Topics: {p.get('kafka_topics', [])}")
            print(f"  Has Debezium Config: {bool(p.get('debezium_config'))}")
            print(f"  Has Sink Config: {bool(p.get('sink_config'))}")
            return p
        else:
            print(f"✗ Failed to get pipeline: {r.status_code}")
            print(f"  Response: {r.text[:500]}")
            return None
    except Exception as e:
        print(f"✗ Error getting pipeline: {e}")
        return None

def check_pipeline_from_db():
    """Check pipeline directly from database."""
    print("\n" + "=" * 70)
    print("3. Checking Pipeline from Database")
    print("=" * 70)
    try:
        from ingestion.database.session import get_db
        from ingestion.database.models_db import PipelineModel
        
        db = next(get_db())
        p = db.query(PipelineModel).filter_by(id=PIPELINE_ID).first()
        
        if p:
            print(f"✓ Pipeline found in DB: {p.name}")
            print(f"  Mode: {p.mode}")
            print(f"  Full Load Status: {p.full_load_status}")
            print(f"  CDC Status: {p.cdc_status}")
            print(f"  Debezium Connector Name: {p.debezium_connector_name}")
            print(f"  Sink Connector Name: {p.sink_connector_name}")
            print(f"  Kafka Topics: {p.kafka_topics}")
            print(f"  Debezium Config Keys: {list(p.debezium_config.keys())[:5] if p.debezium_config else 'None'}")
            print(f"  Sink Config Keys: {list(p.sink_config.keys())[:5] if p.sink_config else 'None'}")
            db.close()
            return p
        else:
            print(f"✗ Pipeline not found in database")
            db.close()
            return None
    except Exception as e:
        print(f"✗ Error querying database: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_connector_creation():
    """Test creating a connector directly."""
    print("\n" + "=" * 70)
    print("4. Testing Direct Connector Creation")
    print("=" * 70)
    
    from ingestion.debezium_config import DebeziumConfigGenerator
    from ingestion.models import Connection
    
    # Create test Oracle connection
    oracle_conn = Connection(
        id="test",
        name="oracle-s",
        connection_type="source",
        database_type="oracle",
        host="72.61.233.209",
        port=1521,
        database="XE",
        username="c##cdc_user",
        password="cdc_pass",
        additional_config={}
    )
    
    # Generate config
    try:
        config = DebeziumConfigGenerator._generate_oracle_config(
            pipeline_name="test_oracle_diagnosis",
            connection=oracle_conn,
            database="XE",
            schema="C##CDC_USER",
            tables=["test"],
            full_load_lsn="SCN:123456",
            snapshot_mode="initial_only"
        )
        
        print(f"✓ Config generated successfully")
        print(f"  Snapshot mode: {config.get('snapshot.mode')}")
        print(f"  Connector class: {config.get('connector.class')}")
        print(f"  Database: {config.get('database.dbname')}")
        
        # Try to create connector
        test_name = "test-oracle-diagnosis-delete-me"
        try:
            r = requests.post(
                f"{KAFKA_CONNECT_URL}/connectors",
                json={"name": test_name, "config": config},
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            if r.status_code in [200, 201]:
                print(f"✓ Connector creation successful (status: {r.status_code})")
                # Delete test connector
                requests.delete(f"{KAFKA_CONNECT_URL}/connectors/{test_name}")
                print(f"✓ Test connector deleted")
                return True
            else:
                print(f"✗ Connector creation failed (status: {r.status_code})")
                print(f"  Response: {r.text[:500]}")
                return False
        except Exception as e:
            print(f"✗ Error creating connector: {e}")
            return False
            
    except Exception as e:
        print(f"✗ Error generating config: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("\n" + "=" * 70)
    print("Oracle Pipeline CDC Diagnosis")
    print("=" * 70)
    
    kafka_ok = check_kafka_connect()
    pipeline_status = check_pipeline_status()
    pipeline_db = check_pipeline_from_db()
    connector_test = test_connector_creation()
    
    print("\n" + "=" * 70)
    print("Summary")
    print("=" * 70)
    print(f"Kafka Connect: {'✓ OK' if kafka_ok else '✗ FAILED'}")
    print(f"Pipeline Status API: {'✓ OK' if pipeline_status else '✗ FAILED'}")
    print(f"Pipeline Database: {'✓ OK' if pipeline_db else '✗ FAILED'}")
    print(f"Connector Creation Test: {'✓ OK' if connector_test else '✗ FAILED'}")
    
    if pipeline_db:
        if not pipeline_db.debezium_connector_name:
            print("\n⚠ ISSUE: Pipeline has no Debezium connector name in database")
        if not pipeline_db.debezium_config:
            print("⚠ ISSUE: Pipeline has no Debezium config in database")
        if not pipeline_db.sink_connector_name:
            print("⚠ ISSUE: Pipeline has no Sink connector name in database")
        if not pipeline_db.sink_config:
            print("⚠ ISSUE: Pipeline has no Sink config in database")
    
    print("\n" + "=" * 70)

if __name__ == "__main__":
    main()

