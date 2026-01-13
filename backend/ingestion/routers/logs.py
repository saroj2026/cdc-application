"""Application logs router."""
from fastapi import APIRouter, Depends, Query, HTTPException
from typing import Optional, List
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import text
import logging
import os

from ingestion.database import get_db

router = APIRouter()

# Configure logger
logger = logging.getLogger(__name__)


@router.get("/application-logs")
async def get_application_logs(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    level: Optional[str] = Query(None, description="Filter by log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)"),
    search: Optional[str] = Query(None, description="Search in log messages"),
    start_date: Optional[str] = Query(None, description="Start date (ISO format)"),
    end_date: Optional[str] = Query(None, description="End date (ISO format)"),
    db: Session = Depends(get_db)
):
    """Get application logs from database or log files."""
    try:
        # Try to get logs from a logs table if it exists
        try:
            # Check if application_logs table exists
            check_table = db.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = 'application_logs'
                )
            """))
            table_exists = check_table.scalar()
            
            if table_exists:
                # Query from application_logs table
                query = """
                    SELECT 
                        id,
                        level,
                        logger_name,
                        message,
                        timestamp,
                        module,
                        function_name,
                        line_number,
                        extra_data
                    FROM application_logs
                    WHERE 1=1
                """
                params = {}
                
                # Filter by level
                if level:
                    query += " AND LOWER(level) = LOWER(:level)"
                    params["level"] = level
                
                # Filter by search term
                if search:
                    query += " AND (message ILIKE :search OR logger_name ILIKE :search)"
                    params["search"] = f"%{search}%"
                
                # Filter by date range
                if start_date:
                    query += " AND timestamp >= :start_date"
                    params["start_date"] = start_date
                if end_date:
                    query += " AND timestamp <= :end_date"
                    params["end_date"] = end_date
                
                # Build count query (before adding LIMIT/OFFSET)
                count_query = """
                    SELECT COUNT(*) as total
                    FROM application_logs
                    WHERE 1=1
                """
                count_params = {}
                
                # Apply same filters for count
                if level:
                    count_query += " AND LOWER(level) = LOWER(:level)"
                    count_params["level"] = level
                if search:
                    count_query += " AND (message ILIKE :search OR logger_name ILIKE :search)"
                    count_params["search"] = f"%{search}%"
                if start_date:
                    count_query += " AND timestamp >= :start_date"
                    count_params["start_date"] = start_date
                if end_date:
                    count_query += " AND timestamp <= :end_date"
                    count_params["end_date"] = end_date
                
                count_result = db.execute(text(count_query), count_params)
                total_count = count_result.scalar() or 0
                
                # Order by timestamp descending (most recent first)
                query += " ORDER BY timestamp DESC LIMIT :limit OFFSET :skip"
                params["limit"] = limit
                params["skip"] = skip
                
                result = db.execute(text(query), params)
                rows = result.fetchall()
                
                # Convert to log format
                logs = []
                for row in rows:
                    logs.append({
                        "id": str(row[0]),
                        "level": row[1] or "INFO",
                        "logger": row[2] or "application",
                        "message": row[3] or "",
                        "timestamp": row[4].isoformat() + "Z" if row[4] else datetime.utcnow().isoformat() + "Z",
                        "module": row[5],
                        "funcName": row[6],  # Changed from "function" to "funcName" to match frontend
                        "lineno": row[7],  # Changed from "line" to "lineno" to match frontend
                        "extra": row[8] if row[8] else {}
                    })
                
                return {"logs": logs, "total": total_count}
        except Exception as e:
            logger.warning(f"Could not query application_logs table: {e}")
        
        # Fallback: Get logs from audit_logs table (user actions)
        try:
            query = """
                SELECT 
                    id,
                    action as level,
                    entity_type as logger_name,
                    CONCAT(action, ' on ', entity_type, ' ', entity_id) as message,
                    created_at as timestamp,
                    old_values,
                    new_values
                FROM audit_logs
                WHERE 1=1
            """
            params = {}
            
            # Filter by search term
            if search:
                query += " AND (action ILIKE :search OR entity_type ILIKE :search)"
                params["search"] = f"%{search}%"
            
            # Filter by date range
            if start_date:
                query += " AND created_at >= :start_date"
                params["start_date"] = start_date
            if end_date:
                query += " AND created_at <= :end_date"
                params["end_date"] = end_date
            
            # Build count query (before adding LIMIT/OFFSET)
            count_query = """
                SELECT COUNT(*) as total
                FROM audit_logs
                WHERE 1=1
            """
            count_params = {}
            
            # Apply same filters for count
            if search:
                count_query += " AND (action ILIKE :search OR entity_type ILIKE :search)"
                count_params["search"] = f"%{search}%"
            if start_date:
                count_query += " AND created_at >= :start_date"
                count_params["start_date"] = start_date
            if end_date:
                count_query += " AND created_at <= :end_date"
                count_params["end_date"] = end_date
            
            count_result = db.execute(text(count_query), count_params)
            total_count = count_result.scalar() or 0
            
            # Order by timestamp descending
            query += " ORDER BY created_at DESC LIMIT :limit OFFSET :skip"
            params["limit"] = limit
            params["skip"] = skip
            
            result = db.execute(text(query), params)
            rows = result.fetchall()
            
            # Convert to log format
            logs = []
            for row in rows:
                logs.append({
                    "id": str(row[0]),
                    "level": "INFO" if row[1] else "INFO",
                    "logger": row[2] or "audit",
                    "message": row[3] or "",
                    "timestamp": row[4].isoformat() + "Z" if row[4] else datetime.utcnow().isoformat() + "Z",
                    "module": None,
                    "funcName": None,  # Changed from "function" to "funcName" to match frontend
                    "lineno": None,  # Changed from "line" to "lineno" to match frontend
                    "extra": {
                        "old_values": row[5] if row[5] else {},
                        "new_values": row[6] if row[6] else {}
                    }
                })
            
            return {"logs": logs, "total": total_count}
        except Exception as e:
            logger.warning(f"Could not query audit_logs table: {e}")
        
        # If no logs found, return empty array with total count
        return {"logs": [], "total": 0}
        
    except Exception as e:
        logger.error(f"Error fetching application logs: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to fetch logs: {str(e)}")


@router.get("/application-logs/levels")
async def get_log_levels(db: Session = Depends(get_db)):
    """Get available log levels."""
    try:
        # Try to get distinct levels from application_logs table
        try:
            # Check if table exists first to avoid timeout
            check_table = db.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = 'application_logs'
                )
            """))
            table_exists = check_table.scalar()
            
            if table_exists:
                result = db.execute(text("""
                    SELECT DISTINCT level 
                    FROM application_logs 
                    WHERE level IS NOT NULL
                    ORDER BY level
                    LIMIT 20
                """))
                levels = [row[0] for row in result.fetchall()]
                if levels:
                    return levels
        except Exception as e:
            logger.warning(f"Could not query application_logs for levels: {e}")
            # Return default levels on error
            return ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        
        # Return default levels if table doesn't exist or no levels found
        return ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
    except Exception as e:
        logger.error(f"Error fetching log levels: {str(e)}")
        # Always return default levels on any error
        return ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]

