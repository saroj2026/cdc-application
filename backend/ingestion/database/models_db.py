"""Database models."""
from sqlalchemy import Column, String, Integer, DateTime, Text, JSON, Enum as SQLEnum, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase
from datetime import datetime
import enum
import uuid


class Base(DeclarativeBase):
    """Base class for all models."""
    pass


class PipelineStatus(str, enum.Enum):
    """Pipeline status enum."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"
    PAUSED = "paused"


class CDCStatus(str, enum.Enum):
    """CDC status enum."""
    RUNNING = "running"
    STOPPED = "stopped"
    ERROR = "error"
    PAUSED = "paused"


class PipelineModel(Base):
    """Pipeline database model."""
    __tablename__ = "pipelines"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, unique=True, nullable=False)
    source_connection_id = Column(UUID(as_uuid=True))
    target_connection_id = Column(UUID(as_uuid=True))
    source_database = Column(String)
    source_schema = Column(String)
    source_tables = Column(JSON)
    target_database = Column(String)
    target_schema = Column(String)
    target_tables = Column(JSON)
    mode = Column(String)
    status = Column(SQLEnum(PipelineStatus), default=PipelineStatus.INACTIVE)
    cdc_status = Column(SQLEnum(CDCStatus), default=CDCStatus.STOPPED)
    debezium_connector_name = Column(String)
    sink_connector_name = Column(String)
    kafka_topics = Column(JSON)
    debezium_config = Column(JSON)
    sink_config = Column(JSON)
    # Offset/LSN/SCN tracking fields (database-specific)
    current_lsn = Column(String, nullable=True)  # PostgreSQL/SQL Server LSN
    current_offset = Column(String, nullable=True)  # MySQL binlog position (file:position)
    current_scn = Column(String, nullable=True)  # Oracle SCN
    last_offset_updated = Column(DateTime, nullable=True)  # When offset was last updated
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ConnectionModel(Base):
    """Connection database model."""
    __tablename__ = "connections"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False, index=True)
    connection_type = Column(String(50), nullable=False)  # 'source' or 'target'
    database_type = Column(String(50), nullable=False)  # 'postgresql', 'sqlserver', 'mysql', 's3'
    host = Column(String(255), nullable=False)
    port = Column(Integer, nullable=False)
    database = Column(String(255), nullable=False)
    username = Column(String(255), nullable=False)
    password = Column(Text, nullable=False)
    schema = Column(String(255), nullable=True)  # Note: database uses 'schema', not 'db_schema'
    additional_config = Column(JSON, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    last_tested_at = Column(DateTime, nullable=True)
    last_test_status = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    deleted_at = Column(DateTime, nullable=True)


class UserStatus(str, enum.Enum):
    """User status enum."""
    INVITED = "invited"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    DEACTIVATED = "deactivated"


class UserRole(str, enum.Enum):
    """User role enum."""
    SUPER_ADMIN = "super_admin"
    ORG_ADMIN = "org_admin"
    DATA_ENGINEER = "data_engineer"
    OPERATOR = "operator"
    VIEWER = "viewer"


class UserModel(Base):
    """User database model with RBAC and tenant isolation.
    
    Note: New columns (tenant_id, status, last_login) are nullable for backward compatibility.
    Run the migration script (backend/migrations/add_user_management_columns.sql) to add these columns.
    """
    __tablename__ = "users"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String(255), nullable=False, index=True)
    full_name = Column(String(255), nullable=False)
    hashed_password = Column(Text, nullable=False)
    role_name = Column(String(50), nullable=False, default="viewer")
    is_active = Column(Boolean, default=True, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # New columns - added via migration (nullable for backward compatibility)
    # These will be None until migration is run
    tenant_id = Column(UUID(as_uuid=True), nullable=True)  # Tenant isolation
    status = Column(String(20), nullable=True)  # User status (INVITED, ACTIVE, SUSPENDED, DEACTIVATED)
    last_login = Column(DateTime, nullable=True)  # Last login timestamp


class UserSessionModel(Base):
    """User session model for refresh tokens."""
    __tablename__ = "user_sessions"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), nullable=False, index=True)
    refresh_token_hash = Column(Text, nullable=False)
    expires_at = Column(DateTime, nullable=False, index=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        """Safe string representation that doesn't expose sensitive data."""
        return f"<UserSessionModel(id='{self.id[:8]}...', user_id='{self.user_id[:8] if self.user_id else None}...', expires_at={self.expires_at})>"


class AuditLogModel(Base):
    """Audit log model for tracking all user actions."""
    __tablename__ = "audit_logs"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    user_id = Column(String(36), nullable=True, index=True)
    action = Column(String(100), nullable=False, index=True)  # e.g., "create_pipeline", "start_pipeline"
    resource_type = Column(String(50), nullable=True, index=True)  # e.g., "pipeline", "connection"
    resource_id = Column(String(36), nullable=True, index=True)
    old_value = Column(JSON, nullable=True)  # Previous state
    new_value = Column(JSON, nullable=True)  # New state
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

