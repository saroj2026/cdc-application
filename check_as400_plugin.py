#!/usr/bin/env python3
"""Check if AS400 Debezium connector plugin is available in Kafka Connect"""
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
    """Check AS400 plugin availability."""
    print("\n" + "="*60)
    print("🔍 CHECKING AS400 DEBEZIUM CONNECTOR PLUGIN")
    print("="*60 + "\n")
    
    print_status(f"Connecting to Kafka Connect: {KAFKA_CONNECT_URL}", "INFO")
    
    # Test basic connectivity
    try:
        response = requests.get(f"{KAFKA_CONNECT_URL}/", timeout=10)
        if response.status_code == 200:
            print_status("Kafka Connect is accessible", "SUCCESS")
        else:
            print_status(f"Kafka Connect returned status {response.status_code}", "WARNING")
    except requests.exceptions.ConnectionError:
        print_status("Cannot connect to Kafka Connect. Is it running?", "ERROR")
        print(f"   URL: {KAFKA_CONNECT_URL}")
        print("\nTroubleshooting:")
        print("1. Check if Kafka Connect is running on the server")
        print("2. Verify port 8083 is accessible")
        print("3. Check firewall settings")
        return 1
    except Exception as e:
        print_status(f"Error connecting: {e}", "ERROR")
        return 1
    
    # Get connector plugins
    print_status("\nFetching connector plugins...", "INFO")
    try:
        response = requests.get(f"{KAFKA_CONNECT_URL}/connector-plugins", timeout=10)
        response.raise_for_status()
        plugins = response.json()
        
        print_status(f"Found {len(plugins)} connector plugin(s)", "SUCCESS")
        print()
        
        # Search for AS400 connector
        as400_plugins = []
        db2_plugins = []
        ibmi_plugins = []
        
        for plugin in plugins:
            class_name = plugin.get("class", "")
            if "As400RpcConnector" in class_name or "db2as400" in class_name.lower():
                as400_plugins.append(plugin)
            elif "Db2Connector" in class_name and "db2" in class_name.lower():
                db2_plugins.append(plugin)
            elif "ibmi" in class_name.lower() or "ibm_i" in class_name.lower():
                ibmi_plugins.append(plugin)
        
        # Check for AS400 connector
        if as400_plugins:
            print_status("AS400 Connector Found!", "SUCCESS")
            print()
            for plugin in as400_plugins:
                print(f"   Class: {plugin.get('class')}")
                print(f"   Type: {plugin.get('type', 'N/A')}")
                print(f"   Version: {plugin.get('version', 'N/A')}")
                print()
        else:
            print_status("AS400 Connector (As400RpcConnector) NOT found", "ERROR")
            print()
        
        # Check for IBM i connector
        if ibmi_plugins:
            print_status("IBM i Connector Found!", "SUCCESS")
            print()
            for plugin in ibmi_plugins:
                print(f"   Class: {plugin.get('class')}")
                print(f"   Type: {plugin.get('type', 'N/A')}")
                print(f"   Version: {plugin.get('version', 'N/A')}")
                print()
        
        # Check for Db2 connector (fallback)
        if db2_plugins:
            print_status("Db2 Connector Found (may work for AS400)", "WARNING")
            print()
            for plugin in db2_plugins:
                print(f"   Class: {plugin.get('class')}")
                print(f"   Type: {plugin.get('type', 'N/A')}")
                print(f"   Version: {plugin.get('version', 'N/A')}")
                print()
            print("   Note: Db2 connector can be used for AS400 with proper configuration")
            print()
        
        # Show all available connectors
        print_status("\nAll Available Connectors:", "INFO")
        print("-" * 60)
        for plugin in plugins:
            class_name = plugin.get("class", "")
            if any(keyword in class_name.lower() for keyword in ["debezium", "db2", "as400", "ibmi", "postgres", "sqlserver", "mysql"]):
                print(f"   • {class_name}")
        print()
        
        # Summary
        print("="*60)
        if as400_plugins:
            print_status("✅ AS400 Connector is INSTALLED and AVAILABLE", "SUCCESS")
            print("\nYou can now start AS400 pipelines!")
        elif ibmi_plugins:
            print_status("✅ IBM i Connector is INSTALLED (may work for AS400)", "SUCCESS")
            print("\nThis connector may work for AS400 pipelines.")
        elif db2_plugins:
            print_status("⚠️  Only Db2 Connector found (may work with configuration)", "WARNING")
            print("\nYou may need to install the AS400-specific connector:")
            print("   io.debezium.connector.db2as400.As400RpcConnector")
        else:
            print_status("❌ AS400 Connector is NOT INSTALLED", "ERROR")
            print("\nTo install:")
            print("1. SSH to server: ssh root@72.61.233.209")
            print("2. Run: /tmp/install_as400_connector_remote.sh")
            print("   OR manually install debezium-connector-ibmi plugin")
        print("="*60 + "\n")
        
        return 0 if as400_plugins or ibmi_plugins else 1
        
    except requests.exceptions.HTTPError as e:
        print_status(f"HTTP Error: {e}", "ERROR")
        if e.response.status_code == 404:
            print("   Kafka Connect endpoint not found. Check URL and port.")
        return 1
    except Exception as e:
        print_status(f"Error fetching plugins: {e}", "ERROR")
        return 1

if __name__ == "__main__":
    sys.exit(main())


