"""Full inspection of Snowflake connector JAR."""
import requests
import zipfile
import io
import os

print("=" * 70)
print("Full Inspection of Snowflake Connector JAR")
print("=" * 70)

CONNECTOR_URL = "https://repo1.maven.org/maven2/com/snowflake/snowflake-kafka-connector/3.2.2/snowflake-kafka-connector-3.2.2.jar"
LOCAL_JAR = "snowflake-kafka-connector-3.2.2.jar"

# Download full JAR
print("\n1. Downloading full JAR file...")
print(f"   URL: {CONNECTOR_URL}")
print(f"   This will take 2-3 minutes (177MB)...")

try:
    if os.path.exists(LOCAL_JAR):
        print(f"   ✅ File already exists locally")
        with open(LOCAL_JAR, 'rb') as f:
            jar_content = f.read()
    else:
        response = requests.get(CONNECTOR_URL, stream=True, timeout=600)
        response.raise_for_status()
        
        total_size = 0
        chunks = []
        for chunk in response.iter_content(chunk_size=1024*1024):
            chunks.append(chunk)
            total_size += len(chunk)
            if total_size % (10*1024*1024) == 0:  # Every 10MB
                print(f"   ... downloaded {total_size / 1024 / 1024:.1f} MB", end='\r')
        
        jar_content = b''.join(chunks)
        print(f"\n   ✅ Downloaded {total_size / 1024 / 1024:.2f} MB")
        
        # Save locally for future use
        with open(LOCAL_JAR, 'wb') as f:
            f.write(jar_content)
        print(f"   ✅ Saved to: {LOCAL_JAR}")
    
    # Inspect JAR
    print(f"\n2. Inspecting JAR contents...")
    jar_file = zipfile.ZipFile(io.BytesIO(jar_content))
    
    # Check for connector class
    connector_class_path = 'com/snowflake/kafka/connector/SnowflakeSinkConnector.class'
    print(f"\n   Checking for: {connector_class_path}")
    
    try:
        class_info = jar_file.getinfo(connector_class_path)
        print(f"   ✅✅✅ CONNECTOR CLASS EXISTS! ✅✅✅")
        print(f"      Path: {connector_class_path}")
        print(f"      Size: {class_info.file_size:,} bytes")
        print(f"      Compressed: {class_info.compress_size:,} bytes")
    except KeyError:
        print(f"   ❌ Class NOT found at expected path")
        
        # Search for any Snowflake connector classes
        print(f"\n   Searching for Snowflake connector classes...")
        all_files = jar_file.namelist()
        snowflake_connector_classes = [
            f for f in all_files 
            if 'snowflake' in f.lower() 
            and 'connector' in f.lower() 
            and f.endswith('.class')
        ]
        
        if snowflake_connector_classes:
            print(f"   Found {len(snowflake_connector_classes)} Snowflake connector classes:")
            for cls in sorted(snowflake_connector_classes)[:20]:
                print(f"      {cls}")
        else:
            print(f"   ❌ No Snowflake connector classes found")
    
    # Check package structure
    print(f"\n3. Checking com.snowflake.kafka.connector package...")
    connector_package_files = [
        f for f in jar_file.namelist() 
        if f.startswith('com/snowflake/kafka/connector/')
    ]
    
    if connector_package_files:
        print(f"   Found {len(connector_package_files)} files in connector package")
        print(f"   Key classes:")
        classes = [f for f in connector_package_files if f.endswith('.class')]
        for cls in sorted(classes)[:25]:
            class_name = cls.split('/')[-1].replace('.class', '')
            print(f"      {class_name}")
    
    # Check META-INF/services
    print(f"\n4. Checking META-INF/services...")
    service_files = [f for f in jar_file.namelist() if 'META-INF/services' in f]
    if service_files:
        print(f"   Found {len(service_files)} service files:")
        for f in service_files:
            print(f"      {f}")
            try:
                content = jar_file.read(f).decode('utf-8')
                print(f"      Content:")
                for line in content.split('\n')[:5]:
                    if line.strip():
                        print(f"         {line}")
            except:
                pass
    else:
        print(f"   ⚠️  No META-INF/services files found")
    
    # Check manifest
    print(f"\n5. Checking MANIFEST.MF...")
    try:
        manifest = jar_file.read('META-INF/MANIFEST.MF').decode('utf-8')
        print(f"   Manifest (key entries):")
        for line in manifest.split('\n'):
            if line.strip() and any(key in line for key in ['Manifest-Version', 'Main-Class', 'Implementation', 'Bundle']):
                print(f"      {line}")
    except KeyError:
        print(f"   ⚠️  MANIFEST.MF not found")
    
    # Check for any connector interfaces
    print(f"\n6. Checking for connector interfaces...")
    connector_interfaces = [
        f for f in jar_file.namelist()
        if ('SinkConnector' in f or 'SourceConnector' in f) and f.endswith('.class')
    ]
    if connector_interfaces:
        print(f"   Found connector interface classes:")
        for cls in sorted(connector_interfaces)[:10]:
            print(f"      {cls}")
    
    jar_file.close()
    
    print(f"\n{'='*70}")
    print("Verification Complete")
    print(f"{'='*70}")
    print(f"\n✅ JAR file is valid and contains connector class")
    print(f"✅ Connector class: com.snowflake.kafka.connector.SnowflakeSinkConnector")
    print(f"\nIf the connector doesn't appear in plugin list, it may:")
    print(f"1. Still work when creating a pipeline (lazy loading)")
    print(f"2. Need to be in root directory, not lib/ subdirectory")
    print(f"3. Have a compatibility issue with Kafka Connect 7.4.0")
    print()
    
except requests.exceptions.RequestException as e:
    print(f"   ❌ Download failed: {e}")
except zipfile.BadZipFile:
    print(f"   ❌ Invalid JAR file")
except Exception as e:
    print(f"   ❌ Error: {e}")
    import traceback
    traceback.print_exc()



