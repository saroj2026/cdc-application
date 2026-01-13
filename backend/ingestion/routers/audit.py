"""Audit log router."""
from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_, or_, func

from ingestion.database import get_db
from ingestion.database.models_db import AuditLogModel, UserModel
from ingestion.routers.auth import get_current_user
from ingestion.rbac import require_permission

router = APIRouter()


class AuditLogResponse(BaseModel):
    id: str
    tenant_id: Optional[str]
    user_id: Optional[str]
    user_email: Optional[str]
    action: str
    resource_type: Optional[str]
    resource_id: Optional[str]
    old_value: Optional[Dict[str, Any]]
    new_value: Optional[Dict[str, Any]]
    ip_address: Optional[str]
    user_agent: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


@router.get("", response_model=List[AuditLogResponse])
async def get_audit_logs(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    action: Optional[str] = Query(None, description="Filter by action"),
    resource_type: Optional[str] = Query(None, description="Filter by resource type"),
    resource_id: Optional[str] = Query(None, description="Filter by resource ID"),
    user_id: Optional[str] = Query(None, description="Filter by user ID"),
    start_date: Optional[datetime] = Query(None, description="Start date filter"),
    end_date: Optional[datetime] = Query(None, description="End date filter"),
    current_user: UserModel = Depends(require_permission("view_audit_logs")),
    db: Session = Depends(get_db)
):
    """Get audit logs with filtering."""
    try:
        # Check if audit_logs table exists
        from sqlalchemy import inspect, text
        inspector = inspect(db.bind)
        tables = inspector.get_table_names()
        
        if 'audit_logs' not in tables:
            # Table doesn't exist - return empty list
            import logging
            logging.warning("audit_logs table does not exist. Please run: python create_audit_logs_table.py")
            return []
        
        # Verify table has required columns
        try:
            columns = [col['name'] for col in inspector.get_columns('audit_logs')]
            required_columns = ['id', 'action', 'created_at']
            missing_columns = [col for col in required_columns if col not in columns]
            if missing_columns:
                import logging
                logging.warning(f"audit_logs table is missing columns: {missing_columns}. Please run: python create_audit_logs_table.py")
                return []
        except Exception as col_check_error:
            import logging
            logging.warning(f"Could not verify audit_logs table columns: {str(col_check_error)}")
        
        query = db.query(AuditLogModel)
        
        # Apply filters
        if action:
            query = query.filter(AuditLogModel.action.ilike(f"%{action}%"))
        
        if resource_type:
            query = query.filter(AuditLogModel.resource_type == resource_type)
        
        if resource_id:
            query = query.filter(AuditLogModel.resource_id == resource_id)
        
        if user_id:
            query = query.filter(AuditLogModel.user_id == user_id)
        
        if start_date:
            query = query.filter(AuditLogModel.created_at >= start_date)
        
        if end_date:
            query = query.filter(AuditLogModel.created_at <= end_date)
        
        # Tenant isolation (if not super admin) - handle gracefully if tenant_id column doesn't exist
        try:
            if not current_user.is_superuser and hasattr(current_user, 'tenant_id') and current_user.tenant_id:
                query = query.filter(
                    or_(
                        AuditLogModel.tenant_id == str(current_user.tenant_id),
                        AuditLogModel.tenant_id.is_(None)  # System-wide logs
                    )
                )
        except Exception:
            # If tenant_id filtering fails, continue without it
            import logging
            logging.warning("Tenant isolation filter failed, continuing without it")
        
        # Order by created_at descending (most recent first)
        query = query.order_by(desc(AuditLogModel.created_at))
        
        # Use raw SQL for better performance and to avoid SQLAlchemy issues
        try:
            from sqlalchemy import text
            
            # Build WHERE clause based on filters
            where_clauses = []
            params = {"limit": limit, "skip": skip}
            
            if action:
                where_clauses.append("action ILIKE :action")
                params["action"] = f"%{action}%"
            
            if resource_type:
                # Case-insensitive filtering for resource_type
                where_clauses.append("LOWER(resource_type) = LOWER(:resource_type)")
                params["resource_type"] = resource_type
            
            if resource_id:
                where_clauses.append("resource_id = :resource_id")
                params["resource_id"] = resource_id
            
            if user_id:
                where_clauses.append("user_id = :user_id")
                params["user_id"] = user_id
            
            if start_date:
                where_clauses.append("created_at >= :start_date")
                params["start_date"] = start_date
            
            if end_date:
                where_clauses.append("created_at <= :end_date")
                params["end_date"] = end_date
            
            # Tenant isolation - only apply if user is not superuser and has tenant_id
            # For now, let's be more permissive - show all logs if tenant_id is None or matches
            tenant_filter_applied = False
            if not current_user.is_superuser and hasattr(current_user, 'tenant_id') and current_user.tenant_id:
                where_clauses.append("(tenant_id = :tenant_id OR tenant_id IS NULL)")
                params["tenant_id"] = str(current_user.tenant_id)
                tenant_filter_applied = True
            
            where_sql = " AND ".join(where_clauses) if where_clauses else "1=1"
            
            # Debug logging
            import logging
            logging.info(f"Audit logs query - WHERE: {where_sql}, params: {params}")
            
            # First, check total logs in table (no filters) for debugging
            total_in_table = db.execute(text("SELECT COUNT(*) FROM audit_logs")).scalar() or 0
            logging.info(f"Total audit logs in table (no filters): {total_in_table}")
            
            # Get total count with filters
            count_query = text(f"SELECT COUNT(*) FROM audit_logs WHERE {where_sql}")
            total = db.execute(count_query, params).scalar() or 0
            logging.info(f"Total audit logs matching query: {total}")
            
            # If no logs with filters but there are logs in table, try without tenant filter
            if total == 0 and total_in_table > 0 and tenant_filter_applied:
                logging.warning("No logs found with tenant filter, retrying without tenant filter...")
                # Remove tenant filter and try again
                where_clauses = [clause for clause in where_clauses if "tenant_id" not in clause]
                where_sql = " AND ".join(where_clauses) if where_clauses else "1=1"
                params.pop("tenant_id", None)
                logging.info(f"Retrying without tenant filter - WHERE: {where_sql}")
                total = db.execute(count_query, params).scalar() or 0
                logging.info(f"Total audit logs without tenant filter: {total}")
            
            # Get logs with raw SQL for better performance
            raw_query = text(f"""
                SELECT id, tenant_id, user_id, action, resource_type, resource_id,
                       old_value, new_value, ip_address, user_agent, created_at
                FROM audit_logs
                WHERE {where_sql}
                ORDER BY created_at DESC
                LIMIT :limit OFFSET :skip
            """)
            
            raw_logs = db.execute(raw_query, params).fetchall()
            logging.info(f"Retrieved {len(raw_logs)} audit log rows from database")
            logs = []
            for row in raw_logs:
                # Create a simple dict from row
                log_dict = {
                    "id": str(row[0]) if row[0] else "",
                    "tenant_id": str(row[1]) if row[1] else None,
                    "user_id": str(row[2]) if row[2] else None,
                    "action": row[3] or "",
                    "resource_type": row[4],
                    "resource_id": row[5],
                    "old_value": row[6],
                    "new_value": row[7],
                    "ip_address": row[8],
                    "user_agent": row[9],
                    "created_at": row[10]
                }
                logs.append(log_dict)
        except Exception as query_error:
            import logging
            import traceback
            error_msg = str(query_error)
            logging.error(f"Query failed: {error_msg}")
            logging.error(f"Traceback: {traceback.format_exc()}")
            
            # Try a simpler query as fallback
            try:
                logging.info("Attempting fallback query without filters...")
                fallback_query = text("""
                    SELECT id, tenant_id, user_id, action, resource_type, resource_id,
                           old_value, new_value, ip_address, user_agent, created_at
                    FROM audit_logs
                    ORDER BY created_at DESC
                    LIMIT :limit OFFSET :skip
                """)
                raw_logs = db.execute(fallback_query, {"limit": limit, "skip": skip}).fetchall()
                logging.info(f"Fallback query returned {len(raw_logs)} rows")
                # Process the fallback results
                logs = []
                for row in raw_logs:
                    log_dict = {
                        "id": str(row[0]) if row[0] else "",
                        "tenant_id": str(row[1]) if row[1] else None,
                        "user_id": str(row[2]) if row[2] else None,
                        "action": row[3] or "",
                        "resource_type": row[4],
                        "resource_id": row[5],
                        "old_value": row[6],
                        "new_value": row[7],
                        "ip_address": row[8],
                        "user_agent": row[9],
                        "created_at": row[10]
                    }
                    logs.append(log_dict)
            except Exception as fallback_error:
                logging.error(f"Fallback query also failed: {str(fallback_error)}")
                return []
        
        # Enrich with user email - batch lookup for better performance
        result = []
        user_emails_map = {}
        
        # Collect all unique user IDs
        user_ids = set()
        for log in logs:
            if log.get("user_id"):
                user_ids.add(log["user_id"])
        
        # Batch lookup users
        if user_ids:
            try:
                user_id_list = list(user_ids)
                users = db.query(UserModel).filter(UserModel.id.in_(user_id_list)).all()
                for user in users:
                    user_emails_map[str(user.id)] = user.email
            except Exception as batch_lookup_error:
                import logging
                logging.warning(f"Batch user lookup failed: {str(batch_lookup_error)}")
        
        # Build response
        for log in logs:
            try:
                log_id = log.get("id", "")
                log_user_id = log.get("user_id")
                log_action = log.get("action", "")
                log_resource_type = log.get("resource_type")
                log_resource_id = log.get("resource_id")
                log_tenant_id = log.get("tenant_id")
                log_old_value = log.get("old_value")
                log_new_value = log.get("new_value")
                log_ip_address = log.get("ip_address")
                log_user_agent = log.get("user_agent")
                log_created_at = log.get("created_at")
                
                # Get user email from map
                user_email = user_emails_map.get(str(log_user_id)) if log_user_id else None
                
                result.append(AuditLogResponse(
                    id=log_id,
                    tenant_id=log_tenant_id,
                    user_id=log_user_id,
                    user_email=user_email,
                    action=log_action,
                    resource_type=log_resource_type,
                    resource_id=log_resource_id,
                    old_value=log_old_value,
                    new_value=log_new_value,
                    ip_address=log_ip_address,
                    user_agent=log_user_agent,
                    created_at=log_created_at
                ))
            except Exception as log_error:
                # If processing a single log fails, skip it and continue
                import logging
                logging.warning(f"Failed to process audit log entry: {type(log_error).__name__}: {str(log_error)}")
                continue
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        import logging
        error_msg = str(e)
        # Check if it's a table doesn't exist error
        if "does not exist" in error_msg.lower() or "relation" in error_msg.lower() or "table" in error_msg.lower():
            logging.warning("audit_logs table does not exist. Returning empty list.")
            return []
        logging.error(f"Failed to fetch audit logs: {type(e).__name__}: {error_msg}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch audit logs: {error_msg[:200]}")


@router.get("/filters")
async def get_audit_log_filters(
    current_user: UserModel = Depends(require_permission("view_audit_logs")),
    db: Session = Depends(get_db)
):
    """Get available filter options for audit logs."""
    try:
        from sqlalchemy import text
        
        # Check if audit_logs table exists
        from sqlalchemy import inspect
        inspector = inspect(db.bind)
        tables = inspector.get_table_names()
        
        if 'audit_logs' not in tables:
            return {
                "actions": [],
                "resource_types": []
            }
        
        # Get distinct actions
        actions_query = text("SELECT DISTINCT action FROM audit_logs WHERE action IS NOT NULL ORDER BY action")
        actions_result = db.execute(actions_query).fetchall()
        actions = [row[0] for row in actions_result if row[0]]
        
        # Get distinct resource types
        resource_types_query = text("SELECT DISTINCT resource_type FROM audit_logs WHERE resource_type IS NOT NULL ORDER BY resource_type")
        resource_types_result = db.execute(resource_types_query).fetchall()
        resource_types = [row[0] for row in resource_types_result if row[0]]
        
        return {
            "actions": actions,
            "resource_types": resource_types
        }
    except Exception as e:
        import logging
        logging.error(f"Failed to get audit log filters: {str(e)}")
        return {
            "actions": [],
            "resource_types": []
        }


@router.get("/stats")
async def get_audit_log_stats(
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    current_user: UserModel = Depends(require_permission("view_audit_logs")),
    db: Session = Depends(get_db)
):
    """Get audit log statistics."""
    try:
        # Check if audit_logs table exists
        from sqlalchemy import inspect
        inspector = inspect(db.bind)
        tables = inspector.get_table_names()
        
        if 'audit_logs' not in tables:
            # Table doesn't exist - return empty stats
            import logging
            logging.warning("audit_logs table does not exist. Returning empty stats.")
            return {
                "total_logs": 0,
                "action_counts": {},
                "resource_type_counts": {}
            }
        
        query = db.query(AuditLogModel)
        
        if start_date:
            query = query.filter(AuditLogModel.created_at >= start_date)
        
        if end_date:
            query = query.filter(AuditLogModel.created_at <= end_date)
        
        # Tenant isolation - handle gracefully
        try:
            if not current_user.is_superuser and hasattr(current_user, 'tenant_id') and current_user.tenant_id:
                query = query.filter(
                    or_(
                        AuditLogModel.tenant_id == str(current_user.tenant_id),
                        AuditLogModel.tenant_id.is_(None)
                    )
                )
        except Exception:
            # If tenant_id filtering fails, continue without it
            import logging
            logging.warning("Tenant isolation filter failed in stats, continuing without it")
        
        total_logs = query.count()
        
        # Count by action
        try:
            actions = db.query(
                AuditLogModel.action,
                func.count(AuditLogModel.id).label('count')
            ).group_by(AuditLogModel.action).all()
            action_counts = {action: count for action, count in actions}
        except Exception:
            action_counts = {}
        
        # Count by resource type
        try:
            resource_types = db.query(
                AuditLogModel.resource_type,
                func.count(AuditLogModel.id).label('count')
            ).filter(AuditLogModel.resource_type.isnot(None)).group_by(AuditLogModel.resource_type).all()
            resource_type_counts = {rtype: count for rtype, count in resource_types}
        except Exception:
            resource_type_counts = {}
        
        return {
            "total_logs": total_logs,
            "action_counts": action_counts,
            "resource_type_counts": resource_type_counts
        }
        
    except HTTPException:
        raise
    except Exception as e:
        import logging
        error_msg = str(e)
        # Check if it's a table doesn't exist error
        if "does not exist" in error_msg.lower() or "relation" in error_msg.lower() or "table" in error_msg.lower():
            logging.warning("audit_logs table does not exist. Returning empty stats.")
            return {
                "total_logs": 0,
                "action_counts": {},
                "resource_type_counts": {}
            }
        logging.error(f"Failed to fetch audit log stats: {type(e).__name__}: {error_msg}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch audit log stats: {error_msg[:200]}")

