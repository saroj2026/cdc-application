"""Kafka Connect REST API client."""

from __future__ import annotations

import logging
import time
from typing import Any, Dict, List, Optional
from urllib.parse import quote

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from ingestion.retry import retry_on_connection_error, retry_on_timeout

logger = logging.getLogger(__name__)


class KafkaConnectClient:
    """Client for interacting with Kafka Connect REST API."""
    
    def __init__(
        self,
        base_url: str = "http://localhost:8083",
        timeout: int = 30,
        max_retries: int = 3
    ):
        """Initialize Kafka Connect client.
        
        Args:
            base_url: Base URL for Kafka Connect REST API
            timeout: Request timeout in seconds
            max_retries: Maximum number of retries for failed requests
        """
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.session = requests.Session()
        
        # Configure retry strategy - retry on transient errors
        retry_strategy = Retry(
            total=3,  # 3 retry attempts
            backoff_factor=1.0,
            status_forcelist=[429, 500, 502, 503, 504],  # Retry on server errors
            allowed_methods=["GET", "POST", "PUT", "DELETE"]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
    
    @retry_on_connection_error(max_attempts=3, delay=1.0, backoff=2.0)
    @retry_on_timeout(max_attempts=2, delay=0.5, backoff=2.0)
    def _request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Make HTTP request to Kafka Connect API with retry logic.
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint (without base URL)
            data: Request body data
            params: Query parameters
            
        Returns:
            Response JSON data
            
        Raises:
            requests.RequestException: If request fails after retries
        """
        # URL encode the endpoint to handle special characters in connector names
        # Note: connector names in Kafka Connect should not have special characters,
        # but we encode to be safe
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = self.session.request(
                method=method,
                url=url,
                json=data,
                params=params,
                timeout=self.timeout,
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            
            # Some endpoints return empty response
            if response.content:
                return response.json()
            return {}
            
        except requests.exceptions.HTTPError as e:
            # Handle different HTTP status codes appropriately
            if e.response:
                status_code = e.response.status_code
                
                # 404 Not Found - connector doesn't exist (expected in some cases)
                if status_code == 404:
                    logger.debug(f"Kafka Connect API {method} {url} returned 404 Not Found (connector may not exist)")
                    # Don't log as error - this is expected when checking for non-existent connectors
                
                # 409 Conflict - connector already exists (expected during creation)
                elif status_code == 409:
                    logger.debug(f"Kafka Connect API {method} {url} returned 409 Conflict (will be handled by caller)")
                
                # Other errors - log as warning or error depending on severity
                else:
                    # Provide better error messages for other errors
                    error_msg = f"Kafka Connect API {method} {url} failed with status {status_code}"
                    if hasattr(e.response, 'text'):
                        try:
                            error_json = e.response.json()
                            error_detail = error_json.get('message', error_json.get('error', str(error_json)))
                            error_msg += f": {error_detail}"
                        except:
                            error_detail = e.response.text[:1000]  # Limit error message length
                            error_msg += f": {error_detail}"
                    
                    # Log 4xx as warning, 5xx as error
                    if status_code >= 500:
                        logger.error(error_msg)
                    else:
                        logger.warning(error_msg)
            # Log the request data for debugging
            if data:
                logger.debug(f"Request data: {data}")
            raise
        except requests.exceptions.RequestException as e:
            logger.error(f"Kafka Connect API request failed: {method} {url} - {e}")
            raise
    
    def list_connectors(self) -> List[str]:
        """List all connector names.
        
        Returns:
            List of connector names
        """
        try:
            response = self._request("GET", "/connectors")
            # Handle both list and dict responses
            if isinstance(response, list):
                return response
            return response.get("connectors", [])
        except requests.exceptions.HTTPError as e:
            # If we get 400/500 errors, it might be a temporary issue or API change
            # Return empty list and let the caller handle it
            if e.response and e.response.status_code in [400, 500]:
                error_detail = ""
                if hasattr(e.response, 'text'):
                    try:
                        error_json = e.response.json()
                        error_detail = error_json.get('message', error_json.get('error', ''))
                    except:
                        error_detail = e.response.text[:200]
                logger.warning(f"Kafka Connect returned {e.response.status_code} when listing connectors (may be temporary): {error_detail}")
                return []
            logger.error(f"Failed to list connectors: {e}")
            return []
        except Exception as e:
            logger.error(f"Failed to list connectors: {e}")
            return []
    
    def get_connector_info(self, connector_name: str) -> Dict[str, Any]:
        """Get connector information.
        
        Args:
            connector_name: Name of the connector
            
        Returns:
            Connector information dictionary
            
        Raises:
            requests.exceptions.HTTPError: If connector not found or server error
        """
        try:
            return self._request("GET", f"/connectors/{connector_name}")
        except requests.exceptions.HTTPError as e:
            # Re-raise to let caller handle
            raise
        except Exception as e:
            # Wrap other exceptions
            raise requests.exceptions.HTTPError(f"Failed to get connector info: {e}")
    
    def get_connector_config(self, connector_name: str) -> Dict[str, Any]:
        """Get connector configuration.
        
        Args:
            connector_name: Name of the connector
            
        Returns:
            Connector configuration dictionary
        """
        # URL encode connector name to handle special characters like #
        encoded_name = quote(connector_name, safe='')
        return self._request("GET", f"/connectors/{encoded_name}/config")
    
    def get_connector_status(self, connector_name: str) -> Optional[Dict[str, Any]]:
        """Get connector status.
        
        Args:
            connector_name: Name of the connector
            
        Returns:
            Connector status dictionary with state and tasks, or None if connector doesn't exist
        """
        # URL encode connector name to handle special characters like #
        encoded_name = quote(connector_name, safe='')
        try:
            return self._request("GET", f"/connectors/{encoded_name}/status")
        except requests.exceptions.HTTPError as e:
            # 404 means connector doesn't exist - return None instead of raising
            if e.response and e.response.status_code == 404:
                logger.debug(f"Connector {connector_name} not found (404) - this is expected if connector was deleted")
                return None
            # Re-raise other errors
            raise
    
    def create_connector(
        self,
        connector_name: str,
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create a new connector.
        
        Args:
            connector_name: Name of the connector
            config: Connector configuration dictionary
            
        Returns:
            Created connector information
        """
        data = {
            "name": connector_name,
            "config": config
        }
        
        logger.info(f"Creating connector: {connector_name}")
        try:
            response = self._request("POST", "/connectors", data=data)
            logger.info(f"Connector created: {connector_name}")
            return response
        except requests.exceptions.HTTPError as e:
            if e.response and e.response.status_code == 409:
                # Connector already exists - check its status
                logger.info(f"Connector {connector_name} already exists, checking status...")
                try:
                    status = self.get_connector_status(connector_name)
                    if status is None:
                        # Connector doesn't exist, create it
                        logger.info(f"Connector {connector_name} not found, will create new one")
                        # Continue to create the connector
                    else:
                        connector_state = status.get('connector', {}).get('state', 'UNKNOWN')
                    
                    if connector_state == 'RUNNING':
                        logger.info(f"Connector {connector_name} is already RUNNING, reusing it")
                        return self.get_connector_info(connector_name)
                    elif connector_state in ['FAILED', 'STOPPED']:
                        logger.warning(f"Connector {connector_name} is {connector_state}, attempting restart...")
                        try:
                            self.restart_connector(connector_name)
                            # Wait for restart
                            if self.wait_for_connector(connector_name, "RUNNING", max_wait_seconds=30):
                                logger.info(f"Successfully restarted connector {connector_name}")
                                return self.get_connector_info(connector_name)
                            else:
                                logger.warning(f"Restart did not bring connector to RUNNING state, will delete and recreate")
                                self.delete_connector(connector_name)
                                # Retry creation
                                response = self._request("POST", "/connectors", data=data)
                                logger.info(f"Connector recreated: {connector_name}")
                                return response
                        except Exception as restart_error:
                            logger.warning(f"Failed to restart connector: {restart_error}, will delete and recreate")
                            self.delete_connector(connector_name)
                            # Retry creation
                            response = self._request("POST", "/connectors", data=data)
                            logger.info(f"Connector recreated: {connector_name}")
                            return response
                    else:
                        # UNASSIGNED or other state - wait and check
                        logger.info(f"Connector {connector_name} is {connector_state}, waiting...")
                        if self.wait_for_connector(connector_name, "RUNNING", max_wait_seconds=30):
                            logger.info(f"Connector {connector_name} is now RUNNING")
                            return self.get_connector_info(connector_name)
                        else:
                            raise Exception(f"Connector {connector_name} exists but could not be started (state: {connector_state})")
                except requests.exceptions.HTTPError as status_error:
                    # If we can't get status, the connector might be in a bad state
                    logger.warning(f"Could not get connector status: {status_error}, will delete and recreate")
                    try:
                        self.delete_connector(connector_name)
                    except Exception:
                        pass  # Ignore deletion errors
                    # Retry creation
                    response = self._request("POST", "/connectors", data=data)
                    logger.info(f"Connector recreated: {connector_name}")
                    return response
            else:
                # Re-raise other HTTP errors
                raise
    
    def update_connector(
        self,
        connector_name: str,
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update connector configuration.
        
        Args:
            connector_name: Name of the connector
            config: Updated connector configuration dictionary
            
        Returns:
            Updated connector information
        """
        logger.info(f"Updating connector: {connector_name}")
        # URL encode connector name to handle special characters like #
        encoded_name = quote(connector_name, safe='')
        response = self._request("PUT", f"/connectors/{encoded_name}/config", data=config)
        logger.info(f"Connector updated: {connector_name}")
        return response
    
    def restart_connector(self, connector_name: str) -> Dict[str, Any]:
        """Restart a connector.
        
        Args:
            connector_name: Name of the connector
            
        Returns:
            Restart result
        """
        logger.info(f"Restarting connector: {connector_name}")
        try:
            # Kafka Connect REST API: POST /connectors/{name}/restart
            response = self._request("POST", f"/connectors/{connector_name}/restart")
            logger.info(f"Connector restart initiated: {connector_name}")
            return response
        except requests.exceptions.HTTPError as e:
            if e.response and e.response.status_code == 404:
                logger.warning(f"Connector {connector_name} not found, cannot restart")
                raise
            else:
                logger.error(f"Failed to restart connector {connector_name}: {e}")
                raise
    
    def delete_connector(self, connector_name: str) -> None:
        """Delete a connector.
        
        Args:
            connector_name: Name of the connector to delete
        """
        logger.info(f"Deleting connector: {connector_name}")
        try:
            # URL encode connector name to handle special characters like #
            encoded_name = quote(connector_name, safe='')
            self._request("DELETE", f"/connectors/{encoded_name}")
            logger.info(f"Connector deleted: {connector_name}")
        except requests.exceptions.HTTPError as e:
            if e.response and e.response.status_code == 404:
                logger.debug(f"Connector {connector_name} not found, skipping deletion")
                return
            elif e.response and e.response.status_code == 500:
                # Kafka Connect might be having issues - log but don't fail
                logger.warning(f"Kafka Connect returned 500 when deleting connector {connector_name} (continuing anyway)")
                return
            else:
                # For other errors, log but don't fail
                logger.warning(f"Could not delete connector {connector_name}: {e}")
                return
    
    def restart_connector(self, connector_name: str) -> None:
        """Restart a connector.
        
        Args:
            connector_name: Name of the connector to restart
        """
        logger.info(f"Restarting connector: {connector_name}")
        self._request("POST", f"/connectors/{connector_name}/restart")
        logger.info(f"Connector restarted: {connector_name}")
    
    def pause_connector(self, connector_name: str) -> None:
        """Pause a connector.
        
        Args:
            connector_name: Name of the connector to pause
        """
        logger.info(f"Pausing connector: {connector_name}")
        self._request("PUT", f"/connectors/{connector_name}/pause")
        logger.info(f"Connector paused: {connector_name}")
    
    def resume_connector(self, connector_name: str) -> None:
        """Resume a paused connector.
        
        Args:
            connector_name: Name of the connector to resume
        """
        logger.info(f"Resuming connector: {connector_name}")
        self._request("PUT", f"/connectors/{connector_name}/resume")
        logger.info(f"Connector resumed: {connector_name}")
    
    def wait_for_connector(
        self,
        connector_name: str,
        target_state: str = "RUNNING",
        max_wait_seconds: int = 60,
        poll_interval: int = 3
    ) -> bool:
        """Wait for connector to reach target state.
        
        Args:
            connector_name: Name of the connector
            target_state: Target state to wait for (RUNNING, FAILED, etc.)
            max_wait_seconds: Maximum time to wait in seconds
            poll_interval: Polling interval in seconds
            
        Returns:
            True if connector reached target state, False if timeout
        """
        start_time = time.time()
        
        while time.time() - start_time < max_wait_seconds:
            try:
                status = self.get_connector_status(connector_name)
                if status is None:
                    # Connector doesn't exist, return False
                    logger.debug(f"Connector {connector_name} not found, cannot check state")
                    return False
                connector_state = status.get("connector", {}).get("state", "UNKNOWN")
                
                logger.debug(
                    f"Connector {connector_name} state: {connector_state} "
                    f"(waiting for {target_state})"
                )
                
                if connector_state == target_state:
                    logger.info(
                        f"Connector {connector_name} reached state: {target_state}"
                    )
                    return True
                
                if connector_state == "FAILED":
                    logger.error(f"Connector {connector_name} failed")
                    return False
                
                time.sleep(poll_interval)
                
            except Exception as e:
                logger.warning(f"Error checking connector status: {e}")
                time.sleep(poll_interval)
        
        logger.warning(
            f"Timeout waiting for connector {connector_name} to reach state {target_state}"
        )
        return False
    
    def get_connector_plugins(self) -> List[Dict[str, Any]]:
        """Get list of available connector plugins.
        
        Returns:
            List of connector plugin information
        """
        try:
            response = self._request("GET", "/connector-plugins")
            return response
        except Exception as e:
            logger.error(f"Failed to get connector plugins: {e}")
            return []
    
    def validate_connector_config(
        self,
        connector_class: str,
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate connector configuration.
        
        Args:
            connector_class: Connector class name
            config: Configuration to validate
            
        Returns:
            Validation result dictionary
        """
        # URL encode the connector class
        import urllib.parse
        encoded_class = urllib.parse.quote(connector_class, safe='')
        
        return self._request(
            "PUT",
            f"/connector-plugins/{encoded_class}/config/validate",
            data=config
        )
    
    def test_connection(self) -> bool:
        """Test connection to Kafka Connect REST API.
        
        Returns:
            True if connection is successful, False otherwise
        """
        try:
            self._request("GET", "/")
            return True
        except Exception as e:
            logger.error(f"Kafka Connect connection test failed: {e}")
            return False



