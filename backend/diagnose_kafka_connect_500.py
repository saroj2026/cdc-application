#!/usr/bin/env python3
"""Diagnose Kafka Connect 500 errors"""
import requests
import sys
import json

KAFKA_CONNECT_URL = "http://72.61.233.209:8083"

def print_status(message: str, status: str = "INFO"):
    """Print colored status message."""
    colors = {
        "SUCCESS": "\033[92m",  # Green
        "ERROR": "\033[91m",     # Red
        "WARNING": "\033[93m",   # Yellow
        "INFO": "\033[94m",      # Blue
        "RESET": "\033[0m"
    }
    symbol = {
        "SUCCESS": "✅",
        "ERROR": "❌",
        "WARNING": "⚠️",
        "INFO": "ℹ️"
    }
    print(f"{colors.get(status, '')}{symbol.get(status, '')} {message}{colors['RESET']}")

def main():
    """Diagnose Kafka Connect 500 errors."""
    print("\n" + "="*70)
    print("🔍 DIAGNOSING KAFKA CONNECT 500 ERRORS")
    print("="*70 + "\n")
    
    # Test basic connectivity
    print_status("1. Testing basic connectivity...", "INFO")
    try:
        response = requests.get(f"{KAFKA_CONNECT_URL}/", timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print_status("   Kafka Connect is accessible", "SUCCESS")
        else:
            print_status(f"   Unexpected status: {response.status_code}", "WARNING")
    except requests.exceptions.ConnectionError:
        print_status("   Cannot connect to Kafka Connect", "ERROR")
        print(f"   URL: {KAFKA_CONNECT_URL}")
        print("\n   Check:")
        print("   1. Kafka Connect is running")
        print("   2. Port 8083 is accessible")
        print("   3. Firewall is not blocking")
        return 1
    except Exception as e:
        print_status(f"   Error: {e}", "ERROR")
        return 1
    
    # Test connector-plugins endpoint
    print_status("\n2. Testing connector-plugins endpoint...", "INFO")
    try:
        response = requests.get(f"{KAFKA_CONNECT_URL}/connector-plugins", timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            plugins = response.json()
            print_status(f"   Found {len(plugins)} connector plugin(s)", "SUCCESS")
            
            # Check for AS400 connector
            as400_found = any("As400RpcConnector" in str(p) or "db2as400" in str(p).lower() for p in plugins)
            if as400_found:
                print_status("   AS400 connector plugin is available", "SUCCESS")
            else:
                print_status("   AS400 connector plugin NOT found", "WARNING")
        else:
            print_status(f"   Error: {response.status_code}", "ERROR")
            print(f"   Response: {response.text[:500]}")
    except Exception as e:
        print_status(f"   Error: {e}", "ERROR")
    
    # Test connectors endpoint (the one that's failing)
    print_status("\n3. Testing /connectors endpoint (the failing one)...", "INFO")
    try:
        response = requests.get(f"{KAFKA_CONNECT_URL}/connectors", timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            connectors = response.json()
            print_status(f"   Found {len(connectors)} connector(s)", "SUCCESS")
            if connectors:
                print("   Connectors:")
                for conn in connectors[:10]:
                    print(f"     - {conn}")
        elif response.status_code == 500:
            print_status("   Getting 500 error!", "ERROR")
            print(f"   Response: {response.text[:500]}")
            
            # Try to get more details
            try:
                error_json = response.json()
                print(f"   Error details: {json.dumps(error_json, indent=2)}")
            except:
                print(f"   Error text: {response.text[:500]}")
        else:
            print_status(f"   Unexpected status: {response.status_code}", "WARNING")
            print(f"   Response: {response.text[:500]}")
    except requests.exceptions.HTTPError as e:
        print_status(f"   HTTP Error: {e}", "ERROR")
        if hasattr(e.response, 'text'):
            print(f"   Response: {e.response.text[:500]}")
    except Exception as e:
        print_status(f"   Error: {e}", "ERROR")
    
    # Check cluster information
    print_status("\n4. Checking cluster information...", "INFO")
    try:
        response = requests.get(f"{KAFKA_CONNECT_URL}/", timeout=10)
        if response.status_code == 200:
            print("   Cluster info available")
    except Exception as e:
        print_status(f"   Error: {e}", "WARNING")
    
    # Recommendations
    print("\n" + "="*70)
    print("DIAGNOSIS & RECOMMENDATIONS")
    print("="*70)
    
    print("\nPossible causes of 500 errors:")
    print("1. ❌ Kafka Connect internal error")
    print("2. ❌ Corrupted connector state")
    print("3. ❌ Missing or incompatible connector plugin")
    print("4. ❌ Kafka/Zookeeper connectivity issues")
    print("5. ❌ Insufficient resources (memory/disk)")
    
    print("\nRecommended fixes:")
    print("1. ✅ Restart Kafka Connect container:")
    print("   ssh root@72.61.233.209")
    print("   docker restart $(docker ps | grep -i connect | awk '{print $1}' | head -1)")
    print("   sleep 30")
    
    print("\n2. ✅ Check Kafka Connect logs:")
    print("   docker logs $(docker ps | grep -i connect | awk '{print $1}' | head -1) | tail -100")
    
    print("\n3. ✅ Check if Kafka/Zookeeper are running:")
    print("   docker ps | grep -E 'kafka|zookeeper'")
    
    print("\n4. ✅ Verify AS400 connector plugin is installed:")
    print("   docker exec $(docker ps | grep -i connect | awk '{print $1}' | head -1) ls -la /kafka/connect/debezium-connector-ibmi")
    
    print("\n5. ✅ Check connector state files (may need cleanup):")
    print("   docker exec $(docker ps | grep -i connect | awk '{print $1}' | head -1) ls -la /tmp/kafka-connect/offsets")
    
    print("\n6. ✅ If all else fails, restart entire Kafka stack:")
    print("   docker-compose restart")
    print("   OR")
    print("   docker restart kafka zookeeper kafka-connect")
    
    print("\n" + "="*70)
    print("Next steps:")
    print("1. Restart Kafka Connect container")
    print("2. Check logs for specific error messages")
    print("3. Verify all services are running")
    print("4. Try starting pipeline again")
    print("="*70 + "\n")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())


