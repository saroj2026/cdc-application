"""Connection service for testing and discovery operations."""

import uuid
import logging
import time
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime

from ingestion.database import SessionLocal
from ingestion.database.models_db import ConnectionModel, ConnectionTestModel
from ingestion.connectors.postgresql import PostgreSQLConnector
from ingestion.connectors.sqlserver import SQLServerConnector
from ingestion.connectors.s3 import S3Connector
from ingestion.connectors.as400 import AS400Connector
from ingestion.connectors.oracle import OracleConnector

logger = logging.getLogger(__name__)


class ConnectionService:
    """Service for managing database connections."""
    
    def __init__(self):
        """Initialize connection service."""
        self.session = SessionLocal()
    
    def test_connection(
        self,
        connection_id: str,
        save_history: bool = True
    ) -> Dict[str, Any]:
        """Test database connection and optionally save to history.
        
        Args:
            connection_id: Connection ID to test
            save_history: Whether to save test result to history
            
        Returns:
            Test result dictionary with status and details
        """
        try:
            connection = self.session.query(ConnectionModel).filter_by(
                id=connection_id
            ).first()
            
            if not connection:
                return {
                    "success": False,
                    "error": f"Connection not found: {connection_id}",
                    "status": "NOT_FOUND"
                }
            
            start_time = time.time()
            
            connector = self._get_connector(connection)
            connection_obj = None
            
            try:
                connection_obj = connector.connect()
                
                # Get version if method exists, otherwise use test_connection result
                if hasattr(connector, 'get_version'):
                    version = connector.get_version()
                else:
                    # For connectors without get_version (like S3), use test_connection
                    test_result = connector.test_connection()
                    version = "Connection verified" if test_result else "Connection failed"
                
                # Disconnect if method exists and we have a connection object
                if hasattr(connector, 'disconnect') and connection_obj:
                    connector.disconnect(connection_obj)
                
                response_time_ms = int((time.time() - start_time) * 1000)
                
                result = {
                    "success": True,
                    "status": "SUCCESS",
                    "response_time_ms": response_time_ms,
                    "version": version,
                    "tested_at": datetime.utcnow().isoformat()
                }
                
                if save_history:
                    self._save_test_history(
                        connection_id=connection_id,
                        status="SUCCESS",
                        response_time_ms=response_time_ms
                    )
                    
                    connection.last_tested_at = datetime.utcnow()
                    connection.last_test_status = "success"  # Use lowercase to match frontend
                    self.session.commit()
                
                return result
                
            except Exception as e:
                response_time_ms = int((time.time() - start_time) * 1000)
                error_msg = str(e)
                
                logger.error(f"Connection test failed for {connection_id}: {error_msg}")
                
                result = {
                    "success": False,
                    "status": "FAILED",
                    "error": error_msg,
                    "response_time_ms": response_time_ms,
                    "tested_at": datetime.utcnow().isoformat()
                }
                
                if save_history:
                    self._save_test_history(
                        connection_id=connection_id,
                        status="FAILED",
                        response_time_ms=response_time_ms,
                        error_message=error_msg
                    )
                    
                    connection.last_tested_at = datetime.utcnow()
                    connection.last_test_status = "failed"  # Use lowercase to match frontend
                    self.session.commit()
                
                return result
                
        except Exception as e:
            logger.error(f"Error testing connection {connection_id}: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "status": "ERROR"
            }
    
    def discover_databases(self, connection_id: str) -> Dict[str, Any]:
        """Discover available databases in a connection.
        
        Args:
            connection_id: Connection ID
            
        Returns:
            Dictionary with list of databases
        """
        try:
            connection = self.session.query(ConnectionModel).filter_by(
                id=connection_id
            ).first()
            
            if not connection:
                return {
                    "success": False,
                    "error": f"Connection not found: {connection_id}"
                }
            
            connector = self._get_connector(connection)
            connection_obj = connector.connect()
            
            databases = connector.list_databases()
            
            if hasattr(connector, 'disconnect') and connection_obj:
                connector.disconnect(connection_obj)
            
            return {
                "success": True,
                "databases": databases,
                "count": len(databases)
            }
            
        except Exception as e:
            logger.error(f"Error discovering databases: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }
    
    def discover_schemas(
        self,
        connection_id: str,
        database: Optional[str] = None
    ) -> Dict[str, Any]:
        """Discover schemas in a database.
        
        Args:
            connection_id: Connection ID
            database: Target database (optional, uses connection default)
            
        Returns:
            Dictionary with list of schemas
        """
        try:
            connection = self.session.query(ConnectionModel).filter_by(
                id=connection_id
            ).first()
            
            if not connection:
                return {
                    "success": False,
                    "error": f"Connection not found: {connection_id}"
                }
            
            target_db = database or connection.database
            
            connector = self._get_connector(connection)
            connection_obj = connector.connect()
            
            schemas = connector.list_schemas(database=target_db)
            
            if hasattr(connector, 'disconnect') and connection_obj:
                connector.disconnect(connection_obj)
            
            return {
                "success": True,
                "database": target_db,
                "schemas": schemas,
                "count": len(schemas)
            }
            
        except Exception as e:
            logger.error(f"Error discovering schemas: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }
    
    def discover_tables(
        self,
        connection_id: str,
        database: Optional[str] = None,
        schema: Optional[str] = None
    ) -> Dict[str, Any]:
        """Discover tables in a schema.
        
        Args:
            connection_id: Connection ID
            database: Target database (optional)
            schema: Target schema (optional)
            
        Returns:
            Dictionary with list of tables and their metadata
        """
        try:
            connection = self.session.query(ConnectionModel).filter_by(
                id=connection_id
            ).first()
            
            if not connection:
                return {
                    "success": False,
                    "error": f"Connection not found: {connection_id}"
                }
            
            target_db = database or connection.database
            # Default schema based on database type
            if not schema:
                if connection.database_type.value.lower() in ["sqlserver", "mssql"]:
                    target_schema = connection.schema or "dbo"
                else:
                    target_schema = connection.schema or "public"
            else:
                target_schema = schema
            
            connector = self._get_connector(connection)
            conn = connector.connect()
            
            try:
                tables = connector.list_tables(
                    database=target_db,
                    schema=target_schema
                )
                # Handle both list of strings and list of ConnectorTable objects
                if tables and len(tables) > 0:
                    # Check if first item is a ConnectorTable object (has 'name' attribute)
                    if hasattr(tables[0], 'name'):
                        # Convert ConnectorTable objects to table names
                        table_names = [table.name for table in tables]
                    elif isinstance(tables[0], dict) and 'name' in tables[0]:
                        # Handle list of dictionaries
                        table_names = [table['name'] for table in tables]
                    else:
                        # Assume it's already a list of strings
                        table_names = tables
                else:
                    table_names = []
            except AttributeError as e:
                # If list_tables doesn't exist, try alternative method
                if "list_tables" in str(e):
                    logger.warning(f"list_tables not available, trying alternative method: {e}")
                    # Try using extract_schema for PostgreSQL
                    if hasattr(connector, 'extract_schema'):
                        schema_info = connector.extract_schema(database=target_db, schema=target_schema)
                        table_names = [table["name"] for table in schema_info.get("tables", [])]
                    else:
                        raise
                else:
                    raise
            
            table_details = []
            for table_name in table_names:
                try:
                    # Use the existing connection for better performance and to ensure database context
                    if hasattr(connector, 'get_table_row_count'):
                        row_count = connector.get_table_row_count(
                            table=table_name,
                            database=target_db,
                            schema=target_schema
                        )
                    else:
                        # Fallback: query directly using existing connection
                        cursor = conn.cursor()
                        if connection.database_type.value.lower() in ["sqlserver", "mssql"]:
                            cursor.execute(f"USE [{target_db}]")
                            cursor.execute(f"SELECT COUNT(*) FROM [{target_schema}].[{table_name}]")
                        else:
                            from psycopg2 import sql
                            query = sql.SQL("SELECT COUNT(*) FROM {}.{}").format(
                                sql.Identifier(target_schema),
                                sql.Identifier(table_name)
                            )
                            cursor.execute(query)
                        row_count = cursor.fetchone()[0]
                        cursor.close()
                        row_count = int(row_count) if row_count else 0
                    
                    # Get column information
                    column_count = 0
                    columns = []
                    try:
                        if hasattr(connector, 'get_table_columns'):
                            columns = connector.get_table_columns(
                                table=table_name,
                                database=target_db,
                                schema=target_schema
                            )
                            column_count = len(columns) if columns else 0
                    except Exception as e:
                        logger.warning(f"Could not get columns for {table_name}: {e}")
                        # Continue without column info
                    
                    table_details.append({
                        "name": table_name,
                        "row_count": row_count,
                        "schema": target_schema,
                        "database": target_db,
                        "column_count": column_count,
                        "columns": columns if columns else []
                    })
                except Exception as e:
                    logger.error(f"Could not get row count for {table_name}: {e}", exc_info=True)
                    table_details.append({
                        "name": table_name,
                        "row_count": None,
                        "schema": target_schema,
                        "database": target_db,
                        "column_count": 0,
                        "columns": []
                    })
            
            if hasattr(connector, 'disconnect') and conn:
                connector.disconnect(conn)
            
            return {
                "success": True,
                "database": target_db,
                "schema": target_schema,
                "tables": table_details,
                "count": len(table_details)
            }
            
        except Exception as e:
            logger.error(f"Error discovering tables: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_table_schema(
        self,
        connection_id: str,
        table_name: str,
        database: Optional[str] = None,
        schema: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get detailed schema information for a table.
        
        Args:
            connection_id: Connection ID
            table_name: Table name
            database: Target database (optional)
            schema: Target schema (optional)
            
        Returns:
            Dictionary with table schema details
        """
        try:
            connection = self.session.query(ConnectionModel).filter_by(
                id=connection_id
            ).first()
            
            if not connection:
                return {
                    "success": False,
                    "error": f"Connection not found: {connection_id}"
                }
            
            target_db = database or connection.database
            target_schema = schema or connection.schema or "public"
            
            # For Oracle, if database parameter is provided and connection.database is empty/None,
            # create connector with database from parameter to avoid validation error
            if connection.database_type.value.lower() == "oracle":
                # Use database parameter if provided, otherwise use connection.database
                oracle_db = database if database else connection.database
                if not oracle_db or (isinstance(oracle_db, str) and oracle_db.strip() == ""):
                    # If both are empty, try to get from additional_config
                    if hasattr(connection, 'additional_config') and connection.additional_config:
                        oracle_db = connection.additional_config.get("service_name") or connection.additional_config.get("database")
                
                if not oracle_db:
                    return {
                        "success": False,
                        "error": "Either 'database' (SID) or 'service_name' must be provided for Oracle connection"
                    }
                
                # Create connector with proper database value
                from .connectors.oracle import OracleConnector
                config = {
                    "host": connection.host,
                    "port": connection.port,
                    "database": oracle_db,  # Use database/SID
                    "username": connection.username,
                    "password": connection.password,
                }
                if hasattr(connection, 'schema') and connection.schema:
                    config["schema"] = connection.schema
                if hasattr(connection, 'additional_config') and connection.additional_config:
                    config.update(connection.additional_config)
                connector = OracleConnector(config)
            else:
                connector = self._get_connector(connection)
            
            conn = connector.connect()
            
            columns = connector.get_table_columns(
                table=table_name,
                database=target_db,
                schema=target_schema
            )
            
            primary_keys = connector.get_primary_keys(
                table=table_name,
                database=target_db,
                schema=target_schema
            )
            
            if hasattr(connector, 'disconnect') and conn:
                connector.disconnect(conn)
            
            return {
                "success": True,
                "table": table_name,
                "database": target_db,
                "schema": target_schema,
                "columns": columns,
                "primary_keys": primary_keys,
                "column_count": len(columns)
            }
            
        except Exception as e:
            logger.error(f"Error getting table schema: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_test_history(
        self,
        connection_id: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get connection test history.
        
        Args:
            connection_id: Connection ID
            limit: Maximum number of records to return
            
        Returns:
            List of test history records
        """
        try:
            tests = self.session.query(ConnectionTestModel).filter_by(
                connection_id=connection_id
            ).order_by(
                ConnectionTestModel.tested_at.desc()
            ).limit(limit).all()
            
            return [
                {
                    "id": test.id,
                    "status": test.test_status,
                    "response_time_ms": test.response_time_ms,
                    "error_message": test.error_message,
                    "tested_at": test.tested_at.isoformat() if test.tested_at else None
                }
                for test in tests
            ]
            
        except Exception as e:
            logger.error(f"Error getting test history: {e}", exc_info=True)
            return []
    
    def validate_connection(self, connection_id: str) -> Tuple[bool, Optional[str]]:
        """Validate if a connection is usable.
        
        Args:
            connection_id: Connection ID
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        result = self.test_connection(connection_id, save_history=False)
        
        if result["success"]:
            return True, None
        else:
            return False, result.get("error", "Connection test failed")
    
    def test_connection_data(
        self,
        connection: Any,  # Can be Connection model or ConnectionModel
        save_history: bool = False
    ) -> Dict[str, Any]:
        """Test database connection from connection data (without saving to DB).
        
        Args:
            connection: Connection object (Connection or ConnectionModel)
            save_history: Whether to save test result to history (only if connection has ID)
            
        Returns:
            Test result dictionary with status and details
        """
        try:
            start_time = time.time()
            
            connector = self._get_connector_from_data(connection)
            
            try:
                connection_obj = connector.connect()
                
                # Get version if method exists, otherwise use test_connection result
                if hasattr(connector, 'get_version'):
                    version = connector.get_version()
                else:
                    # For connectors without get_version (like S3), use test_connection
                    test_result = connector.test_connection()
                    version = "Connection verified" if test_result else "Connection failed"
                
                # Disconnect if method exists and we have a connection object
                if hasattr(connector, 'disconnect') and connection_obj:
                    connector.disconnect(connection_obj)
                
                response_time_ms = int((time.time() - start_time) * 1000)
                
                result = {
                    "success": True,
                    "status": "SUCCESS",
                    "response_time_ms": response_time_ms,
                    "version": version,
                    "tested_at": datetime.utcnow().isoformat()
                }
                
                # Only save history if connection has an ID (exists in DB)
                if save_history and hasattr(connection, 'id') and connection.id:
                    self._save_test_history(
                        connection_id=connection.id,
                        status="SUCCESS",
                        response_time_ms=response_time_ms
                    )
                    
                    if isinstance(connection, ConnectionModel):
                        connection.last_tested_at = datetime.utcnow()
                        connection.last_test_status = "success"  # Use lowercase to match frontend
                        self.session.commit()
                
                return result
                
            except Exception as e:
                response_time_ms = int((time.time() - start_time) * 1000)
                error_msg = str(e)
                
                logger.error(f"Connection test failed: {error_msg}")
                
                result = {
                    "success": False,
                    "status": "FAILED",
                    "error": error_msg,
                    "response_time_ms": response_time_ms,
                    "tested_at": datetime.utcnow().isoformat()
                }
                
                # Only save history if connection has an ID
                if save_history and hasattr(connection, 'id') and connection.id:
                    self._save_test_history(
                        connection_id=connection.id,
                        status="FAILED",
                        response_time_ms=response_time_ms,
                        error_message=error_msg
                    )
                    
                    if isinstance(connection, ConnectionModel):
                        connection.last_tested_at = datetime.utcnow()
                        connection.last_test_status = "failed"  # Use lowercase to match frontend
                        self.session.commit()
                
                return result
                
        except Exception as e:
            logger.error(f"Error testing connection: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "status": "ERROR"
            }
    
    def _get_connector_from_data(self, connection: Any):
        """Get connector instance from connection data (Connection or ConnectionModel)."""
        from ingestion.models import Connection as ConnectionModel
        
        # Handle both Connection model and ConnectionModel
        if hasattr(connection, 'database_type'):
            db_type = connection.database_type
            if hasattr(db_type, 'value'):
                db_type = db_type.value
            db_type = str(db_type).lower()
        else:
            raise ValueError("Connection must have database_type")
        
        if db_type == "postgresql":
            # PostgreSQL connector expects config dict with 'host', 'user', etc.
            config = {
                "host": connection.host,
                "port": connection.port,
                "database": connection.database,
                "username": connection.username,  # Will be normalized to 'user' by connector
                "password": connection.password,
            }
            if hasattr(connection, 'schema') and connection.schema:
                config["schema"] = connection.schema
            if hasattr(connection, 'additional_config') and connection.additional_config:
                config.update(connection.additional_config)
            return PostgreSQLConnector(config)
        elif db_type in ["sqlserver", "mssql"]:
            # SQL Server connector expects 'server' instead of 'host', and 'user' instead of 'username'
            config = {
                "server": connection.host,  # Map 'host' to 'server'
                "port": connection.port,
                "database": connection.database,
                "username": connection.username,  # Will be normalized to 'user' by connector
                "password": connection.password,
                "trust_server_certificate": True,  # Default to True to avoid SSL certificate issues
            }
            if hasattr(connection, 'schema') and connection.schema:
                config["schema"] = connection.schema
            if hasattr(connection, 'additional_config') and connection.additional_config:
                # Allow additional_config to override defaults (e.g., if user explicitly sets trust_server_certificate=False)
                config.update(connection.additional_config)
            return SQLServerConnector(config)
        elif db_type == "s3":
            # S3 connector expects bucket, aws_access_key_id, aws_secret_access_key
            config = {
                "bucket": connection.database,  # Use database field for bucket name
                "aws_access_key_id": connection.username,  # Use username for AWS access key
                "aws_secret_access_key": connection.password,  # Use password for AWS secret key
            }
            if hasattr(connection, 'schema') and connection.schema:
                config["prefix"] = connection.schema  # Use schema field for S3 prefix
            if hasattr(connection, 'additional_config') and connection.additional_config:
                # Allow additional_config for region_name, endpoint_url, etc.
                config.update(connection.additional_config)
            return S3Connector(config)
        elif db_type == "oracle":
            # Oracle connector expects host, port, database (SID) or service_name, user, password
            from .connectors.oracle import OracleConnector
            config = {
                "host": connection.host,
                "port": connection.port,
                "database": connection.database,  # SID
                "username": connection.username,  # Will be normalized to 'user' by connector
                "password": connection.password,
            }
            if hasattr(connection, 'schema') and connection.schema:
                config["schema"] = connection.schema
            if hasattr(connection, 'additional_config') and connection.additional_config:
                # Allow additional_config for service_name, mode, etc.
                config.update(connection.additional_config)
            return OracleConnector(config)
        else:
            raise ValueError(f"Unsupported database type: {db_type}")
    
    def _get_connector(self, connection: ConnectionModel):
        """Get appropriate connector for connection type.
        
        Args:
            connection: Connection model
            
        Returns:
            Database connector instance
        """
        # Get database type value (handle enum)
        db_type = connection.database_type
        if hasattr(db_type, 'value'):
            db_type = db_type.value
        db_type = str(db_type).lower()
        
        if db_type == "postgresql":
            config = {
                "host": connection.host,
                "port": connection.port,
                "database": connection.database,
                "username": connection.username,
                "password": connection.password
            }
            if connection.schema:
                config["schema"] = connection.schema
            if connection.additional_config:
                config.update(connection.additional_config)
            return PostgreSQLConnector(config)
        elif db_type in ["sqlserver", "mssql"]:
            # SQL Server connector expects 'server' instead of 'host'
            config = {
                "server": connection.host,  # Map 'host' to 'server'
                "port": connection.port,
                "database": connection.database,
                "username": connection.username,  # Will be normalized to 'user' by connector
                "password": connection.password,
                "trust_server_certificate": True,  # Default to True to avoid SSL certificate issues
            }
            if connection.schema:
                config["schema"] = connection.schema
            if connection.additional_config:
                # Allow additional_config to override defaults (e.g., if user explicitly sets trust_server_certificate=False)
                # Also allow specifying 'driver' explicitly if auto-detection fails
                config.update(connection.additional_config)
            return SQLServerConnector(config)
        elif db_type == "s3":
            # S3 connector expects bucket, aws_access_key_id, aws_secret_access_key
            config = {
                "bucket": connection.database,  # Use database field for bucket name
                "aws_access_key_id": connection.username,  # Use username for AWS access key
                "aws_secret_access_key": connection.password,  # Use password for AWS secret key
            }
            if hasattr(connection, 'schema') and connection.schema:
                config["prefix"] = connection.schema  # Use schema field for S3 prefix
            if hasattr(connection, 'additional_config') and connection.additional_config:
                # Allow additional_config for region_name, endpoint_url, etc.
                config.update(connection.additional_config)
            return S3Connector(config)
        elif db_type in ["as400", "ibm_i"]:
            # AS400 connector expects 'server' instead of 'host'
            # Use library from additional_config or schema or database
            library = (
                connection.additional_config.get("library") if connection.additional_config 
                else connection.schema or connection.database or ""
            )
            
            config = {
                "server": connection.host,  # Map 'host' to 'server'
                "port": connection.port or 446,  # Default AS400 port
                "database": library,  # Library name (can be empty, will use additional_config)
                "username": connection.username,
                "password": connection.password,
                "additional_config": {
                    "journal_library": connection.additional_config.get("journal_library", "") if connection.additional_config else "",
                    "library": library,
                    "tablename": connection.additional_config.get("tablename", "") if connection.additional_config else "",
                }
            }
            if connection.schema:
                config["schema"] = connection.schema
            if connection.additional_config:
                # Merge additional_config (driver, etc.)
                config["additional_config"].update({
                    k: v for k, v in connection.additional_config.items() 
                    if k not in ["journal_library", "library", "tablename"]
                })
            from ingestion.connectors.as400 import AS400Connector
            return AS400Connector(config)
        elif db_type == "snowflake":
            # Snowflake connector expects account, user, password, database, schema, warehouse, role
            # Account can be provided in 'host' field or 'additional_config.account'
            account = connection.host or (connection.additional_config.get("account") if connection.additional_config else None)
            if not account:
                raise ValueError("Snowflake account is required. Provide it in 'host' field or 'additional_config.account'")
            
            config = {
                "account": account,
                "user": connection.username,
                "password": connection.password,
                "database": connection.database,
                "schema": connection.schema or "PUBLIC",
            }
            
            # Add optional parameters from additional_config
            if connection.additional_config:
                if "warehouse" in connection.additional_config:
                    config["warehouse"] = connection.additional_config["warehouse"]
                if "role" in connection.additional_config:
                    config["role"] = connection.additional_config["role"]
                if "private_key" in connection.additional_config:
                    config["private_key"] = connection.additional_config["private_key"]
                if "private_key_passphrase" in connection.additional_config:
                    config["private_key_passphrase"] = connection.additional_config["private_key_passphrase"]
            
            from ingestion.connectors.snowflake import SnowflakeConnector
            return SnowflakeConnector(config)
        elif db_type == "oracle":
            # Oracle connector expects host, port, database (SID) or service_name, user, password
            config = {
                "host": connection.host,
                "port": connection.port,
                "user": connection.username,
                "password": connection.password,
            }
            # Oracle connector accepts 'database' for SID or 'service_name' for service name
            # Check additional_config first for explicit service_name or sid
            if connection.additional_config:
                if 'service_name' in connection.additional_config:
                    config["service_name"] = connection.additional_config['service_name']
                elif 'sid' in connection.additional_config:
                    config["database"] = connection.additional_config['sid']
                # Add other additional_config items
                for key, value in connection.additional_config.items():
                    if key not in ['service_name', 'sid']:
                        config[key] = value
            
            # If not set from additional_config, use connection.database
            if 'service_name' not in config and 'database' not in config:
                if connection.database:
                    # Check if it looks like a service name (contains /) or is a SID
                    if '/' in connection.database:
                        config["service_name"] = connection.database
                    else:
                        config["database"] = connection.database  # Use 'database' for SID
            
            if connection.schema:
                config["schema"] = connection.schema
            return OracleConnector(config)
        else:
            raise ValueError(f"Unsupported database type: {db_type}")
    
    def _save_test_history(
        self,
        connection_id: str,
        status: str,
        response_time_ms: int,
        error_message: Optional[str] = None
    ):
        """Save connection test result to history.
        
        Args:
            connection_id: Connection ID
            status: Test status
            response_time_ms: Response time in milliseconds
            error_message: Error message if failed
        """
        try:
            test = ConnectionTestModel(
                id=str(uuid.uuid4()),
                connection_id=connection_id,
                test_status=status,
                response_time_ms=response_time_ms,
                error_message=error_message,
                tested_at=datetime.utcnow()
            )
            
            self.session.add(test)
            self.session.commit()
            
        except Exception as e:
            logger.error(f"Error saving test history: {e}", exc_info=True)
            self.session.rollback()
    
    def close(self):
        """Close database session."""
        self.session.close()
