"""Audit logging for CDC Replication Application."""
from fastapi import Request
from typing import Optional, Dict, Any
from datetime import datetime
import uuid
from sqlalchemy.orm import Session

from ingestion.database.models_db import AuditLogModel, UserModel


def log_audit_event(
    db: Session,
    user: Optional[UserModel],
    action: str,
    resource_type: Optional[str] = None,
    resource_id: Optional[str] = None,
    old_value: Optional[Dict[str, Any]] = None,
    new_value: Optional[Dict[str, Any]] = None,
    request: Optional[Request] = None
):
    """Log an audit event to the database.
    
    Args:
        db: Database session
        user: User performing the action (None for system actions)
        action: Action name (e.g., "create_pipeline", "start_pipeline")
        resource_type: Type of resource (e.g., "pipeline", "connection")
        resource_id: ID of the resource
        old_value: Previous state (for updates)
        new_value: New state (for creates/updates)
        request: FastAPI request object (for IP address and user agent)
    """
    try:
        # Get IP address and user agent from request
        ip_address = None
        user_agent = None
        if request:
            ip_address = request.client.host if request.client else None
            user_agent = request.headers.get("user-agent")
        
        # Get tenant_id from user if available
        tenant_id = None
        if user and hasattr(user, 'tenant_id'):
            try:
                tenant_id = user.tenant_id
            except Exception:
                pass
        
        # Get user_id safely
        user_id_str = None
        if user and hasattr(user, 'id'):
            try:
                user_id_str = str(user.id) if user.id else None
            except Exception:
                pass
        
        # Serialize JSON values properly to avoid SQLAlchemy f405 error
        import json
        old_value_json = None
        new_value_json = None
        
        if old_value is not None:
            try:
                # Convert dict to JSON string if needed, or use as-is if already serializable
                if isinstance(old_value, (dict, list)):
                    old_value_json = json.loads(json.dumps(old_value))  # Ensure it's JSON-serializable
                else:
                    old_value_json = old_value
            except Exception:
                old_value_json = None
        
        if new_value is not None:
            try:
                # Convert dict to JSON string if needed, or use as-is if already serializable
                if isinstance(new_value, (dict, list)):
                    new_value_json = json.loads(json.dumps(new_value))  # Ensure it's JSON-serializable
                else:
                    new_value_json = new_value
            except Exception:
                new_value_json = None
        
        # Create audit log entry
        audit_log = AuditLogModel(
            id=str(uuid.uuid4()),
            tenant_id=tenant_id,
            user_id=user_id_str,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            old_value=old_value_json,
            new_value=new_value_json,
            ip_address=ip_address,
            user_agent=user_agent,
            created_at=datetime.utcnow()
        )
        
        db.add(audit_log)
        db.flush()  # Flush to get any immediate errors
        
        try:
            db.commit()
            # Detach audit log to prevent serialization issues
            try:
                db.expunge(audit_log)
            except Exception:
                pass  # If expunge fails, continue anyway
        except Exception as commit_error:
            db.rollback()
            raise commit_error  # Re-raise to be caught by outer except
    except Exception as e:
        # Don't fail the request if audit logging fails
        # Log error but continue
        try:
            db.rollback()
        except Exception:
            pass  # If rollback fails, continue anyway
        
        import logging
        error_msg = str(e)
        # Check if it's a table doesn't exist error
        if "does not exist" in error_msg.lower() or "relation" in error_msg.lower() or "table" in error_msg.lower():
            logging.warning(f"audit_logs table does not exist. Please run create_audit_logs_table.py")
        elif "column" in error_msg.lower() and "does not exist" in error_msg.lower():
            logging.warning(f"audit_logs table is missing columns. Please run create_audit_logs_table.py")
        else:
            # Log the full error for debugging
            logging.error(f"Failed to log audit event: {type(e).__name__}: {error_msg}")
            # Also log the action that failed
            logging.error(f"  Action: {action}, Resource: {resource_type}, Resource ID: {resource_id}")


def mask_sensitive_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """Mask sensitive fields in audit logs (passwords, tokens, etc.)."""
    if not isinstance(data, dict):
        return data
    
    masked = data.copy()
    sensitive_fields = ['password', 'hashed_password', 'token', 'access_token', 'refresh_token', 'secret', 'api_key']
    
    for key, value in masked.items():
        if any(sensitive in key.lower() for sensitive in sensitive_fields):
            masked[key] = "***MASKED***"
        elif isinstance(value, dict):
            masked[key] = mask_sensitive_data(value)
        elif isinstance(value, list):
            masked[key] = [mask_sensitive_data(item) if isinstance(item, dict) else item for item in value]
    
    return masked

