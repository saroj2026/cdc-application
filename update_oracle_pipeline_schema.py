"""Update Oracle pipeline to use PUBLIC schema."""

import requests

API_BASE_URL = "http://localhost:8000/api/v1"
PIPELINE_NAME = "oracle_sf_p"

print("=" * 70)
print("Updating Oracle Pipeline Target Schema to PUBLIC")
print("=" * 70)

# Step 1: Get pipeline
print(f"\n1. Finding pipeline '{PIPELINE_NAME}'...")
try:
    response = requests.get(f"{API_BASE_URL}/pipelines", timeout=10)
    pipelines = response.json() if response.status_code == 200 else []
    
    pipeline = None
    for p in pipelines:
        if p.get("name") == PIPELINE_NAME:
            pipeline = p
            break
    
    if not pipeline:
        print(f"   ❌ Pipeline '{PIPELINE_NAME}' not found")
        exit(1)
    
    pipeline_id = pipeline.get("id")
    print(f"   ✅ Found pipeline: {pipeline_id}")
    print(f"   Current target_schema: {pipeline.get('target_schema', 'None')}")
    
except Exception as e:
    print(f"   ❌ Error: {e}")
    exit(1)

# Step 2: Update pipeline
print("\n2. Updating pipeline with target_schema='PUBLIC'...")
try:
    update_data = {
        "target_schema": "public"  # Use lowercase like ps_sn_p pipeline
    }
    
    response = requests.put(
        f"{API_BASE_URL}/pipelines/{pipeline_id}",
        json=update_data,
        timeout=30
    )
    
    if response.status_code in [200, 201]:
        updated_pipeline = response.json()
        print(f"   ✅ Pipeline updated successfully!")
        print(f"   New target_schema: {updated_pipeline.get('target_schema')}")
        print(f"   Target database: {updated_pipeline.get('target_database')}")
    else:
        print(f"   ❌ Failed to update pipeline: {response.status_code}")
        print(f"   Response: {response.text}")
        exit(1)
        
except Exception as e:
    print(f"   ❌ Error updating pipeline: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

print("\n" + "=" * 70)
print("✅ Pipeline updated successfully!")
print("=" * 70)
print(f"\nPipeline: {PIPELINE_NAME}")
print(f"Target: {pipeline.get('target_database')}.PUBLIC.test")
print("\nYou can now start the pipeline again.")

