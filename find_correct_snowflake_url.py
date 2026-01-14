"""Find the correct Snowflake Kafka Connector download URL."""
import requests
import json

print("=" * 70)
print("Finding Correct Snowflake Kafka Connector URL")
print("=" * 70)

# Try different possible paths
possible_paths = [
    "https://repo1.maven.org/maven2/com/snowflake/snowflake-kafka-connector/",
    "https://repo1.maven.org/maven2/net/snowflake/snowflake-kafka-connector/",
    "https://repo1.maven.org/maven2/com/snowflake/kafka-connector/",
    "https://repo1.maven.org/maven2/net/snowflake/kafka-connector/",
]

print("\n1. Checking Maven Central for Snowflake Kafka Connector...\n")

for base_path in possible_paths:
    print(f"   Trying: {base_path}")
    try:
        response = requests.get(base_path, timeout=10)
        if response.status_code == 200:
            print(f"   ✅ Path exists!")
            # Try to find versions
            if "snowflake-kafka-connector" in response.text:
                print(f"   ✅ Found connector references")
                # Look for version directories
                import re
                versions = re.findall(r'href="([\d.]+)/"', response.text)
                if versions:
                    latest = sorted(versions, key=lambda x: [int(i) for i in x.split('.')], reverse=True)[0]
                    print(f"   ✅ Latest version found: {latest}")
                    jar_url = f"{base_path}{latest}/snowflake-kafka-connector-{latest}.jar"
                    print(f"\n   Correct URL: {jar_url}")
                    
                    # Test if file exists
                    test_response = requests.head(jar_url, timeout=10)
                    if test_response.status_code == 200:
                        size = test_response.headers.get('Content-Length', 'unknown')
                        if size != 'unknown':
                            size_mb = int(size) / 1024 / 1024
                            print(f"   ✅ File exists! Size: {size_mb:.2f} MB")
                        else:
                            print(f"   ✅ File exists!")
                        break
                    else:
                        print(f"   ⚠️  File not found at that URL")
        else:
            print(f"   ❌ Path not found (Status: {response.status_code})")
    except Exception as e:
        print(f"   ❌ Error: {e}")

# Also check Maven search API
print(f"\n2. Searching Maven Central API...")
try:
    search_url = "https://search.maven.org/solrsearch/select?q=g:com.snowflake+AND+a:snowflake-kafka-connector&rows=1&wt=json"
    response = requests.get(search_url, timeout=10)
    if response.status_code == 200:
        data = response.json()
        if data.get('response', {}).get('docs'):
            doc = data['response']['docs'][0]
            group_id = doc.get('g', '')
            artifact_id = doc.get('a', '')
            latest_version = doc.get('latestVersion', '')
            print(f"   ✅ Found!")
            print(f"   Group ID: {group_id}")
            print(f"   Artifact ID: {artifact_id}")
            print(f"   Latest Version: {latest_version}")
            
            # Build correct URL
            correct_url = f"https://repo1.maven.org/maven2/{group_id.replace('.', '/')}/{artifact_id}/{latest_version}/{artifact_id}-{latest_version}.jar"
            print(f"\n   ✅ Correct URL: {correct_url}")
            
            # Test URL
            test_response = requests.head(correct_url, timeout=10)
            if test_response.status_code == 200:
                size = test_response.headers.get('Content-Length', 'unknown')
                if size != 'unknown':
                    size_mb = int(size) / 1024 / 1024
                    print(f"   ✅ Verified! Size: {size_mb:.2f} MB")
                else:
                    print(f"   ✅ Verified!")
except Exception as e:
    print(f"   ⚠️  API search failed: {e}")

print(f"\n{'='*70}")



