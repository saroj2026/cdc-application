"""Kafka Connect API client."""
import requests
import os
from typing import Dict, Any, Optional, List


class KafkaConnectClient:
    """Client for interacting with Kafka Connect REST API.
    
    Note: Kafka UI (typically on port 8080) is different from Kafka Connect REST API (port 8083).
    This client connects to the REST API endpoint for managing connectors.
    
    Example:
        # Using environment variable
        client = KafkaConnectClient()  # Reads from KAFKA_CONNECT_URL env var
        
        # Using explicit URL
        client = KafkaConnectClient("http://72.61.233.209:8083")
    """
    
    def __init__(self, base_url: Optional[str] = None):
        """Initialize Kafka Connect client.
        
        Args:
            base_url: Base URL of Kafka Connect REST API. If not provided, 
                     reads from KAFKA_CONNECT_URL environment variable or 
                     defaults to http://72.61.233.209:8083
                     
        Note: 
            - Kafka Connect REST API: http://72.61.233.209:8083
            - Kafka UI (for monitoring): http://72.61.233.209:8080
        """
        if base_url is None:
            base_url = os.getenv("KAFKA_CONNECT_URL", "http://72.61.233.209:8083")
        self.base_url = base_url.rstrip('/')
    
    def get_connector_status(self, connector_name: str) -> Dict[str, Any]:
        """Get connector status.
        
        Args:
            connector_name: Name of the connector
            
        Returns:
            Connector status dictionary
        """
        url = f"{self.base_url}/connectors/{connector_name}/status"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    
    def get_connector_config(self, connector_name: str) -> Dict[str, Any]:
        """Get connector configuration.
        
        Args:
            connector_name: Name of the connector
            
        Returns:
            Connector configuration dictionary
        """
        url = f"{self.base_url}/connectors/{connector_name}/config"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    
    def create_connector(self, connector_name: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new connector.
        
        Args:
            connector_name: Name of the connector
            config: Connector configuration
            
        Returns:
            Created connector information
        """
        url = f"{self.base_url}/connectors"
        payload = {
            "name": connector_name,
            "config": config
        }
        response = requests.post(url, json=payload, timeout=30)
        response.raise_for_status()
        return response.json()
    
    def delete_connector(self, connector_name: str) -> None:
        """Delete a connector.
        
        Args:
            connector_name: Name of the connector
        """
        url = f"{self.base_url}/connectors/{connector_name}"
        response = requests.delete(url, timeout=10)
        response.raise_for_status()
    
    def list_connectors(self) -> List[str]:
        """List all connectors.
        
        Returns:
            List of connector names
        """
        url = f"{self.base_url}/connectors"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()

