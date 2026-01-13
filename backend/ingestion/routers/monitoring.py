"""Monitoring router."""
from fastapi import APIRouter, Depends, Query, HTTPException
from typing import Optional
from datetime import datetime, timedelta

from ingestion.database import get_db
from sqlalchemy.orm import Session

router = APIRouter()


@router.get("/dashboard")
async def get_dashboard(db: Session = Depends(get_db)):
    """Get monitoring dashboard data."""
    try:
        from sqlalchemy import text
        from ingestion.database.models_db import PipelineModel, ConnectionModel, PipelineStatus
        
        # Use raw SQL to avoid ORM issues with missing offset columns
        try:
            total_pipelines = db.query(PipelineModel).count()
            active_pipelines = db.query(PipelineModel).filter(
                PipelineModel.status == PipelineStatus.ACTIVE
            ).count()
        except Exception:
            # If ORM fails (e.g., missing offset columns), use raw SQL
            from sqlalchemy import text
            db.rollback()
            total_result = db.execute(text("SELECT COUNT(*) FROM pipelines"))
            total_pipelines = total_result.scalar() or 0
            
            from sqlalchemy import text
            active_result = db.execute(text("""
                SELECT COUNT(*) FROM pipelines 
                WHERE status::text IN ('RUNNING', 'STARTING', 'ACTIVE')
            """))
            active_pipelines = active_result.scalar() or 0
        
        # Get total connections (including soft-deleted check)
        try:
            total_connections = db.query(ConnectionModel).filter(
                ConnectionModel.deleted_at.is_(None)
            ).count()
        except Exception:
            db.rollback()
            # Try raw SQL if ORM fails
            conn_result = db.execute(text("""
                SELECT COUNT(*) FROM connections 
                WHERE deleted_at IS NULL
            """))
            total_connections = conn_result.scalar() or 0
        
        # Get total events count from pipeline_runs
        try:
            events_result = db.execute(text("SELECT COUNT(*) FROM pipeline_runs"))
            total_events = events_result.scalar() or 0
        except Exception:
            total_events = 0
        
        # Get failed events count - include COMPLETED events with errors
        try:
            failed_result = db.execute(text("""
                SELECT COUNT(*) FROM pipeline_runs 
                WHERE status::text IN ('FAILED', 'ERROR')
                OR (status::text = 'COMPLETED' AND (error_message IS NOT NULL AND error_message != ''))
                OR (status::text = 'COMPLETED' AND (errors_count IS NOT NULL AND errors_count > 0))
            """))
            failed_events = failed_result.scalar() or 0
        except Exception:
            failed_events = 0
        
        # Get successful events count - only count COMPLETED events with no errors
        try:
            success_result = db.execute(text("""
                SELECT COUNT(*) FROM pipeline_runs 
                WHERE status::text = 'COMPLETED'
                AND (error_message IS NULL OR error_message = '')
                AND (errors_count IS NULL OR errors_count = 0)
            """))
            success_events = success_result.scalar() or 0
        except Exception:
            success_events = 0
        
        # Calculate total rows processed
        try:
            rows_result = db.execute(text("""
                SELECT COALESCE(SUM(rows_processed), 0) FROM pipeline_runs
            """))
            total_rows_processed = rows_result.scalar() or 0
        except Exception:
            total_rows_processed = 0
        
        return {
            "total_pipelines": total_pipelines,
            "active_pipelines": active_pipelines,
            "total_connections": total_connections,
            "total_events": total_events,
            "failed_events": failed_events,
            "success_events": success_events,
            "total_rows_processed": total_rows_processed,
            "active_alerts": 0  # TODO: Implement alerts
        }
    except Exception as e:
        import logging
        logging.error(f"Error in get_dashboard: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to get dashboard data: {str(e)}")


@router.get("/events")
async def get_replication_events(
    pipeline_id: Optional[str] = Query(None),
    table_name: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=10000),  # Increased limit to 10000 for analytics
    today_only: bool = Query(False),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Get replication events - returns array directly."""
    try:
        from sqlalchemy import text
        from ingestion.database.models_db import PipelineModel
        import uuid
        
        # Query pipeline_runs table for replication events
        # Also include audit_logs for pipeline/connection actions to show more activity
        query = """
            SELECT 
                pr.id,
                pr.pipeline_id,
                pr.run_type,
                pr.status,
                pr.started_at,
                pr.completed_at,
                pr.rows_processed,
                COALESCE(pr.errors_count, 0) as errors_count,
                pr.error_message,
                pr.run_metadata,
                p.name as pipeline_name
            FROM pipeline_runs pr
            LEFT JOIN pipelines p ON pr.pipeline_id = p.id
            WHERE 1=1
        """
        params = {}
        
        # Filter by pipeline_id
        if pipeline_id:
            try:
                # Try to find pipeline by UUID or numeric ID
                pipeline_uuid = None
                try:
                    pipeline_uuid = uuid.UUID(pipeline_id)
                except ValueError:
                    # Try numeric ID lookup
                    from ingestion.routers.pipelines import pipeline_id_to_int
                    try:
                        all_pipelines = db.query(PipelineModel).all()
                    except Exception:
                        # If ORM fails (e.g., missing offset columns), use raw SQL
                        db.rollback()
                        result = db.execute(text("SELECT id FROM pipelines"))
                        all_pipelines = [type('Pipeline', (), {'id': row[0]})() for row in result.fetchall()]
                    
                    for p in all_pipelines:
                        if pipeline_id_to_int(str(p.id)) == int(pipeline_id):
                            pipeline_uuid = p.id
                            break
                
                if pipeline_uuid:
                    query += " AND pr.pipeline_id = :pipeline_id"
                    params["pipeline_id"] = str(pipeline_uuid)
            except (ValueError, TypeError):
                pass
        
        # Filter by table_name (from run_metadata)
        if table_name:
            query += " AND pr.run_metadata->>'table_name' = :table_name"
            params["table_name"] = table_name
        
        # Filter by date range
        if today_only:
            query += " AND DATE(pr.started_at) = CURRENT_DATE"
        elif start_date:
            query += " AND pr.started_at >= :start_date"
            params["start_date"] = start_date
        if end_date:
            query += " AND pr.started_at <= :end_date"
            params["end_date"] = end_date
        
        # Order by started_at descending (most recent first)
        query += " ORDER BY pr.started_at DESC LIMIT :limit OFFSET :skip"
        params["limit"] = limit
        params["skip"] = skip
        
        result = db.execute(text(query), params)
        rows = result.fetchall()
        
        # Log query results for debugging
        import logging
        logging.info(f"[Monitoring] Query returned {len(rows)} pipeline_runs (limit={limit}, skip={skip}, pipeline_id={pipeline_id})")
        if len(rows) > 0:
            logging.info(f"[Monitoring] First row sample: id={rows[0][0]}, pipeline_id={rows[0][1]}, run_type={rows[0][2]}, status={rows[0][3]}, metadata={rows[0][9]}")
        
        # Convert pipeline_runs to ReplicationEvent format
        events = []
        for row in rows:
            run_metadata = row[9] or {}  # run_metadata (can be None or empty dict)
            
            # Determine event_type from run_metadata or run_type
            event_type = 'insert'  # default
            if isinstance(run_metadata, dict) and run_metadata:
                # Try multiple fields to determine event type
                event_type = (
                    run_metadata.get('event_type') or 
                    run_metadata.get('operation') or 
                    run_metadata.get('op') or
                    'insert'
                )
            # Also check run_type field (e.g., "CDC", "FULL_LOAD")
            run_type = row[2] or ''  # run_type
            if run_type.upper() == 'CDC' and (not isinstance(run_metadata, dict) or not run_metadata):
                # If it's a CDC run but no metadata, try to infer from status
                event_type = 'insert'
            
            event_type = str(event_type).lower()
            
            # Normalize event_type to valid values
            if event_type not in ['insert', 'update', 'delete']:
                # Try to infer from operation name
                event_type_lower = event_type.lower()
                if 'update' in event_type_lower or 'modify' in event_type_lower:
                    event_type = 'update'
                elif 'delete' in event_type_lower or 'remove' in event_type_lower:
                    event_type = 'delete'
                else:
                    event_type = 'insert'  # default to insert
            
            # Get table_name from metadata or use default
            table_name = 'unknown'
            if isinstance(run_metadata, dict):
                table_name = run_metadata.get('table_name', 'unknown')
            
            # Map status - check error_message and errors_count first to determine if it's actually a failure
            raw_status = str(row[3]).upper() if row[3] else ''
            error_message_raw = row[8]  # error_message column
            errors_count = row[7] if row[7] is not None else 0
            
            # Convert error_message to string, handling None and empty strings
            error_message = None
            if error_message_raw:
                error_message_str = str(error_message_raw).strip()
                if error_message_str and error_message_str.lower() not in ['none', 'null', '']:
                    error_message = error_message_str
            
            # Determine status based on error presence and raw status
            # Priority: error_message > errors_count > raw_status
            if error_message:
                # If there's an error message, it's definitely a failure
                status = 'failed'
            elif errors_count > 0:
                # If errors_count > 0, it's a failure
                status = 'failed'
            elif raw_status in ['FAILED', 'ERROR']:
                # If raw status indicates failure, it's a failure
                status = 'failed'
            else:
                # Map status only if no errors
                status_map = {
                    'COMPLETED': 'applied',
                    'FAILED': 'failed',
                    'ERROR': 'failed',
                    'IN_PROGRESS': 'captured',
                    'RUNNING': 'captured',
                    'PENDING': 'pending',
                    'STARTING': 'captured',
                    'STOPPED': 'pending'
                }
                status = status_map.get(raw_status, 'captured')
            
            # Calculate latency if both started_at and completed_at exist
            latency_ms = None
            if row[4] and row[5]:  # started_at and completed_at
                try:
                    latency_ms = int((row[5] - row[4]).total_seconds() * 1000)
                except (AttributeError, TypeError):
                    latency_ms = None
            
            # Extract metadata fields safely
            metadata_dict = run_metadata if isinstance(run_metadata, dict) else {}
            
            event = {
                "id": str(row[0]),  # id
                "pipeline_id": str(row[1]),  # pipeline_id
                "event_type": event_type,
                "table_name": table_name,
                "schema_name": metadata_dict.get('schema_name'),
                "source_data": metadata_dict.get('source_data'),
                "target_data": metadata_dict.get('target_data'),
                "changed_columns": metadata_dict.get('changed_columns'),
                "source_commit_time": row[4].isoformat() + "Z" if row[4] else None,  # started_at
                "target_apply_time": row[5].isoformat() + "Z" if row[5] else None,  # completed_at
                "latency_ms": latency_ms,
                "source_lsn": metadata_dict.get('source_lsn'),
                "source_scn": metadata_dict.get('source_scn'),
                "source_binlog_file": metadata_dict.get('source_binlog_file'),
                "source_binlog_position": metadata_dict.get('source_binlog_position'),
                "sql_server_lsn": metadata_dict.get('sql_server_lsn'),
                "status": status,
                "error_message": error_message,  # Always include error_message if it exists, regardless of status
                "created_at": row[4].isoformat() + "Z" if row[4] else datetime.utcnow().isoformat() + "Z"  # started_at
            }
            events.append(event)
        
        return events
    except Exception as e:
        import logging
        logging.error(f"Error fetching replication events: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch events: {str(e)}")


@router.get("/metrics")
async def get_monitoring_metrics(
    pipeline_id: str = Query(..., description="Pipeline ID (required)"),
    start_time: Optional[str] = Query(None),
    end_time: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Get monitoring metrics - returns array directly."""
    try:
        from sqlalchemy import text
        from ingestion.database.models_db import PipelineModel
        import uuid
        
        # Find pipeline by UUID or numeric ID
        pipeline_uuid = None
        try:
            pipeline_uuid = uuid.UUID(pipeline_id)
        except ValueError:
            # Try numeric ID lookup
            from ingestion.routers.pipelines import pipeline_id_to_int
            try:
                all_pipelines = db.query(PipelineModel).all()
            except Exception:
                # If ORM fails (e.g., missing offset columns), use raw SQL
                db.rollback()
                result = db.execute(text("SELECT id FROM pipelines"))
                all_pipelines = [type('Pipeline', (), {'id': row[0]})() for row in result.fetchall()]
            
            for p in all_pipelines:
                if pipeline_id_to_int(str(p.id)) == int(pipeline_id):
                    pipeline_uuid = p.id
                    break
        
        if not pipeline_uuid:
            raise HTTPException(status_code=404, detail=f"Pipeline not found: {pipeline_id}")
        
        # Query pipeline_metrics table
        query = """
            SELECT 
                id,
                pipeline_id,
                timestamp,
                throughput_events_per_sec,
                lag_seconds,
                error_count,
                bytes_processed,
                source_offset,
                target_offset,
                connector_status
            FROM pipeline_metrics
            WHERE pipeline_id = :pipeline_id
        """
        params = {"pipeline_id": str(pipeline_uuid)}
        
        # Filter by time range
        if start_time:
            query += " AND timestamp >= :start_time"
            params["start_time"] = start_time
        if end_time:
            query += " AND timestamp <= :end_time"
            params["end_time"] = end_time
        
        # Order by timestamp descending (most recent first)
        query += " ORDER BY timestamp DESC LIMIT 1000"
        
        result = db.execute(text(query), params)
        rows = result.fetchall()
        
        # Convert to MonitoringMetric format
        metrics = []
        for row in rows:
            # Calculate event counts from connector_status or use defaults
            connector_status = row[9] or {}  # connector_status JSON
            insert_count = connector_status.get('insert_count', 0)
            update_count = connector_status.get('update_count', 0)
            delete_count = connector_status.get('delete_count', 0)
            total_events = insert_count + update_count + delete_count
            
            metric = {
                "id": str(row[0]),  # id
                "pipeline_id": str(row[1]),  # pipeline_id
                "timestamp": row[2].isoformat() + "Z" if row[2] else datetime.utcnow().isoformat() + "Z",  # timestamp
                "events_per_second": row[3] or 0,  # throughput_events_per_sec
                "avg_latency_ms": row[4] * 1000 if row[4] else 0,  # lag_seconds converted to ms
                "total_events": total_events,
                "insert_count": insert_count,
                "update_count": update_count,
                "delete_count": delete_count,
                "error_count": row[5] or 0  # error_count
            }
            metrics.append(metric)
        
        # If no metrics found, return empty array (frontend will handle gracefully)
        return metrics
    except HTTPException:
        raise
    except Exception as e:
        import logging
        logging.error(f"Error fetching monitoring metrics: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch metrics: {str(e)}")


@router.get("/pipelines/{pipeline_id}/metrics")
async def get_pipeline_metrics(pipeline_id: str, db: Session = Depends(get_db)):
    """Get pipeline metrics."""
    # TODO: Implement metrics retrieval
    return {
        "pipeline_id": pipeline_id,
        "throughput_events_per_sec": 0,
        "lag_seconds": 0,
        "error_count": 0
    }


@router.get("/pipelines/{pipeline_id}/metrics/history")
async def get_pipeline_metrics_history(pipeline_id: str, hours: Optional[int] = 24, db: Session = Depends(get_db)):
    """Get historical pipeline metrics."""
    # TODO: Implement historical metrics
    return []


@router.get("/pipelines/{pipeline_id}/lag")
async def get_pipeline_lag(pipeline_id: str, db: Session = Depends(get_db)):
    """Get replication lag for pipeline."""
    # TODO: Implement lag calculation
    return {
        "pipeline_id": pipeline_id,
        "lag_seconds": 0,
        "lag_status": "healthy"
    }


@router.get("/pipelines/{pipeline_id}/health")
async def get_pipeline_health(pipeline_id: str, db: Session = Depends(get_db)):
    """Get pipeline health status."""
    # TODO: Implement health check
    return {
        "pipeline_id": pipeline_id,
        "health": "healthy",
        "status": "active"
    }


@router.get("/pipelines/{pipeline_id}/data-quality")
async def get_pipeline_data_quality(pipeline_id: str, db: Session = Depends(get_db)):
    """Get data quality metrics."""
    # TODO: Implement data quality checks
    return {
        "pipeline_id": pipeline_id,
        "row_count_match": True,
        "schema_drift": False
    }


@router.get("/alerts")
async def get_alerts(db: Session = Depends(get_db)):
    """Get active alerts."""
    # TODO: Implement alert retrieval
    return []


@router.get("/pipelines/{pipeline_id}/checkpoints")
async def get_pipeline_checkpoints(pipeline_id: str, db: Session = Depends(get_db)):
    """Get pipeline checkpoints."""
    try:
        # TODO: Implement checkpoint retrieval from database
        # For now, return empty array matching frontend expectations
        return []
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get checkpoints: {str(e)}")


@router.get("/health")
async def get_system_health():
    """Get system health status."""
    return {
        "status": "healthy",
        "kafka_connect": "connected",
        "database": "connected"
    }

