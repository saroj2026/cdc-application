"""Connections router."""
from fastapi import APIRouter, HTTPException, Depends, Query, Request
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid

from ingestion.database import get_db
from ingestion.database.models_db import ConnectionModel
from sqlalchemy.orm import Session
from ingestion.audit import log_audit_event, mask_sensitive_data
from ingestion.routers.auth import get_current_user
from ingestion.database.models_db import UserModel

router = APIRouter()


class ConnectionCreate(BaseModel):
    name: str
    connection_type: str  # source or target
    database_type: str
    host: str
    port: int
    database: str
    username: str
    password: str
    db_schema: Optional[str] = None
    additional_config: Optional[Dict[str, Any]] = None


class ConnectionUpdate(BaseModel):
    name: Optional[str] = None
    host: Optional[str] = None
    port: Optional[int] = None
    database: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    db_schema: Optional[str] = None
    additional_config: Optional[Dict[str, Any]] = None


def connection_id_to_int(conn_id) -> int:
    """Convert UUID string to numeric ID for frontend."""
    if isinstance(conn_id, int):
        return conn_id
    try:
        id_str = str(conn_id).replace("-", "")
        return int(id_str[:8], 16) if len(id_str) > 8 else abs(hash(str(conn_id))) % (10**9)
    except (ValueError, AttributeError):
        return abs(hash(str(conn_id))) % (10**9)


def connection_to_dict(conn: ConnectionModel) -> dict:
    """Convert connection model to dict matching frontend expectations."""
    # Get ssl_enabled from additional_config
    ssl_enabled = False
    if conn.additional_config and isinstance(conn.additional_config, dict):
        ssl_enabled = conn.additional_config.get("ssl_enabled", False)
    
    return {
        "id": connection_id_to_int(conn.id),
        "name": conn.name,
        "description": conn.additional_config.get("description", "") if conn.additional_config else "",
        "connection_type": conn.database_type,  # Use database_type for logo mapping (postgresql, mysql, etc.) - backward compatibility
        "database_type": conn.database_type,  # Explicit database_type field (postgresql, mysql, etc.)
        "role": conn.connection_type,  # Frontend expects role to be 'source' or 'target'
        "host": conn.host,
        "port": conn.port,
        "database": conn.database,
        "username": conn.username,
        "ssl_enabled": ssl_enabled,
        "is_active": conn.is_active,
        "last_tested_at": conn.last_tested_at.isoformat() + "Z" if conn.last_tested_at else None,
        "last_test_status": conn.last_test_status,
        "created_at": conn.created_at.isoformat() + "Z" if conn.created_at else None,
        "updated_at": conn.updated_at.isoformat() + "Z" if conn.updated_at else None,
    }


@router.get("")
async def list_connections(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """List all connections - returns array directly."""
    try:
        connections = db.query(ConnectionModel).filter(
            ConnectionModel.deleted_at.is_(None)
        ).offset(skip).limit(limit).all()
        
        # Return array directly (not wrapped in object)
        return [connection_to_dict(conn) for conn in connections]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch connections: {str(e)}")


@router.post("")
async def create_connection(
    connection: ConnectionCreate, 
    request: Request,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new connection."""
    try:
        # Check if connection with same name exists
        existing = db.query(ConnectionModel).filter(
            ConnectionModel.name == connection.name,
            ConnectionModel.deleted_at.is_(None)
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail="Connection with this name already exists")
        
        # Prepare additional_config
        additional_config = connection.additional_config or {}
        if connection.db_schema:
            additional_config["schema"] = connection.db_schema
        
        # Create new connection
        new_conn = ConnectionModel(
            id=str(uuid.uuid4()),
            name=connection.name,
            connection_type=connection.connection_type,
            database_type=connection.database_type,
            host=connection.host,
            port=connection.port,
            database=connection.database,
            username=connection.username,
            password=connection.password,
            schema=connection.db_schema,
            additional_config=additional_config,
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        db.add(new_conn)
        db.commit()
        db.refresh(new_conn)
        
        conn_dict = connection_to_dict(new_conn)
        
        # Log audit event
        log_audit_event(
            db=db,
            user=current_user,
            action="create_connection",
            resource_type="connection",
            resource_id=str(new_conn.id),
            new_value=mask_sensitive_data(conn_dict),
            request=request
        )
        
        return conn_dict
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create connection: {str(e)}")


@router.get("/{connection_id}")
async def get_connection(connection_id: str, db: Session = Depends(get_db)):
    """Get connection by ID."""
    try:
        # Try to find by UUID string first
        conn = db.query(ConnectionModel).filter(
            ConnectionModel.id == connection_id,
            ConnectionModel.deleted_at.is_(None)
        ).first()
        
        # If not found, try to find by numeric ID (convert back)
        if not conn:
            all_conns = db.query(ConnectionModel).filter(
                ConnectionModel.deleted_at.is_(None)
            ).all()
            for c in all_conns:
                if connection_id_to_int(c.id) == int(connection_id):
                    conn = c
                    break
        
        if not conn:
            raise HTTPException(status_code=404, detail="Connection not found")
        
        return connection_to_dict(conn)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get connection: {str(e)}")


@router.put("/{connection_id}")
async def update_connection(
    connection_id: str,
    connection: ConnectionUpdate,
    request: Request,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update connection."""
    try:
        # Find connection
        conn = db.query(ConnectionModel).filter(
            ConnectionModel.id == connection_id,
            ConnectionModel.deleted_at.is_(None)
        ).first()
        
        if not conn:
            raise HTTPException(status_code=404, detail="Connection not found")
        
        # Store old value for audit
        old_value = mask_sensitive_data(connection_to_dict(conn))
        
        # Update fields
        if connection.name is not None:
            conn.name = connection.name
        if connection.host is not None:
            conn.host = connection.host
        if connection.port is not None:
            conn.port = connection.port
        if connection.database is not None:
            conn.database = connection.database
        if connection.username is not None:
            conn.username = connection.username
        if connection.password is not None:
            conn.password = connection.password
        if connection.db_schema is not None:
            conn.schema = connection.db_schema
        if connection.additional_config is not None:
            conn.additional_config = connection.additional_config
        
        conn.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(conn)
        
        new_value = mask_sensitive_data(connection_to_dict(conn))
        
        # Log audit event
        log_audit_event(
            db=db,
            user=current_user,
            action="update_connection",
            resource_type="connection",
            resource_id=str(conn.id),
            old_value=old_value,
            new_value=new_value,
            request=request
        )
        
        return new_value
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to update connection: {str(e)}")


@router.delete("/{connection_id}")
async def delete_connection(
    connection_id: str,
    request: Request,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete connection (soft delete)."""
    try:
        conn = db.query(ConnectionModel).filter(
            ConnectionModel.id == connection_id,
            ConnectionModel.deleted_at.is_(None)
        ).first()
        
        if not conn:
            raise HTTPException(status_code=404, detail="Connection not found")
        
        # Store old value for audit
        old_value = mask_sensitive_data(connection_to_dict(conn))
        
        # Soft delete
        conn.deleted_at = datetime.utcnow()
        conn.is_active = False
        conn.updated_at = datetime.utcnow()
        
        db.commit()
        
        # Log audit event
        log_audit_event(
            db=db,
            user=current_user,
            action="delete_connection",
            resource_type="connection",
            resource_id=str(conn.id),
            old_value=old_value,
            request=request
        )
        
        return {"message": "Connection deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to delete connection: {str(e)}")


@router.post("/{connection_id}/test")
async def test_connection(
    connection_id: str,
    request: Request,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Test connection."""
    try:
        conn = db.query(ConnectionModel).filter(
            ConnectionModel.id == connection_id,
            ConnectionModel.deleted_at.is_(None)
        ).first()
        
        if not conn:
            raise HTTPException(status_code=404, detail="Connection not found")
        
        # TODO: Implement actual connection testing
        # For now, return success
        import time
        start_time = time.time()
        
        # Placeholder: actual test would connect to database here
        # test_result = test_database_connection(conn)
        
        response_time_ms = int((time.time() - start_time) * 1000)
        
        # Update last test info
        conn.last_tested_at = datetime.utcnow()
        conn.last_test_status = "success"
        conn.updated_at = datetime.utcnow()
        db.commit()
        
        # Log audit event
        log_audit_event(
            db=db,
            user=current_user,
            action="test_connection",
            resource_type="connection",
            resource_id=str(conn.id),
            request=request
        )
        
        return {
            "status": "success",
            "message": "Connection test successful",
            "response_time_ms": response_time_ms
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to test connection: {str(e)}")


@router.get("/{connection_id}/databases")
async def list_databases(connection_id: str, db: Session = Depends(get_db)):
    """List databases for a connection."""
    # TODO: Implement database listing
    return []


@router.post("/activate-all")
async def activate_all_connections(db: Session = Depends(get_db)):
    """Activate all connections."""
    try:
        from sqlalchemy import text
        # Activate all non-deleted connections
        result = db.execute(
            text("""
                UPDATE connections 
                SET is_active = true, updated_at = :updated_at
                WHERE deleted_at IS NULL
            """),
            {"updated_at": datetime.utcnow()}
        )
        db.commit()
        return {
            "message": f"Activated {result.rowcount} connections",
            "count": result.rowcount
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to activate connections: {str(e)}")


@router.get("/{connection_id}/schemas")
async def list_schemas(connection_id: str, database: Optional[str] = None, db: Session = Depends(get_db)):
    """List schemas for a connection."""
    # TODO: Implement schema listing
    return []


def get_database_connection_string(conn: ConnectionModel, database: Optional[str] = None) -> str:
    """Build database connection string based on database type."""
    import logging
    logger = logging.getLogger(__name__)
    
    db_type = conn.database_type.lower()
    db_name = database or conn.database
    host = conn.host
    port = conn.port
    username = conn.username
    password = conn.password
    
    # Validate that password exists and is not empty
    if password is None:
        logger.error(f"Connection '{conn.name}' (ID: {conn.id}): Password is None")
        raise ValueError(f"Connection '{conn.name}' has no password configured. Please update the connection settings.")
    
    if isinstance(password, str) and password.strip() == "":
        logger.error(f"Connection '{conn.name}' (ID: {conn.id}): Password is empty string")
        raise ValueError(f"Connection '{conn.name}' has an empty password. Please update the connection settings with a valid password.")
    
    # Log connection details (without password) for debugging
    logger.debug(f"Building connection string for '{conn.name}' (type: {db_type}, host: {host}, user: {username}, password_length: {len(str(password)) if password else 0})")
    
    # Get SSL and other config from additional_config
    ssl_enabled = False
    trust_server_certificate = False
    if conn.additional_config and isinstance(conn.additional_config, dict):
        ssl_enabled = conn.additional_config.get("ssl_enabled", False)
        trust_server_certificate = conn.additional_config.get("trust_server_certificate", False)
    
    if db_type == "postgresql" or db_type == "postgres":
        # URL encode username and password to handle special characters
        from urllib.parse import quote_plus
        encoded_username = quote_plus(username)
        encoded_password = quote_plus(password) if password else ""
        conn_str = f"postgresql://{encoded_username}:{encoded_password}@{host}:{port}/{db_name}"
        params = []
        if ssl_enabled:
            params.append("sslmode=require")
        # Always add connect_timeout for PostgreSQL
        params.append("connect_timeout=10")
        if params:
            conn_str += "?" + "&".join(params)
        return conn_str
    elif db_type == "mysql":
        # URL encode username and password to handle special characters
        from urllib.parse import quote_plus
        encoded_username = quote_plus(username)
        encoded_password = quote_plus(password) if password else ""
        conn_str = f"mysql+pymysql://{encoded_username}:{encoded_password}@{host}:{port}/{db_name}"
        params = []
        if ssl_enabled:
            params.append("ssl_disabled=false")
        # Always add connect_timeout for MySQL
        params.append("connect_timeout=10")
        if params:
            conn_str += "?" + "&".join(params)
        return conn_str
    elif db_type == "sqlserver" or db_type == "mssql":
        # SQL Server connection string - properly escape special characters in ODBC connection string
        from urllib.parse import quote_plus
        
        # Escape special characters in ODBC connection string values
        # ODBC connection strings use {} for driver names and semicolons as separators
        # Special characters in values need to be escaped with {{}} for {} and doubled for semicolons
        def escape_odbc_value(value):
            """Escape special characters in ODBC connection string values."""
            if value is None or value == "":
                return ""
            # Convert to string and escape special ODBC characters
            value = str(value)
            # Replace } with }} and { with {{ to escape them
            value = value.replace("}", "}}").replace("{", "{{")
            # Escape semicolons by doubling them (semicolons are separators in ODBC strings)
            value = value.replace(";", ";;")
            return value
        
        # Build connection string with proper formatting
        # Use pyodbc connection string format
        driver = "ODBC Driver 17 for SQL Server"
        
        # Additional validation for SQL Server (password should already be validated above, but double-check)
        if not password or (isinstance(password, str) and password.strip() == ""):
            logger.error(f"SQL Server connection '{conn.name}': Password validation failed (None or empty)")
            raise ValueError(f"SQL Server connection '{conn.name}' requires a non-empty password. Please check your connection configuration.")
        
        # Ensure password is a string before escaping
        password_str = str(password) if password is not None else ""
        if not password_str.strip():
            logger.error(f"SQL Server connection '{conn.name}': Password is empty after string conversion")
            raise ValueError(f"SQL Server connection '{conn.name}' has an invalid password. Please update the connection settings.")
        
        # Escape values for ODBC connection string
        escaped_host = escape_odbc_value(host)
        escaped_db = escape_odbc_value(db_name)
        escaped_username = escape_odbc_value(username)
        escaped_password = escape_odbc_value(password_str)
        
        # Log that password was escaped (without showing actual password)
        logger.debug(f"SQL Server connection '{conn.name}': Password escaped (length: {len(escaped_password)})")
        
        params = [
            f"DRIVER={{{driver}}}",
            f"SERVER={escaped_host},{port}",
            f"DATABASE={escaped_db}",
            f"UID={escaped_username}",
            f"PWD={escaped_password}"
        ]
        
        if trust_server_certificate:
            params.append("TrustServerCertificate=yes")
        if ssl_enabled:
            params.append("Encrypt=yes")
        
        # Build connection string using pyodbc format
        # The entire ODBC connection string needs to be URL-encoded when passed to odbc_connect
        conn_str_parts = ";".join(params)
        return f"mssql+pyodbc:///?odbc_connect={quote_plus(conn_str_parts)}"
    elif db_type == "oracle":
        # Oracle connection string
        return f"oracle+cx_oracle://{username}:{password}@{host}:{port}/{db_name}"
    elif db_type == "s3" or db_type == "aws_s3":
        # S3 is not a traditional database - return a placeholder connection string
        # S3 connections don't use SQLAlchemy engines
        return "s3://placeholder"
    else:
        raise ValueError(f"Unsupported database type: {db_type}")


# System tables to exclude from discovery
SYSTEM_TABLES = {
    'alembic_version',
    'alert_history',
    'alert_rules',
    'audit_logs',
    'connection_tests',
    'pipeline_runs',
    'pipeline_metrics',
    'connections',
    'pipelines',
    'users',
    # Common PostgreSQL system tables
    'pg_stat_statements',
    'pg_stat_activity',
    'pg_stat_database',
    # Common MySQL system tables
    'information_schema',
    'performance_schema',
    'mysql',
    'sys',
    # Common SQL Server system tables
    'sysdiagrams',
    'dtproperties',
}

def is_system_table(table_name: str) -> bool:
    """Check if a table is a system table."""
    table_lower = table_name.lower()
    # Check exact match
    if table_lower in SYSTEM_TABLES:
        return True
    # Check if starts with system prefixes
    system_prefixes = ['pg_', 'information_schema.', 'sys.', 'mysql.', 'performance_schema.']
    return any(table_lower.startswith(prefix) for prefix in system_prefixes)

def discover_tables_from_db(conn: ConnectionModel, database: Optional[str] = None, schema: Optional[str] = None) -> List[Dict[str, Any]]:
    """Discover tables from a database connection."""
    from sqlalchemy import create_engine, inspect, text
    from sqlalchemy.exc import SQLAlchemyError
    
    db_type = conn.database_type.lower()
    db_name = database or conn.database
    schema_name = schema or conn.schema  # ConnectionModel uses 'schema' field
    
    # Handle S3 connections - S3 doesn't have traditional tables
    if db_type == "s3" or db_type == "aws_s3":
        # For S3, return a list of "tables" which are actually object prefixes/folders
        # S3 stores objects (files), not tables
        return [
            {
                "name": "objects",
                "full_name": f"s3://{db_name}/objects",
                "schema": "",
                "columns": [
                    {"name": "key", "type": "string"},
                    {"name": "size", "type": "bigint"},
                    {"name": "last_modified", "type": "timestamp"}
                ]
            }
        ]
    
    try:
        # Build connection string (already includes connect_timeout for PostgreSQL/MySQL)
        conn_str = get_database_connection_string(conn, database)
        
        # Create engine - no timeout in connect_args for PostgreSQL/MySQL (already in connection string)
        connect_args = {}
        if "sqlite" in conn_str:
            connect_args["timeout"] = 10
        
        engine = create_engine(
            conn_str,
            pool_pre_ping=True,
            connect_args=connect_args
        )
        
        tables = []
        
        with engine.connect() as connection:
            inspector = inspect(engine)
            
            if db_type in ["postgresql", "postgres", "mysql"]:
                # PostgreSQL and MySQL: use inspector
                if schema_name:
                    table_names = inspector.get_table_names(schema=schema_name)
                else:
                    # Get default schema
                    if db_type in ["postgresql", "postgres"]:
                        default_schema = schema_name or "public"
                    else:
                        default_schema = schema_name or db_name
                    table_names = inspector.get_table_names(schema=default_schema)
                
                for table_name in table_names:
                    # Skip system tables
                    if is_system_table(table_name):
                        continue
                    
                    # Get columns for each table
                    try:
                        if schema_name:
                            columns = inspector.get_columns(table_name, schema=schema_name)
                        else:
                            default_schema = schema_name or ("public" if db_type in ["postgresql", "postgres"] else db_name)
                            columns = inspector.get_columns(table_name, schema=default_schema)
                        
                        column_info = []
                        for col in columns:
                            column_info.append({
                                "name": col["name"],
                                "type": str(col["type"]),
                                "nullable": col.get("nullable", True),
                                "default": str(col.get("default", "")) if col.get("default") else None
                            })
                        
                        full_name = f"{schema_name or 'public'}.{table_name}" if schema_name or db_type in ["postgresql", "postgres"] else table_name
                        
                        tables.append({
                            "name": table_name,
                            "full_name": full_name,
                            "schema": schema_name or ("public" if db_type in ["postgresql", "postgres"] else db_name),
                            "columns": column_info
                        })
                    except Exception as e:
                        # If column fetch fails, still include table name (if not system table)
                        full_name = f"{schema_name or 'public'}.{table_name}" if schema_name or db_type in ["postgresql", "postgres"] else table_name
                        tables.append({
                            "name": table_name,
                            "full_name": full_name,
                            "schema": schema_name or ("public" if db_type in ["postgresql", "postgres"] else db_name),
                            "columns": []
                        })
            
            elif db_type in ["sqlserver", "mssql"]:
                # SQL Server: use INFORMATION_SCHEMA
                if schema_name:
                    query = text("""
                        SELECT TABLE_SCHEMA, TABLE_NAME
                        FROM INFORMATION_SCHEMA.TABLES
                        WHERE TABLE_TYPE = 'BASE TABLE'
                        AND TABLE_SCHEMA = :schema
                        ORDER BY TABLE_SCHEMA, TABLE_NAME
                    """)
                    result = connection.execute(query, {"schema": schema_name})
                else:
                    query = text("""
                        SELECT TABLE_SCHEMA, TABLE_NAME
                        FROM INFORMATION_SCHEMA.TABLES
                        WHERE TABLE_TYPE = 'BASE TABLE'
                        ORDER BY TABLE_SCHEMA, TABLE_NAME
                    """)
                    result = connection.execute(query)
                
                for row in result:
                    table_schema = row[0]
                    table_name = row[1]
                    
                    # Skip system tables
                    if is_system_table(table_name) or is_system_table(f"{table_schema}.{table_name}"):
                        continue
                    
                    full_name = f"{table_schema}.{table_name}"
                    
                    # Get columns
                    col_query = text("""
                        SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE, COLUMN_DEFAULT
                        FROM INFORMATION_SCHEMA.COLUMNS
                        WHERE TABLE_SCHEMA = :schema AND TABLE_NAME = :table
                        ORDER BY ORDINAL_POSITION
                    """)
                    col_result = connection.execute(col_query, {"schema": table_schema, "table": table_name})
                    
                    column_info = []
                    for col_row in col_result:
                        column_info.append({
                            "name": col_row[0],
                            "type": col_row[1],
                            "nullable": col_row[2] == "YES",
                            "default": col_row[3] if col_row[3] else None
                        })
                    
                    tables.append({
                        "name": table_name,
                        "full_name": full_name,
                        "schema": table_schema,
                        "columns": column_info
                    })
            
            elif db_type == "oracle":
                # Oracle: use ALL_TABLES
                if schema_name:
                    query = text("""
                        SELECT OWNER, TABLE_NAME
                        FROM ALL_TABLES
                        WHERE (OWNER = USER OR OWNER IN (SELECT GRANTEE FROM USER_TAB_PRIVS WHERE PRIVILEGE = 'SELECT'))
                        AND OWNER = :schema
                        ORDER BY OWNER, TABLE_NAME
                    """)
                    result = connection.execute(query, {"schema": schema_name.upper()})
                else:
                    query = text("""
                        SELECT OWNER, TABLE_NAME
                        FROM ALL_TABLES
                        WHERE OWNER = USER OR OWNER IN (SELECT GRANTEE FROM USER_TAB_PRIVS WHERE PRIVILEGE = 'SELECT')
                        ORDER BY OWNER, TABLE_NAME
                    """)
                    result = connection.execute(query)
                for row in result:
                    table_schema = row[0]
                    table_name = row[1]
                    
                    # Skip system tables
                    if is_system_table(table_name) or is_system_table(f"{table_schema}.{table_name}"):
                        continue
                    
                    full_name = f"{table_schema}.{table_name}"
                    
                    # Get columns
                    col_query = text(f"""
                        SELECT COLUMN_NAME, DATA_TYPE, NULLABLE, DATA_DEFAULT
                        FROM ALL_TAB_COLUMNS
                        WHERE OWNER = :owner AND TABLE_NAME = :table
                        ORDER BY COLUMN_ID
                    """)
                    col_result = connection.execute(col_query, {"owner": table_schema, "table": table_name})
                    
                    column_info = []
                    for col_row in col_result:
                        column_info.append({
                            "name": col_row[0],
                            "type": col_row[1],
                            "nullable": col_row[2] == "Y",
                            "default": col_row[3] if col_row[3] else None
                        })
                    
                    tables.append({
                        "name": table_name,
                        "full_name": full_name,
                        "schema": table_schema,
                        "columns": column_info
                    })
            
            else:
                # Fallback: try inspector
                if schema_name:
                    table_names = inspector.get_table_names(schema=schema_name)
                else:
                    table_names = inspector.get_table_names()
                
                for table_name in table_names:
                    # Skip system tables
                    if is_system_table(table_name):
                        continue
                    
                    try:
                        if schema_name:
                            columns = inspector.get_columns(table_name, schema=schema_name)
                        else:
                            columns = inspector.get_columns(table_name)
                        
                        column_info = []
                        for col in columns:
                            column_info.append({
                                "name": col["name"],
                                "type": str(col["type"]),
                                "nullable": col.get("nullable", True),
                                "default": str(col.get("default", "")) if col.get("default") else None
                            })
                        
                        tables.append({
                            "name": table_name,
                            "full_name": table_name,
                            "schema": schema_name or "",
                            "columns": column_info
                        })
                    except Exception:
                        tables.append({
                            "name": table_name,
                            "full_name": table_name,
                            "schema": schema_name or "",
                            "columns": []
                        })
        
        return tables
    
    except SQLAlchemyError as e:
        error_str = str(e)
        # Provide more helpful error messages for common issues
        if "password authentication failed" in error_str.lower() or "authentication failed" in error_str.lower():
            raise HTTPException(
                status_code=500,
                detail=f"Database authentication failed. Please check the username and password for connection '{conn.name}' (host: {conn.host}). Error: {error_str}"
            )
        elif "invalid value specified for connection string attribute 'PWD'" in error_str.lower():
            raise HTTPException(
                status_code=500,
                detail=f"SQL Server connection error: Invalid password format. Please check the password for connection '{conn.name}'. The password may be empty or contain invalid characters. Error: {error_str}"
            )
        elif "connection" in error_str.lower() and ("refused" in error_str.lower() or "timeout" in error_str.lower()):
            raise HTTPException(
                status_code=500,
                detail=f"Database connection failed. Please check if the database server at {conn.host}:{conn.port} is running and accessible. Error: {error_str}"
            )
        else:
            raise HTTPException(status_code=500, detail=f"Database connection error: {error_str}")
    except ValueError as e:
        # Handle validation errors (e.g., empty password for SQL Server)
        raise HTTPException(status_code=400, detail=f"Connection configuration error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to discover tables: {str(e)}")


@router.get("/{connection_id}/tables")
async def list_tables(
    connection_id: str,
    database: Optional[str] = Query(None),
    schema: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """List tables for a connection."""
    try:
        # Find connection by ID (support both UUID and numeric ID)
        conn = None
        import logging
        
        # First try direct string match (most common case - UUID string)
        conn = db.query(ConnectionModel).filter(
            ConnectionModel.id == str(connection_id),
            ConnectionModel.deleted_at.is_(None)
        ).first()
        
        if not conn:
            # Try as UUID object (parse and convert to string)
            try:
                conn_uuid = uuid.UUID(str(connection_id))
                conn_uuid_str = str(conn_uuid)
                conn = db.query(ConnectionModel).filter(
                    ConnectionModel.id == conn_uuid_str,
                    ConnectionModel.deleted_at.is_(None)
                ).first()
            except (ValueError, TypeError):
                pass
        
        if not conn:
            # Try numeric ID lookup
            try:
                numeric_id = int(connection_id)
                all_conns = db.query(ConnectionModel).filter(ConnectionModel.deleted_at.is_(None)).all()
                for c in all_conns:
                    try:
                        # Use the same conversion function as pipelines.py
                        conn_numeric_id = connection_id_to_int(str(c.id))
                        if conn_numeric_id == numeric_id:
                            conn = c
                            logging.info(f"Found connection by numeric ID: {numeric_id} -> {c.id}")
                            break
                    except (ValueError, AttributeError, TypeError) as e:
                        logging.debug(f"Error converting connection ID {c.id}: {e}")
                        continue
            except (ValueError, TypeError):
                pass
        
        if not conn:
            # Provide detailed error message for debugging
            try:
                all_conns = db.query(ConnectionModel).filter(ConnectionModel.deleted_at.is_(None)).all()
                all_conn_ids = [str(c.id) for c in all_conns]
                all_numeric_ids = []
                for c in all_conns:
                    try:
                        all_numeric_ids.append(connection_id_to_int(str(c.id)))
                    except:
                        pass
                
                error_msg = f"Connection not found. Requested ID: {connection_id} (type: {type(connection_id).__name__})"
                if all_conn_ids:
                    error_msg += f". Available UUIDs (first 3): {all_conn_ids[:3]}"
                if all_numeric_ids:
                    error_msg += f". Available numeric IDs (first 3): {all_numeric_ids[:3]}"
                if connection_id in all_conn_ids:
                    error_msg += f". Note: Connection exists but lookup failed - possible ID format mismatch"
                
                logging.error(error_msg)
                raise HTTPException(status_code=404, detail=error_msg)
            except HTTPException:
                raise
            except Exception as e:
                logging.error(f"Error generating error message: {e}")
                raise HTTPException(status_code=404, detail=f"Connection not found: {connection_id}")
        
        # Ensure connection is active - activate if not
        if not conn.is_active:
            conn.is_active = True
            conn.updated_at = datetime.utcnow()
            db.commit()
        
        # Discover tables
        tables = discover_tables_from_db(conn, database=database, schema=schema)
        
        return {"tables": tables}
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list tables: {str(e)}")


@router.get("/{connection_id}/tables/{table_name}/data")
async def get_table_data(
    connection_id: str,
    table_name: str,
    schema: Optional[str] = Query(None),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """Get table data for a connection."""
    try:
        # Find connection by ID (support both UUID and numeric ID)
        conn = None
        import logging
        
        # First try direct string match (most common case - UUID string)
        conn = db.query(ConnectionModel).filter(
            ConnectionModel.id == str(connection_id),
            ConnectionModel.deleted_at.is_(None)
        ).first()
        
        if not conn:
            # Try as UUID object (parse and convert to string)
            try:
                conn_uuid = uuid.UUID(str(connection_id))
                conn_uuid_str = str(conn_uuid)
                conn = db.query(ConnectionModel).filter(
                    ConnectionModel.id == conn_uuid_str,
                    ConnectionModel.deleted_at.is_(None)
                ).first()
            except (ValueError, TypeError):
                pass
        
        if not conn:
            # Try numeric ID lookup
            try:
                numeric_id = int(connection_id)
                all_conns = db.query(ConnectionModel).filter(ConnectionModel.deleted_at.is_(None)).all()
                for c in all_conns:
                    try:
                        # Use the same conversion function as pipelines.py
                        conn_numeric_id = connection_id_to_int(str(c.id))
                        if conn_numeric_id == numeric_id:
                            conn = c
                            logging.info(f"Found connection by numeric ID: {numeric_id} -> {c.id}")
                            break
                    except (ValueError, AttributeError, TypeError) as e:
                        logging.debug(f"Error converting connection ID {c.id}: {e}")
                        continue
            except (ValueError, TypeError):
                pass
        
        if not conn:
            # Provide detailed error message for debugging
            try:
                all_conns = db.query(ConnectionModel).filter(ConnectionModel.deleted_at.is_(None)).all()
                all_conn_ids = [str(c.id) for c in all_conns]
                all_numeric_ids = []
                for c in all_conns:
                    try:
                        all_numeric_ids.append(connection_id_to_int(str(c.id)))
                    except:
                        pass
                
                error_msg = f"Connection not found. Requested ID: {connection_id} (type: {type(connection_id).__name__})"
                if all_conn_ids:
                    error_msg += f". Available UUIDs (first 3): {all_conn_ids[:3]}"
                if all_numeric_ids:
                    error_msg += f". Available numeric IDs (first 3): {all_numeric_ids[:3]}"
                if connection_id in all_conn_ids:
                    error_msg += f". Note: Connection exists but lookup failed - possible ID format mismatch"
                
                logging.error(error_msg)
                raise HTTPException(status_code=404, detail=error_msg)
            except HTTPException:
                raise
            except Exception as e:
                logging.error(f"Error generating error message: {e}")
                raise HTTPException(status_code=404, detail=f"Connection not found: {connection_id}")
        
        # Ensure connection is active - activate if not
        if not conn.is_active:
            conn.is_active = True
            conn.updated_at = datetime.utcnow()
            db.commit()
        
        # Get table data
        from sqlalchemy import create_engine, text
        from sqlalchemy.exc import SQLAlchemyError
        
        db_type = conn.database_type.lower()
        schema_name = schema or conn.schema
        
        # Handle S3 connections - S3 doesn't support SQL queries
        if db_type == "s3" or db_type == "aws_s3":
            # For S3, return a mock response indicating files/objects instead of table data
            # S3 stores objects (files), not tables with rows
            return {
                "columns": [
                    {"name": "key", "type": "string"},
                    {"name": "size", "type": "bigint"},
                    {"name": "last_modified", "type": "timestamp"}
                ],
                "records": [
                    {
                        "key": f"s3://{conn.database}/{table_name}",
                        "size": 0,
                        "last_modified": None
                    }
                ],
                "count": 1,
                "limit": limit,
                "message": "S3 stores objects (files), not table rows. This is a placeholder response."
            }
        
        try:
            # Build connection string (already includes connect_timeout for PostgreSQL/MySQL)
            conn_str = get_database_connection_string(conn)
            
            # Create engine - no timeout in connect_args for PostgreSQL/MySQL (already in connection string)
            connect_args = {}
            if "sqlite" in conn_str:
                connect_args["timeout"] = 10
            
            engine = create_engine(
                conn_str,
                pool_pre_ping=True,
                connect_args=connect_args
            )
            
            records = []
            columns = []
            
            with engine.connect() as connection:
                # Parse table_name to handle cases where it might include schema prefix
                # e.g., "public.employees" -> extract just "employees"
                actual_table_name = table_name
                if '.' in table_name:
                    # If table_name contains a dot, split it and use the last part as table name
                    parts = table_name.split('.')
                    actual_table_name = parts[-1]  # Get the last part (actual table name)
                    # If schema wasn't provided but is in table_name, use it
                    if not schema_name and len(parts) > 1:
                        schema_name = parts[0]  # Use the first part as schema
                
                # Build table reference based on database type
                if db_type in ["postgresql", "postgres"]:
                    if schema_name:
                        table_ref = f'"{schema_name}"."{actual_table_name}"'
                    else:
                        table_ref = f'"{actual_table_name}"'  # Default to public schema
                    
                    # Get columns first
                    col_query = text("""
                        SELECT column_name, data_type
                        FROM information_schema.columns
                        WHERE table_schema = COALESCE(:schema, 'public') AND table_name = :table
                        ORDER BY ordinal_position
                    """)
                    col_result = connection.execute(col_query, {"schema": schema_name, "table": actual_table_name})
                    columns = [{"name": row[0], "type": row[1]} for row in col_result]
                    
                    # Get data
                    data_query = text(f"SELECT * FROM {table_ref} LIMIT :limit")
                    result = connection.execute(data_query, {"limit": limit})
                    
                elif db_type in ["mysql"]:
                    if schema_name:
                        table_ref = f"`{schema_name}`.`{actual_table_name}`"
                    else:
                        table_ref = f"`{actual_table_name}`"
                    
                    # Get columns
                    col_query = text("""
                        SELECT column_name, data_type
                        FROM information_schema.columns
                        WHERE table_schema = :schema AND table_name = :table
                        ORDER BY ordinal_position
                    """)
                    schema_for_query = schema_name or conn.database
                    col_result = connection.execute(col_query, {"schema": schema_for_query, "table": actual_table_name})
                    columns = [{"name": row[0], "type": row[1]} for row in col_result]
                    
                    # Get data
                    data_query = text(f"SELECT * FROM {table_ref} LIMIT :limit")
                    result = connection.execute(data_query, {"limit": limit})
                    
                elif db_type in ["sqlserver", "mssql"]:
                    # Parse table_name to handle cases where it might include schema prefix
                    # e.g., "public.employees" -> extract just "employees"
                    actual_table_name = table_name
                    if '.' in table_name:
                        # If table_name contains a dot, split it and use the last part as table name
                        parts = table_name.split('.')
                        actual_table_name = parts[-1]  # Get the last part (actual table name)
                        # If schema wasn't provided but is in table_name, use it
                        if not schema_name and len(parts) > 1:
                            schema_name = parts[0]  # Use the first part as schema
                    
                    if schema_name:
                        table_ref = f"[{schema_name}].[{actual_table_name}]"
                    else:
                        # SQL Server default schema is usually 'dbo'
                        table_ref = f"[dbo].[{actual_table_name}]"
                    
                    # Get columns
                    col_query = text("""
                        SELECT column_name, data_type
                        FROM information_schema.columns
                        WHERE table_schema = COALESCE(:schema, 'dbo') AND table_name = :table
                        ORDER BY ordinal_position
                    """)
                    col_result = connection.execute(col_query, {"schema": schema_name, "table": actual_table_name})
                    columns = [{"name": row[0], "type": row[1]} for row in col_result]
                    
                    # Get data - SQL Server TOP clause doesn't support parameters, use string formatting
                    # Safe because limit is validated (1-1000)
                    data_query = text(f"SELECT TOP {limit} * FROM {table_ref}")
                    result = connection.execute(data_query)
                    
                elif db_type == "oracle":
                    if schema_name:
                        table_ref = f'"{schema_name}"."{actual_table_name}"'
                    else:
                        # Oracle uses current user schema
                        table_ref = f'"{actual_table_name}"'
                    
                    # Get columns
                    col_query = text("""
                        SELECT column_name, data_type
                        FROM all_tab_columns
                        WHERE owner = COALESCE(:schema, USER) AND table_name = :table
                        ORDER BY column_id
                    """)
                    col_result = connection.execute(col_query, {"schema": schema_name, "table": actual_table_name.upper()})
                    columns = [{"name": row[0], "type": row[1]} for row in col_result]
                    
                    # Get data
                    # Get data - Oracle ROWNUM doesn't support parameters, use string formatting
                    # Safe because limit is validated (1-1000)
                    data_query = text(f"SELECT * FROM {table_ref} WHERE ROWNUM <= {limit}")
                    result = connection.execute(data_query)
                    
                else:
                    # Fallback for other database types
                    table_ref = actual_table_name
                    if schema_name:
                        table_ref = f"{schema_name}.{actual_table_name}"
                    
                    # Get columns using inspector
                    from sqlalchemy import inspect
                    inspector = inspect(engine)
                    if schema_name:
                        columns_info = inspector.get_columns(actual_table_name, schema=schema_name)
                    else:
                        columns_info = inspector.get_columns(actual_table_name)
                    columns = [{"name": col["name"], "type": str(col["type"])} for col in columns_info]
                    
                    # Get data
                    data_query = text(f"SELECT * FROM {table_ref} LIMIT :limit")
                    result = connection.execute(data_query, {"limit": limit})
                
                # Convert rows to dictionaries
                # SQLAlchemy 2.0 returns Row objects that can be accessed by column name
                for row in result:
                    record = {}
                    # Try to access by column name first (SQLAlchemy 2.0 Row)
                    if hasattr(row, '_mapping'):
                        # Row object with _mapping (SQLAlchemy 2.0)
                        for col in columns:
                            col_name = col["name"]
                            value = row._mapping.get(col_name) if hasattr(row, '_mapping') else None
                            if value is None and hasattr(row, col_name):
                                value = getattr(row, col_name, None)
                            # Convert non-serializable types to strings
                            if value is not None:
                                try:
                                    import json
                                    json.dumps(value)
                                    record[col_name] = value
                                except (TypeError, ValueError):
                                    record[col_name] = str(value)
                            else:
                                record[col_name] = None
                    else:
                        # Fallback: access by index
                        for i, col in enumerate(columns):
                            value = row[i] if i < len(row) else None
                            # Convert non-serializable types to strings
                            if value is not None:
                                try:
                                    import json
                                    json.dumps(value)
                                    record[col["name"]] = value
                                except (TypeError, ValueError):
                                    record[col["name"]] = str(value)
                            else:
                                record[col["name"]] = None
                    records.append(record)
            
            return {
                "columns": columns,
                "records": records,
                "count": len(records),
                "limit": limit
            }
        
        except ValueError as e:
            # Handle validation errors (e.g., empty password for SQL Server)
            error_msg = str(e)
            if "password" in error_msg.lower() and "empty" in error_msg.lower():
                raise HTTPException(
                    status_code=400,
                    detail=f"Connection configuration error for '{conn.name}': {error_msg}. Please update the connection settings with a valid password."
                )
            raise HTTPException(status_code=400, detail=f"Connection configuration error: {error_msg}")
        except SQLAlchemyError as e:
            error_str = str(e)
            # Provide more helpful error messages for common issues
            if "password authentication failed" in error_str.lower() or "authentication failed" in error_str.lower():
                raise HTTPException(
                    status_code=500,
                    detail=f"Database authentication failed for connection '{conn.name}' (host: {conn.host}, user: {conn.username}). Please verify the username and password are correct. Error: {error_str}"
                )
            elif "invalid value specified for connection string attribute 'PWD'" in error_str.lower():
                raise HTTPException(
                    status_code=500,
                    detail=f"SQL Server connection error for '{conn.name}': Invalid password format. The password may be empty, None, or contain invalid characters. Please update the connection settings with a valid password. Error: {error_str}"
                )
            elif "connection" in error_str.lower() and ("refused" in error_str.lower() or "timeout" in error_str.lower()):
                raise HTTPException(
                    status_code=500,
                    detail=f"Database connection failed. Please check if the database server at {conn.host}:{conn.port} is running and accessible. Error: {error_str}"
                )
            else:
                raise HTTPException(status_code=500, detail=f"Database error: {error_str}")
        except ValueError as e:
            # Handle validation errors (e.g., empty password for SQL Server)
            raise HTTPException(status_code=400, detail=f"Connection configuration error: {str(e)}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to get table data: {str(e)}")
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get table data: {str(e)}")

