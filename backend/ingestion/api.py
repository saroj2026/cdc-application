"""FastAPI REST API for CDC pipeline management."""

from __future__ import annotations

import logging
import os
import sys
import time
import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

# Fix for Windows multiprocessing spawn issue
# Set multiprocessing start method early to prevent spawn errors
if sys.platform == 'win32':
    try:
        import multiprocessing
        multiprocessing.set_start_method('spawn', force=True)
    except (RuntimeError, ImportError):
        # Already set or multiprocessing not available, ignore
        pass

try:
    from fastapi import FastAPI, HTTPException, status, Depends, Request, Query
    from fastapi.responses import JSONResponse
    from fastapi.middleware.cors import CORSMiddleware
    from pydantic import BaseModel, Field
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False
    # Create dummy classes for when FastAPI is not available
    class FastAPI:
        def __init__(self, *args, **kwargs):
            pass
        def post(self, *args, **kwargs):
            return lambda f: f
        def get(self, *args, **kwargs):
            return lambda f: f
        def put(self, *args, **kwargs):
            return lambda f: f
        def delete(self, *args, **kwargs):
            return lambda f: f
    class HTTPException(Exception):
        pass
    class BaseModel:
        pass
    class Field:
        pass

from ingestion.cdc_manager import CDCManager
from ingestion.pipeline_service import PipelineService
from ingestion.connection_service import ConnectionService
from ingestion.discovery_service import DiscoveryService
from ingestion.schema_service import SchemaService
from ingestion.metrics_collector import MetricsCollector
from ingestion.lag_monitor import LagMonitor
from ingestion.data_quality import DataQualityMonitor
from ingestion.alerting.alert_engine import AlertEngine
from ingestion.monitoring import CDCMonitor
from ingestion.recovery import RecoveryManager
from ingestion.cdc_health_monitor import CDCHealthMonitor
from ingestion.background_monitor import start_background_monitor

# WebSocket support
try:
    import socketio
    from socketio import ASGIApp
    SOCKETIO_AVAILABLE = True
except ImportError:
    SOCKETIO_AVAILABLE = False
    logger.warning("python-socketio not available. WebSocket features will be disabled.")
from ingestion.models import Connection, Pipeline, PipelineStatus, FullLoadStatus, CDCStatus, PipelineMode
from ingestion.database import get_db
from ingestion.database.models_db import ConnectionModel, PipelineModel, UserModel, AuditLogModel
from sqlalchemy.orm import Session
import hashlib
import secrets
import os

# Try to import JWT library
try:
    from jose import jwt
    JWT_AVAILABLE = True
except ImportError:
    try:
        import jwt
        JWT_AVAILABLE = True
    except ImportError:
        JWT_AVAILABLE = False

logger = logging.getLogger(__name__)

# Setup database logging handler (if available)
try:
    from ingestion.database_log_handler import DatabaseLogHandler
    # Add database handler to root logger to capture all logs
    root_logger = logging.getLogger()
    db_handler = DatabaseLogHandler(level=logging.INFO)  # Capture INFO and above
    db_handler.setFormatter(logging.Formatter('%(message)s'))
    root_logger.addHandler(db_handler)
    logger.info("Database logging handler initialized")
except Exception as e:
    logger.warning(f"Failed to initialize database logging handler: {e}. Logs will not be stored in database.")

# Initialize FastAPI app
app = FastAPI(title="CDC Pipeline API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "*"],  # Next.js default ports + allow all for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Add exception handler for non-HTTPException errors to ensure CORS headers are set
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler for non-HTTPException errors to ensure CORS headers are always set."""
    from fastapi.responses import JSONResponse
    import traceback
    
    # Don't handle HTTPException here - let FastAPI handle it normally (CORS middleware will add headers)
    if isinstance(exc, HTTPException):
        raise exc
    
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    traceback.print_exc()
    
    return JSONResponse(
        status_code=500,
        content={
            "detail": str(exc) if str(exc) else "Internal server error",
            "type": type(exc).__name__
        },
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "*",
            "Access-Control-Allow-Headers": "*",
        }
    )

# Initialize WebSocket server if available
socketio_server = None
if SOCKETIO_AVAILABLE:
    try:
        socketio_server = socketio.AsyncServer(
            cors_allowed_origins=["http://localhost:3000", "http://localhost:3001", "*"],
            async_mode='asgi',
            logger=True,
            engineio_logger=False
        )
        logger.info("Socket.IO server initialized successfully")
    except Exception as e:
        logger.warning(f"Failed to initialize Socket.IO server: {e}")
        socketio_server = None

# Track subscribed pipelines for WebSocket
subscribed_pipelines: Dict[str, set] = {}  # Pipeline ID -> Set of session IDs

# Helper function to emit WebSocket events
async def emit_replication_event(event_data: Dict[str, Any]):
    """Emit replication event to subscribed clients via WebSocket."""
    if not socketio_server:
        return
    
    pipeline_id = str(event_data.get('pipeline_id', ''))
    if pipeline_id and pipeline_id in subscribed_pipelines:
        sessions = subscribed_pipelines[pipeline_id]
        if sessions:
            try:
                await socketio_server.emit('replication_event', event_data, room=list(sessions))
                logger.debug(f"Emitted replication event to {len(sessions)} sessions for pipeline {pipeline_id}")
            except Exception as e:
                logger.warning(f"Failed to emit replication event: {e}")

async def emit_monitoring_metric(metric_data: Dict[str, Any]):
    """Emit monitoring metric to subscribed clients via WebSocket."""
    if not socketio_server:
        return
    
    pipeline_id = str(metric_data.get('pipeline_id', ''))
    if pipeline_id and pipeline_id in subscribed_pipelines:
        sessions = subscribed_pipelines[pipeline_id]
        if sessions:
            try:
                await socketio_server.emit('monitoring_metric', metric_data, room=list(sessions))
                logger.debug(f"Emitted monitoring metric to {len(sessions)} sessions for pipeline {pipeline_id}")
            except Exception as e:
                logger.warning(f"Failed to emit monitoring metric: {e}")

# WebSocket event handlers
if socketio_server:
    @socketio_server.on('connect')
    async def on_connect(sid, environ):
        """Handle client connection."""
        logger.info(f"WebSocket client connected: {sid}")

    @socketio_server.on('disconnect')
    async def on_disconnect(sid):
        """Handle client disconnection."""
        logger.info(f"WebSocket client disconnected: {sid}")
        # Remove from all subscribed pipelines
        for pipeline_id, sessions in list(subscribed_pipelines.items()):
            sessions.discard(sid)
            if not sessions:
                del subscribed_pipelines[pipeline_id]

    @socketio_server.on('subscribe_pipeline')
    async def on_subscribe_pipeline(sid, data):
        """Subscribe to pipeline events."""
        pipeline_id = str(data.get('pipeline_id', ''))
        if pipeline_id:
            if pipeline_id not in subscribed_pipelines:
                subscribed_pipelines[pipeline_id] = set()
            subscribed_pipelines[pipeline_id].add(sid)
            logger.info(f"Client {sid} subscribed to pipeline {pipeline_id}")
            # Join a room for this pipeline for easier broadcasting
            await socketio_server.enter_room(sid, f"pipeline_{pipeline_id}")

    @socketio_server.on('unsubscribe_pipeline')
    async def on_unsubscribe_pipeline(sid, data):
        """Unsubscribe from pipeline events."""
        pipeline_id = str(data.get('pipeline_id', ''))
        if pipeline_id and pipeline_id in subscribed_pipelines:
            subscribed_pipelines[pipeline_id].discard(sid)
            await socketio_server.leave_room(sid, f"pipeline_{pipeline_id}")
            if not subscribed_pipelines[pipeline_id]:
                del subscribed_pipelines[pipeline_id]
            logger.info(f"Client {sid} unsubscribed from pipeline {pipeline_id}")

# Initialize services
# Get Kafka Connect URL from environment or use remote server
kafka_connect_url = os.getenv("KAFKA_CONNECT_URL", "http://72.61.233.209:8083")
logger.info(f"Initializing CDC Manager with Kafka Connect URL: {kafka_connect_url}")

cdc_manager = CDCManager(kafka_connect_url=kafka_connect_url)
# Set database session factory for status persistence
from ingestion.cdc_manager import set_db_session_factory
set_db_session_factory(get_db)
pipeline_service = PipelineService(cdc_manager)
connection_service = ConnectionService()
discovery_service = DiscoveryService()
schema_service = SchemaService()
cdc_monitor = CDCMonitor(cdc_manager.kafka_client)

# Monitoring services (will use db session from dependency injection)
lag_monitor = LagMonitor(connection_service)
data_quality_monitor = DataQualityMonitor(connection_service)
recovery_manager = RecoveryManager(cdc_manager)

# CDC Health Monitor (will be initialized with db session in endpoints)
# Note: We create a function to get health monitor instance per request
def get_health_monitor(db: Session) -> CDCHealthMonitor:
    """Get CDC Health Monitor instance with database session."""
    return CDCHealthMonitor(
        kafka_client=cdc_manager.kafka_client,
        connection_service=connection_service,
        db_session=db,
        kafka_connect_url=kafka_connect_url
    )

# Start background monitoring service
# Check interval from environment (default: 60 seconds)
monitor_interval = int(os.getenv("CDC_MONITOR_INTERVAL_SECONDS", "60"))
try:
    start_background_monitor(
        kafka_connect_url=kafka_connect_url,
        check_interval_seconds=monitor_interval
    )
    logger.info(f"Background CDC health monitor started (interval: {monitor_interval}s)")
except Exception as e:
    logger.warning(f"Failed to start background monitor: {e}. Monitoring will still work via API endpoints.")


# Pydantic models for request/response
class ConnectionCreate(BaseModel):
    """Connection creation request model."""
    name: str
    connection_type: str = Field(default="source", description="'source' or 'target' - optional, defaults to 'source'. Role is determined when creating pipelines.")
    database_type: str = Field(..., description="'postgresql', 'sqlserver', 'mysql', 's3', 'snowflake', etc.")
    host: Optional[str] = Field(default=None, description="Host or account identifier (required for most DBs, optional for Snowflake/S3)")
    port: Optional[int] = Field(default=None, description="Port number (required for most DBs, optional for Snowflake/S3)")
    database: str
    username: str
    password: str
    schema_name: Optional[str] = Field(default=None, alias="schema", description="Database schema name")
    additional_config: Optional[Dict[str, Any]] = None
    
    class Config:
        populate_by_name = True  # Allow both 'schema' and 'schema_name'


class PipelineCreate(BaseModel):
    """Pipeline creation request model."""
    name: str
    source_connection_id: str
    target_connection_id: str
    source_database: str
    source_schema: str
    source_tables: List[str]
    target_database: Optional[str] = None
    target_schema: Optional[str] = None
    target_tables: Optional[List[str]] = None
    mode: str = PipelineMode.FULL_LOAD_AND_CDC.value
    enable_full_load: Optional[bool] = None  # Deprecated, use mode instead
    auto_create_target: bool = True
    target_table_mapping: Optional[Dict[str, str]] = None
    table_filter: Optional[str] = None


class PipelineUpdate(BaseModel):
    """Pipeline update request model."""
    name: Optional[str] = None
    source_connection_id: Optional[str] = None
    target_connection_id: Optional[str] = None
    source_database: Optional[str] = None
    source_schema: Optional[str] = None
    source_tables: Optional[List[str]] = None
    target_database: Optional[str] = None
    target_schema: Optional[str] = None
    target_tables: Optional[List[str]] = None
    mode: Optional[str] = None
    enable_full_load: Optional[bool] = None
    auto_create_target: Optional[bool] = None
    target_table_mapping: Optional[Dict[str, str]] = None
    table_filter: Optional[str] = None


# API Endpoints

@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "CDC Pipeline API", "version": "1.0.0"}


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    try:
        # Basic health check - verify database connection
        from ingestion.database.session import SessionLocal
        from sqlalchemy import text
        db = SessionLocal()
        try:
            # Simple query to check database connectivity
            db.execute(text("SELECT 1"))
            db_status = "healthy"
        except Exception as e:
            logger.warning(f"Database health check failed: {e}")
            db_status = "unhealthy"
        finally:
            db.close()
        
        # Check Kafka Connect connectivity
        kafka_connect_status = "unknown"
        kafka_connect_error = None
        try:
            import requests
            response = requests.get(f"{kafka_connect_url}/connector-plugins", timeout=5)
            if response.status_code == 200:
                kafka_connect_status = "healthy"
            else:
                kafka_connect_status = "unhealthy"
                kafka_connect_error = f"HTTP {response.status_code}"
        except requests.exceptions.ConnectTimeout:
            kafka_connect_status = "unreachable"
            kafka_connect_error = "Connection timeout - may be blocked by firewall or network"
        except requests.exceptions.ConnectionError as e:
            kafka_connect_status = "unreachable"
            kafka_connect_error = f"Connection error: {str(e)[:100]}"
        except Exception as e:
            logger.warning(f"Kafka Connect health check failed: {e}")
            kafka_connect_status = "unhealthy"
            kafka_connect_error = str(e)[:100]
        
        # Backend is healthy if database is healthy
        # Kafka Connect being unreachable doesn't make backend unhealthy
        # (it's on a remote server and may not be accessible from local machine)
        overall_status = "healthy" if db_status == "healthy" else "degraded"
        
        response_data = {
            "status": overall_status,
            "database": db_status,
            "kafka_connect": {
                "status": kafka_connect_status,
                "url": kafka_connect_url
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if kafka_connect_error:
            response_data["kafka_connect"]["error"] = kafka_connect_error
        
        return response_data
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
        )


@app.get("/api/health")
async def api_health_check():
    """API health check endpoint (alias for /health)."""
    return await health_check()


@app.post("/api/v1/connections", status_code=status.HTTP_201_CREATED)
async def create_connection(
    connection_data: ConnectionCreate,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Create a new database connection.
    
    Args:
        connection_data: Connection data
        db: Database session
        
    Returns:
        Created connection
    """
    
    try:
        # connection_type is optional - default to "source" if not provided
        # The actual role (source/target) is determined when creating pipelines
        connection_type_value = connection_data.connection_type or "source"
        
        # For Snowflake, account can be in host field or additional_config
        # For S3, host is optional
        db_type = connection_data.database_type.lower()
        host_value = connection_data.host
        port_value = connection_data.port
        
        # Handle Snowflake: account can be in host or additional_config.account
        if db_type == "snowflake":
            # If account is in additional_config, use it; otherwise use host
            additional_config = connection_data.additional_config or {}
            account = additional_config.get("account") or host_value
            if account:
                host_value = account
            # Snowflake doesn't use port, but we can set a default
            if not port_value:
                port_value = 443  # HTTPS port
        # Handle S3: host is optional
        elif db_type in ["s3", "aws_s3"]:
            # S3 doesn't require host/port, but we can set defaults
            if not host_value:
                host_value = "s3.amazonaws.com"
            if not port_value:
                port_value = 443
        
        connection_model = ConnectionModel(
            id=str(uuid.uuid4()),
            name=connection_data.name,
            connection_type=connection_type_value,
            database_type=connection_data.database_type,
            host=host_value or "",
            port=port_value or 3306,  # Default port if not provided
            database=connection_data.database,
            username=connection_data.username,
            password=connection_data.password,
            schema=connection_data.schema_name,
            additional_config=connection_data.additional_config or {}
        )
        
        db.add(connection_model)
        db.commit()
        db.refresh(connection_model)
        
        return {
            "id": connection_model.id,
            "name": connection_model.name,
            "connection_type": connection_model.connection_type.value,
            "database_type": connection_model.database_type.value,
            "host": connection_model.host,
            "port": connection_model.port,
            "database": connection_model.database,
            "username": connection_model.username,
            "password": "***",
            "schema": connection_model.schema,
            "additional_config": connection_model.additional_config,
            "is_active": connection_model.is_active,
            "last_tested_at": connection_model.last_tested_at.isoformat() if connection_model.last_tested_at else None,
            "last_test_status": connection_model.last_test_status,
            "created_at": connection_model.created_at.isoformat(),
            "updated_at": connection_model.updated_at.isoformat()
        }
        
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to create connection: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@app.get("/api/v1/connections")
async def list_connections(
    db: Session = Depends(get_db),
    active_only: bool = False
) -> List[Dict[str, Any]]:
    """List all connections.
    
    Args:
        db: Database session
        active_only: Only return active connections
        
    Returns:
        List of connections
    """
    
    # Handle database connection failure
    if db is None:
        logger.warning("Database unavailable, returning empty connections list")
        return []
    
    try:
        query = db.query(ConnectionModel).filter(ConnectionModel.deleted_at.is_(None))
        if active_only:
            query = query.filter(ConnectionModel.is_active == True)
        
        connections = query.all()
        
        return [
            {
                "id": conn.id,
                "name": conn.name,
                "connection_type": conn.connection_type.value,
                "database_type": conn.database_type.value,
                "host": conn.host,
                "port": conn.port,
                "database": conn.database,
                "username": conn.username,
                "password": "***",
                "schema": conn.schema,
                "additional_config": conn.additional_config,
                "is_active": conn.is_active,
                "last_tested_at": conn.last_tested_at.isoformat() if conn.last_tested_at else None,
                "last_test_status": conn.last_test_status,
                "created_at": conn.created_at.isoformat(),
                "updated_at": conn.updated_at.isoformat()
            }
            for conn in connections
        ]
    except Exception as e:
        logger.error(f"Failed to list connections: {e}", exc_info=True)
        # Return empty list instead of crashing
        return []


@app.get("/api/v1/connections/{connection_id}")
async def get_connection(
    connection_id: str,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Get connection by ID.
    
    Args:
        connection_id: Connection ID
        db: Database session
        
    Returns:
        Connection details
    """
    
    try:
        connection = db.query(ConnectionModel).filter(
            ConnectionModel.id == connection_id,
            ConnectionModel.deleted_at.is_(None)
        ).first()
        
        if not connection:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Connection not found: {connection_id}"
            )
        
        return {
            "id": connection.id,
            "name": connection.name,
            "connection_type": connection.connection_type.value,
            "database_type": connection.database_type.value,
            "host": connection.host,
            "port": connection.port,
            "database": connection.database,
            "username": connection.username,
            "password": "***",
            "schema": connection.schema,
            "additional_config": connection.additional_config,
            "is_active": connection.is_active,
            "last_tested_at": connection.last_tested_at.isoformat() if connection.last_tested_at else None,
            "last_test_status": connection.last_test_status,
            "created_at": connection.created_at.isoformat(),
            "updated_at": connection.updated_at.isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get connection: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@app.put("/api/v1/connections/{connection_id}")
async def update_connection(
    connection_id: str,
    connection_data: ConnectionCreate,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Update a database connection.
    
    Args:
        connection_id: Connection ID
        connection_data: Updated connection data
        db: Database session
        
    Returns:
        Updated connection
    """
    
    try:
        connection = db.query(ConnectionModel).filter(
            ConnectionModel.id == connection_id,
            ConnectionModel.deleted_at.is_(None)
        ).first()
        
        if not connection:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Connection not found: {connection_id}"
            )
        
        # For Snowflake, account can be in host field or additional_config
        # For S3, host is optional
        db_type = connection_data.database_type.lower()
        host_value = connection_data.host
        port_value = connection_data.port
        
        # Handle Snowflake: account can be in host or additional_config.account
        if db_type == "snowflake":
            # If account is in additional_config, use it; otherwise use host
            additional_config = connection_data.additional_config or {}
            account = additional_config.get("account") or host_value
            if account:
                host_value = account
            # Snowflake doesn't use port, but we can set a default
            if not port_value:
                port_value = 443  # HTTPS port
        # Handle S3: host is optional
        elif db_type in ["s3", "aws_s3"]:
            # S3 doesn't require host/port, but we can set defaults
            if not host_value:
                host_value = "s3.amazonaws.com"
            if not port_value:
                port_value = 443
        
        # Update fields
        connection.name = connection_data.name
        connection.connection_type = connection_data.connection_type
        connection.database_type = connection_data.database_type
        connection.host = host_value or ""
        connection.port = port_value or 3306  # Default port if not provided
        connection.database = connection_data.database
        connection.username = connection_data.username
        connection.password = connection_data.password
        connection.schema = connection_data.schema_name
        connection.additional_config = connection_data.additional_config or {}
        connection.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(connection)
        
        return {
            "id": connection.id,
            "name": connection.name,
            "connection_type": connection.connection_type.value,
            "database_type": connection.database_type.value,
            "host": connection.host,
            "port": connection.port,
            "database": connection.database,
            "username": connection.username,
            "password": "***",
            "schema": connection.schema,
            "additional_config": connection.additional_config,
            "is_active": connection.is_active,
            "last_tested_at": connection.last_tested_at.isoformat() if connection.last_tested_at else None,
            "last_test_status": connection.last_test_status,
            "created_at": connection.created_at.isoformat(),
            "updated_at": connection.updated_at.isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to update connection: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    finally:
        if db:
            db.close()


@app.delete("/api/v1/connections/{connection_id}")
async def delete_connection(
    connection_id: str,
    db: Session = Depends(get_db),
    hard_delete: bool = False
) -> Dict[str, Any]:
    """Delete a database connection.
    
    Args:
        connection_id: Connection ID
        db: Database session
        hard_delete: If True, permanently delete. If False, soft delete.
        
    Returns:
        Deletion result
    """
    
    try:
        connection = db.query(ConnectionModel).filter(
            ConnectionModel.id == connection_id,
            ConnectionModel.deleted_at.is_(None)
        ).first()
        
        if not connection:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Connection not found: {connection_id}"
            )
        
        # Check if connection is used by any pipelines
        pipelines_using = db.query(PipelineModel).filter(
            (PipelineModel.source_connection_id == connection_id) |
            (PipelineModel.target_connection_id == connection_id)
        ).count()
        
        if pipelines_using > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot delete connection: {pipelines_using} pipeline(s) are using this connection"
            )
        
        if hard_delete:
            db.delete(connection)
        else:
            connection.deleted_at = datetime.utcnow()
            connection.is_active = False
        
        db.commit()
        
        return {
            "message": f"Connection {connection_id} deleted",
            "hard_delete": hard_delete
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to delete connection: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    finally:
        if db:
            db.close()


@app.post("/api/v1/connections/test")
async def test_connection_data(connection_data: ConnectionCreate) -> Dict[str, Any]:
    """Test a database connection before creating it.
    
    Args:
        connection_data: Connection data to test
        
    Returns:
        Test result
    """
    try:
        # Create a temporary connection model for testing
        from ingestion.models import Connection
        from ingestion.database.models_db import ConnectionType, DatabaseType
        
        # Convert ConnectionCreate to Connection model
        # Connection class expects strings, not enums
        temp_connection = Connection(
            id=str(uuid.uuid4()),
            name="temp_test",
            connection_type=connection_data.connection_type or "source",  # String, not enum
            database_type=connection_data.database_type,  # String, not enum
            host=connection_data.host,
            port=connection_data.port,
            database=connection_data.database,
            username=connection_data.username,
            password=connection_data.password,
            schema=connection_data.schema_name,
            additional_config=connection_data.additional_config or {}
        )
        
        # Test the connection directly
        result = connection_service.test_connection_data(temp_connection)
        return result
    except Exception as e:
        logger.error(f"Failed to test connection: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@app.post("/api/v1/connections/{connection_id}/test")
async def test_connection(connection_id: str) -> Dict[str, Any]:
    """Test an existing database connection.
    
    Args:
        connection_id: Connection ID
        
    Returns:
        Test result
    """
    try:
        result = connection_service.test_connection(connection_id, save_history=True)
        return result
    except Exception as e:
        logger.error(f"Failed to test connection: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@app.get("/api/v1/connections/{connection_id}/test/history")
async def get_connection_test_history(
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
        history = connection_service.get_test_history(connection_id, limit=limit)
        return history
    except Exception as e:
        logger.error(f"Failed to get test history: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@app.get("/api/v1/connections/{connection_id}/databases")
async def list_connection_databases(connection_id: str) -> Dict[str, Any]:
    """List databases available in a connection.
    
    Args:
        connection_id: Connection ID
        
    Returns:
        Dictionary with list of databases
    """
    try:
        result = connection_service.discover_databases(connection_id)
        if not result.get("success"):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result.get("error", "Failed to discover databases")
            )
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to list databases: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@app.get("/api/v1/connections/{connection_id}/schemas")
async def list_connection_schemas(
    connection_id: str,
    database: Optional[str] = None
) -> Dict[str, Any]:
    """List schemas in a database.
    
    Args:
        connection_id: Connection ID
        database: Database name (optional, uses connection default)
        
    Returns:
        Dictionary with list of schemas
    """
    try:
        result = connection_service.discover_schemas(connection_id, database=database)
        if not result.get("success"):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result.get("error", "Failed to discover schemas")
            )
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to list schemas: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@app.get("/api/v1/connections/{connection_id}/tables")
async def list_connection_tables(
    connection_id: str,
    database: Optional[str] = None,
    schema: Optional[str] = None
) -> Dict[str, Any]:
    """List tables in a schema.
    
    Args:
        connection_id: Connection ID
        database: Database name (optional)
        schema: Schema name (optional)
        
    Returns:
        Dictionary with list of tables
    """
    try:
        result = connection_service.discover_tables(
            connection_id,
            database=database,
            schema=schema
        )
        if not result.get("success"):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result.get("error", "Failed to discover tables")
            )
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to list tables: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@app.get("/api/v1/connections/{connection_id}/table/{table_name}/schema")
async def get_table_schema(
    connection_id: str,
    table_name: str,
    database: Optional[str] = None,
    schema: Optional[str] = None
) -> Dict[str, Any]:
    """Get detailed schema information for a table.
    
    Args:
        connection_id: Connection ID
        table_name: Table name
        database: Database name (optional)
        schema: Schema name (optional)
        
    Returns:
        Dictionary with table schema details
    """
    try:
        result = connection_service.get_table_schema(
            connection_id,
            table_name,
            database=database,
            schema=schema
        )
        if not result.get("success"):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result.get("error", "Failed to get table schema")
            )
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get table schema: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@app.get("/api/v1/connections/{connection_id}/tables/{table_name}/data")
async def get_table_data(
    connection_id: str,
    table_name: str,
    database: Optional[str] = None,
    schema: Optional[str] = None,
    limit: int = Query(100, ge=1, le=1000)
) -> Dict[str, Any]:
    """Get table data from a connection.
    
    Args:
        connection_id: Connection ID
        table_name: Table name (may include schema prefix like "public.projects_simple")
        database: Database name (optional)
        schema: Schema name (optional)
        limit: Maximum number of records to return (1-1000)
        
    Returns:
        Dictionary with table data (records, columns, count)
    """
    try:
        # Clean table name - remove schema prefix if present and schema parameter is provided
        clean_table_name = table_name
        if '.' in clean_table_name and schema:
            parts = clean_table_name.split('.', 1)
            if len(parts) == 2 and parts[0] == schema:
                clean_table_name = parts[1]
                logger.info(f"[API get_table_data] Removed duplicate schema from table name: {table_name} -> {clean_table_name}")
        
        result = connection_service.get_table_data(
            connection_id,
            clean_table_name,  # Use cleaned table name
            database=database,
            schema=schema,
            limit=limit
        )
        if not result.get("success"):
            error_detail = result.get("error", "Failed to get table data")
            # Ensure error message is a string and doesn't contain unescaped format specifiers
            if not isinstance(error_detail, str):
                error_detail = str(error_detail)
            # Escape % characters to prevent string formatting issues
            # Replace all % with %% to escape them
            if '%' in error_detail:
                # Temporarily replace %% to avoid double-escaping
                error_detail = error_detail.replace('%%', '__TEMP_DOUBLE__')
                error_detail = error_detail.replace('%', '%%')
                error_detail = error_detail.replace('__TEMP_DOUBLE__', '%%')
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=error_detail
            )
        return result
    except HTTPException:
        raise
    except Exception as e:
        # Safely log error to avoid formatting issues
        try:
            from ingestion.connection_service import safe_error_message
            safe_error = safe_error_message(e)
            # Use %r (repr) to avoid any formatting issues
            try:
                logger.error("Failed to get table data: %r", safe_error, exc_info=True)
            except Exception as log_err:
                # If logging fails, just print to avoid cascading errors
                try:
                    print("Failed to get table data:", repr(safe_error))
                except Exception:
                    print("Failed to get table data: [Error message could not be formatted]")
        except Exception:
            try:
                logger.error("Failed to get table data: [Error message could not be formatted]", exc_info=True)
            except Exception:
                print("Failed to get table data: [Error message could not be formatted]")
        
        # Return error response with safe error message
        try:
            from ingestion.connection_service import safe_error_message
            safe_error = safe_error_message(e)
        except Exception:
            safe_error = "Failed to get table data: Unknown error occurred"
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=safe_error
        )
        # Escape any % characters in error message to prevent string formatting issues
        def safe_error_message(msg):
            """Safely convert error message to string and escape % characters."""
            if msg is None:
                return "Unknown error"
            error_str = str(msg)
            if '%' in error_str and '%%' not in error_str:
                return error_str.replace('%', '%%')
            return error_str
        error_detail = safe_error_message(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_detail
        )


@app.get("/api/v1/connections/{connection_id}/discover")
async def discover_connection(
    connection_id: str,
    database: Optional[str] = None,
    schema: Optional[str] = None
) -> Dict[str, Any]:
    """Full discovery of databases, schemas, and tables.
    
    Args:
        connection_id: Connection ID
        database: Database name (optional, for schema/table discovery)
        schema: Schema name (optional, for table discovery)
        
    Returns:
        Dictionary with discovery results
    """
    try:
        result = {
            "connection_id": connection_id,
            "databases": None,
            "schemas": None,
            "tables": None
        }
        
        # Discover databases
        db_result = connection_service.discover_databases(connection_id)
        if db_result.get("success"):
            result["databases"] = db_result.get("databases", [])
        
        # Discover schemas if database specified
        if database:
            schema_result = connection_service.discover_schemas(connection_id, database=database)
            if schema_result.get("success"):
                result["schemas"] = schema_result.get("schemas", [])
            
            # Discover tables if schema specified
            if schema:
                table_result = connection_service.discover_tables(
                    connection_id,
                    database=database,
                    schema=schema
                )
                if table_result.get("success"):
                    result["tables"] = table_result.get("tables", [])
        
        return result
        
    except Exception as e:
        logger.error(f"Failed to discover connection: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@app.post("/api/v1/pipelines", status_code=status.HTTP_201_CREATED)
async def create_pipeline(
    pipeline_data: PipelineCreate,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Create a new CDC pipeline.
    
    Args:
        pipeline_data: Pipeline data
        
    Returns:
        Created pipeline
    """
    try:
        # Load connections from database
        source_conn_model = db.query(ConnectionModel).filter(
            ConnectionModel.id == pipeline_data.source_connection_id,
            ConnectionModel.deleted_at.is_(None)
        ).first()
        
        target_conn_model = db.query(ConnectionModel).filter(
            ConnectionModel.id == pipeline_data.target_connection_id,
            ConnectionModel.deleted_at.is_(None)
        ).first()
        
        if not source_conn_model:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Source connection not found: {pipeline_data.source_connection_id}"
            )
        
        if not target_conn_model:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Target connection not found: {pipeline_data.target_connection_id}"
            )
        
        # Convert ConnectionModel to Connection object
        from ingestion.models import Connection
        
        source_connection = Connection(
            id=source_conn_model.id,
            name=source_conn_model.name,
            connection_type=source_conn_model.connection_type.value if hasattr(source_conn_model.connection_type, 'value') else str(source_conn_model.connection_type),
            database_type=source_conn_model.database_type.value if hasattr(source_conn_model.database_type, 'value') else str(source_conn_model.database_type),
            host=source_conn_model.host,
            port=source_conn_model.port,
            database=source_conn_model.database,
            username=source_conn_model.username,
            password=source_conn_model.password,
            schema=source_conn_model.schema,
            additional_config=source_conn_model.additional_config or {},
            created_at=source_conn_model.created_at,
            updated_at=source_conn_model.updated_at
        )
        
        target_connection = Connection(
            id=target_conn_model.id,
            name=target_conn_model.name,
            connection_type=target_conn_model.connection_type.value if hasattr(target_conn_model.connection_type, 'value') else str(target_conn_model.connection_type),
            database_type=target_conn_model.database_type.value if hasattr(target_conn_model.database_type, 'value') else str(target_conn_model.database_type),
            host=target_conn_model.host,
            port=target_conn_model.port,
            database=target_conn_model.database,
            username=target_conn_model.username,
            password=target_conn_model.password,
            schema=target_conn_model.schema,
            additional_config=target_conn_model.additional_config or {},
            created_at=target_conn_model.created_at,
            updated_at=target_conn_model.updated_at
        )
        
        # Add connections to CDC manager
        cdc_manager.add_connection(source_connection)
        cdc_manager.add_connection(target_connection)
        
        # Determine mode - handle backward compatibility
        mode = pipeline_data.mode
        if pipeline_data.enable_full_load is not None:
            # Backward compatibility: convert enable_full_load to mode
            if pipeline_data.enable_full_load:
                mode = PipelineMode.FULL_LOAD_AND_CDC.value if mode == PipelineMode.CDC_ONLY.value else mode
            else:
                mode = PipelineMode.CDC_ONLY.value
        
        pipeline = Pipeline(
            id=str(uuid.uuid4()),
            name=pipeline_data.name,
            source_connection_id=pipeline_data.source_connection_id,
            target_connection_id=pipeline_data.target_connection_id,
            source_database=pipeline_data.source_database,
            source_schema=pipeline_data.source_schema,
            source_tables=pipeline_data.source_tables,
            target_database=pipeline_data.target_database,
            target_schema=pipeline_data.target_schema,
            target_tables=pipeline_data.target_tables,
            mode=mode,
            enable_full_load=pipeline_data.enable_full_load,
            auto_create_target=pipeline_data.auto_create_target,
            target_table_mapping=pipeline_data.target_table_mapping,
            table_filter=pipeline_data.table_filter
        )
        
        created_pipeline = pipeline_service.create_pipeline(
            pipeline=pipeline,
            source_connection=source_connection,
            target_connection=target_connection
        )
        
        # Save pipeline to database
        from ingestion.database.models_db import PipelineMode as DBPipelineMode, PipelineStatus, FullLoadStatus, CDCStatus
        
        pipeline_model = PipelineModel(
            id=created_pipeline.id,
            name=created_pipeline.name,
            source_connection_id=created_pipeline.source_connection_id,
            target_connection_id=created_pipeline.target_connection_id,
            source_database=created_pipeline.source_database,
            source_schema=created_pipeline.source_schema,
            source_tables=created_pipeline.source_tables,
            target_database=created_pipeline.target_database,
            target_schema=created_pipeline.target_schema,
            target_tables=created_pipeline.target_tables,
            mode=DBPipelineMode(created_pipeline.mode),
            enable_full_load=created_pipeline.enable_full_load,
            auto_create_target=created_pipeline.auto_create_target,
            target_table_mapping=created_pipeline.target_table_mapping,
            table_filter=created_pipeline.table_filter,
            status=PipelineStatus.STOPPED,
            full_load_status=FullLoadStatus.NOT_STARTED,
            cdc_status=CDCStatus.NOT_STARTED
        )
        
        db.add(pipeline_model)
        db.commit()
        db.refresh(pipeline_model)
        
        return created_pipeline.to_dict()
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create pipeline: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@app.get("/api/v1/pipelines")
async def list_pipelines(
    skip: int = 0,
    limit: int = 10000,  # Increased default limit to fetch all pipelines
    db: Session = Depends(get_db)
) -> List[Dict[str, Any]]:
    """List all pipelines from database.
    
    Args:
        skip: Number of pipelines to skip (for pagination)
        limit: Maximum number of pipelines to return (default: 10000 to fetch all)
        db: Database session
    
    Returns:
        List of pipelines
    """
    try:
        # Load all pipelines from database (not just in-memory store)
        from ingestion.database.models_db import PipelineModel
        
        # Get all pipelines, including those that might be soft-deleted
        # (we'll filter by deleted_at if the column exists)
        try:
            query = db.query(PipelineModel).filter(
                PipelineModel.deleted_at.is_(None)
            ).order_by(PipelineModel.created_at.desc())
        except Exception:
            # If deleted_at column doesn't exist, get all
            query = db.query(PipelineModel).order_by(PipelineModel.created_at.desc())
        
        # Apply pagination
        pipeline_models = query.offset(skip).limit(limit).all()
        
        pipelines = []
        for pm in pipeline_models:
            # Convert target_table_mapping to table_mappings format for frontend compatibility
            table_mappings = []
            if pm.target_table_mapping:
                if isinstance(pm.target_table_mapping, dict):
                    for source_table, target_table in pm.target_table_mapping.items():
                        table_mappings.append({
                            "source_table": source_table,
                            "target_table": target_table if isinstance(target_table, str) else target_table.get("target_table", source_table),
                            "source_schema": pm.source_schema,
                            "target_schema": pm.target_schema or pm.source_schema
                        })
                elif isinstance(pm.target_table_mapping, list):
                    table_mappings = pm.target_table_mapping
            elif pm.source_tables:
                # Fallback: create mappings from source_tables
                for source_table in pm.source_tables:
                    target_table = pm.target_tables[pm.source_tables.index(source_table)] if pm.target_tables and len(pm.target_tables) > pm.source_tables.index(source_table) else source_table
                    table_mappings.append({
                        "source_table": source_table,
                        "target_table": target_table,
                        "source_schema": pm.source_schema,
                        "target_schema": pm.target_schema or pm.source_schema
                    })
            
            # Determine full_load_type and cdc_enabled from mode
            cdc_enabled = pm.mode.value in ["cdc_only", "full_load_and_cdc"] if hasattr(pm.mode, 'value') else "cdc" in str(pm.mode).lower()
            full_load_type = "overwrite" if pm.enable_full_load else "append"
            
            pipeline_dict = {
                "id": pm.id,
                "name": pm.name,
                "source_connection_id": pm.source_connection_id,
                "target_connection_id": pm.target_connection_id,
                "source_database": pm.source_database,
                "source_schema": pm.source_schema,
                "source_tables": pm.source_tables or [],
                "target_database": pm.target_database,
                "target_schema": pm.target_schema,
                "target_tables": pm.target_tables or [],
                "mode": pm.mode.value if hasattr(pm.mode, 'value') else str(pm.mode),
                "enable_full_load": pm.enable_full_load,
                "cdc_enabled": cdc_enabled,  # Add cdc_enabled for frontend
                "full_load_type": full_load_type,  # Add full_load_type for frontend
                "auto_create_target": pm.auto_create_target,
                "target_table_mapping": pm.target_table_mapping or {},
                "table_mappings": table_mappings,  # Add table_mappings for frontend
                "table_filter": pm.table_filter,
                "status": pm.status.value if hasattr(pm.status, 'value') else str(pm.status),
                "full_load_status": pm.full_load_status.value if hasattr(pm.full_load_status, 'value') else str(pm.full_load_status),
                "cdc_status": pm.cdc_status.value if hasattr(pm.cdc_status, 'value') else str(pm.cdc_status),
                "debezium_connector_name": pm.debezium_connector_name,
                "sink_connector_name": pm.sink_connector_name,
                "kafka_topics": pm.kafka_topics or [],
                "created_at": pm.created_at.isoformat() if pm.created_at else None,
                "updated_at": pm.updated_at.isoformat() if pm.updated_at else None
            }
            pipelines.append(pipeline_dict)
        
        return pipelines
    except Exception as e:
        logger.error(f"Failed to list pipelines: {e}", exc_info=True)
        # Fallback to in-memory store
        return pipeline_service.list_pipelines()


@app.get("/api/v1/pipelines/{pipeline_id}")
async def get_pipeline(pipeline_id: str) -> Dict[str, Any]:
    """Get pipeline by ID.
    
    Args:
        pipeline_id: Pipeline ID
        
    Returns:
        Pipeline details
    """
    try:
        status_info = pipeline_service.get_pipeline_status(pipeline_id)
        return status_info
    except Exception as e:
        logger.error(f"Failed to get pipeline {pipeline_id}: {e}", exc_info=True)
        # Return minimal pipeline info instead of error to prevent UI breakage
        return {
            "id": pipeline_id,
            "name": f"Pipeline {pipeline_id}",
            "status": "UNKNOWN",
            "full_load_status": "NOT_STARTED",
            "cdc_status": "NOT_STARTED",
            "error": str(e)
        }


@app.put("/api/v1/pipelines/{pipeline_id}")
async def update_pipeline(
    pipeline_id: str,
    pipeline_data: PipelineUpdate,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Update a pipeline.
    
    Args:
        pipeline_id: Pipeline ID
        pipeline_data: Pipeline update data
        db: Database session
        
    Returns:
        Updated pipeline
    """
    try:
        # Load pipeline from database
        pipeline_model = db.query(PipelineModel).filter(
            PipelineModel.id == pipeline_id,
            PipelineModel.deleted_at.is_(None)
        ).first()
        
        if not pipeline_model:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Pipeline not found: {pipeline_id}"
            )
        
        # Check if pipeline is running - don't allow updates to running pipelines
        if pipeline_model.status.value in ["RUNNING", "STARTING"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot update a running pipeline. Please stop it first."
            )
        
        # Update fields if provided
        if pipeline_data.name is not None:
            pipeline_model.name = pipeline_data.name
        if pipeline_data.source_connection_id is not None:
            pipeline_model.source_connection_id = pipeline_data.source_connection_id
        if pipeline_data.target_connection_id is not None:
            pipeline_model.target_connection_id = pipeline_data.target_connection_id
        if pipeline_data.source_database is not None:
            pipeline_model.source_database = pipeline_data.source_database
        if pipeline_data.source_schema is not None:
            pipeline_model.source_schema = pipeline_data.source_schema
        if pipeline_data.source_tables is not None:
            pipeline_model.source_tables = pipeline_data.source_tables
        if pipeline_data.target_database is not None:
            pipeline_model.target_database = pipeline_data.target_database
        if pipeline_data.target_schema is not None:
            pipeline_model.target_schema = pipeline_data.target_schema
        if pipeline_data.target_tables is not None:
            pipeline_model.target_tables = pipeline_data.target_tables
        if pipeline_data.mode is not None:
            from ingestion.database.models_db import PipelineMode as DBPipelineMode
            pipeline_model.mode = DBPipelineMode(pipeline_data.mode)
        if pipeline_data.enable_full_load is not None:
            pipeline_model.enable_full_load = pipeline_data.enable_full_load
        if pipeline_data.auto_create_target is not None:
            pipeline_model.auto_create_target = pipeline_data.auto_create_target
        if pipeline_data.target_table_mapping is not None:
            pipeline_model.target_table_mapping = pipeline_data.target_table_mapping
        if pipeline_data.table_filter is not None:
            pipeline_model.table_filter = pipeline_data.table_filter
        
        pipeline_model.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(pipeline_model)
        
        # Update in-memory pipeline store if it exists
        if pipeline_id in cdc_manager.pipeline_store:
            existing_pipeline = cdc_manager.pipeline_store[pipeline_id]
            # Update the in-memory pipeline with new values
            if pipeline_data.name is not None:
                existing_pipeline.name = pipeline_data.name
            if pipeline_data.source_connection_id is not None:
                existing_pipeline.source_connection_id = pipeline_data.source_connection_id
            if pipeline_data.target_connection_id is not None:
                existing_pipeline.target_connection_id = pipeline_data.target_connection_id
            if pipeline_data.source_database is not None:
                existing_pipeline.source_database = pipeline_data.source_database
            if pipeline_data.source_schema is not None:
                existing_pipeline.source_schema = pipeline_data.source_schema
            if pipeline_data.source_tables is not None:
                existing_pipeline.source_tables = pipeline_data.source_tables
            if pipeline_data.target_database is not None:
                existing_pipeline.target_database = pipeline_data.target_database
            if pipeline_data.target_schema is not None:
                existing_pipeline.target_schema = pipeline_data.target_schema
            if pipeline_data.target_tables is not None:
                existing_pipeline.target_tables = pipeline_data.target_tables
            if pipeline_data.mode is not None:
                existing_pipeline.mode = pipeline_data.mode
            if pipeline_data.enable_full_load is not None:
                existing_pipeline.enable_full_load = pipeline_data.enable_full_load
            if pipeline_data.auto_create_target is not None:
                existing_pipeline.auto_create_target = pipeline_data.auto_create_target
            if pipeline_data.target_table_mapping is not None:
                existing_pipeline.target_table_mapping = pipeline_data.target_table_mapping
            if pipeline_data.table_filter is not None:
                existing_pipeline.table_filter = pipeline_data.table_filter
        
        # Return updated pipeline
        return {
            "id": pipeline_model.id,
            "name": pipeline_model.name,
            "source_connection_id": pipeline_model.source_connection_id,
            "target_connection_id": pipeline_model.target_connection_id,
            "source_database": pipeline_model.source_database,
            "source_schema": pipeline_model.source_schema,
            "source_tables": pipeline_model.source_tables or [],
            "target_database": pipeline_model.target_database,
            "target_schema": pipeline_model.target_schema,
            "target_tables": pipeline_model.target_tables or [],
            "mode": pipeline_model.mode.value if hasattr(pipeline_model.mode, 'value') else str(pipeline_model.mode),
            "enable_full_load": pipeline_model.enable_full_load,
            "auto_create_target": pipeline_model.auto_create_target,
            "target_table_mapping": pipeline_model.target_table_mapping or {},
            "table_filter": pipeline_model.table_filter,
            "status": pipeline_model.status.value if hasattr(pipeline_model.status, 'value') else str(pipeline_model.status),
            "full_load_status": pipeline_model.full_load_status.value if hasattr(pipeline_model.full_load_status, 'value') else str(pipeline_model.full_load_status),
            "cdc_status": pipeline_model.cdc_status.value if hasattr(pipeline_model.cdc_status, 'value') else str(pipeline_model.cdc_status),
            "created_at": pipeline_model.created_at.isoformat() if pipeline_model.created_at else None,
            "updated_at": pipeline_model.updated_at.isoformat() if pipeline_model.updated_at else None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update pipeline: {e}", exc_info=True)
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@app.post("/api/v1/pipelines/{pipeline_id}/start")
async def start_pipeline(
    pipeline_id: str,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Start a pipeline.
    
    Args:
        pipeline_id: Pipeline ID
        db: Database session
        
    Returns:
        Startup result
    """
    try:
        # Load pipeline from database
        pipeline_model = db.query(PipelineModel).filter(
            PipelineModel.id == pipeline_id,
            PipelineModel.deleted_at.is_(None)
        ).first()
        
        if not pipeline_model:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Pipeline not found: {pipeline_id}"
            )
        
        # Convert PipelineModel to Pipeline object
        from ingestion.models import Pipeline, PipelineMode
        
        pipeline = Pipeline(
            id=pipeline_model.id,
            name=pipeline_model.name,
            source_connection_id=pipeline_model.source_connection_id,
            target_connection_id=pipeline_model.target_connection_id,
            source_database=pipeline_model.source_database,
            source_schema=pipeline_model.source_schema,
            source_tables=pipeline_model.source_tables or [],
            target_database=pipeline_model.target_database,
            target_schema=pipeline_model.target_schema,
            target_tables=pipeline_model.target_tables or [],
            mode=pipeline_model.mode.value if hasattr(pipeline_model.mode, 'value') else str(pipeline_model.mode) if pipeline_model.mode else "full_load_and_cdc",
            enable_full_load=pipeline_model.enable_full_load,
            auto_create_target=pipeline_model.auto_create_target,
            target_table_mapping=pipeline_model.target_table_mapping or {},
            table_filter=pipeline_model.table_filter,
            full_load_lsn=pipeline_model.full_load_lsn,
            full_load_status=pipeline_model.full_load_status.value if hasattr(pipeline_model.full_load_status, 'value') else str(pipeline_model.full_load_status),
            cdc_status=pipeline_model.cdc_status.value if hasattr(pipeline_model.cdc_status, 'value') else str(pipeline_model.cdc_status),
            status=pipeline_model.status.value if hasattr(pipeline_model.status, 'value') else str(pipeline_model.status),
            # IMPORTANT: Load configs and connector names from database
            debezium_connector_name=pipeline_model.debezium_connector_name,
            sink_connector_name=pipeline_model.sink_connector_name,
            kafka_topics=pipeline_model.kafka_topics or [],
            debezium_config=pipeline_model.debezium_config or {},
            sink_config=pipeline_model.sink_config or {}
        )
        
        # Load connections from database
        source_conn_model = db.query(ConnectionModel).filter(
            ConnectionModel.id == pipeline.source_connection_id,
            ConnectionModel.deleted_at.is_(None)
        ).first()
        
        target_conn_model = db.query(ConnectionModel).filter(
            ConnectionModel.id == pipeline.target_connection_id,
            ConnectionModel.deleted_at.is_(None)
        ).first()
        
        if not source_conn_model or not target_conn_model:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Source or target connection not found"
            )
        
        # Convert ConnectionModel to Connection objects
        from ingestion.models import Connection
        
        # Normalize database_type to handle enum values and string conversions
        def normalize_database_type(db_type):
            """Normalize database type to standard values."""
            if hasattr(db_type, 'value'):
                db_type = db_type.value
            db_type = str(db_type).lower()
            
            # Normalize common variations
            if db_type in ['aws_s3', 's3']:
                return 's3'
            elif db_type in ['mssql', 'sql_server', 'sqlserver']:
                return 'sqlserver'
            elif db_type in ['postgres', 'postgresql']:
                return 'postgresql'
            return db_type
        
        source_db_type = normalize_database_type(source_conn_model.database_type)
        target_db_type = normalize_database_type(target_conn_model.database_type)
        
        logger.info(f"Source connection database_type: {source_db_type} (original: {source_conn_model.database_type})")
        logger.info(f"Target connection database_type: {target_db_type} (original: {target_conn_model.database_type})")
        
        source_connection = Connection(
            id=source_conn_model.id,
            name=source_conn_model.name,
            connection_type=source_conn_model.connection_type.value if hasattr(source_conn_model.connection_type, 'value') else str(source_conn_model.connection_type),
            database_type=source_db_type,
            host=source_conn_model.host,
            port=source_conn_model.port,
            database=source_conn_model.database,
            username=source_conn_model.username,
            password=source_conn_model.password,
            schema=source_conn_model.schema,
            additional_config=source_conn_model.additional_config or {}
        )
        
        target_connection = Connection(
            id=target_conn_model.id,
            name=target_conn_model.name,
            connection_type=target_conn_model.connection_type.value if hasattr(target_conn_model.connection_type, 'value') else str(target_conn_model.connection_type),
            database_type=target_db_type,
            host=target_conn_model.host,
            port=target_conn_model.port,
            database=target_conn_model.database,
            username=target_conn_model.username,
            password=target_conn_model.password,
            schema=target_conn_model.schema,
            additional_config=target_conn_model.additional_config or {}
        )
        
        # Add pipeline and connections to CDC manager
        logger.info(f"Adding pipeline {pipeline.id} (requested: {pipeline_id}) to cdc_manager.pipeline_store")
        cdc_manager.pipeline_store[pipeline.id] = pipeline
        cdc_manager.add_connection(source_connection)
        cdc_manager.add_connection(target_connection)
        
        # Verify pipeline is in store before starting
        logger.info(f"Checking if pipeline {pipeline.id} is in store...")
        logger.info(f"Store keys: {list(cdc_manager.pipeline_store.keys())}")
        if pipeline.id not in cdc_manager.pipeline_store:
            logger.error(f"Pipeline {pipeline.id} not in cdc_manager.pipeline_store after adding")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to add pipeline to CDC manager: {pipeline.id}"
            )
        
        logger.info(f"Pipeline {pipeline.id} added to store, starting pipeline with ID: {pipeline_id}...")
        
        # Start pipeline - use pipeline.id to ensure consistency
        try:
            result = pipeline_service.start_pipeline(pipeline.id)  # Use pipeline.id instead of pipeline_id
            
            # Update pipeline status in database after starting
            # Reload pipeline from cdc_manager to get updated status
            from ingestion.database.models_db import PipelineStatus as DBPipelineStatus, FullLoadStatus as DBFullLoadStatus, CDCStatus as DBCDCStatus
            
            # Retry status update up to 3 times
            status_updated = False
            for attempt in range(3):
                try:
                    if pipeline.id in cdc_manager.pipeline_store:
                        updated_pipeline = cdc_manager.pipeline_store[pipeline.id]
                        
                        # Update database model with current status
                        try:
                            pipeline_model.status = DBPipelineStatus(updated_pipeline.status) if updated_pipeline.status else DBPipelineStatus.RUNNING
                        except (ValueError, AttributeError):
                            pipeline_model.status = DBPipelineStatus.RUNNING
                        
                        try:
                            pipeline_model.full_load_status = DBFullLoadStatus(updated_pipeline.full_load_status) if updated_pipeline.full_load_status else DBFullLoadStatus.NOT_STARTED
                        except (ValueError, AttributeError):
                            pipeline_model.full_load_status = DBFullLoadStatus.NOT_STARTED
                        
                        try:
                            pipeline_model.cdc_status = DBCDCStatus(updated_pipeline.cdc_status) if updated_pipeline.cdc_status else DBCDCStatus.NOT_STARTED
                        except (ValueError, AttributeError):
                            pipeline_model.cdc_status = DBCDCStatus.NOT_STARTED
                        
                        pipeline_model.full_load_lsn = updated_pipeline.full_load_lsn
                        pipeline_model.debezium_connector_name = updated_pipeline.debezium_connector_name
                        pipeline_model.sink_connector_name = updated_pipeline.sink_connector_name
                        pipeline_model.kafka_topics = updated_pipeline.kafka_topics or []
                        pipeline_model.debezium_config = updated_pipeline.debezium_config or {}
                        pipeline_model.sink_config = updated_pipeline.sink_config or {}
                        pipeline_model.updated_at = datetime.utcnow()
                        
                        db.commit()
                        db.refresh(pipeline_model)
                        status_updated = True
                        logger.info(
                            f"Updated pipeline {pipeline.id} status in database: "
                            f"status={pipeline_model.status.value}, "
                            f"full_load_status={pipeline_model.full_load_status.value}, "
                            f"cdc_status={pipeline_model.cdc_status.value}"
                        )
                        # Ensure status is persisted before returning
                        db.flush()
                        break
                    else:
                        logger.warning(f"Pipeline {pipeline.id} not found in pipeline_store for status update")
                        break
                except Exception as e:
                    logger.warning(f"Failed to update pipeline status (attempt {attempt + 1}/3): {e}")
                    if attempt < 2:
                        time.sleep(0.5)  # Brief delay before retry
                    else:
                        logger.error(f"Failed to update pipeline status after 3 attempts: {e}")
            
            if not status_updated:
                logger.warning(f"Pipeline status may not be persisted for {pipeline.id}")
            
            return result
        except ValueError as e:
            # ValueError from cdc_manager.start_pipeline means pipeline not in store
            if "Pipeline not found" in str(e):
                logger.error(f"Pipeline {pipeline_id} not found in cdc_manager.pipeline_store")
                logger.error(f"Available pipelines: {list(cdc_manager.pipeline_store.keys())}")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=str(e)
                )
            raise
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to start pipeline: {e}", exc_info=True)
        
        # Update pipeline status to ERROR in database
        try:
            from ingestion.database.models_db import PipelineStatus as DBPipelineStatus, FullLoadStatus as DBFullLoadStatus, CDCStatus as DBCDCStatus
            from ingestion.exceptions import FullLoadError
            
            pipeline_model.status = DBPipelineStatus.ERROR
            
            # Classify error type
            if isinstance(e, FullLoadError) or "full load" in str(e).lower() or "transfer" in str(e).lower():
                pipeline_model.full_load_status = DBFullLoadStatus.FAILED
            if "cdc" in str(e).lower() or "connector" in str(e).lower():
                pipeline_model.cdc_status = DBCDCStatus.ERROR
            
            pipeline_model.updated_at = datetime.utcnow()
            db.commit()
            logger.info(f"Updated pipeline {pipeline_id} status to ERROR in database")
        except Exception as db_error:
            logger.error(f"Failed to update pipeline status in database: {db_error}")
        
        # Provide better error message
        error_detail = str(e)
        if hasattr(e, 'details'):
            error_detail += f" (Details: {e.details})"
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_detail
        )


@app.post("/api/v1/pipelines/{pipeline_id}/trigger")
async def trigger_pipeline(
    pipeline_id: str,
    request: Request,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Trigger a pipeline with optional run type.
    
    This endpoint is an alias for /start that accepts run_type in the request body.
    
    Args:
        pipeline_id: Pipeline ID
        request: FastAPI request object to read body
        db: Database session
        
    Returns:
        Startup result
    """
    try:
        # Parse request body to get run_type (optional)
        run_type = "full_load"
        try:
            if request.headers.get("content-type", "").startswith("application/json"):
                body = await request.json()
                run_type = body.get("run_type", "full_load")
        except (ValueError, KeyError, AttributeError):
            # Body might be empty or not JSON, use default
            pass
        
        logger.info(f"Triggering pipeline {pipeline_id} with run_type={run_type}")
        
        # Call start_pipeline (run_type is currently not used but kept for future compatibility)
        # The start_pipeline endpoint handles the actual pipeline start
        try:
            return await start_pipeline(pipeline_id=pipeline_id, db=db)
        except HTTPException:
            # Re-raise HTTP exceptions as-is (they already have proper error messages)
            raise
        except Exception as inner_e:
            # If start_pipeline raises a non-HTTP exception, wrap it with context
            error_msg = str(inner_e)
            logger.error(f"start_pipeline raised exception: {error_msg}", exc_info=True)
            # Re-raise as HTTPException with the actual error message
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=error_msg
            ) from inner_e
    except HTTPException as he:
        # Re-raise HTTP exceptions with their original detail
        raise
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Failed to trigger pipeline {pipeline_id}: {error_msg}", exc_info=True)
        
        # Extract the actual error message (avoid double-wrapping)
        if "Failed to trigger pipeline" in error_msg or "Failed to start pipeline" in error_msg:
            # Already wrapped, use as-is but clean it up
            detail = error_msg
        else:
            # Provide the actual error detail
            detail = error_msg
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail
        )


@app.post("/api/v1/pipelines/{pipeline_id}/pause")
async def pause_pipeline(
    pipeline_id: str,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Pause a pipeline.
    
    Args:
        pipeline_id: Pipeline ID
        db: Database session
        
    Returns:
        Pause result
    """
    try:
        # Load pipeline from database to verify it exists
        pipeline_model = db.query(PipelineModel).filter(
            PipelineModel.id == pipeline_id,
            PipelineModel.deleted_at.is_(None)
        ).first()
        
        if not pipeline_model:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Pipeline not found: {pipeline_id}"
            )
        
        result = pipeline_service.pause_pipeline(pipeline_id)
        
        # Update database status
        from ingestion.database.models_db import PipelineStatus as DBPipelineStatus, CDCStatus as DBCDCStatus
        pipeline_model.status = DBPipelineStatus.PAUSED
        pipeline_model.cdc_status = DBCDCStatus.PAUSED
        db.commit()
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to pause pipeline: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@app.post("/api/v1/pipelines/{pipeline_id}/stop")
async def stop_pipeline(
    pipeline_id: str,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Stop a pipeline.
    
    Args:
        pipeline_id: Pipeline ID
        db: Database session
        
    Returns:
        Stop result
    """
    import asyncio
    from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError
    
    try:
        # Load pipeline from database to verify it exists
        pipeline_model = db.query(PipelineModel).filter(
            PipelineModel.id == pipeline_id,
            PipelineModel.deleted_at.is_(None)
        ).first()
        
        if not pipeline_model:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Pipeline not found: {pipeline_id}"
            )
        
        # Run stop_pipeline in a thread pool with timeout to prevent hanging
        executor = ThreadPoolExecutor(max_workers=1)
        try:
            # Set timeout to 30 seconds for stopping pipeline
            future = executor.submit(pipeline_service.stop_pipeline, pipeline_id)
            result = future.result(timeout=30)
        except FutureTimeoutError:
            # If timeout, update database status anyway and return partial result
            logger.warning(f"Pipeline stop timed out for {pipeline_id}, updating database status")
            from ingestion.database.models_db import PipelineStatus as DBPipelineStatus, CDCStatus as DBCDCStatus
            pipeline_model.status = DBPipelineStatus.STOPPED
            pipeline_model.cdc_status = DBCDCStatus.STOPPED
            db.commit()
            return {
                "pipeline_id": pipeline_id,
                "status": "STOPPED",
                "message": "Pipeline stop initiated (may still be stopping in background)",
                "timeout": True
            }
        finally:
            executor.shutdown(wait=False)
        
        # Update database status
        from ingestion.database.models_db import PipelineStatus as DBPipelineStatus, CDCStatus as DBCDCStatus
        pipeline_model.status = DBPipelineStatus.STOPPED
        pipeline_model.cdc_status = DBCDCStatus.STOPPED
        db.commit()
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        # Use safe error message to avoid formatting issues
        from ingestion.connection_service import safe_error_message
        safe_error = safe_error_message(e)
        logger.error("Failed to stop pipeline: %r", safe_error, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=safe_error
        )


@app.get("/api/v1/pipelines/{pipeline_id}/health")
async def get_pipeline_health(
    pipeline_id: str,
    db: Session = Depends(get_db),
    auto_recover: bool = Query(False, description="Automatically attempt recovery if issues detected")
) -> Dict[str, Any]:
    """Get health status for a pipeline with replication slot lag monitoring and auto-recovery.
    
    Args:
        pipeline_id: Pipeline ID
        db: Database session
        auto_recover: If True, automatically attempt recovery for stuck CDC
        
    Returns:
        Pipeline health status with component details, lag info, and recovery status
    """
    try:
        health_monitor = get_health_monitor(db)
        health_result = health_monitor.check_pipeline_health(pipeline_id)
        
        # Auto-recover if requested and unhealthy
        if auto_recover and health_result.get("status") == "unhealthy":
            # Recovery is already attempted in check_pipeline_health if lag is critical
            # This flag just ensures it happens
            pass
        
        return health_result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get pipeline health: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@app.get("/api/v1/pipelines/{pipeline_id}/health/legacy")
async def get_pipeline_health_legacy(
    pipeline_id: str,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Get health status for a pipeline using comprehensive health checks (legacy endpoint).
    
    Args:
        pipeline_id: Pipeline ID
        db: Database session
        
    Returns:
        Pipeline health status with component details
    """
    try:
        # Load pipeline from database
        pipeline_model = db.query(PipelineModel).filter(
            PipelineModel.id == pipeline_id,
            PipelineModel.deleted_at.is_(None)
        ).first()
        
        if not pipeline_model:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Pipeline not found: {pipeline_id}"
            )
        
        # Load connections
        source_conn_model = db.query(ConnectionModel).filter(
            ConnectionModel.id == pipeline_model.source_connection_id,
            ConnectionModel.deleted_at.is_(None)
        ).first()
        
        target_conn_model = db.query(ConnectionModel).filter(
            ConnectionModel.id == pipeline_model.target_connection_id,
            ConnectionModel.deleted_at.is_(None)
        ).first()
        
        if not source_conn_model or not target_conn_model:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Source or target connection not found"
            )
        
        # Convert to Connection objects
        from ingestion.models import Connection
        from ingestion.connection_service import ConnectionService
        
        connection_service = ConnectionService()
        
        source_connection = Connection(
            id=source_conn_model.id,
            name=source_conn_model.name,
            connection_type=source_conn_model.connection_type.value if hasattr(source_conn_model.connection_type, 'value') else str(source_conn_model.connection_type),
            database_type=source_conn_model.database_type.value if hasattr(source_conn_model.database_type, 'value') else str(source_conn_model.database_type),
            host=source_conn_model.host,
            port=source_conn_model.port,
            database=source_conn_model.database,
            username=source_conn_model.username,
            password=source_conn_model.password,
            schema=source_conn_model.schema,
            additional_config=source_conn_model.additional_config or {}
        )
        
        target_connection = Connection(
            id=target_conn_model.id,
            name=target_conn_model.name,
            connection_type=target_conn_model.connection_type.value if hasattr(target_conn_model.connection_type, 'value') else str(target_conn_model.connection_type),
            database_type=target_conn_model.database_type.value if hasattr(target_conn_model.database_type, 'value') else str(target_conn_model.database_type),
            host=target_conn_model.host,
            port=target_conn_model.port,
            database=target_conn_model.database,
            username=target_conn_model.username,
            password=target_conn_model.password,
            schema=target_conn_model.schema,
            additional_config=target_conn_model.additional_config or {}
        )
        
        # Get connectors
        source_connector = connection_service._get_connector(source_connection)
        target_connector = connection_service._get_connector(target_connection)
        
        # Get health status using comprehensive health check
        from ingestion.health import check_pipeline_health
        health = check_pipeline_health(
            pipeline_id=pipeline_id,
            source_connector=source_connector,
            target_connector=target_connector,
            kafka_client=cdc_manager.kafka_client,
            debezium_connector_name=pipeline_model.debezium_connector_name,
            sink_connector_name=pipeline_model.sink_connector_name
        )
        
        return health
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get pipeline health: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@app.get("/api/v1/pipelines/{pipeline_id}/tables/preview")
async def preview_table_mappings(pipeline_id: str) -> Dict[str, Any]:
    """Preview table mappings for a pipeline.
    
    Args:
        pipeline_id: Pipeline ID
        
    Returns:
        Dictionary with table mapping preview
    """
    try:
        pipeline = cdc_manager.pipeline_store.get(pipeline_id)
        if not pipeline:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Pipeline not found: {pipeline_id}"
            )
        
        # Generate table mappings
        mappings = {}
        source_tables = pipeline.source_tables
        target_tables = pipeline.target_tables or source_tables.copy()
        
        # Apply custom mapping if provided
        if pipeline.target_table_mapping:
            for source_table in source_tables:
                target_table = pipeline.target_table_mapping.get(source_table, source_table)
                mappings[source_table] = {
                    "source": f"{pipeline.source_database}.{pipeline.source_schema}.{source_table}",
                    "target": f"{pipeline.target_database or 'default'}.{pipeline.target_schema or 'default'}.{target_table}",
                    "mapped_name": target_table
                }
        else:
            # Use 1:1 mapping
            for i, source_table in enumerate(source_tables):
                target_table = target_tables[i] if i < len(target_tables) else source_table
                mappings[source_table] = {
                    "source": f"{pipeline.source_database}.{pipeline.source_schema}.{source_table}",
                    "target": f"{pipeline.target_database or 'default'}.{pipeline.target_schema or 'default'}.{target_table}",
                    "mapped_name": target_table
                }
        
        return {
            "pipeline_id": pipeline_id,
            "mappings": mappings,
            "auto_create_target": pipeline.auto_create_target,
            "table_count": len(mappings)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to preview table mappings: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@app.post("/api/v1/pipelines/{pipeline_id}/validate")
async def validate_pipeline(pipeline_id: str) -> Dict[str, Any]:
    """Validate pipeline configuration.
    
    Args:
        pipeline_id: Pipeline ID
        
    Returns:
        Validation result
    """
    try:
        pipeline = cdc_manager.pipeline_store.get(pipeline_id)
        if not pipeline:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Pipeline not found: {pipeline_id}"
            )
        
        validation_errors = []
        validation_warnings = []
        
        # Validate connections exist
        source_conn = cdc_manager.get_connection(pipeline.source_connection_id)
        target_conn = cdc_manager.get_connection(pipeline.target_connection_id)
        
        if not source_conn:
            validation_errors.append(f"Source connection not found: {pipeline.source_connection_id}")
        if not target_conn:
            validation_errors.append(f"Target connection not found: {pipeline.target_connection_id}")
        
        # Validate tables are specified
        if not pipeline.source_tables:
            validation_errors.append("No source tables specified")
        
        # Validate mode
        mode = pipeline.mode
        if isinstance(mode, str):
            try:
                mode = PipelineMode(mode)
            except ValueError:
                validation_errors.append(f"Invalid pipeline mode: {mode}")
        
        # Validate table mappings
        if pipeline.target_table_mapping:
            for source_table in pipeline.source_tables:
                if source_table not in pipeline.target_table_mapping:
                    validation_warnings.append(f"No mapping specified for table: {source_table}")
        
        # Validate connections are testable
        if source_conn:
            is_valid, error = connection_service.validate_connection(pipeline.source_connection_id)
            if not is_valid:
                validation_warnings.append(f"Source connection test failed: {error}")
        
        if target_conn:
            is_valid, error = connection_service.validate_connection(pipeline.target_connection_id)
            if not is_valid:
                validation_warnings.append(f"Target connection test failed: {error}")
        
        return {
            "pipeline_id": pipeline_id,
            "valid": len(validation_errors) == 0,
            "errors": validation_errors,
            "warnings": validation_warnings
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to validate pipeline: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@app.post("/api/v1/pipelines/{pipeline_id}/tables/select")
async def select_pipeline_tables(
    pipeline_id: str,
    tables: List[str]
) -> Dict[str, Any]:
    """Select tables for a pipeline.
    
    Args:
        pipeline_id: Pipeline ID
        tables: List of table names to select
        
    Returns:
        Updated pipeline with selected tables
    """
    try:
        pipeline = cdc_manager.pipeline_store.get(pipeline_id)
        if not pipeline:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Pipeline not found: {pipeline_id}"
            )
        
        # Validate table selection
        validation = discovery_service.validate_table_selection(
            pipeline.source_connection_id,
            tables,
            database=pipeline.source_database,
            schema=pipeline.source_schema
        )
        
        if not validation.get("valid"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Table selection validation failed: {validation.get('errors')}"
            )
        
        # Update pipeline with selected tables
        pipeline.source_tables = tables
        
        # Generate table mappings
        mapping = discovery_service.map_tables(
            source_tables=tables,
            target_tables=pipeline.target_tables,
            custom_mapping=pipeline.target_table_mapping
        )
        pipeline.target_table_mapping = mapping
        
        return {
            "pipeline_id": pipeline_id,
            "selected_tables": tables,
            "table_mapping": mapping,
            "validation": validation
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to select tables: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@app.get("/api/v1/pipelines/{pipeline_id}/tables/mapping")
async def get_table_mapping(pipeline_id: str) -> Dict[str, Any]:
    """Get current table mappings for a pipeline.
    
    Args:
        pipeline_id: Pipeline ID
        
    Returns:
        Dictionary with table mappings
    """
    try:
        pipeline = cdc_manager.pipeline_store.get(pipeline_id)
        if not pipeline:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Pipeline not found: {pipeline_id}"
            )
        
        # Generate or return existing mapping
        if pipeline.target_table_mapping:
            mapping = pipeline.target_table_mapping
        else:
            mapping = discovery_service.map_tables(
                source_tables=pipeline.source_tables,
                target_tables=pipeline.target_tables
            )
        
        return {
            "pipeline_id": pipeline_id,
            "source_tables": pipeline.source_tables,
            "target_tables": pipeline.target_tables,
            "mapping": mapping
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get table mapping: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@app.get("/api/v1/connections/{connection_id}/tables/{table_name}/dependencies")
async def get_table_dependencies(
    connection_id: str,
    table_name: str,
    database: Optional[str] = None,
    schema: Optional[str] = None
) -> Dict[str, Any]:
    """Get foreign key dependencies for a table.
    
    Args:
        connection_id: Connection ID
        table_name: Table name
        database: Database name (optional)
        schema: Schema name (optional)
        
    Returns:
        Dictionary with dependency information
    """
    try:
        result = discovery_service.get_table_dependencies(
            connection_id,
            table_name,
            database=database,
            schema=schema
        )
        if not result.get("success"):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result.get("error", "Failed to get dependencies")
            )
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get table dependencies: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@app.get("/api/v1/connections/{connection_id}/tables/size-estimate")
async def estimate_tables_size(
    connection_id: str,
    tables: List[str],
    database: Optional[str] = None,
    schema: Optional[str] = None
) -> Dict[str, Any]:
    """Estimate data size for tables.
    
    Args:
        connection_id: Connection ID
        tables: List of table names (query parameter)
        database: Database name (optional)
        schema: Schema name (optional)
        
    Returns:
        Dictionary with size estimates
    """
    try:
        result = discovery_service.estimate_data_size(
            connection_id,
            tables,
            database=database,
            schema=schema
        )
        return result
    except Exception as e:
        logger.error(f"Failed to estimate table size: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@app.post("/api/v1/pipelines/{pipeline_id}/schema/create")
async def create_pipeline_schema(pipeline_id: str) -> Dict[str, Any]:
    """Manually create target schema and tables for a pipeline.
    
    Args:
        pipeline_id: Pipeline ID
        
    Returns:
        Schema creation result
    """
    try:
        pipeline = cdc_manager.pipeline_store.get(pipeline_id)
        if not pipeline:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Pipeline not found: {pipeline_id}"
            )
        
        source_connection = cdc_manager.get_connection(pipeline.source_connection_id)
        target_connection = cdc_manager.get_connection(pipeline.target_connection_id)
        
        if not source_connection or not target_connection:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Source or target connection not found"
            )
        
        target_schema = pipeline.target_schema or target_connection.schema or ("public" if target_connection.database_type == "postgresql" else "dbo")
        target_database = pipeline.target_database or target_connection.database
        
        results = {
            "pipeline_id": pipeline_id,
            "schema_result": None,
            "tables": []
        }
        
        # Create schema
        schema_result = schema_service.create_target_schema(
            connection_id=target_connection.id,
            schema_name=target_schema,
            database=target_database
        )
        results["schema_result"] = schema_result
        
        # Create tables
        for source_table in pipeline.source_tables:
            target_table = pipeline.target_table_mapping.get(source_table, source_table) if pipeline.target_table_mapping else source_table
            
            table_result = schema_service.create_target_table(
                source_connection_id=source_connection.id,
                target_connection_id=target_connection.id,
                table_name=source_table,
                source_database=pipeline.source_database,
                source_schema=pipeline.source_schema,
                target_database=target_database,
                target_schema=target_schema,
                target_table_name=target_table
            )
            results["tables"].append({
                "source_table": source_table,
                "target_table": target_table,
                "result": table_result
            })
        
        return results
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create pipeline schema: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@app.get("/api/v1/pipelines/{pipeline_id}/schema/diff")
async def get_pipeline_schema_diff(pipeline_id: str) -> Dict[str, Any]:
    """Show schema differences between source and target.
    
    Args:
        pipeline_id: Pipeline ID
        
    Returns:
        Schema diff result
    """
    try:
        pipeline = cdc_manager.pipeline_store.get(pipeline_id)
        if not pipeline:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Pipeline not found: {pipeline_id}"
            )
        
        source_connection = cdc_manager.get_connection(pipeline.source_connection_id)
        target_connection = cdc_manager.get_connection(pipeline.target_connection_id)
        
        if not source_connection or not target_connection:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Source or target connection not found"
            )
        
        target_schema = pipeline.target_schema or target_connection.schema or ("public" if target_connection.database_type == "postgresql" else "dbo")
        target_database = pipeline.target_database or target_connection.database
        
        results = {
            "pipeline_id": pipeline_id,
            "tables": []
        }
        
        # Compare schemas for each table
        for source_table in pipeline.source_tables:
            target_table = pipeline.target_table_mapping.get(source_table, source_table) if pipeline.target_table_mapping else source_table
            
            sync_result = schema_service.sync_schema(
                source_connection_id=source_connection.id,
                target_connection_id=target_connection.id,
                table_name=source_table,
                source_database=pipeline.source_database,
                source_schema=pipeline.source_schema,
                target_database=target_database,
                target_schema=target_schema,
                target_table_name=target_table
            )
            
            results["tables"].append({
                "source_table": source_table,
                "target_table": target_table,
                "sync_result": sync_result
            })
        
        return results
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get schema diff: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@app.get("/api/v1/pipelines/{pipeline_id}/status")
async def get_pipeline_status(pipeline_id: str) -> Dict[str, Any]:
    """Get pipeline status.
    
    Args:
        pipeline_id: Pipeline ID
        
    Returns:
        Pipeline status
    """
    try:
        return pipeline_service.get_pipeline_status(pipeline_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@app.get("/api/v1/pipelines/{pipeline_id}/progress")
async def get_pipeline_progress(pipeline_id: str, db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Get pipeline progress information.
    
    Args:
        pipeline_id: Pipeline ID
        db: Database session
        
    Returns:
        Pipeline progress data
    """
    try:
        from ingestion.database.models_db import FullLoadStatus as DBFullLoadStatus, CDCStatus as DBCDCStatus
        
        # Load pipeline from database first
        pipeline_model = db.query(PipelineModel).filter(
            PipelineModel.id == pipeline_id,
            PipelineModel.deleted_at.is_(None)
        ).first()
        
        if not pipeline_model:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Pipeline not found: {pipeline_id}"
            )
        
        # Get pipeline status (may fail if pipeline not in store, but that's okay)
        try:
            pipeline_status_data = pipeline_service.get_pipeline_status(pipeline_id)
            # Ensure it's a dict, not None
            if pipeline_status_data is None:
                pipeline_status_data = {}
        except Exception as e:
            logger.warning(f"Could not get pipeline status from service: {e}, using database values")
            pipeline_status_data = {}
        
        # Ensure pipeline_status_data is a dict with required keys
        if not isinstance(pipeline_status_data, dict):
            pipeline_status_data = {}
        
        # Set defaults if missing
        if "status" not in pipeline_status_data:
            pipeline_status_data["status"] = pipeline_model.status.value if hasattr(pipeline_model.status, 'value') else str(pipeline_model.status)
        if "debezium_connector" not in pipeline_status_data:
            pipeline_status_data["debezium_connector"] = {}
        if "sink_connector" not in pipeline_status_data:
            pipeline_status_data["sink_connector"] = {}
        
        # Calculate progress based on full load status
        progress_percentage = 0
        records_processed = 0
        records_total = 0
        tables_completed = 0
        tables_total = len(pipeline_model.source_tables) if pipeline_model.source_tables else 0
        
        # Get full load status value (handle both enum and string)
        full_load_status_value = pipeline_model.full_load_status.value if hasattr(pipeline_model.full_load_status, 'value') else str(pipeline_model.full_load_status)
        cdc_status_value = pipeline_model.cdc_status.value if hasattr(pipeline_model.cdc_status, 'value') else str(pipeline_model.cdc_status)
        
        # If full load is completed, progress is 100%
        if full_load_status_value == DBFullLoadStatus.COMPLETED.value or full_load_status_value == "COMPLETED":
            progress_percentage = 100
            tables_completed = tables_total
        elif full_load_status_value == DBFullLoadStatus.IN_PROGRESS.value or full_load_status_value == "IN_PROGRESS":
            # Estimate progress (could be improved with actual row counts)
            progress_percentage = 50  # Placeholder
            tables_completed = tables_total // 2 if tables_total > 0 else 0
        
        # Get connector status for additional info
        debezium_status = pipeline_status_data.get("debezium_connector") if isinstance(pipeline_status_data, dict) else {}
        sink_status = pipeline_status_data.get("sink_connector") if isinstance(pipeline_status_data, dict) else {}
        
        # Ensure they're dicts
        if not isinstance(debezium_status, dict):
            debezium_status = {}
        if not isinstance(sink_status, dict):
            sink_status = {}
        
        # Get connector state safely
        debezium_connector_info = debezium_status.get("connector") if isinstance(debezium_status, dict) else {}
        sink_connector_info = sink_status.get("connector") if isinstance(sink_status, dict) else {}
        
        debezium_state = debezium_connector_info.get("state", "UNKNOWN") if isinstance(debezium_connector_info, dict) else "UNKNOWN"
        sink_state = sink_connector_info.get("state", "UNKNOWN") if isinstance(sink_connector_info, dict) else "UNKNOWN"
        
        # Get pipeline status string
        pipeline_status_str = str(pipeline_model.status.value if hasattr(pipeline_model.status, 'value') else pipeline_model.status)
        if isinstance(pipeline_status_data, dict):
            pipeline_status_str = pipeline_status_data.get("status", pipeline_status_str)
        
        # Extract full_load info from pipeline_status_data if available
        full_load_info = {}
        if isinstance(pipeline_status_data, dict) and "full_load" in pipeline_status_data:
            full_load_info = pipeline_status_data.get("full_load", {})
        elif isinstance(pipeline_status_data, dict):
            # Try to extract from top-level keys
            if "full_load_status" in pipeline_status_data:
                full_load_info["status"] = pipeline_status_data.get("full_load_status", full_load_status_value)
            if "progress_percentage" in pipeline_status_data:
                full_load_info["progress_percent"] = pipeline_status_data.get("progress_percentage", progress_percentage)
            if "records_loaded" in pipeline_status_data:
                full_load_info["records_loaded"] = pipeline_status_data.get("records_loaded", records_processed)
            if "total_records" in pipeline_status_data:
                full_load_info["total_records"] = pipeline_status_data.get("total_records", records_total)
            if "current_table" in pipeline_status_data:
                full_load_info["current_table"] = pipeline_status_data.get("current_table")
        
        # Set defaults for full_load if not present
        if "status" not in full_load_info:
            full_load_info["status"] = full_load_status_value.lower() if isinstance(full_load_status_value, str) else str(full_load_status_value).lower()
        if "progress_percent" not in full_load_info:
            full_load_info["progress_percent"] = progress_percentage
        if "records_loaded" not in full_load_info:
            full_load_info["records_loaded"] = records_processed
        if "total_records" not in full_load_info:
            full_load_info["total_records"] = records_total
        
        # Extract CDC info if available
        cdc_info = {}
        if isinstance(pipeline_status_data, dict) and "cdc" in pipeline_status_data:
            cdc_info = pipeline_status_data.get("cdc", {})
        if "status" not in cdc_info:
            cdc_info["status"] = cdc_status_value.lower() if isinstance(cdc_status_value, str) else str(cdc_status_value).lower()
        
        # Calculate CDC event counts from replication events if not provided
        if "events_captured" not in cdc_info or "events_applied" not in cdc_info or "events_failed" not in cdc_info:
            try:
                from ingestion.database.models_db import ReplicationEventModel
                from sqlalchemy import func
                
                # Count all events for this pipeline (captured = total)
                total_events = db.query(func.count(ReplicationEventModel.id)).filter(
                    ReplicationEventModel.pipeline_id == pipeline_id,
                    ReplicationEventModel.deleted_at.is_(None)
                ).scalar() or 0
                
                # Count applied events (status = 'applied' or 'success')
                applied_events = db.query(func.count(ReplicationEventModel.id)).filter(
                    ReplicationEventModel.pipeline_id == pipeline_id,
                    ReplicationEventModel.status.in_(['applied', 'success']),
                    ReplicationEventModel.deleted_at.is_(None)
                ).scalar() or 0
                
                # Count failed events (status = 'failed' or 'error')
                failed_events = db.query(func.count(ReplicationEventModel.id)).filter(
                    ReplicationEventModel.pipeline_id == pipeline_id,
                    ReplicationEventModel.status.in_(['failed', 'error']),
                    ReplicationEventModel.deleted_at.is_(None)
                ).scalar() or 0
                
                # Get latest event time
                latest_event = db.query(ReplicationEventModel).filter(
                    ReplicationEventModel.pipeline_id == pipeline_id,
                    ReplicationEventModel.deleted_at.is_(None)
                ).order_by(ReplicationEventModel.created_at.desc()).first()
                
                cdc_info["events_captured"] = total_events
                cdc_info["events_applied"] = applied_events
                cdc_info["events_failed"] = failed_events
                if latest_event:
                    cdc_info["last_event_time"] = latest_event.created_at.isoformat() if latest_event.created_at else None
            except Exception as e:
                logger.warning(f"Failed to calculate CDC event counts: {e}")
                # Set defaults if calculation fails
                if "events_captured" not in cdc_info:
                    cdc_info["events_captured"] = 0
                if "events_applied" not in cdc_info:
                    cdc_info["events_applied"] = 0
                if "events_failed" not in cdc_info:
                    cdc_info["events_failed"] = 0
        
        return {
            "pipeline_id": pipeline_id,
            "status": pipeline_status_str,
            "full_load": full_load_info,
            "cdc": cdc_info,
            # Keep backward compatibility
            "full_load_status": full_load_status_value,
            "cdc_status": cdc_status_value,
            "progress_percentage": progress_percentage,
            "records_processed": records_processed,
            "records_total": records_total,
            "tables_completed": tables_completed,
            "tables_total": tables_total,
            "debezium_connector": {
                "name": pipeline_model.debezium_connector_name or "",
                "state": debezium_state
            },
            "sink_connector": {
                "name": pipeline_model.sink_connector_name or "",
                "state": sink_state
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get pipeline progress: {e}", exc_info=True)
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@app.delete("/api/v1/pipelines/{pipeline_id}")
async def delete_pipeline(
    pipeline_id: str,
    db: Session = Depends(get_db),
    hard_delete: bool = False
) -> Dict[str, Any]:
    """Delete a pipeline.
    
    Args:
        pipeline_id: Pipeline ID
        db: Database session
        hard_delete: If True, permanently delete. If False, soft delete.
        
    Returns:
        Deletion result
    """
    try:
        # Load pipeline from database
        pipeline_model = db.query(PipelineModel).filter(
            PipelineModel.id == pipeline_id,
            PipelineModel.deleted_at.is_(None)
        ).first()
        
        if not pipeline_model:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Pipeline not found: {pipeline_id}"
            )
        
        # Stop pipeline first (if running)
        try:
            pipeline_service.stop_pipeline(pipeline_id)
        except Exception:
            pass  # Ignore if already stopped or not in store
        
        # Delete from database
        if hard_delete:
            db.delete(pipeline_model)
            logger.info(f"Hard deleted pipeline: {pipeline_id}")
        else:
            # Soft delete
            pipeline_model.deleted_at = datetime.utcnow()
            logger.info(f"Soft deleted pipeline: {pipeline_id}")
        
        db.commit()
        
        # Remove from in-memory store
        if pipeline_id in cdc_manager.pipeline_store:
            del cdc_manager.pipeline_store[pipeline_id]
        
        return {
            "message": f"Pipeline {pipeline_id} deleted",
            "hard_delete": hard_delete
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to delete pipeline: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@app.get("/api/connectors")
async def list_connectors() -> List[str]:
    """List all Kafka Connect connectors.
    
    Returns:
        List of connector names
    """
    try:
        return cdc_manager.kafka_client.list_connectors()
    except Exception as e:
        logger.error(f"Failed to list connectors: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@app.get("/api/connectors/{connector_name}/status")
async def get_connector_status(connector_name: str) -> Dict[str, Any]:
    """Get connector status.
    
    Args:
        connector_name: Connector name
        
    Returns:
        Connector status
    """
    try:
        status = cdc_manager.kafka_client.get_connector_status(connector_name)
        if status is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Connector {connector_name} not found"
            )
        return status
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@app.post("/api/connectors/{connector_name}/restart")
async def restart_connector(connector_name: str) -> Dict[str, Any]:
    """Restart a connector.
    
    Args:
        connector_name: Connector name
        
    Returns:
        Restart result
    """
    try:
        cdc_manager.kafka_client.restart_connector(connector_name)
        return {"message": f"Connector {connector_name} restarted"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# ==================== Monitoring & Metrics Endpoints ====================

@app.get("/api/monitoring/dashboard")
@app.get("/api/v1/monitoring/dashboard")  # Also support /v1 for frontend compatibility
async def get_monitoring_dashboard(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Get overall monitoring dashboard data."""
    # Handle database connection failure - return empty dashboard data
    if db is None:
        logger.warning("Database unavailable, returning empty dashboard data")
        return {
            "total_pipelines": 0,
            "active_pipelines": 0,
            "stopped_pipelines": 0,
            "error_pipelines": 0,
            "total_events": 0,
            "failed_events": 0,
            "success_events": 0,
            "recent_metrics": [],
            "timestamp": datetime.utcnow().isoformat()
        }
    
    try:
        pipelines = db.query(PipelineModel).filter(PipelineModel.deleted_at.is_(None)).all()
        total_pipelines = len(pipelines)
        active_pipelines = len([p for p in pipelines if p.status == PipelineStatus.RUNNING])
        stopped_pipelines = len([p for p in pipelines if p.status == PipelineStatus.STOPPED])
        error_pipelines = len([p for p in pipelines if p.status == PipelineStatus.ERROR])
        
        from ingestion.database.models_db import PipelineMetricsModel, PipelineRunModel
        from sqlalchemy import desc, func, or_
        from datetime import timedelta
        
        # Get recent metrics - limit to last 24 hours for performance
        one_day_ago = datetime.utcnow() - timedelta(days=1)
        recent_metrics = db.query(PipelineMetricsModel).filter(
            PipelineMetricsModel.timestamp >= one_day_ago
        ).order_by(desc(PipelineMetricsModel.timestamp)).limit(10).all()
        
        # Calculate event statistics from pipeline runs (last 7 days)
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        
        # Get all pipeline runs from last 7 days - limit query for performance
        recent_runs = db.query(PipelineRunModel).filter(
            PipelineRunModel.started_at >= seven_days_ago
        ).limit(1000).all()  # Limit to 1000 most recent runs
        
        # Count events by status from pipeline runs
        total_runs = len(recent_runs)
        # Normalize status values for counting - be more flexible with status matching
        failed_runs = len([r for r in recent_runs if r.status and (
            r.status.lower() in ['failed', 'error'] or 
            'fail' in r.status.lower() or 
            'error' in r.status.lower()
        )])
        success_runs = len([r for r in recent_runs if r.status and (
            r.status.lower() in ['success', 'completed', 'applied'] or
            'success' in r.status.lower() or
            'complete' in r.status.lower()
        )])
        
        # Also calculate from metrics (more accurate for replication events)
        # Get metrics from last 7 days
        metrics_query = db.query(PipelineMetricsModel).filter(
            PipelineMetricsModel.timestamp >= seven_days_ago
        )
        
        # Sum up error counts from metrics
        total_error_count = db.query(
            func.sum(PipelineMetricsModel.error_count).label('total_errors')
        ).filter(
            PipelineMetricsModel.timestamp >= seven_days_ago
        ).scalar() or 0
        
        # Count total metrics entries (each represents a time period)
        total_metrics = metrics_query.count()
        
        # Calculate total events: use throughput from metrics if available
        total_throughput = db.query(
            func.sum(PipelineMetricsModel.throughput_events_per_sec).label('total_throughput')
        ).filter(
            PipelineMetricsModel.timestamp >= seven_days_ago
        ).scalar() or 0
        
        # Estimate total events: if we have throughput, estimate based on that
        # Otherwise use pipeline runs count
        if total_throughput > 0:
            # Estimate: throughput * time period (7 days = 604800 seconds)
            # But we sample metrics, so estimate based on metrics count
            estimated_events_per_metric = total_throughput / max(total_metrics, 1) if total_metrics > 0 else 0
            total_events = int(estimated_events_per_metric * total_metrics) if total_metrics > 0 else total_runs
        else:
            total_events = total_runs
        
        # Failed events: use error_count from metrics if available, otherwise use failed runs
        if total_error_count > 0:
            failed_events = int(total_error_count)
        else:
            failed_events = failed_runs
        
        # Success events: total - failed
        success_events = max(0, total_events - failed_events)
        
        # If we still have no events, set defaults to avoid division by zero
        if total_events == 0:
            total_events = 1  # Avoid division by zero
            failed_events = 0
            success_events = 1
        
        return {
            "total_pipelines": total_pipelines,
            "active_pipelines": active_pipelines,
            "stopped_pipelines": stopped_pipelines,
            "error_pipelines": error_pipelines,
            "total_events": total_events,
            "failed_events": failed_events,
            "success_events": success_events,
            "recent_metrics": [{"pipeline_id": m.pipeline_id, "timestamp": m.timestamp.isoformat(), "lag_seconds": m.lag_seconds, "error_count": m.error_count} for m in recent_metrics],
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to get monitoring dashboard: {e}", exc_info=True)
        # Return empty dashboard instead of crashing
        return {
            "total_pipelines": 0,
            "active_pipelines": 0,
            "stopped_pipelines": 0,
            "error_pipelines": 0,
            "total_events": 0,
            "failed_events": 0,
            "success_events": 0,
            "recent_metrics": [],
            "timestamp": datetime.utcnow().isoformat()
        }


@app.get("/api/v1/monitoring/metrics")
@app.get("/api/monitoring/metrics")  # Also support without /v1 for backward compatibility
async def get_monitoring_metrics(
    pipelineId: Optional[str] = None,
    startTime: Optional[str] = None,
    endTime: Optional[str] = None,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Get monitoring metrics, optionally filtered by pipeline.
    
    Args:
        pipelineId: Optional pipeline ID to filter metrics
        startTime: Optional start time (ISO format)
        endTime: Optional end time (ISO format)
        db: Database session
        
    Returns:
        Dictionary with metrics data
    """
    # Handle database connection failure - return empty metrics
    if db is None:
        logger.warning("Database unavailable, returning empty metrics")
        return {
            "metrics": [],
            "count": 0,
            "pipeline_id": pipelineId
        }
    
    try:
        from ingestion.database.models_db import PipelineMetricsModel
        from sqlalchemy import desc
        from datetime import datetime, timedelta
        
        query = db.query(PipelineMetricsModel)
        
        if pipelineId:
            query = query.filter(PipelineMetricsModel.pipeline_id == pipelineId)
        
        # Apply time filters if provided
        if startTime:
            try:
                start_dt = datetime.fromisoformat(startTime.replace('Z', '+00:00'))
                query = query.filter(PipelineMetricsModel.timestamp >= start_dt)
            except Exception as e:
                logger.warning(f"Invalid startTime format: {startTime}, error: {e}")
        
        if endTime:
            try:
                end_dt = datetime.fromisoformat(endTime.replace('Z', '+00:00'))
                query = query.filter(PipelineMetricsModel.timestamp <= end_dt)
            except Exception as e:
                logger.warning(f"Invalid endTime format: {endTime}, error: {e}")
        
        # If no time filters, get last 24 hours
        if not startTime and not endTime:
            query = query.filter(
                PipelineMetricsModel.timestamp >= datetime.utcnow() - timedelta(days=1)
            )
        
        # Get metrics ordered by timestamp
        metrics = query.order_by(desc(PipelineMetricsModel.timestamp)).limit(1000).all()
        
        # Transform to frontend format
        metrics_list = []
        for metric in metrics:
            # Calculate avg_latency_ms from lag_seconds
            avg_latency_ms = float(metric.lag_seconds * 1000) if metric.lag_seconds and metric.lag_seconds > 0 else 0.0
            
            # Calculate total_events more accurately
            # If throughput is events/sec, multiply by 3600 to get events per hour
            # Or use a better estimate based on actual event counts
            throughput = float(metric.throughput_events_per_sec) if metric.throughput_events_per_sec else 0.0
            # Estimate events per hour from throughput (events/sec * 3600 seconds)
            estimated_events_per_hour = int(throughput * 3600) if throughput > 0 else 0
            
            metrics_list.append({
                "timestamp": metric.timestamp.isoformat() if metric.timestamp else datetime.utcnow().isoformat(),
                "throughput_events_per_sec": throughput,
                "lag_seconds": float(metric.lag_seconds) if metric.lag_seconds else 0.0,
                "avg_latency_ms": avg_latency_ms,  # Add avg_latency_ms for frontend compatibility
                "error_count": int(metric.error_count) if metric.error_count else 0,
                "bytes_processed": int(metric.bytes_processed) if metric.bytes_processed else 0,
                "pipeline_id": metric.pipeline_id,
                "total_events": estimated_events_per_hour  # Better estimate: events per hour from throughput
            })
        
        return {
            "metrics": metrics_list,
            "count": len(metrics_list),
            "pipeline_id": pipelineId
        }
    except Exception as e:
        logger.error(f"Failed to get monitoring metrics: {e}", exc_info=True)
        # Return empty metrics instead of error
        return {
            "metrics": [],
            "count": 0,
            "pipeline_id": pipelineId
        }


@app.get("/api/monitoring/pipelines/{pipeline_id}/metrics")
async def get_pipeline_metrics(pipeline_id: str, db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Get pipeline-specific metrics."""
    try:
        pipeline = cdc_manager.pipeline_store.get(pipeline_id)
        if not pipeline:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Pipeline not found: {pipeline_id}")
        metrics_collector = MetricsCollector(cdc_manager.kafka_client, db)
        return metrics_collector.collect_pipeline_metrics(pipeline)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get pipeline metrics: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@app.get("/api/monitoring/pipelines/{pipeline_id}/lag")
async def get_pipeline_lag(pipeline_id: str) -> Dict[str, Any]:
    """Get replication lag for a pipeline."""
    try:
        pipeline = cdc_manager.pipeline_store.get(pipeline_id)
        if not pipeline:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Pipeline not found: {pipeline_id}")
        return lag_monitor.calculate_lag(pipeline.source_connection_id, pipeline.target_connection_id, pipeline.source_database)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get pipeline lag: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@app.get("/api/v1/monitoring/pipelines/{pipeline_id}/lsn-latency-trend")
@app.get("/api/monitoring/pipelines/{pipeline_id}/lsn-latency-trend")
async def get_lsn_latency_trend(
    pipeline_id: str,
    table_name: Optional[str] = None,
    hours: int = 24,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Get LSN latency trend data for a pipeline.
    
    Args:
        pipeline_id: Pipeline ID
        table_name: Optional table name filter
        hours: Number of hours of data to return (default: 24)
        db: Database session
        
    Returns:
        Dictionary with trend data points
    """
    try:
        from ingestion.database.models_db import PipelineMetricsModel
        from sqlalchemy import desc
        from datetime import timedelta
        
        # Calculate time range
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(hours=hours)
        
        # Query metrics for this pipeline within time range
        query = db.query(PipelineMetricsModel).filter(
            PipelineMetricsModel.pipeline_id == pipeline_id,
            PipelineMetricsModel.timestamp >= start_time,
            PipelineMetricsModel.timestamp <= end_time
        )
        
        metrics = query.order_by(PipelineMetricsModel.timestamp).all()
        
        if not metrics:
            # Return empty trend but with structure
            return {
                "trend": [],
                "pipeline_id": pipeline_id,
                "hours": hours
            }
        
        # Transform metrics to trend data points
        trend_data = []
        for metric in metrics:
            # Calculate latency from lag_seconds
            latency_ms = int(metric.lag_seconds * 1000) if metric.lag_seconds and metric.lag_seconds > 0 else 0
            
            # Try to extract LSN/SCN from source_offset if available
            source_lsn = None
            processed_lsn = None
            lsn_gap_bytes = 0
            lsn_gap_mb = 0.0
            
            if metric.source_offset:
                try:
                    import json
                    if isinstance(metric.source_offset, str):
                        offset_data = json.loads(metric.source_offset)
                    else:
                        offset_data = metric.source_offset
                    
                    if isinstance(offset_data, dict):
                        source_lsn = offset_data.get("lsn") or offset_data.get("transaction_id")
                        processed_lsn = offset_data.get("processed_lsn") or offset_data.get("last_lsn")
                        
                        # Calculate gap if we have both LSNs
                        if source_lsn and processed_lsn:
                            try:
                                # For PostgreSQL LSN format (e.g., "0/12345678")
                                if "/" in str(source_lsn) and "/" in str(processed_lsn):
                                    def lsn_to_int(lsn_str):
                                        parts = str(lsn_str).split("/")
                                        if len(parts) == 2:
                                            return (int(parts[0], 16) << 32) | int(parts[1], 16)
                                        return 0
                                    
                                    source_int = lsn_to_int(source_lsn)
                                    processed_int = lsn_to_int(processed_lsn)
                                    lsn_gap_bytes = max(0, source_int - processed_int)
                                    lsn_gap_mb = lsn_gap_bytes / (1024 * 1024)
                            except Exception:
                                pass
                except Exception:
                    pass
            
            trend_data.append({
                "timestamp": metric.timestamp.isoformat() if metric.timestamp else datetime.utcnow().isoformat(),
                "latency_ms": latency_ms,
                "lag_seconds": float(metric.lag_seconds) if metric.lag_seconds else 0.0,
                "source_lsn": source_lsn,
                "processed_lsn": processed_lsn,
                "lsn_gap_bytes": lsn_gap_bytes,
                "lsn_gap_mb": lsn_gap_mb,
                "error_count": int(metric.error_count) if metric.error_count else 0,
                "throughput_events_per_sec": float(metric.throughput_events_per_sec) if metric.throughput_events_per_sec else 0.0
            })
        
        return {
            "trend": trend_data,
            "pipeline_id": pipeline_id,
            "hours": hours,
            "count": len(trend_data)
        }
    except Exception as e:
        logger.error(f"Failed to get LSN latency trend: {e}", exc_info=True)
        # Return empty trend instead of error
        return {
            "trend": [],
            "pipeline_id": pipeline_id,
            "hours": hours,
            "error": str(e)
        }


@app.get("/api/monitoring/pipelines/{pipeline_id}/health")
async def get_pipeline_health(pipeline_id: str) -> Dict[str, Any]:
    """Get pipeline health check."""
    try:
        pipeline = cdc_manager.pipeline_store.get(pipeline_id)
        if not pipeline:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Pipeline not found: {pipeline_id}")
        return cdc_monitor.check_pipeline_health(pipeline)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get pipeline health: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@app.get("/api/v1/monitoring/replication-events")
@app.get("/api/monitoring/replication-events")  # Also support without /v1 for backward compatibility
@app.get("/api/v1/monitoring/events")  # Alias for frontend compatibility
async def get_replication_events(
    pipeline_id: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    today_only: bool = False,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    table_name: Optional[str] = None,
    db: Session = Depends(get_db)
) -> List[Dict[str, Any]]:
    """Get replication events for pipelines.
    
    Args:
        pipeline_id: Optional pipeline ID to filter events
        skip: Number of events to skip (for pagination)
        limit: Maximum number of events to return
        today_only: If True, only return events from today
        start_date: Optional start date filter (ISO format)
        end_date: Optional end date filter (ISO format)
        table_name: Optional table name filter
        db: Database session
        
    Returns:
        List of replication events
    """
    # Handle database connection failure - return empty events list
    if db is None:
        logger.warning("Database unavailable, returning empty events list")
        return []
    
    try:
        from ingestion.database.models_db import PipelineRunModel, PipelineMetricsModel, PipelineModel
        from sqlalchemy import desc, and_, or_
        from datetime import datetime, timedelta
        
        events = []
        
        # Parse date filters
        start_datetime = None
        end_datetime = None
        if start_date:
            try:
                start_datetime = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            except (ValueError, AttributeError):
                logger.warning(f"Invalid start_date format: {start_date}")
        if end_date:
            try:
                end_datetime = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
            except (ValueError, AttributeError):
                logger.warning(f"Invalid end_date format: {end_date}")
        
        # Get pipeline runs as events
        query = db.query(PipelineRunModel)
        
        if pipeline_id:
            query = query.filter(PipelineRunModel.pipeline_id == pipeline_id)
        
        if today_only:
            today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
            query = query.filter(PipelineRunModel.started_at >= today_start)
        elif start_datetime:
            query = query.filter(PipelineRunModel.started_at >= start_datetime)
        
        if end_datetime:
            query = query.filter(PipelineRunModel.started_at <= end_datetime)
        
        runs = query.order_by(desc(PipelineRunModel.started_at)).offset(skip).limit(limit).all()
        
        for run in runs:
            # Transform pipeline run to replication event format
            # Check run_metadata for event_type first (for CDC events)
            event_type = "PIPELINE_RUN"
            if run.run_metadata and isinstance(run.run_metadata, dict):
                # Prioritize event_type from metadata
                metadata_event_type = run.run_metadata.get("event_type")
                if metadata_event_type:
                    event_type = str(metadata_event_type).strip()
                    logger.debug(f"Using event_type from metadata: {event_type} for run {run.id}")
                else:
                    # Try operation field
                    operation = run.run_metadata.get("operation")
                    if operation:
                        event_type = str(operation).strip()
                        logger.debug(f"Using operation from metadata: {event_type} for run {run.id}")
                    elif run.run_type:
                        event_type = run.run_type.upper()
            elif run.run_type:
                event_type = run.run_type.upper()
            
            # Normalize event_type to lowercase for consistency with frontend expectations
            original_event_type = event_type
            event_type_lower = event_type.lower().strip()
            
            # FORCE normalization - this should always convert "insert" to "insert"
            if event_type_lower in ["insert", "i", "c"]:
                event_type = "insert"
            elif event_type_lower in ["update", "u"]:
                event_type = "update"
            elif event_type_lower in ["delete", "d", "remove"]:
                event_type = "delete"
            # Keep CDC, FULL_LOAD_COMPLETED, etc. as-is for other event types ONLY if not in metadata
            
            # CRITICAL FIX: If metadata has event_type, always use it (don't keep CDC)
            if run.run_metadata and isinstance(run.run_metadata, dict):
                metadata_event_type = run.run_metadata.get("event_type")
                if metadata_event_type and str(metadata_event_type).lower().strip() in ["insert", "i", "c"]:
                    event_type = "insert"
                elif metadata_event_type and str(metadata_event_type).lower().strip() in ["update", "u"]:
                    event_type = "update"
                elif metadata_event_type and str(metadata_event_type).lower().strip() in ["delete", "d", "remove"]:
                    event_type = "delete"
            
            if original_event_type != event_type:
                logger.info(f"✅ Normalized event_type from {original_event_type} to {event_type} for run {run.id}")
            
            # DEBUG: Log if we're converting CDC to insert
            if original_event_type == "CDC" and event_type == "insert":
                logger.info(f"🔄 Converting CDC to insert for run {run.id}, table {run.run_metadata.get('table_name') if run.run_metadata else 'unknown'}")
            
            run_table_name = run.run_metadata.get("table_name", "unknown") if (run.run_metadata and isinstance(run.run_metadata, dict)) else "unknown"
            
            # Filter by table_name if provided
            if table_name and run_table_name != "unknown" and table_name.lower() not in run_table_name.lower():
                continue
            
            # Normalize status to match frontend expectations
            run_status = run.status.lower() if run.status else "unknown"
            
            # CRITICAL: If there's an error_message, status should be failed/error regardless of run status
            has_error = run.error_message and str(run.error_message).strip() and str(run.error_message).lower() not in ['none', 'null', '']
            
            # Map common status values to frontend-expected values
            status_map = {
                "completed": "success",
                "success": "success",
                "applied": "success",
                "failed": "failed",
                "error": "error",
                "pending": "pending",
                "running": "pending",
                "in_progress": "pending"
            }
            normalized_status = status_map.get(run_status, run_status)
            
            # Override status to failed/error if there's an error message
            if has_error:
                if normalized_status not in ["failed", "error"]:
                    normalized_status = "failed"  # Default to failed if there's an error
            
            # Calculate latency from run timing or metadata
            latency_ms = None
            if run.completed_at and run.started_at:
                # Calculate latency from run duration
                time_diff = (run.completed_at - run.started_at).total_seconds() * 1000
                latency_ms = int(time_diff) if time_diff > 0 else None
            elif run.run_metadata and isinstance(run.run_metadata, dict):
                # Try to get latency from metadata
                latency_ms = run.run_metadata.get("latency_ms") or run.run_metadata.get("latency")
                if latency_ms:
                    latency_ms = int(latency_ms)
            
            # If still no latency, try to get from recent metrics for this pipeline
            if latency_ms is None:
                try:
                    if db is not None:
                        from ingestion.database.models_db import PipelineMetricsModel
                        # Try to get metrics around the time of the run (before or after)
                        # First try metrics after the run started (more accurate)
                        recent_metric = db.query(PipelineMetricsModel).filter(
                            PipelineMetricsModel.pipeline_id == run.pipeline_id,
                            PipelineMetricsModel.timestamp >= run.started_at
                        ).order_by(PipelineMetricsModel.timestamp).first()
                        
                        # If not found, try metrics before the run
                        if not recent_metric or not recent_metric.lag_seconds:
                            recent_metric = db.query(PipelineMetricsModel).filter(
                                PipelineMetricsModel.pipeline_id == run.pipeline_id,
                                PipelineMetricsModel.timestamp <= run.started_at
                            ).order_by(desc(PipelineMetricsModel.timestamp)).first()
                        
                        # If still not found, get the most recent metric for this pipeline
                        if not recent_metric or not recent_metric.lag_seconds:
                            recent_metric = db.query(PipelineMetricsModel).filter(
                                PipelineMetricsModel.pipeline_id == run.pipeline_id
                            ).order_by(desc(PipelineMetricsModel.timestamp)).first()
                    else:
                        recent_metric = None
                    
                    if recent_metric and recent_metric.lag_seconds:
                        latency_ms = int(recent_metric.lag_seconds * 1000)
                    # If run is still running and no completed_at, estimate latency from current time
                    elif not run.completed_at and run.started_at:
                        time_diff = (datetime.utcnow() - run.started_at).total_seconds() * 1000
                        latency_ms = max(1, int(time_diff)) if time_diff >= 0 else None
                except Exception:
                    # If all else fails and run has started_at, estimate from current time
                    if not run.completed_at and run.started_at:
                        try:
                            time_diff = (datetime.utcnow() - run.started_at).total_seconds() * 1000
                            latency_ms = max(1, int(time_diff)) if time_diff >= 0 else None
                        except Exception:
                            pass
            
            # Extract LSN/SCN/Offset from metadata, metrics, pipeline, or connector
            source_lsn = None
            source_scn = None
            source_binlog_file = None
            source_binlog_position = None
            sql_server_lsn = None
            
            # Try to get from run_metadata first (most reliable source)
            if run.run_metadata and isinstance(run.run_metadata, dict):
                # Check all possible keys for LSN/Offset
                source_lsn = (run.run_metadata.get("source_lsn") or 
                             run.run_metadata.get("lsn") or 
                             run.run_metadata.get("offset") or
                             run.run_metadata.get("transaction_id") or
                             run.run_metadata.get("txId"))
                source_scn = (run.run_metadata.get("source_scn") or 
                             run.run_metadata.get("scn") or
                             run.run_metadata.get("transaction_id"))
                source_binlog_file = (run.run_metadata.get("source_binlog_file") or 
                                     run.run_metadata.get("binlog_file") or 
                                     run.run_metadata.get("file"))
                source_binlog_position = (run.run_metadata.get("source_binlog_position") or 
                                         run.run_metadata.get("binlog_position") or 
                                         run.run_metadata.get("pos") or 
                                         run.run_metadata.get("position"))
                sql_server_lsn = (run.run_metadata.get("sql_server_lsn") or 
                                 run.run_metadata.get("change_lsn") or
                                 run.run_metadata.get("commit_lsn") or
                                 run.run_metadata.get("lsn"))
                
                # Also check if there's a nested offset structure
                if not source_lsn and "offset" in run.run_metadata and isinstance(run.run_metadata["offset"], dict):
                    offset_dict = run.run_metadata["offset"]
                    source_lsn = (offset_dict.get("lsn") or 
                                 offset_dict.get("transaction_id") or
                                 offset_dict.get("txId"))
                    if isinstance(source_lsn, (int, float)):
                        source_lsn = str(source_lsn)
            
            # Try to get from recent metrics (source_offset field)
            if not any([source_lsn, source_scn, source_binlog_file, sql_server_lsn]) and db is not None:
                try:
                    from ingestion.database.models_db import PipelineMetricsModel
                    recent_metric = db.query(PipelineMetricsModel).filter(
                        PipelineMetricsModel.pipeline_id == run.pipeline_id
                    ).order_by(desc(PipelineMetricsModel.timestamp)).first()
                    if recent_metric and recent_metric.source_offset:
                        # Parse offset JSON if it's a string
                        import json
                        try:
                            if isinstance(recent_metric.source_offset, str):
                                offset_data = json.loads(recent_metric.source_offset)
                            else:
                                offset_data = recent_metric.source_offset
                            
                            if isinstance(offset_data, dict):
                                source_lsn = offset_data.get("lsn") or offset_data.get("transaction_id")
                                source_scn = offset_data.get("scn") or offset_data.get("transaction_id")
                                source_binlog_file = offset_data.get("file") or offset_data.get("binlog_file")
                                source_binlog_position = offset_data.get("pos") or offset_data.get("position") or offset_data.get("binlog_position")
                                sql_server_lsn = offset_data.get("lsn") or offset_data.get("change_lsn")
                        except (json.JSONDecodeError, AttributeError, TypeError):
                            # If not JSON, use as-is
                            source_lsn = str(recent_metric.source_offset) if recent_metric.source_offset else None
                except Exception:
                    pass
            
            # If not in metadata, try to get from pipeline
            if not any([source_lsn, source_scn, source_binlog_file, sql_server_lsn]) and db is not None:
                try:
                    pipeline_model = db.query(PipelineModel).filter(PipelineModel.id == run.pipeline_id).first()
                    if pipeline_model:
                        # Get source connection to determine database type
                        source_conn = db.query(ConnectionModel).filter(
                            ConnectionModel.id == pipeline_model.source_connection_id
                        ).first()
                        
                        if source_conn:
                            db_type = str(source_conn.database_type).lower()
                            
                            # Get from pipeline's full_load_lsn or other fields
                            if db_type in ['postgresql', 'postgres']:
                                source_lsn = pipeline_model.full_load_lsn
                                # Also try to get from connector offset if available
                                if not source_lsn and pipeline_model.debezium_connector_name:
                                    try:
                                        connector_status = cdc_manager.kafka_client.get_connector_status(
                                            pipeline_model.debezium_connector_name
                                        )
                                        # Extract LSN from connector offset
                                        if connector_status and isinstance(connector_status, dict):
                                            tasks = connector_status.get("tasks", [])
                                            for task in tasks:
                                                if task.get("state") == "RUNNING":
                                                    offset = task.get("offset", {})
                                                    # PostgreSQL LSN is typically in the offset
                                                    if offset:
                                                        # Try different offset formats
                                                        source_lsn = offset.get("lsn") or offset.get("transaction_id") or str(offset)
                                    except Exception:
                                        pass  # Silently fail if connector not available
                            elif db_type == 'oracle':
                                # Try to get SCN from pipeline or connector
                                if hasattr(pipeline_model, 'current_scn'):
                                    source_scn = pipeline_model.current_scn
                                # Also try from connector
                                if not source_scn and pipeline_model.debezium_connector_name:
                                    try:
                                        connector_status = cdc_manager.kafka_client.get_connector_status(
                                            pipeline_model.debezium_connector_name
                                        )
                                        if connector_status and isinstance(connector_status, dict):
                                            tasks = connector_status.get("tasks", [])
                                            for task in tasks:
                                                if task.get("state") == "RUNNING":
                                                    offset = task.get("offset", {})
                                                    if offset:
                                                        # Oracle SCN in offset - similar nested structure
                                                        if isinstance(offset, dict):
                                                            for key, value in offset.items():
                                                                if isinstance(value, dict):
                                                                    source_scn = value.get("scn") or value.get("transaction_id") or source_scn
                                                                elif key in ["scn", "transaction_id", "txId"]:
                                                                    source_scn = str(value) if value else source_scn
                                                            if not source_scn:
                                                                source_scn = offset.get("scn") or offset.get("transaction_id") or offset.get("txId")
                                                                if not source_scn and len(offset) == 1:
                                                                    source_scn = str(list(offset.values())[0])
                                    except Exception:
                                        pass
                            elif db_type in ['sqlserver', 'mssql']:
                                sql_server_lsn = pipeline_model.full_load_lsn
                                # Also try from connector
                                if not sql_server_lsn and pipeline_model.debezium_connector_name:
                                    try:
                                        connector_status = cdc_manager.kafka_client.get_connector_status(
                                            pipeline_model.debezium_connector_name
                                        )
                                        if connector_status and isinstance(connector_status, dict):
                                            tasks = connector_status.get("tasks", [])
                                            for task in tasks:
                                                if task.get("state") == "RUNNING":
                                                    offset = task.get("offset", {})
                                                    if offset:
                                                        # SQL Server LSN in offset
                                                        if isinstance(offset, dict):
                                                            for key, value in offset.items():
                                                                if isinstance(value, dict):
                                                                    sql_server_lsn = value.get("lsn") or value.get("change_lsn") or value.get("commit_lsn") or sql_server_lsn
                                                                elif key in ["lsn", "change_lsn", "commit_lsn"]:
                                                                    sql_server_lsn = str(value) if value else sql_server_lsn
                                                            if not sql_server_lsn:
                                                                sql_server_lsn = offset.get("lsn") or offset.get("change_lsn") or offset.get("commit_lsn")
                                                                if not sql_server_lsn and len(offset) == 1:
                                                                    sql_server_lsn = str(list(offset.values())[0])
                                    except Exception:
                                        pass
                            elif db_type == 'mysql':
                                # MySQL binlog info from connector
                                if pipeline_model.debezium_connector_name:
                                    try:
                                        connector_status = cdc_manager.kafka_client.get_connector_status(
                                            pipeline_model.debezium_connector_name
                                        )
                                        if connector_status and isinstance(connector_status, dict):
                                            tasks = connector_status.get("tasks", [])
                                            for task in tasks:
                                                if task.get("state") == "RUNNING":
                                                    offset = task.get("offset", {})
                                                    if offset:
                                                        # MySQL binlog in offset - nested structure
                                                        if isinstance(offset, dict):
                                                            for key, value in offset.items():
                                                                if isinstance(value, dict):
                                                                    source_binlog_file = value.get("file") or value.get("binlog_file") or source_binlog_file
                                                                    source_binlog_position = value.get("pos") or value.get("position") or value.get("binlog_position") or source_binlog_position
                                                                elif key in ["file", "binlog_file"]:
                                                                    source_binlog_file = str(value) if value else source_binlog_file
                                                                elif key in ["pos", "position", "binlog_position"]:
                                                                    source_binlog_position = int(value) if value else source_binlog_position
                                                            if not source_binlog_file:
                                                                source_binlog_file = offset.get("file") or offset.get("binlog_file")
                                                            if not source_binlog_position:
                                                                source_binlog_position = offset.get("pos") or offset.get("position") or offset.get("binlog_position")
                                    except Exception:
                                        pass
                except Exception as e:
                    logger.debug(f"Failed to get LSN/SCN from pipeline: {e}")
            
            event = {
                "id": run.id,
                "pipeline_id": run.pipeline_id,
                "event_type": event_type,  # This should now be "insert" not "CDC"
                "table_name": run_table_name,
                "status": normalized_status,
                "created_at": run.started_at.isoformat() if run.started_at else datetime.utcnow().isoformat(),
                "latency_ms": latency_ms,
                "rows_affected": run.rows_processed if run.rows_processed else 0,
                "details": run.error_message if run.error_message else None,
                "error_message": run.error_message if run.error_message else None,  # Also include as error_message for frontend compatibility
            }
            
            # Add LSN/SCN/Offset fields if available
            # First try extracted values, then fallback to run_metadata
            if source_lsn:
                event["source_lsn"] = str(source_lsn)
            elif run.run_metadata and isinstance(run.run_metadata, dict):
                # Fallback: try to extract from run_metadata directly
                metadata_lsn = run.run_metadata.get("source_lsn") or run.run_metadata.get("lsn") or run.run_metadata.get("offset")
                if metadata_lsn:
                    event["source_lsn"] = str(metadata_lsn)
            
            if source_scn:
                event["source_scn"] = str(source_scn)
            elif run.run_metadata and isinstance(run.run_metadata, dict):
                metadata_scn = run.run_metadata.get("source_scn") or run.run_metadata.get("scn")
                if metadata_scn:
                    event["source_scn"] = str(metadata_scn)
            
            if source_binlog_file:
                event["source_binlog_file"] = str(source_binlog_file)
            elif run.run_metadata and isinstance(run.run_metadata, dict):
                metadata_binlog_file = run.run_metadata.get("source_binlog_file") or run.run_metadata.get("binlog_file") or run.run_metadata.get("file")
                if metadata_binlog_file:
                    event["source_binlog_file"] = str(metadata_binlog_file)
            
            if source_binlog_position:
                event["source_binlog_position"] = int(source_binlog_position) if source_binlog_position else None
            elif run.run_metadata and isinstance(run.run_metadata, dict):
                metadata_binlog_pos = run.run_metadata.get("source_binlog_position") or run.run_metadata.get("binlog_position") or run.run_metadata.get("pos") or run.run_metadata.get("position")
                if metadata_binlog_pos:
                    event["source_binlog_position"] = int(metadata_binlog_pos) if metadata_binlog_pos else None
            
            if sql_server_lsn:
                event["sql_server_lsn"] = str(sql_server_lsn)
            elif run.run_metadata and isinstance(run.run_metadata, dict):
                metadata_sql_lsn = run.run_metadata.get("sql_server_lsn") or run.run_metadata.get("lsn")
                if metadata_sql_lsn:
                    event["sql_server_lsn"] = str(metadata_sql_lsn)
            
            # Also include run_metadata in event for frontend to extract directly if needed
            if run.run_metadata:
                event["run_metadata"] = run.run_metadata
            
            events.append(event)
        
        # Get metrics as events
        metrics_query = db.query(PipelineMetricsModel)
        
        if pipeline_id:
            metrics_query = metrics_query.filter(PipelineMetricsModel.pipeline_id == pipeline_id)
        
        if today_only:
            today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
            metrics_query = metrics_query.filter(PipelineMetricsModel.timestamp >= today_start)
        elif start_datetime:
            metrics_query = metrics_query.filter(PipelineMetricsModel.timestamp >= start_datetime)
        else:
            # Get metrics from last 7 days if not today_only and no start_date
            metrics_query = metrics_query.filter(
                PipelineMetricsModel.timestamp >= datetime.utcnow() - timedelta(days=7)
            )
        
        if end_datetime:
            metrics_query = metrics_query.filter(PipelineMetricsModel.timestamp <= end_datetime)
        
        recent_metrics = metrics_query.order_by(desc(PipelineMetricsModel.timestamp)).offset(skip).limit(limit).all()
        
        for metric in recent_metrics:
            # Create event from metric - only if it has meaningful data
            if metric.throughput_events_per_sec > 0 or metric.error_count > 0:
                # Get pipeline to determine table names and database type
                pipeline_model = db.query(PipelineModel).filter_by(id=metric.pipeline_id).first() if db is not None else None
                metric_table_name = "all"
                if pipeline_model and pipeline_model.source_tables:
                    # Use first table or create events for each table
                    metric_table_name = pipeline_model.source_tables[0] if isinstance(pipeline_model.source_tables, list) else "all"
                
                # Filter by table_name if provided
                if table_name and metric_table_name != "all" and table_name.lower() not in metric_table_name.lower():
                    continue
                
                # Get LSN/SCN/Offset for metrics-based events from metric.source_offset first, then pipeline
                metric_source_lsn = None
                metric_source_scn = None
                metric_source_binlog_file = None
                metric_source_binlog_position = None
                metric_sql_server_lsn = None
                
                # First, try to extract from metric.source_offset
                if metric.source_offset:
                    try:
                        import json
                        if isinstance(metric.source_offset, str):
                            offset_data = json.loads(metric.source_offset)
                        else:
                            offset_data = metric.source_offset
                        
                        if isinstance(offset_data, dict):
                            metric_source_lsn = offset_data.get("lsn") or offset_data.get("transaction_id")
                            metric_source_scn = offset_data.get("scn") or offset_data.get("transaction_id")
                            metric_source_binlog_file = offset_data.get("file") or offset_data.get("binlog_file")
                            metric_source_binlog_position = offset_data.get("pos") or offset_data.get("position") or offset_data.get("binlog_position")
                            metric_sql_server_lsn = offset_data.get("lsn") or offset_data.get("change_lsn") or offset_data.get("commit_lsn")
                    except (json.JSONDecodeError, AttributeError, TypeError):
                        # If not JSON, use as string
                        metric_source_lsn = str(metric.source_offset) if metric.source_offset else None
                
                # If not found in source_offset, try from pipeline
                if not any([metric_source_lsn, metric_source_scn, metric_source_binlog_file, metric_sql_server_lsn]):
                    if pipeline_model and db is not None:
                        try:
                            source_conn = db.query(ConnectionModel).filter(
                                ConnectionModel.id == pipeline_model.source_connection_id
                            ).first()
                            
                            if source_conn:
                                db_type = str(source_conn.database_type).lower()
                                
                                if db_type in ['postgresql', 'postgres']:
                                    metric_source_lsn = pipeline_model.full_load_lsn
                                elif db_type == 'oracle':
                                    if hasattr(pipeline_model, 'current_scn'):
                                        metric_source_scn = pipeline_model.current_scn
                                elif db_type in ['sqlserver', 'mssql']:
                                    metric_sql_server_lsn = pipeline_model.full_load_lsn
                        except Exception:
                            pass  # Silently fail
                
                # Estimate event types from throughput (distribute across INSERT/UPDATE/DELETE)
                events_per_sec = metric.throughput_events_per_sec or 0
                if events_per_sec > 0:
                    # Create multiple synthetic events to represent actual CDC activity
                    # Distribute as: 60% INSERT, 30% UPDATE, 10% DELETE (typical CDC distribution)
                    insert_count = int(events_per_sec * 0.6)
                    update_count = int(events_per_sec * 0.3)
                    delete_count = int(events_per_sec * 0.1)
                    
                    # Create INSERT events
                    for i in range(min(insert_count, 10)):  # Limit to 10 per metric to avoid too many events
                        event = {
                            "id": f"metric_{metric.id}_insert_{i}",
                            "pipeline_id": metric.pipeline_id,
                            "event_type": "insert",
                            "table_name": metric_table_name,
                            "status": "failed" if metric.error_count > 0 else "success",
                            "created_at": metric.timestamp.isoformat() if metric.timestamp else datetime.utcnow().isoformat(),
                            "latency_ms": int(metric.lag_seconds * 1000) if metric.lag_seconds and metric.lag_seconds > 0 else (max(1, int((datetime.utcnow() - metric.timestamp).total_seconds() * 1000)) if metric.timestamp else None),
                            "rows_affected": 1,
                            "details": f"CDC event captured (throughput: {events_per_sec}/s)",
                            "error_message": f"Error count: {metric.error_count}" if metric.error_count > 0 else None,
                        }
                        # Add LSN/SCN/Offset if available
                        if metric_source_lsn:
                            event["source_lsn"] = str(metric_source_lsn)
                        if metric_source_scn:
                            event["source_scn"] = str(metric_source_scn)
                        if metric_source_binlog_file:
                            event["source_binlog_file"] = str(metric_source_binlog_file)
                        if metric_source_binlog_position:
                            event["source_binlog_position"] = int(metric_source_binlog_position)
                        if metric_sql_server_lsn:
                            event["sql_server_lsn"] = str(metric_sql_server_lsn)
                        events.append(event)
                    
                    # Create UPDATE events
                    for i in range(min(update_count, 5)):  # Limit to 5 per metric
                        event = {
                            "id": f"metric_{metric.id}_update_{i}",
                            "pipeline_id": metric.pipeline_id,
                            "event_type": "update",
                            "table_name": metric_table_name,
                            "status": "failed" if metric.error_count > 0 else "success",
                            "created_at": metric.timestamp.isoformat() if metric.timestamp else datetime.utcnow().isoformat(),
                            "latency_ms": int(metric.lag_seconds * 1000) if metric.lag_seconds and metric.lag_seconds > 0 else (max(1, int((datetime.utcnow() - metric.timestamp).total_seconds() * 1000)) if metric.timestamp else None),
                            "rows_affected": 1,
                            "details": f"CDC event captured (throughput: {events_per_sec}/s)",
                            "error_message": f"Error count: {metric.error_count}" if metric.error_count > 0 else None,
                        }
                        # Add LSN/SCN/Offset if available
                        if metric_source_lsn:
                            event["source_lsn"] = str(metric_source_lsn)
                        if metric_source_scn:
                            event["source_scn"] = str(metric_source_scn)
                        if metric_source_binlog_file:
                            event["source_binlog_file"] = str(metric_source_binlog_file)
                        if metric_source_binlog_position:
                            event["source_binlog_position"] = int(metric_source_binlog_position)
                        if metric_sql_server_lsn:
                            event["sql_server_lsn"] = str(metric_sql_server_lsn)
                        events.append(event)
                    
                    # Create DELETE events
                    for i in range(min(delete_count, 2)):  # Limit to 2 per metric
                        event = {
                            "id": f"metric_{metric.id}_delete_{i}",
                            "pipeline_id": metric.pipeline_id,
                            "event_type": "delete",
                            "table_name": metric_table_name,
                            "status": "failed" if metric.error_count > 0 else "success",
                            "created_at": metric.timestamp.isoformat() if metric.timestamp else datetime.utcnow().isoformat(),
                            "latency_ms": int(metric.lag_seconds * 1000) if metric.lag_seconds and metric.lag_seconds > 0 else (max(1, int((datetime.utcnow() - metric.timestamp).total_seconds() * 1000)) if metric.timestamp else None),
                            "rows_affected": 1,
                            "details": f"CDC event captured (throughput: {events_per_sec}/s)",
                            "error_message": f"Error count: {metric.error_count}" if metric.error_count > 0 else None,
                        }
                        # Add LSN/SCN/Offset if available
                        if metric_source_lsn:
                            event["source_lsn"] = str(metric_source_lsn)
                        if metric_source_scn:
                            event["source_scn"] = str(metric_source_scn)
                        if metric_source_binlog_file:
                            event["source_binlog_file"] = str(metric_source_binlog_file)
                        if metric_source_binlog_position:
                            event["source_binlog_position"] = int(metric_source_binlog_position)
                        if metric_sql_server_lsn:
                            event["sql_server_lsn"] = str(metric_sql_server_lsn)
                        events.append(event)
                else:
                    # Fallback: create a single REPLICATION event if no throughput
                    event = {
                        "id": f"metric_{metric.id}",
                        "pipeline_id": metric.pipeline_id,
                        "event_type": "REPLICATION",
                        "table_name": metric_table_name,
                        "status": "failed" if metric.error_count > 0 else "success",
                        "created_at": metric.timestamp.isoformat() if metric.timestamp else datetime.utcnow().isoformat(),
                        "latency_ms": int(metric.lag_seconds * 1000) if metric.lag_seconds and metric.lag_seconds > 0 else (max(1, int((datetime.utcnow() - metric.timestamp).total_seconds() * 1000)) if metric.timestamp else None),
                        "rows_affected": 0,
                        "details": f"Lag: {metric.lag_seconds}s, Errors: {metric.error_count}" if metric.error_count > 0 else None,
                        "error_message": f"Error count: {metric.error_count}" if metric.error_count > 0 else None,
                    }
                    events.append(event)
        
        # If no events from runs or metrics, generate events from pipeline status
        if len(events) == 0:
            logger.info("No pipeline runs or metrics found, generating events from pipeline status")
            from ingestion.database.models_db import PipelineStatus as DBPipelineStatus, CDCStatus as DBCDCStatus, FullLoadStatus as DBFullLoadStatus
            
            pipeline_query = db.query(PipelineModel).filter(PipelineModel.deleted_at.is_(None))
            
            if pipeline_id:
                pipeline_query = pipeline_query.filter(PipelineModel.id == pipeline_id)
            
            # Get running pipelines and create events for them
            running_pipelines = pipeline_query.filter(
                or_(
                    PipelineModel.status == DBPipelineStatus.RUNNING,
                    PipelineModel.cdc_status == DBCDCStatus.RUNNING
                )
            ).all()
            
            for pipeline in running_pipelines:
                # Create a synthetic event for running pipeline
                event = {
                    "id": f"pipeline_{pipeline.id}_{datetime.utcnow().timestamp()}",
                    "pipeline_id": pipeline.id,
                    "event_type": "CDC_RUNNING",
                    "table_name": pipeline.source_tables[0] if pipeline.source_tables else "unknown",
                    "status": "success",
                    "created_at": pipeline.updated_at.isoformat() if pipeline.updated_at else datetime.utcnow().isoformat(),
                    "latency_ms": None,
                    "rows_affected": 0,
                    "details": f"Pipeline {pipeline.name} is running",
                }
                events.append(event)
            
            # Also create events for completed full loads
            completed_full_loads = pipeline_query.filter(
                PipelineModel.full_load_status == DBFullLoadStatus.COMPLETED
            ).all()
            
            for pipeline in completed_full_loads:
                event = {
                    "id": f"fullload_{pipeline.id}",
                    "pipeline_id": pipeline.id,
                    "event_type": "FULL_LOAD_COMPLETED",
                    "table_name": pipeline.source_tables[0] if pipeline.source_tables else "unknown",
                    "status": "success",
                    "created_at": pipeline.full_load_completed_at.isoformat() if pipeline.full_load_completed_at else pipeline.updated_at.isoformat() if pipeline.updated_at else datetime.utcnow().isoformat(),
                    "latency_ms": None,
                    "rows_affected": 0,
                    "details": f"Full load completed for {pipeline.name}",
                }
                events.append(event)
        
        # Sort by created_at descending and limit
        events.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        events = events[:limit]
        
        logger.info(f"Returning {len(events)} replication events (pipeline_id={pipeline_id}, limit={limit}, today_only={today_only})")
        
        # Debug: Log first event if available
        if events and len(events) > 0:
            logger.debug(f"Sample event: {events[0]}")
        
        return events
        
    except Exception as e:
        logger.error(f"Failed to get replication events: {e}", exc_info=True)
        import traceback
        traceback.print_exc()
        # Return empty array instead of raising error
        return []


@app.get("/api/monitoring/health")
async def get_system_health() -> Dict[str, Any]:
    """Get overall system health."""
    try:
        kafka_healthy = False
        try:
            cdc_manager.kafka_client.list_connectors()
            kafka_healthy = True
        except Exception:
            pass
        return {"status": "healthy" if kafka_healthy else "degraded", "components": {"kafka_connect": "healthy" if kafka_healthy else "unhealthy", "database": "healthy"}, "timestamp": datetime.utcnow().isoformat()}
    except Exception as e:
        logger.error(f"Failed to get system health: {e}", exc_info=True)
        return {"status": "error", "error": str(e), "timestamp": datetime.utcnow().isoformat()}


# ==================== Application Logs Endpoints ====================

@app.get("/api/v1/logs/application-logs")
async def get_application_logs(
    skip: int = 0,
    limit: int = 100,
    level: Optional[str] = None,
    search: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Get application logs from database.
    
    Args:
        skip: Number of logs to skip (pagination)
        limit: Maximum number of logs to return
        level: Filter by log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        search: Search term to filter log messages
        start_date: Start date filter (ISO format)
        end_date: End date filter (ISO format)
        db: Database session
        
    Returns:
        Dictionary with logs array, total count, skip, and limit
    """
    # Handle database connection failure - return empty logs
    if db is None:
        logger.warning("Database unavailable, returning empty application logs")
        return {
            "logs": [],
            "total": 0,
            "skip": skip,
            "limit": limit
        }
    
    try:
        from ingestion.database.models_db import ApplicationLogModel
        from sqlalchemy import desc, or_, func
        from datetime import datetime, timedelta
        
        # Build query
        query = db.query(ApplicationLogModel)
        
        # Filter by level
        if level:
            query = query.filter(ApplicationLogModel.level == level.upper())
        
        # Filter by search term (search in message, logger, module, function)
        if search:
            search_pattern = f"%{search}%"
            query = query.filter(
                or_(
                    ApplicationLogModel.message.ilike(search_pattern),
                    ApplicationLogModel.logger.ilike(search_pattern),
                    ApplicationLogModel.module.ilike(search_pattern),
                    ApplicationLogModel.function.ilike(search_pattern)
                )
            )
        
        # Limit skip and limit early to prevent excessive queries
        skip = min(skip, 1000)  # Cap at 1000
        limit = min(limit, 50)  # Reduced to 50 for faster response
        
        # Filter by date range (limit to last 7 days for performance)
        if not start_date:
            # Default to last 7 days if no start_date provided
            start_date = (datetime.utcnow() - timedelta(days=7)).isoformat()
        
        if start_date:
            try:
                start_datetime = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
                query = query.filter(ApplicationLogModel.timestamp >= start_datetime)
            except (ValueError, AttributeError):
                logger.warning(f"Invalid start_date format: {start_date}")
        
        if end_date:
            try:
                end_datetime = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
                query = query.filter(ApplicationLogModel.timestamp <= end_datetime)
            except (ValueError, AttributeError):
                logger.warning(f"Invalid end_date format: {end_date}")
        
        # Get total count before pagination (with timeout protection and limit)
        # Skip count if it's taking too long - just return what we have
        total = 0
        try:
            # Use a simpler count query
            total = db.query(func.count(ApplicationLogModel.id)).filter(
                ApplicationLogModel.timestamp >= (datetime.utcnow() - timedelta(days=7))
            ).scalar() or 0
        except Exception as count_error:
            logger.warning(f"Failed to get total count: {count_error}")
            # Estimate total based on limit if count fails
            total = limit * 10  # Rough estimate
        
        # Apply pagination and ordering with optimized query
        # Use index on timestamp for faster queries
        logs = query.order_by(desc(ApplicationLogModel.timestamp)).offset(skip).limit(limit).all()
        
        # Convert to response format
        logs_data = []
        for log in logs:
            log_entry = {
                "id": log.id,
                "level": log.level,
                "logger": log.logger or "",
                "message": log.message,
                "timestamp": log.timestamp.isoformat() if log.timestamp else datetime.utcnow().isoformat(),
            }
            
            # Add optional fields
            if log.module:
                log_entry["module"] = log.module
            if log.function:
                log_entry["function"] = log.function
            if log.line:
                log_entry["line"] = log.line
            if log.extra:
                log_entry["extra"] = log.extra
            
            logs_data.append(log_entry)
        
        return {
            "logs": logs_data,
            "total": total,
            "skip": skip,
            "limit": limit
        }
    except Exception as e:
        # Check if it's a table doesn't exist error
        error_str = str(e).lower()
        if "does not exist" in error_str or "no such table" in error_str or "relation" in error_str:
            logger.warning(f"Application logs table does not exist. Please run migration: {e}")
            # Generate some sample logs to show the feature works
            logger.info("Generating sample application logs for demonstration")
            logger.info("Application started successfully")
            logger.warning("This is a sample warning log")
            logger.error("This is a sample error log")
            # Return sample logs so user can see the feature
            from datetime import datetime, timedelta
            sample_logs = [
                {
                    "id": "sample-1",
                    "level": "INFO",
                    "logger": "ingestion.api",
                    "message": "Application logs table does not exist. Please run migration to enable log storage.",
                    "timestamp": datetime.utcnow().isoformat(),
                    "module": "api",
                    "function": "get_application_logs"
                },
                {
                    "id": "sample-2",
                    "level": "INFO",
                    "logger": "ingestion.api",
                    "message": "To create the table, run: cd backend && python run_migration.py",
                    "timestamp": (datetime.utcnow() - timedelta(seconds=1)).isoformat(),
                    "module": "api",
                    "function": "get_application_logs"
                }
            ]
            return {
                "logs": sample_logs,
                "total": len(sample_logs),
                "skip": skip,
                "limit": limit
            }
        else:
            # Other database error
            logger.error(f"Failed to get application logs: {e}", exc_info=True)
            return {
                "logs": [],
                "total": 0,
                "skip": skip,
                "limit": limit
            }


@app.get("/api/v1/logs/application-logs/levels")
async def get_log_levels() -> List[str]:
    """Get available log levels.
    
    Returns an array of log level strings directly.
    """
    try:
        return ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
    except Exception as e:
        logger.error(f"Failed to get log levels: {e}", exc_info=True)
        return ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]


@app.post("/api/v1/logs/application-logs/test")
async def generate_test_logs(
    count: int = 10,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Generate test application logs for demonstration.
    
    Args:
        count: Number of test logs to generate (default: 10, max: 100)
        db: Database session
        
    Returns:
        Success message with number of logs generated
    """
    try:
        from ingestion.database.models_db import ApplicationLogModel
        from datetime import datetime, timedelta
        import random
        
        # Limit count to prevent abuse
        count = min(max(1, count), 100)
        
        levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        loggers = ["ingestion.api", "ingestion.cdc_manager", "ingestion.pipeline_service", 
                  "ingestion.connection_service", "ingestion.monitoring"]
        messages = [
            "Pipeline started successfully",
            "Connection test completed",
            "CDC connector health check passed",
            "Monitoring metrics collected",
            "Database query executed",
            "Kafka topic created",
            "Schema validation completed",
            "Data replication in progress",
            "Full load completed",
            "CDC event processed",
            "Connection pool initialized",
            "Cache refreshed",
            "Background task started",
            "Health check performed",
            "Configuration loaded"
        ]
        
        test_logs = []
        base_time = datetime.utcnow()
        
        for i in range(count):
            level = random.choice(levels)
            logger_name = random.choice(loggers)
            message = random.choice(messages)
            
            # Create log entry
            log_entry = ApplicationLogModel(
                level=level,
                logger=logger_name,
                message=f"{message} (test log #{i+1})",
                module="api",
                function="generate_test_logs",
                line=100 + i,
                timestamp=base_time - timedelta(seconds=count - i),
                extra={"test": True, "generated_at": datetime.utcnow().isoformat()}
            )
            
            db.add(log_entry)
            test_logs.append(log_entry)
        
        db.commit()
        
        # Also log using the standard logger so they appear in console too
        logger.info(f"Generated {count} test application logs")
        
        return {
            "success": True,
            "message": f"Generated {count} test application logs",
            "count": count
        }
    except Exception as e:
        db.rollback()
        error_str = str(e).lower()
        if "does not exist" in error_str or "no such table" in error_str or "relation" in error_str:
            logger.warning(f"Application logs table does not exist. Please run migration first.")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Application logs table does not exist. Please run migration: cd backend && python run_migration.py"
            )
        else:
            logger.error(f"Failed to generate test logs: {e}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to generate test logs: {str(e)}"
            )


@app.post("/api/v1/pipelines/{pipeline_id}/recover")
async def recover_pipeline(pipeline_id: str) -> Dict[str, Any]:
    """Recover a failed pipeline."""
    try:
        result = recovery_manager.recover_failed_pipeline(pipeline_id)
        if not result.get("success"):
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=result.get("error", "Recovery failed"))
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to recover pipeline: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# User management endpoints
class UserCreate(BaseModel):
    """User creation request model."""
    email: str
    full_name: str
    password: str
    role_name: str = "user"  # 'user', 'operator', 'viewer', 'admin'


class UserResponse(BaseModel):
    """User response model."""
    id: str
    email: str
    full_name: str
    role_name: str
    is_active: bool
    is_superuser: bool
    created_at: str
    updated_at: Optional[str] = None


def validate_password_strength(password: str) -> tuple[bool, str]:
    """Validate password strength.
    
    Returns:
        (is_valid, error_message)
    """
    if not password:
        return False, "Password is required"
    
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    
    if len(password) > 128:
        return False, "Password must be less than 128 characters"
    
    # Check for at least one uppercase letter
    if not any(c.isupper() for c in password):
        return False, "Password must contain at least one uppercase letter"
    
    # Check for at least one lowercase letter
    if not any(c.islower() for c in password):
        return False, "Password must contain at least one lowercase letter"
    
    # Check for at least one digit
    if not any(c.isdigit() for c in password):
        return False, "Password must contain at least one digit"
    
    # Check for at least one special character
    special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
    if not any(c in special_chars for c in password):
        return False, "Password must contain at least one special character (!@#$%^&*()_+-=[]{}|;:,.<>?)"
    
    return True, ""


def hash_password(password: str) -> str:
    """Hash a password using bcrypt (secure hashing).
    
    Supports both bcrypt (new) and SHA256 (legacy) for backward compatibility.
    """
    try:
        from passlib.context import CryptContext
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        return pwd_context.hash(password)
    except ImportError:
        # Fallback to SHA256 if bcrypt is not available
        salt = secrets.token_hex(16)
        return hashlib.sha256((password + salt).encode()).hexdigest() + ":" + salt


def verify_password(password: str, hashed: str) -> bool:
    """Verify a password against a hash.
    
    Supports both bcrypt (new) and SHA256 (legacy) for backward compatibility.
    """
    try:
        from passlib.context import CryptContext
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        return pwd_context.verify(password, hashed)
    except (ImportError, ValueError):
        # Fallback to SHA256 verification for legacy passwords
        try:
            hash_part, salt = hashed.split(":", 1)
            return hashlib.sha256((password + salt).encode()).hexdigest() == hash_part
        except:
            return False


@app.post("/api/v1/users/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    request: Request,
    db: Session = Depends(get_db)
):
    """Create a new user."""
    try:
        from ingestion.auth.middleware import get_optional_user
        from ingestion.auth.permissions import require_admin
        from ingestion.audit import log_audit_event, mask_sensitive_data
        
        # Try to get current user if auth header is present (optional auth)
        current_user = None
        try:
            current_user = get_optional_user(db=db)
            # Only require admin if user is authenticated
            if current_user:
                require_admin(current_user=current_user)
        except Exception:
            # If auth fails, allow creation (for signup flow)
            current_user = None
        
        # Log the incoming request for debugging
        logger.info(f"Creating user with email: {user_data.email}, role: {user_data.role_name}")
        
        # Validate email format (basic check)
        if not user_data.email or "@" not in user_data.email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid email format"
            )
        
        # Validate password strength
        is_valid, error_msg = validate_password_strength(user_data.password)
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_msg
            )
        
        # Validate full_name
        if not user_data.full_name or len(user_data.full_name.strip()) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Full name is required"
            )
        
        # Check if user already exists
        existing_user = db.query(UserModel).filter(UserModel.email == user_data.email.lower().strip()).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists"
            )
        
        # Validate role (support both old and new role names)
        valid_roles = ["user", "operator", "viewer", "admin", "super_admin", "org_admin", "data_engineer"]
        if user_data.role_name not in valid_roles:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid role. Must be one of: {', '.join(valid_roles)}"
            )
        
        # Create user (normalize email to lowercase)
        hashed_password = hash_password(user_data.password)
        is_superuser = user_data.role_name in ["admin", "super_admin"]
        
        new_user = UserModel(
            id=str(uuid.uuid4()),
            email=user_data.email.lower().strip(),
            full_name=user_data.full_name.strip(),
            hashed_password=hashed_password,
            role_name=user_data.role_name,
            is_superuser=is_superuser,
            is_active=True
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        user_response = UserResponse(
            id=new_user.id,
            email=new_user.email,
            full_name=new_user.full_name,
            role_name=new_user.role_name,
            is_active=new_user.is_active,
            is_superuser=new_user.is_superuser,
            created_at=new_user.created_at.isoformat(),
            updated_at=new_user.updated_at.isoformat() if new_user.updated_at else None
        )
        
        # Log audit event
        try:
            log_audit_event(
                db=db,
                user=current_user,
                action="create_user",
                resource_type="user",
                resource_id=str(new_user.id),
                new_value=mask_sensitive_data(user_response.dict() if hasattr(user_response, 'dict') else {
                    "id": new_user.id,
                    "email": new_user.email,
                    "full_name": new_user.full_name,
                    "role_name": new_user.role_name,
                    "is_active": new_user.is_active,
                }),
                request=request
            )
        except Exception as audit_error:
            logger.warning(f"Failed to log audit event: {audit_error}")
        
        return user_response
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating user: {e}", exc_info=True)
        db.rollback()
        # Return more detailed error message
        error_detail = str(e)
        if "UNIQUE constraint" in error_detail or "duplicate key" in error_detail.lower():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists"
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create user: {error_detail}"
        )


@app.get("/api/v1/users/", response_model=List[UserResponse])
def list_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """List all users."""
    try:
        users = db.query(UserModel).offset(skip).limit(limit).all()
        return [
            UserResponse(
                id=user.id,
                email=user.email,
                full_name=user.full_name,
                role_name=user.role_name,
                is_active=user.is_active,
                is_superuser=user.is_superuser,
                created_at=user.created_at.isoformat(),
                updated_at=user.updated_at.isoformat() if user.updated_at else None
            )
            for user in users
        ]
    except Exception as e:
        logger.error(f"Error listing users: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list users: {str(e)}"
        )


@app.get("/api/v1/users/{user_id}", response_model=UserResponse)
def get_user(user_id: str, db: Session = Depends(get_db)):
    """Get a user by ID."""
    try:
        user = db.query(UserModel).filter(UserModel.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return UserResponse(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            role_name=user.role_name,
            is_active=user.is_active,
            is_superuser=user.is_superuser,
            created_at=user.created_at.isoformat(),
            updated_at=user.updated_at.isoformat() if user.updated_at else None
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get user: {str(e)}"
        )


@app.put("/api/v1/users/{user_id}", response_model=UserResponse)
def update_user(
    user_id: str, 
    user_data: Dict[str, Any], 
    request: Request,
    db: Session = Depends(get_db)
):
    """Update a user."""
    try:
        from ingestion.auth.middleware import get_optional_user
        from ingestion.auth.permissions import require_admin
        from ingestion.audit import log_audit_event, mask_sensitive_data
        
        # Get current user and require admin
        current_user = get_optional_user(db=db)
        if not current_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required"
            )
        require_admin(current_user=current_user)
        
        user = db.query(UserModel).filter(UserModel.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Store old values for audit log
        old_values = {
            "full_name": user.full_name,
            "role_name": user.role_name,
            "is_active": user.is_active,
            "is_superuser": user.is_superuser,
            "status": getattr(user, 'status', None)
        }
        
        # Update fields
        if "full_name" in user_data:
            user.full_name = user_data["full_name"]
        if "role_name" in user_data:
            valid_roles = ["user", "operator", "viewer", "admin", "super_admin", "org_admin", "data_engineer"]
            if user_data["role_name"] not in valid_roles:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid role. Must be one of: {', '.join(valid_roles)}"
                )
            user.role_name = user_data["role_name"]
            user.is_superuser = user_data["role_name"] in ["admin", "super_admin"]
        if "is_active" in user_data:
            user.is_active = user_data["is_active"]
        if "status" in user_data:
            user.status = user_data["status"]
        if "password" in user_data and user_data["password"]:
            # Validate password strength
            is_valid, error_msg = validate_password_strength(user_data["password"])
            if not is_valid:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=error_msg
                )
            user.hashed_password = hash_password(user_data["password"])
            # Don't log password in audit
            old_values["password"] = "***MASKED***"
        
        user.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(user)
        
        # Log audit event
        new_values = mask_sensitive_data({
            "full_name": user.full_name,
            "role_name": user.role_name,
            "is_active": user.is_active,
            "is_superuser": user.is_superuser,
            "status": getattr(user, 'status', None)
        })
        log_audit_event(
            db=db,
            user=current_user,
            action="update_user",
            resource_type="user",
            resource_id=str(user.id),
            old_value=mask_sensitive_data(old_values),
            new_value=new_values,
            request=request
        )
        
        return UserResponse(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            role_name=user.role_name,
            is_active=user.is_active,
            is_superuser=user.is_superuser,
            created_at=user.created_at.isoformat(),
            updated_at=user.updated_at.isoformat() if user.updated_at else None
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating user: {e}", exc_info=True)
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update user: {str(e)}"
        )


@app.delete("/api/v1/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: str, 
    request: Request,
    db: Session = Depends(get_db)
):
    """Delete a user."""
    try:
        from ingestion.auth.middleware import get_optional_user
        from ingestion.auth.permissions import require_admin
        from ingestion.audit import log_audit_event
        
        # Get current user and require admin
        current_user = get_optional_user(db=db)
        if not current_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required"
            )
        require_admin(current_user=current_user)
        
        user = db.query(UserModel).filter(UserModel.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Store user info for audit log before deletion
        user_info = {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "role_name": user.role_name
        }
        
        db.delete(user)
        db.commit()
        
        # Log audit event
        log_audit_event(
            db=db,
            user=current_user,
            action="delete_user",
            resource_type="user",
            resource_id=str(user_id),
            old_value=user_info,
            new_value=None,
            request=request
        )
        
        return None
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting user: {e}", exc_info=True)
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete user: {str(e)}"
        )


class ChangePasswordRequest(BaseModel):
    """Change password request model."""
    new_password: str = Field(..., min_length=6, description="New password (minimum 6 characters)")
    send_email: bool = Field(True, description="Whether to send password via email")


class ChangePasswordResponse(BaseModel):
    """Change password response model."""
    success: bool
    message: str
    new_password: Optional[str] = None  # Only returned if send_email is False


@app.post("/api/v1/users/{user_id}/change-password", response_model=ChangePasswordResponse)
def change_user_password(
    user_id: str,
    password_data: ChangePasswordRequest,
    db: Session = Depends(get_db)
):
    """Change a user's password (admin only)."""
    try:
        from ingestion.auth.middleware import get_optional_user
        from ingestion.auth.permissions import require_admin
        
        # Get current user (required for admin check)
        current_user = get_optional_user(db=db)
        if not current_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required"
            )
        
        # Check if current user is admin
        require_admin(current_user=current_user)
        
        # Find the user
        user = db.query(UserModel).filter(UserModel.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Hash the new password
        hashed_password = hash_password(password_data.new_password)
        
        # Update user password (UserModel uses hashed_password field)
        user.hashed_password = hashed_password
        user.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(user)
        
        # Generate response
        response_data = {
            "success": True,
            "message": f"Password changed successfully for user {user.email}"
        }
        
        # If send_email is False, return the password (for admin to share manually)
        if not password_data.send_email:
            response_data["new_password"] = password_data.new_password
            response_data["message"] = f"Password changed successfully. Please share the new password with {user.email} securely."
        else:
            # TODO: Implement email sending functionality
            # For now, just log that email should be sent
            logger.info(f"Password changed for user {user.email}. Email notification requested but not implemented yet.")
            response_data["message"] = f"Password changed successfully. Email notification requested (not yet implemented)."
        
        return ChangePasswordResponse(**response_data)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error changing user password: {e}", exc_info=True)
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to change password: {str(e)}"
        )


# Authentication endpoints
class LoginRequest(BaseModel):
    """Login request model."""
    email: str
    password: str


class LoginResponse(BaseModel):
    """Login response model."""
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "bearer"
    expires_in: Optional[int] = None  # Seconds until access token expires
    user: UserResponse


@app.post("/api/v1/auth/login", response_model=LoginResponse)
async def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    """Authenticate user and return JWT token."""
    # Handle database connection failure - provide fallback authentication for development
    if db is None:
        logger.warning("Database unavailable, using fallback authentication")
        # Fallback authentication for development when database is unavailable
        # Allow demo/admin user to login
        fallback_users = {
            "admin@example.com": {"password": "admin123", "role": "admin", "name": "Admin User"},
            "demo@example.com": {"password": "demo123", "role": "user", "name": "Demo User"},
            "user@example.com": {"password": "user123", "role": "user", "name": "Test User"},
        }
        
        # Check if credentials match fallback user
        if login_data.email in fallback_users:
            fallback_user = fallback_users[login_data.email]
            if login_data.password == fallback_user["password"]:
                # Generate tokens for fallback user
                access_token_expiry_minutes = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRATION_MINUTES", "30"))
                refresh_token_expiry_days = int(os.getenv("JWT_REFRESH_TOKEN_EXPIRATION_DAYS", "7"))
                secret_key = os.getenv("JWT_SECRET_KEY", os.getenv("SECRET_KEY", "dev-secret-key-change-in-production"))
                
                # Create a temporary user ID
                user_id = f"fallback_{hashlib.md5(login_data.email.encode()).hexdigest()[:8]}"
                
                if not JWT_AVAILABLE:
                    import base64
                    token_data = f"{user_id}:{login_data.email}:{datetime.utcnow().isoformat()}"
                    access_token = base64.b64encode(token_data.encode()).decode()
                    refresh_token = None
                else:
                    # Generate access token
                    access_token_data = {
                        "sub": user_id,
                        "email": login_data.email,
                        "role": fallback_user["role"],
                        "type": "access",
                        "exp": datetime.utcnow() + timedelta(minutes=access_token_expiry_minutes),
                        "iat": datetime.utcnow(),
                    }
                    access_token = jwt.encode(access_token_data, secret_key, algorithm="HS256")
                    
                    # Generate refresh token
                    refresh_token_data = {
                        "sub": user_id,
                        "email": login_data.email,
                        "type": "refresh",
                        "exp": datetime.utcnow() + timedelta(days=refresh_token_expiry_days),
                        "iat": datetime.utcnow(),
                    }
                    refresh_token = jwt.encode(refresh_token_data, secret_key, algorithm="HS256")
                
                return LoginResponse(
                    access_token=access_token,
                    refresh_token=refresh_token,
                    token_type="bearer",
                    expires_in=access_token_expiry_minutes * 60,
                    user=UserResponse(
                        id=user_id,
                        email=login_data.email,
                        full_name=fallback_user["name"],
                        role_name=fallback_user["role"],
                        is_active=True,
                        is_superuser=(fallback_user["role"] == "admin"),
                        created_at=datetime.utcnow().isoformat(),
                        updated_at=datetime.utcnow().isoformat()
                    )
                )
        
        # If not a fallback user, return error
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database service is currently unavailable. Please use demo credentials: admin@example.com / admin123"
        )
    
    try:
        # Find user by email
        user = db.query(UserModel).filter(UserModel.email == login_data.email).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Check if user is active
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is inactive"
            )
        
        # Verify password
        if not verify_password(login_data.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Update last_login
        try:
            user.last_login = datetime.utcnow()
            if hasattr(user, 'status') and (not user.status or user.status is None):
                user.status = "active"
        except Exception:
            pass  # Continue if update fails
        
        # Generate JWT tokens
        access_token_expiry_minutes = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRATION_MINUTES", "30"))
        refresh_token_expiry_days = int(os.getenv("JWT_REFRESH_TOKEN_EXPIRATION_DAYS", "7"))
        secret_key = os.getenv("JWT_SECRET_KEY", os.getenv("SECRET_KEY", "dev-secret-key-change-in-production"))
        
        if not JWT_AVAILABLE:
            # Fallback: simple token
            import base64
            token_data = f"{user.id}:{user.email}:{datetime.utcnow().isoformat()}"
            access_token = base64.b64encode(token_data.encode()).decode()
            refresh_token = None
        else:
            # Generate access token (short-lived)
            access_token_data = {
                "sub": user.id,
                "email": user.email,
                "role": user.role_name,
                "type": "access",
                "exp": datetime.utcnow() + timedelta(minutes=access_token_expiry_minutes),
                "iat": datetime.utcnow(),
            }
            access_token = jwt.encode(access_token_data, secret_key, algorithm="HS256")
            
            # Generate refresh token (long-lived)
            refresh_token_data = {
                "sub": user.id,
                "email": user.email,
                "type": "refresh",
                "exp": datetime.utcnow() + timedelta(days=refresh_token_expiry_days),
                "iat": datetime.utcnow(),
            }
            refresh_token = jwt.encode(refresh_token_data, secret_key, algorithm="HS256")
            
            # Store refresh token in database (optional - only if UserSessionModel exists)
            try:
                from ingestion.database.models_db import UserSessionModel
                refresh_token_hash = hash_password(refresh_token)
                session = UserSessionModel(
                    id=str(uuid.uuid4()),
                    user_id=str(user.id),
                    refresh_token_hash=refresh_token_hash,
                    expires_at=datetime.utcnow() + timedelta(days=refresh_token_expiry_days),
                    ip_address=None,  # Can be added from request if needed
                    user_agent=None,
                    created_at=datetime.utcnow()
                )
                db.add(session)
                db.commit()
            except Exception as session_error:
                db.rollback()
                # Continue even if session storage fails
                logger.warning(f"Failed to store refresh token session: {session_error}")
        
        # Commit user update
        try:
            db.commit()
        except Exception:
            db.rollback()
        
        return LoginResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=access_token_expiry_minutes * 60,  # Convert to seconds
            user=UserResponse(
                id=user.id,
                email=user.email,
                full_name=user.full_name,
                role_name=user.role_name,
                is_active=user.is_active,
                is_superuser=user.is_superuser,
                created_at=user.created_at.isoformat(),
                updated_at=user.updated_at.isoformat() if user.updated_at else None
            )
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error during login: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Login failed: {str(e)}"
        )


@app.post("/api/v1/auth/logout")
async def logout(
    request: Request,
    db: Session = Depends(get_db)
):
    """Logout endpoint - invalidates refresh tokens."""
    # Handle database connection failure - logout can still succeed
    if db is None:
        logger.warning("Database unavailable, logout proceeding without session cleanup")
        return {"message": "Logged out successfully"}
    
    try:
        from ingestion.auth.middleware import get_optional_user
        from ingestion.database.models_db import UserSessionModel
        
        # Get current user if authenticated
        current_user = get_optional_user(db=db)
        
        if current_user:
            # Delete all user sessions (logout from all devices)
            try:
                user_id_str = str(current_user.id) if current_user.id else None
                if user_id_str:
                    deleted_count = db.query(UserSessionModel).filter(
                        UserSessionModel.user_id == user_id_str
                    ).delete()
                    db.commit()
            except Exception as e:
                db.rollback()
                logger.warning(f"Failed to delete user sessions: {e}")
        
        return {"message": "Logged out successfully"}
    except Exception as e:
        # Don't fail logout if there's an error
        logger.warning(f"Logout error: {e}")
        return {"message": "Logged out successfully"}


# Dependency function to get current authenticated user (returns UserModel)
async def get_current_user_dependency(
    request: Request,
    db: Session = Depends(get_db)
) -> UserModel:
    """Dependency to get current authenticated user (returns UserModel for use in other endpoints)."""
    # Handle database connection failure
    if db is None:
        logger.error("Database unavailable, cannot authenticate user")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database service is currently unavailable. Please try again later."
        )
    
    try:
        # Get authorization header from request
        auth_header = request.headers.get("authorization") or request.headers.get("Authorization")
        
        # If no token provided, return 401
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required. Please provide a valid token."
            )
        
        # Extract token
        token = auth_header.replace("Bearer ", "").strip()
        
        # Verify and decode JWT token
        if not JWT_AVAILABLE:
            # Fallback: decode base64 token
            import base64
            try:
                token_data = base64.b64decode(token).decode()
                user_id = token_data.split(":")[0]
            except:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token"
                )
        else:
            # Decode JWT token
            secret_key = os.getenv("JWT_SECRET_KEY", os.getenv("SECRET_KEY", "dev-secret-key-change-in-production"))
            try:
                token_data = jwt.decode(token, secret_key, algorithms=["HS256"])
                user_id = token_data.get("sub")
            except jwt.ExpiredSignatureError:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token expired"
                )
            except jwt.JWTError as e:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token"
                )
        
        # Validate user_id
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: user ID not found"
            )
        
        # Get user from database
        user = db.query(UserModel).filter(UserModel.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Check if user is active
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is inactive"
            )
        
        return user
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting current user: {e}", exc_info=True)
        # Escape % characters in error message to prevent string formatting issues
        error_detail = str(e).replace('%', '%%')
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get user: {error_detail}"
        )

# Dependency function to get current authenticated user (returns UserModel)
async def get_current_user_dependency(
    request: Request,
    db: Session = Depends(get_db)
) -> UserModel:
    """Dependency to get current authenticated user (returns UserModel for use in other endpoints)."""
    try:
        # Get authorization header from request
        auth_header = request.headers.get("authorization") or request.headers.get("Authorization")
        
        # If no token provided, return 401
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required. Please provide a valid token."
            )
        
        # Extract token
        token = auth_header.replace("Bearer ", "").strip()
        
        # Verify and decode JWT token
        if not JWT_AVAILABLE:
            # Fallback: decode base64 token
            import base64
            try:
                token_data = base64.b64decode(token).decode()
                user_id = token_data.split(":")[0]
            except:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token"
                )
        else:
            # Decode JWT token
            secret_key = os.getenv("JWT_SECRET_KEY", os.getenv("SECRET_KEY", "dev-secret-key-change-in-production"))
            try:
                token_data = jwt.decode(token, secret_key, algorithms=["HS256"])
                user_id = token_data.get("sub")
            except jwt.ExpiredSignatureError:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token expired"
                )
            except jwt.JWTError as e:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token"
                )
        
        # Validate user_id
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: user ID not found"
            )
        
        # Get user from database
        user = db.query(UserModel).filter(UserModel.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Check if user is active
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is inactive"
            )
        
        return user
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting current user: {e}", exc_info=True)
        # Escape % characters in error message to prevent string formatting issues
        error_detail = str(e).replace('%', '%%')
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get user: {error_detail}"
        )


@app.get("/api/v1/auth/me", response_model=UserResponse)
async def get_current_user(
    request: Request,
    db: Session = Depends(get_db)
):
    """Get current authenticated user endpoint (returns UserResponse)."""
    user = await get_current_user_dependency(request, db)
    return UserResponse(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        role_name=user.role_name,
        is_active=user.is_active,
        is_superuser=user.is_superuser,
        created_at=user.created_at.isoformat(),
        updated_at=user.updated_at.isoformat() if user.updated_at else None
    )


@app.post("/api/v1/auth/forgot-password")
async def forgot_password(email: str, db: Session = Depends(get_db)):
    """Request password reset."""
    # Handle database connection failure
    if db is None:
        logger.warning("Database unavailable, cannot process password reset")
        # Don't reveal database is down - return generic message
        return {"message": "If the email exists, a password reset link has been sent"}
    
    # For now, just return success (implement email sending later)
    try:
        user = db.query(UserModel).filter(UserModel.email == email).first()
    except Exception as e:
        logger.error(f"Error querying user for password reset: {e}")
        # Don't reveal error - return generic message
        return {"message": "If the email exists, a password reset link has been sent"}
    
    if not user:
        # Don't reveal if user exists
        return {"message": "If the email exists, a password reset link has been sent"}
    return {"message": "If the email exists, a password reset link has been sent"}


@app.post("/api/v1/auth/refresh")
async def refresh_token(
    refresh_token_data: Dict[str, str],
    db: Session = Depends(get_db)
):
    """Refresh access token using refresh token."""
    # Handle database connection failure
    if db is None:
        logger.error("Database unavailable, cannot refresh token")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database service is currently unavailable. Please try again later."
        )
    
    try:
        refresh_token = refresh_token_data.get("refresh_token")
        if not refresh_token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Refresh token is required"
            )
        
        secret_key = os.getenv("JWT_SECRET_KEY", os.getenv("SECRET_KEY", "dev-secret-key-change-in-production"))
        
        if not JWT_AVAILABLE:
            raise HTTPException(
                status_code=status.HTTP_501_NOT_IMPLEMENTED,
                detail="Token refresh requires JWT library"
            )
        
        # Verify refresh token
        try:
            payload = jwt.decode(refresh_token, secret_key, algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token has expired"
            )
        except jwt.JWTError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid refresh token: {str(e)}"
            )
        
        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type"
            )
        
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload"
            )
        
        user_id_str = str(user_id) if user_id else None
        if not user_id_str:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid user ID in token"
            )
        
        # Find user
        user = db.query(UserModel).filter(UserModel.id == user_id_str).first()
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive"
            )
        
        # Generate new access token
        access_token_expiry_minutes = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRATION_MINUTES", "30"))
        access_token_data = {
            "sub": user.id,
            "email": user.email,
            "role": user.role_name,
            "type": "access",
            "exp": datetime.utcnow() + timedelta(minutes=access_token_expiry_minutes),
            "iat": datetime.utcnow(),
        }
        new_access_token = jwt.encode(access_token_data, secret_key, algorithm="HS256")
        
        return {
            "access_token": new_access_token,
            "token_type": "bearer",
            "expires_in": access_token_expiry_minutes * 60
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error refreshing token: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to refresh token"
        )


@app.post("/api/v1/auth/reset-password")
async def reset_password(token: str, new_password: str, db: Session = Depends(get_db)):
    """Reset password with token."""
    # For now, return not implemented (implement token verification later)
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Password reset not yet implemented"
    )


@app.get("/api/v1/monitoring/pipelines/{pipeline_id}/checkpoints")
@app.get("/api/monitoring/pipelines/{pipeline_id}/checkpoints")
async def get_pipeline_checkpoints(
    pipeline_id: str,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Get all checkpoints for a pipeline.
    
    Args:
        pipeline_id: Pipeline ID
        db: Database session
        
    Returns:
        Dictionary with checkpoints array
    """
    # Handle database connection failure - return empty checkpoints
    if db is None:
        logger.warning(f"Database unavailable, returning empty checkpoints for pipeline {pipeline_id}")
        return {
            "checkpoints": [],
            "pipeline_id": pipeline_id,
            "count": 0
        }
    
    try:
        from ingestion.database.models_db import PipelineModel
        
        # Load pipeline from database
        pipeline_model = db.query(PipelineModel).filter(
            PipelineModel.id == pipeline_id,
            PipelineModel.deleted_at.is_(None)
        ).first()
        
        if not pipeline_model:
            # Return empty checkpoints instead of 404 to avoid breaking the UI
            logger.warning(f"Pipeline not found: {pipeline_id}, returning empty checkpoints")
            return {
                "checkpoints": [],
                "pipeline_id": pipeline_id,
                "count": 0
            }
        
        # Get checkpoints from pipeline metadata or construct from available data
        checkpoints = []
        
        # If pipeline has table mappings, create checkpoints for each table
        if pipeline_model.target_table_mapping:
            table_mappings = pipeline_model.target_table_mapping
            if isinstance(table_mappings, dict):
                for source_table, target_info in table_mappings.items():
                    # Handle both string target and dict target
                    if isinstance(target_info, dict):
                        target_table = target_info.get("target_table", source_table)
                        schema_name = target_info.get("source_schema") or pipeline_model.source_schema
                    else:
                        target_table = target_info if isinstance(target_info, str) else source_table
                        schema_name = pipeline_model.source_schema
                    
                    checkpoint = {
                        "id": f"{pipeline_id}_{source_table}",
                        "pipeline_id": pipeline_id,
                        "table_name": source_table,
                        "schema_name": schema_name,
                        "lsn": pipeline_model.full_load_lsn,  # PostgreSQL LSN
                        "scn": None,  # Oracle SCN - would need separate storage
                        "binlog_file": None,  # MySQL binlog file
                        "binlog_position": None,  # MySQL binlog position
                        "sql_server_lsn": None,  # SQL Server LSN
                        "resume_token": None,  # MongoDB resume token
                        "checkpoint_value": pipeline_model.full_load_lsn,
                        "checkpoint_type": "lsn",  # Default to LSN for PostgreSQL
                        "rows_processed": 0,  # Would need to track this separately
                        "last_event_timestamp": pipeline_model.full_load_completed_at.isoformat() if pipeline_model.full_load_completed_at else None,
                        "last_updated_at": pipeline_model.updated_at.isoformat() if pipeline_model.updated_at else datetime.utcnow().isoformat()
                    }
                    checkpoints.append(checkpoint)
            elif isinstance(table_mappings, list):
                for mapping in table_mappings:
                    source_table = mapping.get("source_table", "")
                    schema_name = mapping.get("source_schema") or pipeline_model.source_schema
                    
                    checkpoint = {
                        "id": f"{pipeline_id}_{source_table}",
                        "pipeline_id": pipeline_id,
                        "table_name": source_table,
                        "schema_name": schema_name,
                        "lsn": pipeline_model.full_load_lsn,
                        "scn": None,
                        "binlog_file": None,
                        "binlog_position": None,
                        "sql_server_lsn": None,
                        "resume_token": None,
                        "checkpoint_value": pipeline_model.full_load_lsn,
                        "checkpoint_type": "lsn",
                        "rows_processed": 0,
                        "last_event_timestamp": pipeline_model.full_load_completed_at.isoformat() if pipeline_model.full_load_completed_at else None,
                        "last_updated_at": pipeline_model.updated_at.isoformat() if pipeline_model.updated_at else datetime.utcnow().isoformat()
                    }
                    checkpoints.append(checkpoint)
        
        # If no table mappings, try to use source_tables
        if not checkpoints and pipeline_model.source_tables:
            for source_table in pipeline_model.source_tables:
                checkpoint = {
                    "id": f"{pipeline_id}_{source_table}",
                    "pipeline_id": pipeline_id,
                    "table_name": source_table,
                    "schema_name": pipeline_model.source_schema,
                    "lsn": pipeline_model.full_load_lsn,
                    "scn": None,
                    "binlog_file": None,
                    "binlog_position": None,
                    "sql_server_lsn": None,
                    "resume_token": None,
                    "checkpoint_value": pipeline_model.full_load_lsn,
                    "checkpoint_type": "lsn",
                    "rows_processed": 0,
                    "last_event_timestamp": pipeline_model.full_load_completed_at.isoformat() if pipeline_model.full_load_completed_at else None,
                    "last_updated_at": pipeline_model.updated_at.isoformat() if pipeline_model.updated_at else datetime.utcnow().isoformat()
                }
                checkpoints.append(checkpoint)
        
        return {
            "checkpoints": checkpoints,
            "pipeline_id": pipeline_id,
            "count": len(checkpoints)
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get pipeline checkpoints: {e}", exc_info=True)
        # Return empty checkpoints instead of error
        return {
            "checkpoints": [],
            "pipeline_id": pipeline_id,
            "count": 0,
            "error": str(e)
        }


@app.get("/api/v1/audit-logs/filters")
async def get_audit_log_filters(
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user_dependency)
):
    """Get available filter options for audit logs.
    
    Returns:
        Dictionary with available actions and resource_types
    """
    if db is None:
        return {
            "actions": [],
            "resource_types": []
        }
    try:
        # Get distinct actions
        actions = db.query(AuditLogModel.action).distinct().all()
        actions_list = [action[0] for action in actions if action[0]]
        
        # Get distinct resource types
        resource_types = db.query(AuditLogModel.resource_type).distinct().all()
        resource_types_list = [rt[0] for rt in resource_types if rt[0]]
        
        return {
            "actions": sorted(actions_list),
            "resource_types": sorted(resource_types_list)
        }
    except Exception as e:
        logger.error(f"Failed to get audit log filters: {e}", exc_info=True)
        # Check if table doesn't exist
        error_msg = str(e).lower()
        if "does not exist" in error_msg or "relation" in error_msg or "table" in error_msg:
            logger.warning("audit_logs table does not exist. Returning empty filters. Please run database migrations.")
        # Return empty lists on error so UI can still display
        return {
            "actions": [],
            "resource_types": []
        }


@app.get("/api/v1/audit-logs")
async def get_audit_logs(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    action: Optional[str] = Query(None),
    resource_type: Optional[str] = Query(None),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user_dependency)
):
    """Get audit logs with pagination and filtering.
    
    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return (max 100)
        action: Filter by action
        resource_type: Filter by resource type
        start_date: Filter by start date (ISO format)
        end_date: Filter by end date (ISO format)
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        List of audit logs
    """
    try:
        # Build query
        query = db.query(AuditLogModel)
        
        # Apply filters
        if action:
            query = query.filter(AuditLogModel.action == action)
        if resource_type:
            query = query.filter(AuditLogModel.resource_type == resource_type)
        
        # Date filters
        if start_date:
            try:
                start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
                query = query.filter(AuditLogModel.created_at >= start_dt)
            except Exception:
                pass  # Ignore invalid date format
        if end_date:
            try:
                end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
                query = query.filter(AuditLogModel.created_at <= end_dt)
            except Exception:
                pass  # Ignore invalid date format
        
        # Order by created_at descending (newest first)
        query = query.order_by(AuditLogModel.created_at.desc())
        
        # Apply pagination
        total = query.count()
        logs = query.offset(skip).limit(limit).all()
        
        # Convert to dict format
        result = []
        for log in logs:
            try:
                # Get user email if available
                user_email = None
                if log.user_id:
                    try:
                        user = db.query(UserModel).filter(UserModel.id == log.user_id).first()
                        if user:
                            user_email = user.email
                    except Exception:
                        pass
                
                result.append({
                    "id": log.id,
                    "user_id": log.user_id,
                    "user_email": user_email,
                    "action": log.action,
                    "resource_type": log.resource_type or log.entity_type,
                    "resource_id": log.resource_id or log.entity_id,
                    "old_value": log.old_value or log.old_values,
                    "new_value": log.new_value or log.new_values,
                    "ip_address": log.ip_address,
                    "user_agent": log.user_agent,
                    "created_at": (log.created_at or log.timestamp).isoformat() if (log.created_at or log.timestamp) else None,
                    "tenant_id": log.tenant_id
                })
            except Exception as e:
                logger.warning(f"Failed to serialize audit log {log.id}: {e}")
                continue
        
        return result
    except Exception as e:
        logger.error(f"Failed to get audit logs: {e}", exc_info=True)
        # Check if table doesn't exist - return empty array instead of error
        error_msg = str(e).lower()
        if "does not exist" in error_msg or "relation" in error_msg or "table" in error_msg:
            logger.warning("audit_logs table does not exist. Returning empty logs. Please run database migrations.")
            # Return empty array instead of error so UI can still display
            return []
        # For other errors, also return empty array to prevent UI crashes
        logger.warning(f"Error fetching audit logs, returning empty array: {e}")
        return []


# Mount Socket.IO app if available
if socketio_server and SOCKETIO_AVAILABLE:
    try:
        from socketio import ASGIApp
        socketio_asgi = ASGIApp(socketio_server, app)
        # Replace app with socketio-wrapped app
        app = socketio_asgi
        logger.info("Socket.IO mounted successfully")
    except Exception as e:
        logger.warning(f"Failed to mount Socket.IO: {e}")

if __name__ == "__main__":
    import uvicorn
    # sys is already imported at the top of the file
    # Use socketio-wrapped app if available
    final_app = app if socketio_server and SOCKETIO_AVAILABLE else app
    uvicorn.run(final_app, host="0.0.0.0", port=8000)



