"""Inspect Snowflake connector JAR contents using alternative methods."""
import paramiko
import requests
import zipfile
import io

print("=" * 70)
print("Inspecting Snowflake Connector JAR")
print("=" * 70)

# Method 1: Download directly and inspect
print("\n1. Downloading JAR directly to inspect...")
CONNECTOR_URL = "https://repo1.maven.org/maven2/com/snowflake/snowflake-kafka-connector/3.2.2/snowflake-kafka-connector-3.2.2.jar"

try:
    print(f"   Downloading from: {CONNECTOR_URL}")
    print(f"   This may take 1-2 minutes (177MB)...")
    
    response = requests.get(CONNECTOR_URL, stream=True, timeout=300)
    response.raise_for_status()
    
    # Read first part to check
    chunk_size = 1024 * 1024  # 1MB chunks
    total_size = 0
    chunks = []
    
    for chunk in response.iter_content(chunk_size=chunk_size):
        chunks.append(chunk)
        total_size += len(chunk)
        if total_size > 50 * 1024 * 1024:  # Read first 50MB to inspect
            break
    
    jar_content = b''.join(chunks)
    print(f"   ✅ Downloaded {total_size / 1024 / 1024:.2f} MB for inspection")
    
    # Inspect JAR
    print(f"\n2. Inspecting JAR contents...")
    try:
        jar_file = zipfile.ZipFile(io.BytesIO(jar_content))
        
        # Check for connector class
        connector_class = 'com/snowflake/kafka/connector/SnowflakeSinkConnector.class'
        try:
            info = jar_file.getinfo(connector_class)
            print(f"   ✅✅✅ CONNECTOR CLASS FOUND! ✅✅✅")
            print(f"      Path: {connector_class}")
            print(f"      Size: {info.file_size} bytes")
            print(f"      Compressed: {info.compress_size} bytes")
        except KeyError:
            print(f"   ❌ Connector class NOT found at: {connector_class}")
            
            # Search for any Snowflake connector classes
            print(f"\n   Searching for Snowflake connector classes...")
            snowflake_classes = [f for f in jar_file.namelist() 
                               if 'snowflake' in f.lower() and 'connector' in f.lower() and f.endswith('.class')]
            if snowflake_classes:
                print(f"   Found {len(snowflake_classes)} Snowflake connector classes:")
                for cls in snowflake_classes[:15]:
                    print(f"      {cls}")
            else:
                print(f"   ❌ No Snowflake connector classes found")
        
        # Check package structure
        print(f"\n3. Checking package structure...")
        packages = set()
        for name in jar_file.namelist():
            if name.startswith('com/snowflake/kafka/connector/'):
                parts = name.split('/')
                if len(parts) > 4:
                    pkg = '/'.join(parts[:4])
                    packages.add(pkg)
        
        if packages:
            print(f"   Package structure:")
            for pkg in sorted(list(packages))[:10]:
                print(f"      {pkg}/")
        
        # Check META-INF/services
        print(f"\n4. Checking META-INF/services...")
        service_files = [f for f in jar_file.namelist() if 'META-INF/services' in f]
        if service_files:
            print(f"   Found {len(service_files)} service files:")
            for f in service_files:
                print(f"      {f}")
                try:
                    content = jar_file.read(f).decode('utf-8')
                    print(f"      Content: {content[:150]}")
                except:
                    pass
        else:
            print(f"   ⚠️  No META-INF/services files found")
        
        # Check manifest
        print(f"\n5. Checking MANIFEST.MF...")
        try:
            manifest = jar_file.read('META-INF/MANIFEST.MF').decode('utf-8')
            print(f"   Manifest (first 30 lines):")
            for line in manifest.split('\n')[:30]:
                if line.strip():
                    print(f"      {line}")
        except KeyError:
            print(f"   ⚠️  MANIFEST.MF not found")
        
        # List all files in connector package
        print(f"\n6. Listing all files in connector package...")
        connector_files = [f for f in jar_file.namelist() 
                          if f.startswith('com/snowflake/kafka/connector/')]
        if connector_files:
            print(f"   Found {len(connector_files)} files in connector package")
            print(f"   Key files:")
            for f in sorted(connector_files)[:20]:
                if f.endswith('.class'):
                    print(f"      {f}")
        
        jar_file.close()
        
    except zipfile.BadZipFile:
        print(f"   ❌ Invalid JAR file (not a valid ZIP)")
    except Exception as e:
        print(f"   ❌ Error inspecting JAR: {e}")
        import traceback
        traceback.print_exc()
    
except Exception as e:
    print(f"   ❌ Download failed: {e}")

print(f"\n{'='*70}")
print("Documentation Summary")
print(f"{'='*70}")
print(f"\n✅ Connector Class: com.snowflake.kafka.connector.SnowflakeSinkConnector")
print(f"✅ Documentation: https://docs.snowflake.com/en/user-guide/kafka-connector-install.html")
print(f"\nKey Requirements:")
print(f"1. JAR file in plugins directory")
print(f"2. Restart Kafka Connect after installation")
print(f"3. Connector class: com.snowflake.kafka.connector.SnowflakeSinkConnector")
print(f"4. Compatible with Kafka Connect API 3.9.0+")
print(f"\nIf connector class exists but doesn't appear in plugin list,")
print(f"it may still work when creating a pipeline (lazy loading).")
print()



