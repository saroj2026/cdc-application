"""Pipelines router."""
from fastapi import APIRouter, HTTPException, Depends, Query, Body, Request, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid
import logging

from ingestion.database import get_db
from ingestion.database.models_db import PipelineModel, PipelineStatus, CDCStatus, ConnectionModel, UserRole
from ingestion.routers.auth import get_current_user
from ingestion.rbac import require_roles, require_permission, require_sensitive_action
from ingestion.audit import log_audit_event, mask_sensitive_data
from ingestion.database_offset_utils import get_database_offset, update_pipeline_offset
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

router = APIRouter()


class PipelineCreate(BaseModel):
    name: str
    source_connection_id: str
    target_connection_id: str
    source_database: str
    source_schema: str
    source_tables: List[str]
    target_database: str
    target_schema: str
    mode: str  # full_load_only, cdc_only, full_load_and_cdc
    auto_create_target: Optional[bool] = False
    target_table_mapping: Optional[Dict[str, str]] = None


class PipelineUpdate(BaseModel):
    name: Optional[str] = None
    mode: Optional[str] = None
    source_tables: Optional[List[str]] = None
    target_table_mapping: Optional[Dict[str, str]] = None
    # Frontend sends these fields instead of mode
    cdc_enabled: Optional[bool] = None
    full_load_type: Optional[str] = None
    description: Optional[str] = None
    source_connection_id: Optional[str] = None
    target_connection_id: Optional[str] = None
    cdc_filters: Optional[List[Dict[str, Any]]] = None
    table_mappings: Optional[List[Dict[str, Any]]] = None


def pipeline_id_to_int(pipeline_id) -> int:
    """Convert UUID to numeric ID for frontend."""
    if isinstance(pipeline_id, int):
        return pipeline_id
    try:
        id_str = str(pipeline_id).replace("-", "")
        return int(id_str[:8], 16) if len(id_str) > 8 else abs(hash(str(pipeline_id))) % (10**9)
    except (ValueError, AttributeError):
        return abs(hash(str(pipeline_id))) % (10**9)


def connection_id_to_int(conn_id) -> int:
    """Convert connection UUID to numeric ID."""
    if isinstance(conn_id, int):
        return conn_id
    try:
        id_str = str(conn_id).replace("-", "")
        return int(id_str[:8], 16) if len(id_str) > 8 else abs(hash(str(conn_id))) % (10**9)
    except (ValueError, AttributeError):
        return abs(hash(str(conn_id))) % (10**9)


def map_status_to_frontend(status) -> str:
    """Map backend PipelineStatus enum to frontend status string."""
    # Handle both enum and string values
    if isinstance(status, str):
        status_upper = status.upper()
        # Map database enum values (STOPPED, STARTING, RUNNING, STOPPING, ERROR) to frontend
        db_status_mapping = {
            "RUNNING": "active",
            "STOPPED": "draft",
            "STARTING": "active",  # Starting is considered active
            "STOPPING": "paused",  # Stopping is considered paused
            "ERROR": "error",
        }
        if status_upper in db_status_mapping:
            return db_status_mapping[status_upper]
        
        # Fallback: try lowercase mapping (for Python enum values)
        status_mapping = {
            "inactive": "draft",
            "active": "active",
            "paused": "paused",
            "error": "error",
            "stopped": "draft",  # Handle invalid 'stopped' value
        }
        return status_mapping.get(status.lower(), "draft")
    
    # Handle enum
    mapping = {
        PipelineStatus.INACTIVE: "draft",
        PipelineStatus.ACTIVE: "active",
        PipelineStatus.PAUSED: "paused",
        PipelineStatus.ERROR: "error",
    }
    return mapping.get(status, "draft")


def pipeline_to_dict(pipeline: PipelineModel, db: Session = None) -> dict:
    """Convert pipeline model to dict matching frontend expectations."""
    try:
        # Build table_mappings from source_tables and target_table_mapping
        table_mappings = []
        source_tables = pipeline.source_tables or []
        target_tables = pipeline.target_tables or []
        target_table_mapping = {}
        try:
            if pipeline.sink_config and isinstance(pipeline.sink_config, dict):
                target_table_mapping = pipeline.sink_config.get("target_table_mapping", {})
        except (AttributeError, TypeError):
            target_table_mapping = {}
        
        for i, source_table in enumerate(source_tables):
            # Get target table name (from mapping or same as source)
            target_table = target_table_mapping.get(source_table, source_table)
            if isinstance(target_tables, list) and i < len(target_tables):
                target_table = target_tables[i]
            
            table_mappings.append({
                "source_schema": pipeline.source_schema or "",
                "source_table": source_table,
                "target_schema": pipeline.target_schema or "",
                "target_table": target_table
            })
        
        # Determine full_load_type from mode
        full_load_type = "overwrite"
        try:
            if pipeline.mode:
                if "append" in pipeline.mode.lower():
                    full_load_type = "append"
                elif "merge" in pipeline.mode.lower():
                    full_load_type = "merge"
        except (AttributeError, TypeError):
            full_load_type = "overwrite"
        
        # Determine cdc_enabled from mode
        cdc_enabled = False
        try:
            cdc_enabled = pipeline.mode and "cdc" in pipeline.mode.lower()
        except (AttributeError, TypeError):
            cdc_enabled = False
        
        # Safely get status - handle invalid enum values
        try:
            status_value = pipeline.status
            if hasattr(status_value, 'value'):
                status_value = status_value.value
            status_str = map_status_to_frontend(status_value)
        except (AttributeError, ValueError, TypeError) as status_error:
            # If status is invalid, try to get raw status from database
            try:
                # Try to get status as string directly
                if hasattr(pipeline, 'status'):
                    raw_status = str(pipeline.status)
                    # Try uppercase mapping for database enum values
                    if raw_status.upper() in ['RUNNING', 'STARTING']:
                        status_str = "active"
                    elif raw_status.upper() in ['STOPPED', 'STOPPING']:
                        status_str = "draft"
                    elif raw_status.upper() == 'ERROR':
                        status_str = "error"
                    else:
                        status_str = "draft"
                else:
                    status_str = "draft"
            except Exception:
                # If all else fails, default to draft
                status_str = "draft"
        
        # Safely get description
        description = ""
        try:
            if pipeline.debezium_config and isinstance(pipeline.debezium_config, dict):
                description = pipeline.debezium_config.get("description", "")
        except (AttributeError, TypeError):
            description = ""
        
        # Safely get cdc_filters
        cdc_filters = []
        try:
            if pipeline.debezium_config and isinstance(pipeline.debezium_config, dict):
                cdc_filters = pipeline.debezium_config.get("filters", [])
        except (AttributeError, TypeError):
            cdc_filters = []
        
        # Safely get connection IDs
        source_conn_id = 0
        target_conn_id = 0
        try:
            if pipeline.source_connection_id:
                source_conn_id = connection_id_to_int(pipeline.source_connection_id)
            if pipeline.target_connection_id:
                target_conn_id = connection_id_to_int(pipeline.target_connection_id)
        except (AttributeError, TypeError, ValueError):
            source_conn_id = 0
            target_conn_id = 0
        
        # Safely get CDC status
        cdc_status_str = "stopped"
        try:
            if hasattr(pipeline, 'cdc_status') and pipeline.cdc_status:
                if hasattr(pipeline.cdc_status, 'value'):
                    cdc_status_str = pipeline.cdc_status.value
                else:
                    cdc_status_str = str(pipeline.cdc_status)
        except (AttributeError, TypeError):
            cdc_status_str = "stopped"
        
        # Safely get dates
        created_at = None
        updated_at = None
        try:
            if pipeline.created_at:
                created_at = pipeline.created_at.isoformat() + "Z"
            if pipeline.updated_at:
                updated_at = pipeline.updated_at.isoformat() + "Z"
        except (AttributeError, TypeError):
            pass
        
        # Get actual connection UUIDs for frontend (in addition to numeric IDs)
        source_conn_uuid = None
        target_conn_uuid = None
        try:
            if pipeline.source_connection_id:
                source_conn_uuid = str(pipeline.source_connection_id)
            if pipeline.target_connection_id:
                target_conn_uuid = str(pipeline.target_connection_id)
        except (AttributeError, TypeError):
            pass
        
        # Safely get offset fields (may not exist on PipelineProxy objects)
        current_lsn = getattr(pipeline, 'current_lsn', None)
        current_offset = getattr(pipeline, 'current_offset', None)
        current_scn = getattr(pipeline, 'current_scn', None)
        last_offset_updated = getattr(pipeline, 'last_offset_updated', None)
        
        return {
            "id": pipeline_id_to_int(pipeline.id),
            "name": pipeline.name or "",
            "description": description,
            "source_connection_id": source_conn_id,
            "target_connection_id": target_conn_id,
            "source_connection_uuid": source_conn_uuid,  # Add actual UUID for connection lookup
            "target_connection_uuid": target_conn_uuid,  # Add actual UUID for connection lookup
            "source_database": pipeline.source_database or "",
            "source_schema": pipeline.source_schema or "",
            "source_tables": source_tables,
            "target_database": pipeline.target_database or "",
            "target_schema": pipeline.target_schema or "",
            "target_tables": target_tables,
            "mode": pipeline.mode or "",
            "full_load_type": full_load_type,
            "cdc_enabled": cdc_enabled,
            "cdc_filters": cdc_filters,
            "table_mappings": table_mappings,
            "airflow_dag_id": pipeline.debezium_connector_name or "",
            "status": status_str,
            "cdc_status": cdc_status_str,
            "current_lsn": current_lsn,
            "current_offset": current_offset,
            "current_scn": current_scn,
            "last_offset_updated": last_offset_updated.isoformat() + "Z" if last_offset_updated else None,
            "created_at": created_at,
            "updated_at": updated_at,
        }
    except Exception as e:
        # If anything fails, log and re-raise with context
        import traceback
        error_msg = f"Error in pipeline_to_dict: {str(e)}\n{traceback.format_exc()}"
        print(error_msg)
        raise ValueError(f"Failed to convert pipeline to dict: {str(e)}") from e


@router.get("")
async def list_pipelines(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """List all pipelines - returns array directly."""
    try:
        from sqlalchemy import text
        
        # First, fix any invalid status values in the database
        # Database enum: STOPPED, STARTING, RUNNING, STOPPING, ERROR
        # Map invalid values to STOPPED
        try:
            db.execute(
                text("""
                    UPDATE pipelines 
                    SET status = 'STOPPED'::pipelinestatus
                    WHERE status::text NOT IN ('STOPPED', 'STARTING', 'RUNNING', 'STOPPING', 'ERROR')
                """)
            )
            db.commit()
        except Exception as fix_error:
            db.rollback()
            # Continue even if update fails - might be permission issue
        
        # Try to query pipelines normally first
        try:
            pipelines = db.query(PipelineModel).offset(skip).limit(limit).all()
            # Return array directly (not wrapped in object)
            return [pipeline_to_dict(p, db) for p in pipelines]
        except Exception as orm_error:
            # If ORM query fails (e.g., enum conversion error), use raw SQL
            db.rollback()
            try:
                # Check if offset columns exist before selecting them
                try:
                    check_result = db.execute(text("""
                        SELECT column_name 
                        FROM information_schema.columns 
                        WHERE table_name = 'pipelines' 
                        AND column_name IN ('current_lsn', 'current_offset', 'current_scn', 'last_offset_updated')
                    """))
                    offset_columns_exist = len(check_result.fetchall()) > 0
                except Exception:
                    offset_columns_exist = False
                
                # Build query with or without offset columns
                if offset_columns_exist:
                    query_sql = """
                        SELECT id, name, source_connection_id, target_connection_id,
                               source_database, source_schema, source_tables,
                               target_database, target_schema, target_tables,
                               mode, status::text, cdc_status::text, debezium_connector_name,
                               sink_connector_name, kafka_topics, debezium_config, sink_config,
                               current_lsn, current_offset, current_scn, last_offset_updated,
                               created_at, updated_at
                        FROM pipelines
                        ORDER BY created_at DESC
                        LIMIT :limit OFFSET :skip
                    """
                else:
                    query_sql = """
                        SELECT id, name, source_connection_id, target_connection_id,
                               source_database, source_schema, source_tables,
                               target_database, target_schema, target_tables,
                               mode, status::text, cdc_status::text, debezium_connector_name,
                               sink_connector_name, kafka_topics, debezium_config, sink_config,
                               NULL::text as current_lsn, NULL::text as current_offset, 
                               NULL::text as current_scn, NULL::timestamp as last_offset_updated,
                               created_at, updated_at
                        FROM pipelines
                        ORDER BY created_at DESC
                        LIMIT :limit OFFSET :skip
                    """
                
                result = db.execute(text(query_sql), {"limit": limit, "skip": skip})
                
                result_list = []
                for row in result:
                    # Create a proxy object to mimic PipelineModel for pipeline_to_dict
                    class PipelineProxy:
                        def __init__(self, row_data):
                            self.id = uuid.UUID(row_data[0])
                            self.name = row_data[1]
                            self.source_connection_id = uuid.UUID(row_data[2]) if row_data[2] else None
                            self.target_connection_id = uuid.UUID(row_data[3]) if row_data[3] else None
                            self.source_database = row_data[4]
                            self.source_schema = row_data[5]
                            self.source_tables = row_data[6] if isinstance(row_data[6], list) else []
                            self.target_database = row_data[7]
                            self.target_schema = row_data[8]
                            self.target_tables = row_data[9] if isinstance(row_data[9], list) else []
                            self.mode = row_data[10]
                            # Map database enum values to Python enum
                            # Database: STOPPED, STARTING, RUNNING, STOPPING, ERROR
                            # Python: ACTIVE, INACTIVE, ERROR, PAUSED
                            db_status = row_data[11] or 'STOPPED'
                            if db_status == 'RUNNING':
                                self.status = PipelineStatus.ACTIVE
                            elif db_status == 'STOPPED':
                                self.status = PipelineStatus.INACTIVE
                            elif db_status == 'ERROR':
                                self.status = PipelineStatus.ERROR
                            elif db_status in ['STARTING', 'STOPPING']:
                                self.status = PipelineStatus.INACTIVE  # Map intermediate states to INACTIVE
                            else:
                                self.status = PipelineStatus.INACTIVE
                            
                            # Map CDC status: Database: NOT_STARTED, STARTING, RUNNING, STOPPED, ERROR
                            # Python: RUNNING, STOPPED, ERROR, PAUSED
                            db_cdc_status = row_data[12] or 'STOPPED'
                            if db_cdc_status == 'RUNNING':
                                self.cdc_status = CDCStatus.RUNNING
                            elif db_cdc_status == 'STOPPED':
                                self.cdc_status = CDCStatus.STOPPED
                            elif db_cdc_status == 'ERROR':
                                self.cdc_status = CDCStatus.ERROR
                            elif db_cdc_status in ['NOT_STARTED', 'STARTING']:
                                self.cdc_status = CDCStatus.STOPPED  # Map initial states to STOPPED
                            else:
                                self.cdc_status = CDCStatus.STOPPED
                            self.debezium_connector_name = row_data[13]
                            self.sink_connector_name = row_data[14]
                            self.kafka_topics = row_data[15]
                            self.debezium_config = row_data[16] or {}
                            self.sink_config = row_data[17] or {}
                            # Offset fields (added in migration)
                            self.current_lsn = row_data[18] if len(row_data) > 18 else None
                            self.current_offset = row_data[19] if len(row_data) > 19 else None
                            self.current_scn = row_data[20] if len(row_data) > 20 else None
                            self.last_offset_updated = row_data[21] if len(row_data) > 21 else None
                            self.created_at = row_data[22] if len(row_data) > 22 else None
                            self.updated_at = row_data[23] if len(row_data) > 23 else None
                    
                    proxy = PipelineProxy(row)
                    # Ensure connection UUIDs are available as strings for frontend
                    if proxy.source_connection_id:
                        proxy.source_connection_id = str(proxy.source_connection_id)
                    if proxy.target_connection_id:
                        proxy.target_connection_id = str(proxy.target_connection_id)
                    result_list.append(pipeline_to_dict(proxy, db))
                
                return result_list
            except Exception as e2:
                raise HTTPException(status_code=500, detail=f"Failed to fetch pipelines: {str(e2)}")
    except Exception as e:
        # If enum conversion still fails (e.g., database has other invalid values),
        # use raw SQL query as fallback
        try:
            from sqlalchemy import text
            # Check if offset columns exist
            try:
                check_result = db.execute(text("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = 'pipelines' 
                    AND column_name IN ('current_lsn', 'current_offset', 'current_scn', 'last_offset_updated')
                """))
                offset_columns_exist = len(check_result.fetchall()) > 0
            except Exception:
                offset_columns_exist = False
            
            # Build query with or without offset columns
            if offset_columns_exist:
                query_sql = """
                    SELECT id::text, name, source_connection_id::text, target_connection_id::text,
                           source_database, source_schema, source_tables,
                           target_database, target_schema, target_tables,
                           mode, 
                           CASE 
                               WHEN status::text IN ('STOPPED', 'STARTING', 'RUNNING', 'STOPPING', 'ERROR') THEN status::text
                               ELSE 'STOPPED'
                           END as status,
                           cdc_status::text as cdc_status, debezium_connector_name,
                           debezium_config, sink_config, 
                           current_lsn, current_offset, current_scn, last_offset_updated,
                           created_at, updated_at
                    FROM pipelines
                    ORDER BY created_at DESC
                    LIMIT :limit OFFSET :skip
                """
            else:
                query_sql = """
                    SELECT id::text, name, source_connection_id::text, target_connection_id::text,
                           source_database, source_schema, source_tables,
                           target_database, target_schema, target_tables,
                           mode, 
                           CASE 
                               WHEN status::text IN ('STOPPED', 'STARTING', 'RUNNING', 'STOPPING', 'ERROR') THEN status::text
                               ELSE 'STOPPED'
                           END as status,
                           cdc_status::text as cdc_status, debezium_connector_name,
                           debezium_config, sink_config, 
                           NULL::text as current_lsn, NULL::text as current_offset, 
                           NULL::text as current_scn, NULL::timestamp as last_offset_updated,
                           created_at, updated_at
                    FROM pipelines
                    ORDER BY created_at DESC
                    LIMIT :limit OFFSET :skip
                """
            
            result = db.execute(text(query_sql), {"limit": limit, "skip": skip})
            
            pipelines_data = result.fetchall()
            result_list = []
            for row in pipelines_data:
                # Create a dict that matches PipelineModel structure
                class PipelineProxy:
                    def __init__(self, row_data):
                        self.id = uuid.UUID(row_data[0])
                        self.name = row_data[1]
                        self.source_connection_id = uuid.UUID(row_data[2]) if row_data[2] else None
                        self.target_connection_id = uuid.UUID(row_data[3]) if row_data[3] else None
                        self.source_database = row_data[4]
                        self.source_schema = row_data[5]
                        self.source_tables = row_data[6] if isinstance(row_data[6], list) else []
                        self.target_database = row_data[7]
                        self.target_schema = row_data[8]
                        self.target_tables = row_data[9] if isinstance(row_data[9], list) else []
                        self.mode = row_data[10]
                        # Convert database enum status string to Python enum
                        # Database enum: STOPPED, STARTING, RUNNING, STOPPING, ERROR
                        # Python enum: ACTIVE, INACTIVE, ERROR, PAUSED
                        db_status = row_data[11] or 'STOPPED'
                        if db_status == 'RUNNING':
                            self.status = PipelineStatus.ACTIVE
                        elif db_status == 'STOPPED':
                            self.status = PipelineStatus.INACTIVE
                        elif db_status == 'ERROR':
                            self.status = PipelineStatus.ERROR
                        elif db_status in ['STARTING', 'STOPPING']:
                            self.status = PipelineStatus.INACTIVE  # Map intermediate states to INACTIVE
                        else:
                            self.status = PipelineStatus.INACTIVE
                        
                        # Convert CDC status: Database: NOT_STARTED, STARTING, RUNNING, STOPPED, ERROR
                        # Python: RUNNING, STOPPED, ERROR, PAUSED
                        db_cdc_status = row_data[12] or 'STOPPED'
                        if db_cdc_status == 'RUNNING':
                            self.cdc_status = CDCStatus.RUNNING
                        elif db_cdc_status == 'STOPPED':
                            self.cdc_status = CDCStatus.STOPPED
                        elif db_cdc_status == 'ERROR':
                            self.cdc_status = CDCStatus.ERROR
                        elif db_cdc_status in ['NOT_STARTED', 'STARTING']:
                            self.cdc_status = CDCStatus.STOPPED  # Map initial states to STOPPED
                        else:
                            self.cdc_status = CDCStatus.STOPPED
                        
                        # CDC status mapping already done above
                        # No need for additional try/except
                        self.debezium_connector_name = row_data[13]
                        self.debezium_config = row_data[14] or {}
                        self.sink_config = row_data[15] or {}
                        # Offset fields (added in migration)
                        self.current_lsn = row_data[16] if len(row_data) > 16 else None
                        self.current_offset = row_data[17] if len(row_data) > 17 else None
                        self.current_scn = row_data[18] if len(row_data) > 18 else None
                        self.last_offset_updated = row_data[19] if len(row_data) > 19 else None
                        self.created_at = row_data[20] if len(row_data) > 20 else None
                        self.updated_at = row_data[21] if len(row_data) > 21 else None
                
                proxy = PipelineProxy(row)
                # Ensure connection UUIDs are available as strings for frontend
                if proxy.source_connection_id:
                    proxy.source_connection_id = str(proxy.source_connection_id)
                if proxy.target_connection_id:
                    proxy.target_connection_id = str(proxy.target_connection_id)
                result_list.append(pipeline_to_dict(proxy, db))
            
            return result_list
        except Exception as e2:
            raise HTTPException(status_code=500, detail=f"Failed to fetch pipelines: {str(e2)}")


@router.post("")
async def create_pipeline(
    pipeline: PipelineCreate,
    request: Request,
    current_user = Depends(require_permission("create_pipeline")),
    db: Session = Depends(get_db)
):
    """Create a new pipeline - requires DATA_ENGINEER, ORG_ADMIN, or SUPER_ADMIN role."""
    try:
        # Check if pipeline with same name exists
        try:
            existing = db.query(PipelineModel).filter(PipelineModel.name == pipeline.name).first()
        except Exception:
            # If ORM fails (e.g., missing offset columns), use raw SQL
            db.rollback()
            result = db.execute(text("SELECT id FROM pipelines WHERE name = :name"), {"name": pipeline.name})
            existing = result.fetchone()
        
        if existing:
            raise HTTPException(status_code=400, detail="Pipeline with this name already exists")
        
        # Convert connection IDs from string to UUID
        try:
            source_conn_id = uuid.UUID(pipeline.source_connection_id)
            target_conn_id = uuid.UUID(pipeline.target_connection_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid connection ID format")
        
        # Verify connections exist
        source_conn = db.query(ConnectionModel).filter(ConnectionModel.id == str(source_conn_id)).first()
        target_conn = db.query(ConnectionModel).filter(ConnectionModel.id == str(target_conn_id)).first()
        if not source_conn or not target_conn:
            raise HTTPException(status_code=404, detail="Source or target connection not found")
        
        # Build target_table_mapping
        target_table_mapping = pipeline.target_table_mapping or {}
        target_tables = [target_table_mapping.get(t, t) for t in pipeline.source_tables]
        
        # Import CDCStatus
        from ingestion.database.models_db import CDCStatus
        
        # Create pipeline
        new_pipeline = PipelineModel(
            id=uuid.uuid4(),
            name=pipeline.name,
            source_connection_id=source_conn_id,
            target_connection_id=target_conn_id,
            source_database=pipeline.source_database,
            source_schema=pipeline.source_schema,
            source_tables=pipeline.source_tables,
            target_database=pipeline.target_database,
            target_schema=pipeline.target_schema,
            target_tables=target_tables,
            mode=pipeline.mode,
            status=PipelineStatus.INACTIVE,  # Maps to 'draft' in frontend
            cdc_status=CDCStatus.STOPPED,  # Use enum value, not None
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        db.add(new_pipeline)
        db.commit()
        db.refresh(new_pipeline)
        
        pipeline_dict = pipeline_to_dict(new_pipeline, db)
        
        # Log audit event
        log_audit_event(
            db=db,
            user=current_user,
            action="create_pipeline",
            resource_type="pipeline",
            resource_id=str(new_pipeline.id),
            new_value=mask_sensitive_data(pipeline_dict),
            request=request
        )
        
        return pipeline_dict
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create pipeline: {str(e)}")


@router.get("/{pipeline_id}")
async def get_pipeline(pipeline_id: str, db: Session = Depends(get_db)):
    """Get pipeline by ID."""
    try:
        from sqlalchemy import text
        
        # First, fix any invalid status values in the database to prevent enum errors
        pipeline_id = pipeline_id.strip()  # Handle URL encoded spaces
        pipeline_found = False
        pipeline_uuid_obj = None
        
        try:
            pipeline_uuid_obj = uuid.UUID(pipeline_id)
            result = db.execute(
                text("SELECT id FROM pipelines WHERE id = :pipeline_id"),
                {"pipeline_id": pipeline_uuid_obj}
            )
            if result.fetchone():
                pipeline_found = True
        except ValueError:
            # Not a valid UUID, try numeric ID
            try:
                numeric_id = int(pipeline_id)
                result = db.execute(
                    text("SELECT id FROM pipelines")
                )
                all_ids = result.fetchall()
                for (db_id,) in all_ids:
                    if pipeline_id_to_int(str(db_id)) == numeric_id:
                        pipeline_uuid_obj = db_id
                        pipeline_found = True
                        break
            except ValueError:
                pass
        
        if not pipeline_found or pipeline_uuid_obj is None:
            raise HTTPException(status_code=404, detail="Pipeline not found")
        
        # Fix any invalid status values for this pipeline
        # Database enum: ACTIVE, INACTIVE, ERROR, PAUSED
        try:
            db.execute(
                text("""
                    UPDATE pipelines 
                    SET status = 'STOPPED'::pipelinestatus
                    WHERE id = :pipeline_id 
                    AND status::text NOT IN ('STOPPED', 'STARTING', 'RUNNING', 'STOPPING', 'ERROR')
                """),
                {"pipeline_id": pipeline_uuid_obj}
            )
            db.commit()
        except Exception:
            db.rollback()
            # Continue even if fix fails
        
        # Try to query pipeline normally first
        try:
            pipeline = db.query(PipelineModel).filter(PipelineModel.id == pipeline_uuid_obj).first()
            if pipeline:
                try:
                    return pipeline_to_dict(pipeline, db)
                except Exception as dict_error:
                    # If pipeline_to_dict fails, fall through to raw SQL
                    db.rollback()
                    raise dict_error
        except Exception as model_error:
            # If model query fails (e.g., enum conversion error), use raw SQL
            db.rollback()
            try:
                # Check if offset columns exist
                try:
                    check_result = db.execute(text("""
                        SELECT column_name 
                        FROM information_schema.columns 
                        WHERE table_name = 'pipelines' 
                        AND column_name IN ('current_lsn', 'current_offset', 'current_scn', 'last_offset_updated')
                    """))
                    offset_columns_exist = len(check_result.fetchall()) > 0
                except Exception:
                    offset_columns_exist = False
                
                # Build query with or without offset columns
                if offset_columns_exist:
                    query_sql = """
                        SELECT id, name, source_connection_id, target_connection_id,
                               source_database, source_schema, source_tables,
                               target_database, target_schema, target_tables,
                               mode, status::text, cdc_status::text, debezium_connector_name,
                               sink_connector_name, kafka_topics, debezium_config, sink_config,
                               current_lsn, current_offset, current_scn, last_offset_updated,
                               created_at, updated_at
                        FROM pipelines
                        WHERE id = :pipeline_id
                    """
                else:
                    query_sql = """
                        SELECT id, name, source_connection_id, target_connection_id,
                               source_database, source_schema, source_tables,
                               target_database, target_schema, target_tables,
                               mode, status::text, cdc_status::text, debezium_connector_name,
                               sink_connector_name, kafka_topics, debezium_config, sink_config,
                               NULL::text as current_lsn, NULL::text as current_offset, 
                               NULL::text as current_scn, NULL::timestamp as last_offset_updated,
                               created_at, updated_at
                        FROM pipelines
                        WHERE id = :pipeline_id
                    """
                
                result = db.execute(text(query_sql), {"pipeline_id": pipeline_uuid_obj})
                row = result.fetchone()
                if not row:
                    raise HTTPException(status_code=404, detail="Pipeline not found")
                
                # Create a proxy object to mimic PipelineModel for pipeline_to_dict
                class PipelineProxy:
                    def __init__(self, row_data):
                        self.id = uuid.UUID(row_data[0])
                        self.name = row_data[1]
                        self.source_connection_id = uuid.UUID(row_data[2]) if row_data[2] else None
                        self.target_connection_id = uuid.UUID(row_data[3]) if row_data[3] else None
                        self.source_database = row_data[4]
                        self.source_schema = row_data[5]
                        self.source_tables = row_data[6] if isinstance(row_data[6], list) else []
                        self.target_database = row_data[7]
                        self.target_schema = row_data[8]
                        self.target_tables = row_data[9] if isinstance(row_data[9], list) else []
                        self.mode = row_data[10]
                        # Convert database enum status string to Python enum
                        # Database enum: STOPPED, STARTING, RUNNING, STOPPING, ERROR
                        # Python enum: ACTIVE, INACTIVE, ERROR, PAUSED
                        db_status = row_data[11] or 'STOPPED'
                        if db_status == 'RUNNING':
                            self.status = PipelineStatus.ACTIVE
                        elif db_status == 'STOPPED':
                            self.status = PipelineStatus.INACTIVE
                        elif db_status == 'ERROR':
                            self.status = PipelineStatus.ERROR
                        elif db_status in ['STARTING', 'STOPPING']:
                            self.status = PipelineStatus.INACTIVE  # Map intermediate states to INACTIVE
                        else:
                            self.status = PipelineStatus.INACTIVE
                        
                        # Convert CDC status: Database: NOT_STARTED, STARTING, RUNNING, STOPPED, ERROR
                        # Python: RUNNING, STOPPED, ERROR, PAUSED
                        db_cdc_status = row_data[12] or 'STOPPED'
                        if db_cdc_status == 'RUNNING':
                            self.cdc_status = CDCStatus.RUNNING
                        elif db_cdc_status == 'STOPPED':
                            self.cdc_status = CDCStatus.STOPPED
                        elif db_cdc_status == 'ERROR':
                            self.cdc_status = CDCStatus.ERROR
                        elif db_cdc_status in ['NOT_STARTED', 'STARTING']:
                            self.cdc_status = CDCStatus.STOPPED  # Map initial states to STOPPED
                        else:
                            self.cdc_status = CDCStatus.STOPPED
                        
                        # Status and CDC status mapping already done above
                        # No additional mapping needed
                        self.debezium_connector_name = row_data[13]
                        self.sink_connector_name = row_data[14]
                        self.kafka_topics = row_data[15]
                        self.debezium_config = row_data[16] or {}
                        self.sink_config = row_data[17] or {}
                        # Offset fields (added in migration)
                        self.current_lsn = row_data[18] if len(row_data) > 18 else None
                        self.current_offset = row_data[19] if len(row_data) > 19 else None
                        self.current_scn = row_data[20] if len(row_data) > 20 else None
                        self.last_offset_updated = row_data[21] if len(row_data) > 21 else None
                        self.created_at = row_data[22] if len(row_data) > 22 else row_data[18]
                        self.updated_at = row_data[23] if len(row_data) > 23 else row_data[19]
                
                proxy = PipelineProxy(row)
                # Ensure connection UUIDs are available as strings for frontend
                if proxy.source_connection_id:
                    proxy.source_connection_id = str(proxy.source_connection_id)
                if proxy.target_connection_id:
                    proxy.target_connection_id = str(proxy.target_connection_id)
                return pipeline_to_dict(proxy, db)
            except HTTPException:
                raise
            except Exception as sql_error:
                raise HTTPException(status_code=500, detail=f"Failed to get pipeline: {str(sql_error)}")
        
        # If we get here, pipeline was not found
        raise HTTPException(status_code=404, detail="Pipeline not found")
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to get pipeline: {str(e)}")


@router.put("/{pipeline_id}")
async def update_pipeline(
    pipeline_id: str,
    pipeline: PipelineUpdate,
    request: Request,
    current_user = Depends(require_permission("create_pipeline")),
    db: Session = Depends(get_db)
):
    """Update pipeline."""
    try:
        from sqlalchemy import text
        
        # Find pipeline using raw SQL first to avoid enum conversion errors
        pipeline_found = False
        pipeline_uuid_obj = None
        try:
            pipeline_uuid_obj = uuid.UUID(pipeline_id)
            result = db.execute(
                text("SELECT id FROM pipelines WHERE id = :pipeline_id"),
                {"pipeline_id": pipeline_uuid_obj}
            )
            if result.fetchone():
                pipeline_found = True
        except ValueError:
            # Not a valid UUID, try numeric ID
            try:
                numeric_id = int(pipeline_id)
                result = db.execute(text("SELECT id FROM pipelines"))
                all_ids = result.fetchall()
                for (db_id,) in all_ids:
                    if pipeline_id_to_int(str(db_id)) == numeric_id:
                        pipeline_uuid_obj = db_id
                        pipeline_found = True
                        break
            except ValueError:
                pass
        
        if not pipeline_found or pipeline_uuid_obj is None:
            raise HTTPException(status_code=404, detail="Pipeline not found")
        
        # First, fix any invalid status values in the database to prevent enum errors
        # Database enum: STOPPED, STARTING, RUNNING, STOPPING, ERROR
        try:
            db.execute(
                text("""
                    UPDATE pipelines 
                    SET status = 'STOPPED'::pipelinestatus
                    WHERE id = :pipeline_id 
                    AND status::text NOT IN ('STOPPED', 'STARTING', 'RUNNING', 'STOPPING', 'ERROR')
                """),
                {"pipeline_id": pipeline_uuid_obj}
            )
            db.commit()
        except Exception:
            db.rollback()
        
        # Now get pipeline using ORM (status should be valid now)
        try:
            db_pipeline = db.query(PipelineModel).filter(PipelineModel.id == pipeline_uuid_obj).first()
        except Exception as orm_err:
            # If ORM still fails, rollback and use raw SQL for everything
            try:
                db.rollback()
            except Exception:
                pass  # Already rolled back or no transaction
            db_pipeline = None
        
        # Convert frontend fields (cdc_enabled, full_load_type) to mode if provided
        mode_to_update = pipeline.mode
        if pipeline.cdc_enabled is not None or pipeline.full_load_type is not None:
            # Determine mode from cdc_enabled and full_load_type
            if pipeline.cdc_enabled is False:
                # CDC disabled - always full_load_only regardless of full_load_type
                mode_to_update = "full_load_only"
            elif pipeline.cdc_enabled is True:
                # CDC enabled - determine based on full_load_type
                if pipeline.full_load_type == "overwrite":
                    mode_to_update = "full_load_and_cdc"
                elif pipeline.full_load_type == "append":
                    mode_to_update = "cdc_only"
                else:
                    # Default to full_load_and_cdc if full_load_type not specified
                    mode_to_update = "full_load_and_cdc"
            # If mode is explicitly provided, use it (but cdc_enabled takes precedence)
            elif pipeline.mode is not None:
                mode_to_update = pipeline.mode
        
        # Determine CDC status based on mode
        # Database enum: NOT_STARTED, STARTING, RUNNING, STOPPED, ERROR
        cdc_status_to_update = None
        if mode_to_update:
            if mode_to_update in ["full_load_and_cdc", "cdc_only"]:
                cdc_status_to_update = "RUNNING"
            elif mode_to_update == "full_load_only":
                cdc_status_to_update = "STOPPED"
        
        # Use raw SQL to update to avoid enum validation issues
        try:
            import json
            update_fields = []
            params = {"pipeline_id": pipeline_uuid_obj, "updated_at": datetime.utcnow()}
            
            if pipeline.name is not None:
                update_fields.append("name = :name")
                params["name"] = pipeline.name
            
            if mode_to_update is not None:
                update_fields.append("mode = :mode")
                params["mode"] = mode_to_update
            
            if cdc_status_to_update is not None:
                # Use CAST instead of :: syntax to avoid parameter binding issues
                update_fields.append("cdc_status = CAST(:cdc_status AS cdcstatus)")
                params["cdc_status"] = cdc_status_to_update
            
            # Handle connection ID updates (only if provided and not empty)
            if pipeline.source_connection_id is not None and pipeline.source_connection_id != "":
                try:
                    source_conn_uuid = uuid.UUID(pipeline.source_connection_id)
                    update_fields.append("source_connection_id = :source_connection_id")
                    params["source_connection_id"] = source_conn_uuid
                except ValueError:
                    # If not a valid UUID, try to find by numeric ID
                    try:
                        # Ensure transaction is clean before querying
                        # If there was a previous error, rollback first
                        try:
                            db.rollback()
                        except Exception:
                            pass  # No active transaction or already rolled back
                        
                        numeric_id = int(pipeline.source_connection_id)
                        result = db.execute(text("SELECT id FROM connections"))
                        all_conn_ids = result.fetchall()
                        for (conn_id,) in all_conn_ids:
                            # Import here to avoid circular dependency
                            try:
                                id_str = str(conn_id).replace("-", "")
                                conn_numeric_id = int(id_str[:8], 16) if len(id_str) > 8 else abs(hash(str(conn_id))) % (10**9)
                                if conn_numeric_id == numeric_id:
                                    update_fields.append("source_connection_id = :source_connection_id")
                                    params["source_connection_id"] = conn_id
                                    break
                            except (ValueError, AttributeError):
                                continue
                    except (ValueError, TypeError):
                        pass  # Skip if can't convert
            
            if pipeline.target_connection_id is not None and pipeline.target_connection_id != "":
                try:
                    target_conn_uuid = uuid.UUID(pipeline.target_connection_id)
                    update_fields.append("target_connection_id = :target_connection_id")
                    params["target_connection_id"] = target_conn_uuid
                except ValueError:
                    # If not a valid UUID, try to find by numeric ID
                    try:
                        # Ensure transaction is clean before querying
                        # If there was a previous error, rollback first
                        try:
                            db.rollback()
                        except Exception:
                            pass  # No active transaction or already rolled back
                        
                        numeric_id = int(pipeline.target_connection_id)
                        result = db.execute(text("SELECT id FROM connections"))
                        all_conn_ids = result.fetchall()
                        for (conn_id,) in all_conn_ids:
                            # Import here to avoid circular dependency
                            try:
                                id_str = str(conn_id).replace("-", "")
                                conn_numeric_id = int(id_str[:8], 16) if len(id_str) > 8 else abs(hash(str(conn_id))) % (10**9)
                                if conn_numeric_id == numeric_id:
                                    update_fields.append("target_connection_id = :target_connection_id")
                                    params["target_connection_id"] = conn_id
                                    break
                            except (ValueError, AttributeError):
                                continue
                    except (ValueError, TypeError):
                        pass  # Skip if can't convert
            
            if pipeline.source_tables is not None:
                update_fields.append("source_tables = :source_tables::jsonb")
                params["source_tables"] = json.dumps(pipeline.source_tables)
            
            # Handle table_mappings if provided (convert to source_tables and target_tables)
            if pipeline.table_mappings is not None and len(pipeline.table_mappings) > 0:
                source_tables_list = []
                target_tables_list = []
                target_mapping_dict = {}
                
                for mapping in pipeline.table_mappings:
                    source_table = mapping.get("source_table", "")
                    target_table = mapping.get("target_table", source_table)
                    
                    source_tables_list.append(source_table)
                    target_tables_list.append(target_table)
                    target_mapping_dict[source_table] = target_table
                
                update_fields.append("source_tables = :source_tables::jsonb")
                params["source_tables"] = json.dumps(source_tables_list)
                
                update_fields.append("target_tables = :target_tables::jsonb")
                params["target_tables"] = json.dumps(target_tables_list)
                
                # Update sink_config with target_table_mapping
                # Get current sink_config using raw SQL to avoid ORM issues
                try:
                    sink_config_result = db.execute(
                        text("SELECT sink_config FROM pipelines WHERE id = :pipeline_id"),
                        {"pipeline_id": pipeline_uuid_obj}
                    )
                    sink_config_row = sink_config_result.fetchone()
                    sink_config = sink_config_row[0].copy() if sink_config_row and sink_config_row[0] else {}
                except Exception:
                    sink_config = {}
                sink_config["target_table_mapping"] = target_mapping_dict
                update_fields.append("sink_config = :sink_config::jsonb")
                params["sink_config"] = json.dumps(sink_config)
            
            if update_fields:
                update_fields.append("updated_at = :updated_at")
                db.execute(
                    text(f"UPDATE pipelines SET {', '.join(update_fields)} WHERE id = :pipeline_id"),
                    params
                )
                db.commit()
        except Exception as sql_error:
            db.rollback()
            raise HTTPException(status_code=500, detail=f"Failed to update pipeline: {str(sql_error)}")
        
        # Get the full updated pipeline using get_pipeline logic
        # This ensures we return the complete pipeline object
        try:
            # Check if offset columns exist
            try:
                check_result = db.execute(text("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = 'pipelines' 
                    AND column_name IN ('current_lsn', 'current_offset', 'current_scn', 'last_offset_updated')
                """))
                offset_columns_exist = len(check_result.fetchall()) > 0
            except Exception:
                offset_columns_exist = False
            
            # Build query with or without offset columns
            if offset_columns_exist:
                query_sql = """
                    SELECT id, name, source_connection_id, target_connection_id,
                           source_database, source_schema, source_tables,
                           target_database, target_schema, target_tables,
                           mode, status::text, cdc_status::text, debezium_connector_name,
                           sink_connector_name, kafka_topics, debezium_config, sink_config,
                           current_lsn, current_offset, current_scn, last_offset_updated,
                           created_at, updated_at
                    FROM pipelines 
                    WHERE id = :pipeline_id
                """
            else:
                query_sql = """
                    SELECT id, name, source_connection_id, target_connection_id,
                           source_database, source_schema, source_tables,
                           target_database, target_schema, target_tables,
                           mode, status::text, cdc_status::text, debezium_connector_name,
                           sink_connector_name, kafka_topics, debezium_config, sink_config,
                           NULL::text as current_lsn, NULL::text as current_offset, 
                           NULL::text as current_scn, NULL::timestamp as last_offset_updated,
                           created_at, updated_at
                    FROM pipelines 
                    WHERE id = :pipeline_id
                """
            
            result = db.execute(text(query_sql), {"pipeline_id": pipeline_uuid_obj})
            row = result.fetchone()
            if row:
                # Create a proxy object for pipeline_to_dict
                class PipelineProxy:
                    def __init__(self, row_data):
                        self.id = uuid.UUID(row_data[0])
                        self.name = row_data[1]
                        self.source_connection_id = uuid.UUID(row_data[2]) if row_data[2] else None
                        self.target_connection_id = uuid.UUID(row_data[3]) if row_data[3] else None
                        self.source_database = row_data[4]
                        self.source_schema = row_data[5]
                        self.source_tables = row_data[6] if isinstance(row_data[6], list) else []
                        self.target_database = row_data[7]
                        self.target_schema = row_data[8]
                        self.target_tables = row_data[9] if isinstance(row_data[9], list) else []
                        self.mode = row_data[10]
                        # Map database enum values to Python enum
                        db_status = row_data[11] or 'STOPPED'
                        if db_status == 'RUNNING':
                            self.status = PipelineStatus.ACTIVE
                        elif db_status == 'STOPPED':
                            self.status = PipelineStatus.INACTIVE
                        elif db_status == 'ERROR':
                            self.status = PipelineStatus.ERROR
                        elif db_status in ['STARTING', 'STOPPING']:
                            self.status = PipelineStatus.INACTIVE
                        else:
                            self.status = PipelineStatus.INACTIVE
                        # Map CDC status
                        db_cdc_status = row_data[12] or 'STOPPED'
                        if db_cdc_status == 'RUNNING':
                            self.cdc_status = CDCStatus.RUNNING
                        elif db_cdc_status == 'STOPPED':
                            self.cdc_status = CDCStatus.STOPPED
                        elif db_cdc_status == 'ERROR':
                            self.cdc_status = CDCStatus.ERROR
                        else:
                            self.cdc_status = CDCStatus.STOPPED
                        self.debezium_connector_name = row_data[13]
                        self.sink_connector_name = row_data[14]
                        self.kafka_topics = row_data[15]
                        self.debezium_config = row_data[16] or {}
                        self.sink_config = row_data[17] or {}
                        # Offset fields (added in migration)
                        self.current_lsn = row_data[18] if len(row_data) > 18 else None
                        self.current_offset = row_data[19] if len(row_data) > 19 else None
                        self.current_scn = row_data[20] if len(row_data) > 20 else None
                        self.last_offset_updated = row_data[21] if len(row_data) > 21 else None
                        self.created_at = row_data[22] if len(row_data) > 22 else None
                        self.updated_at = row_data[23] if len(row_data) > 23 else None
                
                proxy = PipelineProxy(row)
                # Ensure connection UUIDs are available as strings for frontend
                if proxy.source_connection_id:
                    proxy.source_connection_id = str(proxy.source_connection_id)
                if proxy.target_connection_id:
                    proxy.target_connection_id = str(proxy.target_connection_id)
                result_dict = pipeline_to_dict(proxy, db)
                
                # Log audit event
                log_audit_event(
                    db=db,
                    user=current_user,
                    action="update_pipeline",
                    resource_type="pipeline",
                    resource_id=str(pipeline_uuid_obj),
                    new_value=mask_sensitive_data(result_dict),
                    request=request
                )
                
                return result_dict
        except Exception as e:
            # If raw SQL fails, try ORM refresh (only if db_pipeline exists)
            try:
                if db_pipeline:
                    db.refresh(db_pipeline)
                    result_dict = pipeline_to_dict(db_pipeline, db)
                    
                    # Log audit event
                    log_audit_event(
                        db=db,
                        user=current_user,
                        action="update_pipeline",
                        resource_type="pipeline",
                        resource_id=str(pipeline_uuid_obj),
                        new_value=mask_sensitive_data(result_dict),
                        request=request
                    )
                    
                    return result_dict
            except Exception:
                pass
            
            # Last resort: return basic response using raw SQL
            try:
                result = db.execute(
                    text("SELECT name, mode FROM pipelines WHERE id = :pipeline_id"),
                    {"pipeline_id": pipeline_uuid_obj}
                )
                row = result.fetchone()
                pipeline_name = row[0] if row else ""
                pipeline_mode = row[1] if row else ""
                return {
                    "id": pipeline_id_to_int(str(pipeline_uuid_obj)),
                    "name": pipeline_name,
                    "mode": mode_to_update or pipeline_mode,
                    "status": "draft",
                    "message": "Pipeline updated successfully"
                }
            except Exception:
                return {
                    "id": pipeline_id_to_int(str(pipeline_uuid_obj)),
                    "name": "",
                    "mode": mode_to_update or "",
                    "status": "draft",
                    "message": "Pipeline updated successfully"
                }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to update pipeline: {str(e)}")


@router.delete("/{pipeline_id}")
async def delete_pipeline(
    pipeline_id: str,
    request: Request,
    current_user = Depends(require_sensitive_action),  # Sensitive action - requires admin
    db: Session = Depends(get_db)
):
    """Delete pipeline."""
    try:
        try:
            pipeline_uuid = uuid.UUID(pipeline_id)
            try:
                pipeline = db.query(PipelineModel).filter(PipelineModel.id == pipeline_uuid).first()
            except Exception:
                # If ORM fails (e.g., missing offset columns), use raw SQL
                db.rollback()
                result = db.execute(text("SELECT id FROM pipelines WHERE id = :pipeline_id"), {"pipeline_id": pipeline_uuid})
                row = result.fetchone()
                pipeline = type('Pipeline', (), {'id': row[0]})() if row else None
        except ValueError:
            try:
                all_pipelines = db.query(PipelineModel).all()
            except Exception:
                # If ORM fails (e.g., missing offset columns), use raw SQL
                db.rollback()
                result = db.execute(text("SELECT id FROM pipelines"))
                all_pipelines = [type('Pipeline', (), {'id': row[0]})() for row in result.fetchall()]
            
            pipeline = None
            for p in all_pipelines:
                if pipeline_id_to_int(p.id) == int(pipeline_id):
                    pipeline = p
                    break
        
        if not pipeline:
            raise HTTPException(status_code=404, detail="Pipeline not found")
        
        # Get pipeline data before deletion for audit log
        pipeline_dict = pipeline_to_dict(pipeline, db) if pipeline else None
        
        db.delete(pipeline)
        db.commit()
        
        # Log audit event
        log_audit_event(
            db=db,
            user=current_user,
            action="delete_pipeline",
            resource_type="pipeline",
            resource_id=pipeline_id,
            old_value=mask_sensitive_data(pipeline_dict) if pipeline_dict else None,
            request=request
        )
        
        return {"message": "Pipeline deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to delete pipeline: {str(e)}")


class TriggerPipelineRequest(BaseModel):
    """Request model for triggering a pipeline."""
    run_type: Optional[str] = "full_load"


@router.post("/{pipeline_id}/trigger")
async def trigger_pipeline(
    pipeline_id: str,
    request: Request,
    request_data: TriggerPipelineRequest = Body(...),
    current_user = Depends(require_permission("trigger_full_load")),
    db: Session = Depends(get_db)
):
    """Trigger pipeline with optional run type (full_load, cdc_only, full_load_cdc)."""
    try:
        from sqlalchemy import text
        
        # Get run_type from request body, default to "full_load"
        run_type = request_data.run_type or "full_load"
        
        # Determine CDC status value (database enum: NOT_STARTED, STARTING, RUNNING, STOPPED, ERROR)
        cdc_status_str = "RUNNING" if run_type in ["cdc_only", "full_load_cdc"] else "STOPPED"
        
        # First, check if pipeline exists using raw SQL to avoid enum validation errors
        # Try UUID first
        pipeline_found = False
        pipeline_uuid_obj = None
        try:
            pipeline_uuid_obj = uuid.UUID(pipeline_id)
            result = db.execute(
                text("SELECT id FROM pipelines WHERE id = :pipeline_id"),
                {"pipeline_id": pipeline_uuid_obj}
            )
            if result.fetchone():
                pipeline_found = True
        except ValueError:
            # Not a valid UUID, try numeric ID
            try:
                numeric_id = int(pipeline_id)
                # Query all pipelines and find by numeric ID
                result = db.execute(
                    text("SELECT id FROM pipelines")
                )
                all_ids = result.fetchall()
                for (db_id,) in all_ids:
                    if pipeline_id_to_int(str(db_id)) == numeric_id:
                        pipeline_uuid_obj = db_id
                        pipeline_found = True
                        break
            except ValueError:
                pass
        
        if not pipeline_found or pipeline_uuid_obj is None:
            raise HTTPException(status_code=404, detail="Pipeline not found")
        
        # First, fix any invalid status values in the database
        # Database enum: STOPPED, STARTING, RUNNING, STOPPING, ERROR
        try:
            db.execute(
                text("""
                    UPDATE pipelines 
                    SET status = 'STOPPED'::pipelinestatus
                    WHERE id = :pipeline_id 
                    AND status::text NOT IN ('STOPPED', 'STARTING', 'RUNNING', 'STOPPING', 'ERROR')
                """),
                {"pipeline_id": pipeline_uuid_obj}
            )
            db.commit()
        except Exception:
            db.rollback()
            # Continue even if fix fails
        
        # Now update the pipeline using raw SQL to bypass enum validation
        # Use string formatting for enum values (safe since we control the values: 'running' or 'stopped')
        try:
            # Validate cdc_status_str to ensure it's a valid enum value
            # Database enum: NOT_STARTED, STARTING, RUNNING, STOPPED, ERROR
            valid_cdc_statuses = ['NOT_STARTED', 'STARTING', 'RUNNING', 'STOPPED', 'ERROR']
            if cdc_status_str not in valid_cdc_statuses:
                cdc_status_str = 'STOPPED'  # Default to safe value
            
            # Escape single quotes to prevent SQL injection (defense in depth)
            cdc_status_escaped = cdc_status_str.replace("'", "''")
            
            # Database enum values: STOPPED, STARTING, RUNNING, STOPPING, ERROR
            # When triggering pipeline, set status to RUNNING
            db.execute(
                text(f"""
                    UPDATE pipelines 
                    SET status = 'RUNNING'::pipelinestatus,
                        cdc_status = '{cdc_status_escaped}'::cdcstatus,
                        updated_at = :updated_at
                    WHERE id = :pipeline_id
                """),
                {
                    "updated_at": datetime.utcnow(),
                    "pipeline_id": pipeline_uuid_obj
                }
            )
            db.commit()
            
            # Get the numeric ID for response
            numeric_id = pipeline_id_to_int(str(pipeline_uuid_obj))
            
            # Log that pipeline was triggered
            logger.info(f"Pipeline {pipeline_id} triggered with run_type: {run_type}, status: RUNNING, cdc_status: {cdc_status_str}")
            
            return {
                "id": numeric_id,
                "status": "active",
                "cdc_status": cdc_status_str,
                "message": f"Pipeline triggered successfully with run_type: {run_type}. Status updated to RUNNING."
            }
        except Exception as sql_error:
            db.rollback()
            # If CAST fails, try using string concatenation for enum casting
            try:
                # Use string formatting to build the enum cast
                # Ensure valid CDC status enum values (database enum: NOT_STARTED, STARTING, RUNNING, STOPPED, ERROR)
                if cdc_status_str not in ['NOT_STARTED', 'STARTING', 'RUNNING', 'STOPPED', 'ERROR']:
                    cdc_status_str = 'STOPPED'
                
                db.execute(
                    text(f"""
                        UPDATE pipelines 
                        SET status = 'RUNNING'::pipelinestatus,
                            cdc_status = '{cdc_status_str}'::cdcstatus,
                            updated_at = :updated_at
                        WHERE id = :pipeline_id
                    """),
                    {
                        "updated_at": datetime.utcnow(),
                        "pipeline_id": pipeline_uuid_obj
                    }
                )
                db.commit()
                
                numeric_id = pipeline_id_to_int(str(pipeline_uuid_obj))
                
                # Log audit event
                log_audit_event(
                    db=db,
                    user=current_user,
                    action="trigger_pipeline",
                    resource_type="pipeline",
                    resource_id=str(pipeline_uuid_obj),
                    new_value={"run_type": run_type, "cdc_status": cdc_status_str},
                    request=request
                )
                
                return {
                    "id": numeric_id,
                    "status": "active",
                    "cdc_status": cdc_status_str,
                    "message": f"Pipeline triggered successfully with run_type: {run_type}"
                }
            except Exception as fallback_error:
                db.rollback()
                # Last resort: Update without enum casting (let database handle it)
                try:
                    # Ensure valid CDC status enum values (database enum: NOT_STARTED, STARTING, RUNNING, STOPPED, ERROR)
                    if cdc_status_str not in ['NOT_STARTED', 'STARTING', 'RUNNING', 'STOPPED', 'ERROR']:
                        cdc_status_str = 'STOPPED'
                    
                    db.execute(
                        text("""
                            UPDATE pipelines 
                            SET status = 'RUNNING'::pipelinestatus,
                                cdc_status = :cdc_status::cdcstatus,
                                updated_at = :updated_at
                            WHERE id = :pipeline_id
                        """),
                        {
                            "cdc_status": cdc_status_str,
                            "updated_at": datetime.utcnow(),
                            "pipeline_id": pipeline_uuid_obj
                        }
                    )
                    db.commit()
                    
                    numeric_id = pipeline_id_to_int(str(pipeline_uuid_obj))
                    
                    # Log audit event
                    log_audit_event(
                        db=db,
                        user=current_user,
                        action="trigger_pipeline",
                        resource_type="pipeline",
                        resource_id=str(pipeline_uuid_obj),
                        new_value={"run_type": run_type, "cdc_status": cdc_status_str},
                        request=request
                    )
                    
                    return {
                        "id": numeric_id,
                        "status": "active",
                        "cdc_status": cdc_status_str,
                        "message": f"Pipeline triggered successfully with run_type: {run_type}"
                    }
                except Exception as final_error:
                    db.rollback()
                    raise HTTPException(
                        status_code=500, 
                        detail=f"Failed to trigger pipeline. SQL error: {str(sql_error)}. Fallback error: {str(fallback_error)}. Final error: {str(final_error)}"
                    )
    except HTTPException:
        raise
    except Exception as e:
        if hasattr(db, 'rollback'):
            db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to trigger pipeline: {str(e)}")


@router.post("/{pipeline_id}/start")
async def start_pipeline(
    pipeline_id: str,
    request: Request,
    current_user = Depends(require_permission("start_stop_pipeline")),
    db: Session = Depends(get_db)
):
    """Start pipeline (legacy endpoint - use /trigger instead)."""
    try:
        from sqlalchemy import text
        
        # Strip whitespace from pipeline_id (handles URL encoding issues like %20)
        pipeline_id = pipeline_id.strip()
        
        # First, check if pipeline exists using raw SQL to avoid enum validation errors
        pipeline_found = False
        pipeline_uuid_obj = None
        try:
            pipeline_uuid_obj = uuid.UUID(pipeline_id)
            result = db.execute(
                text("SELECT id FROM pipelines WHERE id = :pipeline_id"),
                {"pipeline_id": pipeline_uuid_obj}
            )
            if result.fetchone():
                pipeline_found = True
        except ValueError:
            # Not a valid UUID, try numeric ID
            try:
                numeric_id = int(pipeline_id)
                result = db.execute(text("SELECT id FROM pipelines"))
                all_ids = result.fetchall()
                for (db_id,) in all_ids:
                    if pipeline_id_to_int(str(db_id)) == numeric_id:
                        pipeline_uuid_obj = db_id
                        pipeline_found = True
                        break
            except ValueError:
                pass
        
        if not pipeline_found or pipeline_uuid_obj is None:
            raise HTTPException(status_code=404, detail="Pipeline not found")
        
        # First, fix any invalid status values in the database
        # Database enum: STOPPED, STARTING, RUNNING, STOPPING, ERROR
        try:
            db.execute(
                text("""
                    UPDATE pipelines 
                    SET status = 'STOPPED'::pipelinestatus
                    WHERE id = :pipeline_id 
                    AND status::text NOT IN ('STOPPED', 'STARTING', 'RUNNING', 'STOPPING', 'ERROR')
                """),
                {"pipeline_id": pipeline_uuid_obj}
            )
            db.commit()
        except Exception:
            db.rollback()
        
        # Update status to RUNNING using raw SQL (database enum: STOPPED, STARTING, RUNNING, STOPPING, ERROR)
        try:
            db.execute(
                text("""
                    UPDATE pipelines 
                    SET status = 'RUNNING'::pipelinestatus,
                        updated_at = :updated_at
                    WHERE id = :pipeline_id
                """),
                {
                    "updated_at": datetime.utcnow(),
                    "pipeline_id": pipeline_uuid_obj
                }
            )
            db.commit()
            
            numeric_id = pipeline_id_to_int(str(pipeline_uuid_obj))
            return {
                "pipeline_id": numeric_id,
                "status": "active",
                "message": "Pipeline started successfully"
            }
        except Exception as sql_error:
            db.rollback()
            raise HTTPException(status_code=500, detail=f"Failed to start pipeline: {str(sql_error)}")
    except HTTPException:
        raise
    except Exception as e:
        if hasattr(db, 'rollback'):
            db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to start pipeline: {str(e)}")


@router.post("/{pipeline_id}/stop")
async def stop_pipeline(
    pipeline_id: str,
    request: Request,
    current_user = Depends(require_permission("start_stop_pipeline")),
    db: Session = Depends(get_db)
):
    """Stop pipeline."""
    try:
        from sqlalchemy import text
        
        # Find pipeline by ID
        pipeline_found = False
        pipeline_uuid_obj = None
        try:
            pipeline_uuid_obj = uuid.UUID(pipeline_id)
            result = db.execute(
                text("SELECT id FROM pipelines WHERE id = :pipeline_id"),
                {"pipeline_id": pipeline_uuid_obj}
            )
            if result.fetchone():
                pipeline_found = True
        except ValueError:
            # Not a valid UUID, try numeric ID
            try:
                numeric_id = int(pipeline_id)
                result = db.execute(text("SELECT id FROM pipelines"))
                all_ids = result.fetchall()
                for (db_id,) in all_ids:
                    if pipeline_id_to_int(str(db_id)) == numeric_id:
                        pipeline_uuid_obj = db_id
                        pipeline_found = True
                        break
            except ValueError:
                pass
        
        if not pipeline_found or pipeline_uuid_obj is None:
            raise HTTPException(status_code=404, detail="Pipeline not found")
        
        # Update status to PAUSED using raw SQL (database enum: ACTIVE, INACTIVE, ERROR, PAUSED)
        try:
            db.execute(
                text("""
                    UPDATE pipelines 
                    SET status = 'STOPPED'::pipelinestatus,
                        updated_at = :updated_at
                    WHERE id = :pipeline_id
                """),
                {
                    "updated_at": datetime.utcnow(),
                    "pipeline_id": pipeline_uuid_obj
                }
            )
            db.commit()
            
            numeric_id = pipeline_id_to_int(str(pipeline_uuid_obj))
            
            # Log audit event
            log_audit_event(
                db=db,
                user=current_user,
                action="stop_pipeline",
                resource_type="pipeline",
                resource_id=str(pipeline_uuid_obj),
                request=request
            )
            
            numeric_id = pipeline_id_to_int(str(pipeline_uuid_obj))
            
            # Log audit event
            log_audit_event(
                db=db,
                user=current_user,
                action="stop_pipeline",
                resource_type="pipeline",
                resource_id=str(pipeline_uuid_obj),
                request=request
            )
            
            return {
                "id": numeric_id,
                "status": "paused",
                "message": "Pipeline stopped successfully"
            }
        except Exception as sql_error:
            db.rollback()
            raise HTTPException(status_code=500, detail=f"Failed to stop pipeline: {str(sql_error)}")
    except HTTPException:
        raise
    except Exception as e:
        if hasattr(db, 'rollback'):
            db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to stop pipeline: {str(e)}")


@router.get("/{pipeline_id}/status")
async def get_pipeline_status(pipeline_id: str, db: Session = Depends(get_db)):
    """Get pipeline status."""
    try:
        try:
            pipeline_uuid = uuid.UUID(pipeline_id)
            try:
                pipeline = db.query(PipelineModel).filter(PipelineModel.id == pipeline_uuid).first()
            except Exception:
                # If ORM fails (e.g., missing offset columns), use raw SQL
                db.rollback()
                result = db.execute(text("""
                    SELECT id, status::text, cdc_status::text 
                    FROM pipelines WHERE id = :pipeline_id
                """), {"pipeline_id": pipeline_uuid})
                row = result.fetchone()
                if row:
                    pipeline = type('Pipeline', (), {
                        'id': row[0],
                        'status': row[1],
                        'cdc_status': type('CDCStatus', (), {'value': row[2] or 'stopped'})()
                    })()
                else:
                    pipeline = None
        except ValueError:
            try:
                all_pipelines = db.query(PipelineModel).all()
            except Exception:
                # If ORM fails (e.g., missing offset columns), use raw SQL
                db.rollback()
                result = db.execute(text("SELECT id, status::text, cdc_status::text FROM pipelines"))
                all_pipelines = []
                for row in result.fetchall():
                    p = type('Pipeline', (), {
                        'id': row[0],
                        'status': row[1],
                        'cdc_status': type('CDCStatus', (), {'value': row[2] or 'stopped'})()
                    })()
                    all_pipelines.append(p)
            
            pipeline = None
            for p in all_pipelines:
                if pipeline_id_to_int(p.id) == int(pipeline_id):
                    pipeline = p
                    break
        
        if not pipeline:
            raise HTTPException(status_code=404, detail="Pipeline not found")
        
        # Handle status - could be string or enum
        status_value = getattr(pipeline.status, 'value', None) if hasattr(pipeline.status, 'value') else str(pipeline.status) if pipeline.status else 'STOPPED'
        cdc_status_value = getattr(pipeline.cdc_status, 'value', None) if hasattr(pipeline.cdc_status, 'value') else str(pipeline.cdc_status) if pipeline.cdc_status else 'stopped'
        
        return {
            "id": pipeline_id_to_int(pipeline.id),
            "status": map_status_to_frontend(status_value),
            "cdc_status": cdc_status_value,
            "full_load_status": "completed" if status_value in ['RUNNING', 'ACTIVE'] else "pending"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get pipeline status: {str(e)}")


@router.post("/activate-all")
async def activate_all_pipelines(db: Session = Depends(get_db)):
    """Activate all pipelines (set status to RUNNING)."""
    try:
        from sqlalchemy import text
        # Activate all pipelines by setting status to RUNNING
        result = db.execute(
            text("""
                UPDATE pipelines 
                SET status = 'RUNNING'::pipelinestatus, 
                    updated_at = :updated_at
                WHERE status::text IN ('STOPPED', 'ERROR')
            """),
            {"updated_at": datetime.utcnow()}
        )
        db.commit()
        return {
            "message": f"Activated {result.rowcount} pipelines",
            "count": result.rowcount
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to activate pipelines: {str(e)}")


@router.post("/fix-orphaned-connections")
async def fix_orphaned_connections(db: Session = Depends(get_db)):
    """Fix pipelines with orphaned (non-existent) connections by updating them to use valid connections."""
    try:
        from sqlalchemy import text
        
        # Get all valid connections
        valid_connections = db.query(ConnectionModel).filter(
            ConnectionModel.deleted_at.is_(None)
        ).all()
        
        if not valid_connections:
            raise HTTPException(status_code=404, detail="No valid connections found. Please create connections first.")
        
        # Get source and target connections
        source_connections = [c for c in valid_connections if c.connection_type == 'source']
        target_connections = [c for c in valid_connections if c.connection_type == 'target']
        
        if not source_connections:
            raise HTTPException(status_code=404, detail="No source connections found. Please create a source connection first.")
        if not target_connections:
            raise HTTPException(status_code=404, detail="No target connections found. Please create a target connection first.")
        
        # Use first available source and target connections
        default_source_conn = source_connections[0]
        default_target_conn = target_connections[0]
        
        # Get all pipelines
        all_pipelines = db.execute(text("SELECT id, source_connection_id, target_connection_id FROM pipelines")).fetchall()
        
        fixed_count = 0
        for (pipeline_id, source_conn_id, target_conn_id) in all_pipelines:
            needs_fix = False
            new_source_id = source_conn_id
            new_target_id = target_conn_id
            
            # Check if source connection exists
            if source_conn_id:
                source_exists = any(str(c.id) == str(source_conn_id) for c in valid_connections)
                if not source_exists:
                    new_source_id = default_source_conn.id
                    needs_fix = True
            
            # Check if target connection exists
            if target_conn_id:
                target_exists = any(str(c.id) == str(target_conn_id) for c in valid_connections)
                if not target_exists:
                    new_target_id = default_target_conn.id
                    needs_fix = True
            
            # Update pipeline if needed
            if needs_fix:
                db.execute(
                    text("""
                        UPDATE pipelines 
                        SET source_connection_id = :source_id,
                            target_connection_id = :target_id,
                            updated_at = :updated_at
                        WHERE id = :pipeline_id
                    """),
                    {
                        "source_id": new_source_id,
                        "target_id": new_target_id,
                        "updated_at": datetime.utcnow(),
                        "pipeline_id": pipeline_id
                    }
                )
                fixed_count += 1
        
        db.commit()
        
        return {
            "message": f"Fixed {fixed_count} pipeline(s) with orphaned connections",
            "count": fixed_count,
            "default_source_connection": str(default_source_conn.id),
            "default_target_connection": str(default_target_conn.id)
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to fix orphaned connections: {str(e)}")


@router.get("/{pipeline_id}/checkpoints")
async def get_pipeline_checkpoints(pipeline_id: str, db: Session = Depends(get_db)):
    """Get pipeline checkpoints."""
    # TODO: Implement checkpoint retrieval from database
    return []


@router.get("/{pipeline_id}/progress")
async def get_pipeline_progress(pipeline_id: str, db: Session = Depends(get_db)):
    """Get pipeline progress."""
    try:
        from sqlalchemy import text
        
        # First, check if pipeline exists using raw SQL to avoid enum validation errors
        pipeline_found = False
        pipeline_uuid_obj = None
        try:
            pipeline_uuid_obj = uuid.UUID(pipeline_id)
            result = db.execute(
                text("SELECT id FROM pipelines WHERE id = :pipeline_id"),
                {"pipeline_id": pipeline_uuid_obj}
            )
            if result.fetchone():
                pipeline_found = True
        except ValueError:
            # Not a valid UUID, try numeric ID
            try:
                numeric_id = int(pipeline_id)
                result = db.execute(text("SELECT id FROM pipelines"))
                all_ids = result.fetchall()
                for (db_id,) in all_ids:
                    if pipeline_id_to_int(str(db_id)) == numeric_id:
                        pipeline_uuid_obj = db_id
                        pipeline_found = True
                        break
            except ValueError:
                pass
        
        if not pipeline_found or pipeline_uuid_obj is None:
            raise HTTPException(status_code=404, detail="Pipeline not found")
        
        # Get pipeline status and mode using raw SQL to avoid enum errors
        try:
            result = db.execute(
                text("""
                    SELECT status::text, cdc_status::text, mode
                    FROM pipelines
                    WHERE id = :pipeline_id
                """),
                {"pipeline_id": pipeline_uuid_obj}
            )
            row = result.fetchone()
            if row:
                db_status = row[0] or 'STOPPED'
                db_cdc_status = row[1] or 'STOPPED'
                pipeline_mode = row[2] or ''
                # Map database enum to frontend status
                status = map_status_to_frontend(db_status)
                # Map CDC status
                cdc_status_upper = db_cdc_status.upper()
                if cdc_status_upper == "RUNNING":
                    cdc_status = "running"
                elif cdc_status_upper == "STOPPED":
                    cdc_status = "stopped"
                elif cdc_status_upper == "ERROR":
                    cdc_status = "error"
                else:
                    cdc_status = "stopped"
            else:
                status = "draft"
                cdc_status = "stopped"
                pipeline_mode = ''
        except Exception:
            # If query fails, try ORM as fallback
            try:
                pipeline = db.query(PipelineModel).filter(PipelineModel.id == pipeline_uuid_obj).first()
                if pipeline:
                    status = map_status_to_frontend(pipeline.status)
                    cdc_status = pipeline.cdc_status.value if pipeline.cdc_status else "stopped"
                    pipeline_mode = pipeline.mode or ''
                else:
                    status = "draft"
                    cdc_status = "stopped"
                    pipeline_mode = ''
            except Exception:
                # If enum error, use default values
                status = "draft"
                cdc_status = "stopped"
                pipeline_mode = ''
        
        # Get pipeline details for record counting
        pipeline_details = None
        try:
            result = db.execute(
                text("""
                    SELECT source_connection_id, target_connection_id,
                           source_database, source_schema, source_tables,
                           target_database, target_schema, target_tables
                    FROM pipelines
                    WHERE id = :pipeline_id
                """),
                {"pipeline_id": pipeline_uuid_obj}
            )
            row = result.fetchone()
            if row:
                pipeline_details = {
                    "source_connection_id": row[0],
                    "target_connection_id": row[1],
                    "source_database": row[2],
                    "source_schema": row[3],
                    "source_tables": row[4] if isinstance(row[4], list) else [],
                    "target_database": row[5],
                    "target_schema": row[6],
                    "target_tables": row[7] if isinstance(row[7], list) else []
                }
        except Exception:
            pass
        
        # Calculate actual record counts from source and target databases
        source_record_count = 0
        target_record_count = 0
        total_source_records = 0
        total_target_records = 0
        
        if pipeline_details and pipeline_details["source_tables"] and len(pipeline_details["source_tables"]) > 0:
            try:
                # Get source connection
                source_conn = db.query(ConnectionModel).filter(
                    ConnectionModel.id == pipeline_details["source_connection_id"],
                    ConnectionModel.deleted_at.is_(None)
                ).first()
                
                # Get target connection
                target_conn = db.query(ConnectionModel).filter(
                    ConnectionModel.id == pipeline_details["target_connection_id"],
                    ConnectionModel.deleted_at.is_(None)
                ).first()
                
                if source_conn and target_conn:
                    # Import connection string builder (avoid circular import by importing at function level)
                    from ingestion.routers.connections import get_database_connection_string
                    from sqlalchemy import create_engine, text
                    
                    # Count source records
                    try:
                        source_conn_str = get_database_connection_string(source_conn, pipeline_details["source_database"])
                        source_engine = create_engine(source_conn_str, pool_pre_ping=True)
                        
                        with source_engine.connect() as source_conn_db:
                            for source_table in pipeline_details["source_tables"]:
                                try:
                                    # Build table reference with schema if needed
                                    if pipeline_details["source_schema"]:
                                        table_ref = f"{pipeline_details['source_schema']}.{source_table}"
                                    else:
                                        table_ref = source_table
                                    
                                    # Count records in source table
                                    # Note: table_ref comes from pipeline config, so it's safe
                                    # But we validate it contains only alphanumeric, underscore, dot, and schema separator
                                    if all(c.isalnum() or c in '_.' for c in table_ref.replace('.', '')):
                                        count_query = text(f"SELECT COUNT(*) FROM {table_ref}")
                                        result = source_conn_db.execute(count_query)
                                        count = result.scalar()
                                        if count is not None:
                                            total_source_records += int(count)
                                except Exception as e:
                                    # If counting fails for a table, skip it
                                    pass
                    except Exception:
                        pass
                    
                    # Count target records
                    try:
                        target_conn_str = get_database_connection_string(target_conn, pipeline_details["target_database"])
                        target_engine = create_engine(target_conn_str, pool_pre_ping=True)
                        
                        with target_engine.connect() as target_conn_db:
                            # Get target table names (from mapping or same as source)
                            target_table_mapping = {}
                            if pipeline_details.get("target_tables") and len(pipeline_details["target_tables"]) > 0:
                                for i, source_table in enumerate(pipeline_details["source_tables"]):
                                    if i < len(pipeline_details["target_tables"]):
                                        target_table_mapping[source_table] = pipeline_details["target_tables"][i]
                            
                            for source_table in pipeline_details["source_tables"]:
                                try:
                                    # Get target table name
                                    target_table = target_table_mapping.get(source_table, source_table)
                                    
                                    # Build table reference with schema if needed
                                    if pipeline_details["target_schema"]:
                                        table_ref = f"{pipeline_details['target_schema']}.{target_table}"
                                    else:
                                        table_ref = target_table
                                    
                                    # Handle S3 targets (they don't have traditional tables)
                                    if target_conn.database_type.lower() in ["s3", "aws_s3"]:
                                        # For S3, we can't count records the same way
                                        # Assume 0 for now (or check S3 object count if needed)
                                        pass
                                    else:
                                        # Count records in target table
                                        # Note: table_ref comes from pipeline config, so it's safe
                                        # But we validate it contains only alphanumeric, underscore, dot, and schema separator
                                        if all(c.isalnum() or c in '_.' for c in table_ref.replace('.', '')):
                                            count_query = text(f"SELECT COUNT(*) FROM {table_ref}")
                                            result = target_conn_db.execute(count_query)
                                            count = result.scalar()
                                            if count is not None:
                                                total_target_records += int(count)
                                except Exception as e:
                                    # If counting fails for a table, skip it
                                    pass
                    except Exception:
                        pass
            except Exception:
                pass
        
        # Calculate progress based on actual record counts
        progress_percentage = 0
        full_load_status = "pending"
        records_processed = total_target_records
        records_total = total_source_records
        
        if status == "active":
            if total_source_records > 0:
                # Calculate progress based on actual record replication
                # If target has equal or more records than source, consider it 100% complete
                if total_target_records >= total_source_records:
                    progress_percentage = 100
                    full_load_status = "completed"
                else:
                    # Calculate percentage, but ensure it's reasonable
                    progress_percentage = int((total_target_records / total_source_records) * 100)
                    progress_percentage = min(100, max(0, progress_percentage))
                    
                    # If pipeline is active and has some progress, show as running
                    if progress_percentage == 100:
                        full_load_status = "completed"
                    elif progress_percentage > 0:
                        full_load_status = "running"
                    else:
                        # Active but no progress yet - might be starting
                        full_load_status = "running"  # Show as running if status is active
            else:
                # No source records - check status based on mode and CDC
                if cdc_status == "running":
                    # CDC is running, consider it active but don't show false progress
                    progress_percentage = 0  # Don't show progress if we can't calculate it
                    full_load_status = "running"
                elif pipeline_mode == "full_load_only":
                    # Full load only with no records - might be empty table or not started
                    # If status is active and no source records, consider it complete (empty table)
                    if status == "active":
                        progress_percentage = 100  # Empty table is 100% complete
                        full_load_status = "completed"
                    else:
                        progress_percentage = 0
                        full_load_status = "pending"
                elif pipeline_mode == "cdc_only":
                    # CDC only - if CDC is running, show as active
                    if cdc_status == "running":
                        progress_percentage = 100  # CDC running means replication is active
                        full_load_status = "running"
                    else:
                        progress_percentage = 0
                        full_load_status = "pending"
                else:
                    # Unknown mode or mixed mode
                    if status == "active" and cdc_status == "running":
                        progress_percentage = 100  # Active with CDC running
                        full_load_status = "running"
                    else:
                        progress_percentage = 0
                        full_load_status = "running" if status == "active" else "pending"
        elif status == "draft" or status == "paused":
            progress_percentage = 0
            full_load_status = "pending"
        elif status == "error":
            progress_percentage = 0
            full_load_status = "failed"
        else:
            progress_percentage = 0
            full_load_status = "pending"
        
        # Map cdc_status to frontend format
        cdc_status_str = cdc_status
        if isinstance(cdc_status_str, str):
            # Map database enum values to frontend values
            cdc_status_upper = cdc_status_str.upper()
            if cdc_status_upper == "RUNNING":
                cdc_status_str = "running"
            elif cdc_status_upper == "STOPPED":
                cdc_status_str = "stopped"
            elif cdc_status_upper == "ERROR":
                cdc_status_str = "error"
            else:
                cdc_status_str = "stopped"
        else:
            cdc_status_str = "stopped"
        
        # Return progress with full_load and cdc status
        return {
            "pipeline_id": pipeline_id_to_int(str(pipeline_uuid_obj)),
            "status": status,
            "cdc_status": cdc_status_str,
            "progress_percentage": progress_percentage,
            "records_processed": records_processed,
            "records_total": records_total,
            "full_load": {
                "status": full_load_status,
                "progress_percent": progress_percentage,
                "records_loaded": records_processed,
                "total_records": records_total
            },
            "cdc": {
                "status": cdc_status_str,
                "events_captured": 0,
                "events_applied": 0,
                "events_failed": 0
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get pipeline progress: {str(e)}")


class OffsetUpdateRequest(BaseModel):
    current_lsn: Optional[str] = None
    current_offset: Optional[str] = None
    current_scn: Optional[str] = None


@router.put("/{pipeline_id}/offset")
async def update_pipeline_offset_endpoint(
    pipeline_id: str,
    offset_data: OffsetUpdateRequest = Body(...),
    current_user = Depends(require_permission("start_stop_pipeline")),
    db: Session = Depends(get_db)
):
    """Update pipeline offset/LSN/SCN manually or fetch from database."""
    try:
        from sqlalchemy import text
        
        # Find pipeline
        pipeline_id = pipeline_id.strip()
        pipeline_found = False
        pipeline_uuid_obj = None
        
        try:
            pipeline_uuid_obj = uuid.UUID(pipeline_id)
            result = db.execute(
                text("SELECT id FROM pipelines WHERE id = :pipeline_id"),
                {"pipeline_id": pipeline_uuid_obj}
            )
            if result.fetchone():
                pipeline_found = True
        except ValueError:
            try:
                numeric_id = int(pipeline_id)
                result = db.execute(text("SELECT id FROM pipelines"))
                all_ids = result.fetchall()
                for (db_id,) in all_ids:
                    if pipeline_id_to_int(str(db_id)) == numeric_id:
                        pipeline_uuid_obj = db_id
                        pipeline_found = True
                        break
            except ValueError:
                pass
        
        if not pipeline_found or pipeline_uuid_obj is None:
            raise HTTPException(status_code=404, detail="Pipeline not found")
        
        try:
            pipeline = db.query(PipelineModel).filter(PipelineModel.id == pipeline_uuid_obj).first()
        except Exception:
            # If ORM fails (e.g., missing offset columns), use raw SQL
            db.rollback()
            result = db.execute(text("SELECT id, source_connection_id FROM pipelines WHERE id = :pipeline_id"), {"pipeline_id": pipeline_uuid_obj})
            row = result.fetchone()
            if row:
                pipeline = type('Pipeline', (), {'id': row[0], 'source_connection_id': row[1]})()
            else:
                pipeline = None
        
        if not pipeline:
            raise HTTPException(status_code=404, detail="Pipeline not found")
        
        # Get source connection
        source_conn_id = getattr(pipeline, 'source_connection_id', None)
        if not source_conn_id:
            raise HTTPException(status_code=400, detail="Pipeline has no source connection")
        
        source_connection = db.query(ConnectionModel).filter(
            ConnectionModel.id == str(pipeline.source_connection_id)
        ).first()
        
        if not source_connection:
            raise HTTPException(status_code=404, detail="Source connection not found")
        
        # Check if offset columns exist in database
        try:
            check_result = db.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'pipelines' 
                AND column_name IN ('current_lsn', 'current_offset', 'current_scn', 'last_offset_updated')
            """))
            offset_columns_exist = len(check_result.fetchall()) > 0
        except Exception:
            offset_columns_exist = False
        
        if not offset_columns_exist:
            # Columns don't exist - return error suggesting migration
            raise HTTPException(
                status_code=400,
                detail="Offset columns (current_lsn, current_offset, current_scn) do not exist in the pipelines table. Please run the migration script to add these columns."
            )
        
        # Prepare offset values
        from datetime import datetime
        update_values = {}
        
        # If no offset data provided, fetch from database
        if not offset_data.current_lsn and not offset_data.current_offset and not offset_data.current_scn:
            # Fetch current offset from source database
            offset_info = get_database_offset(source_connection, pipeline)
            
            if offset_info.get('current_lsn'):
                update_values['current_lsn'] = offset_info['current_lsn']
            if offset_info.get('current_offset'):
                update_values['current_offset'] = offset_info['current_offset']
            if offset_info.get('current_scn'):
                update_values['current_scn'] = offset_info['current_scn']
        else:
            # Update with provided values
            if offset_data.current_lsn is not None:
                update_values['current_lsn'] = offset_data.current_lsn
            if offset_data.current_offset is not None:
                update_values['current_offset'] = offset_data.current_offset
            if offset_data.current_scn is not None:
                update_values['current_scn'] = offset_data.current_scn
        
        # Always update timestamp
        update_values['last_offset_updated'] = datetime.utcnow()
        
        # Update using raw SQL to avoid ORM issues
        update_fields = []
        params = {"pipeline_id": pipeline_uuid_obj}
        
        for field, value in update_values.items():
            if field == 'last_offset_updated':
                update_fields.append(f"{field} = :{field}")
                params[field] = value
            else:
                update_fields.append(f"{field} = :{field}")
                params[field] = value
        
        if update_fields:
            db.execute(
                text(f"UPDATE pipelines SET {', '.join(update_fields)} WHERE id = :pipeline_id"),
                params
            )
            db.commit()
        
        # Get updated values for response
        result = db.execute(
            text("""
                SELECT current_lsn, current_offset, current_scn, last_offset_updated
                FROM pipelines WHERE id = :pipeline_id
            """),
            {"pipeline_id": pipeline_uuid_obj}
        )
        row = result.fetchone()
        if row:
            current_lsn = row[0]
            current_offset = row[1]
            current_scn = row[2]
            last_offset_updated = row[3]
        else:
            current_lsn = update_values.get('current_lsn')
            current_offset = update_values.get('current_offset')
            current_scn = update_values.get('current_scn')
            last_offset_updated = update_values.get('last_offset_updated')
        
        # Get offset values safely (may not exist if using raw SQL fallback)
        current_lsn = getattr(pipeline, 'current_lsn', None)
        current_offset = getattr(pipeline, 'current_offset', None)
        current_scn = getattr(pipeline, 'current_scn', None)
        last_offset_updated = getattr(pipeline, 'last_offset_updated', None)
        
        # Log audit event
        log_audit_event(
            db=db,
            user=current_user,
            action="update_pipeline_offset",
            resource_type="pipeline",
            resource_id=str(pipeline.id),
            new_value=mask_sensitive_data({
                "current_lsn": current_lsn,
                "current_offset": current_offset,
                "current_scn": current_scn,
                "last_offset_updated": last_offset_updated.isoformat() if last_offset_updated else None
            }),
            request=None
        )
        
        return {
            "pipeline_id": pipeline_id_to_int(str(pipeline.id)),
            "current_lsn": current_lsn,
            "current_offset": current_offset,
            "current_scn": current_scn,
            "last_offset_updated": last_offset_updated.isoformat() + "Z" if last_offset_updated else None,
            "message": "Offset updated successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to update pipeline offset: {str(e)}")


@router.get("/{pipeline_id}/offset")
async def get_pipeline_offset(
    pipeline_id: str,
    fetch_from_db: bool = Query(False, description="Fetch current offset from source database"),
    current_user = Depends(require_permission("view_metrics")),
    db: Session = Depends(get_db)
):
    """Get pipeline offset/LSN/SCN information."""
    try:
        from sqlalchemy import text
        
        # Find pipeline
        pipeline_id = pipeline_id.strip()
        pipeline_found = False
        pipeline_uuid_obj = None
        
        try:
            pipeline_uuid_obj = uuid.UUID(pipeline_id)
            result = db.execute(
                text("SELECT id FROM pipelines WHERE id = :pipeline_id"),
                {"pipeline_id": pipeline_uuid_obj}
            )
            if result.fetchone():
                pipeline_found = True
        except ValueError:
            try:
                numeric_id = int(pipeline_id)
                result = db.execute(text("SELECT id FROM pipelines"))
                all_ids = result.fetchall()
                for (db_id,) in all_ids:
                    if pipeline_id_to_int(str(db_id)) == numeric_id:
                        pipeline_uuid_obj = db_id
                        pipeline_found = True
                        break
            except ValueError:
                pass
        
        if not pipeline_found or pipeline_uuid_obj is None:
            raise HTTPException(status_code=404, detail="Pipeline not found")
        
        try:
            pipeline = db.query(PipelineModel).filter(PipelineModel.id == pipeline_uuid_obj).first()
        except Exception:
            # If ORM fails (e.g., missing offset columns), use raw SQL
            db.rollback()
            result = db.execute(text("SELECT id, source_connection_id FROM pipelines WHERE id = :pipeline_id"), {"pipeline_id": pipeline_uuid_obj})
            row = result.fetchone()
            if row:
                pipeline = type('Pipeline', (), {'id': row[0], 'source_connection_id': row[1]})()
            else:
                pipeline = None
        
        if not pipeline:
            raise HTTPException(status_code=404, detail="Pipeline not found")
        
        # If requested, fetch current offset from database
        source_conn_id = getattr(pipeline, 'source_connection_id', None)
        if fetch_from_db and source_conn_id:
            source_connection = db.query(ConnectionModel).filter(
                ConnectionModel.id == str(pipeline.source_connection_id)
            ).first()
            
            if source_connection:
                offset_info = get_database_offset(source_connection, pipeline)
                # Get stored offset values safely
                stored_lsn = getattr(pipeline, 'current_lsn', None)
                stored_offset = getattr(pipeline, 'current_offset', None)
                stored_scn = getattr(pipeline, 'current_scn', None)
                last_offset_updated = getattr(pipeline, 'last_offset_updated', None)
                
                return {
                    "pipeline_id": pipeline_id_to_int(str(pipeline.id)),
                    "current_lsn": offset_info.get('current_lsn'),
                    "current_offset": offset_info.get('current_offset'),
                    "current_scn": offset_info.get('current_scn'),
                    "offset_type": offset_info.get('offset_type'),
                    "timestamp": offset_info.get('timestamp'),
                    "stored_lsn": stored_lsn,
                    "stored_offset": stored_offset,
                    "stored_scn": stored_scn,
                    "last_offset_updated": last_offset_updated.isoformat() + "Z" if last_offset_updated else None
                }
        
        # Return stored offset - get values safely
        current_lsn = getattr(pipeline, 'current_lsn', None)
        current_offset = getattr(pipeline, 'current_offset', None)
        current_scn = getattr(pipeline, 'current_scn', None)
        last_offset_updated = getattr(pipeline, 'last_offset_updated', None)
        
        return {
            "pipeline_id": pipeline_id_to_int(str(pipeline.id)),
            "current_lsn": current_lsn,
            "current_offset": current_offset,
            "current_scn": current_scn,
            "last_offset_updated": last_offset_updated.isoformat() + "Z" if last_offset_updated else None
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get pipeline offset: {str(e)}")

