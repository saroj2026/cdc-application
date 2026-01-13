"""Utility functions to get and update database-specific offsets (LSN/SCN/Binlog)."""
from typing import Optional, Dict, Any, Tuple
from datetime import datetime
from sqlalchemy.orm import Session
from ingestion.database.models_db import ConnectionModel, PipelineModel
import logging

logger = logging.getLogger(__name__)


def get_postgresql_lsn(connection: ConnectionModel) -> Optional[str]:
    """Get current LSN from PostgreSQL database."""
    try:
        import psycopg2
        from psycopg2.extras import RealDictCursor
        
        conn = psycopg2.connect(
            host=connection.host,
            port=connection.port,
            database=connection.database,
            user=connection.username,
            password=connection.password,
            connect_timeout=10
        )
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Get current WAL LSN
        cursor.execute("SELECT pg_current_wal_lsn() AS current_lsn")
        result = cursor.fetchone()
        current_lsn = str(result['current_lsn']) if result else None
        
        cursor.close()
        conn.close()
        
        return current_lsn
    except Exception as e:
        logger.error(f"Failed to get PostgreSQL LSN: {str(e)}")
        return None


def get_postgresql_replication_slot_lsn(connection: ConnectionModel, slot_name: str) -> Optional[Dict[str, Any]]:
    """Get LSN information from PostgreSQL replication slot."""
    try:
        import psycopg2
        from psycopg2.extras import RealDictCursor
        
        conn = psycopg2.connect(
            host=connection.host,
            port=connection.port,
            database=connection.database,
            user=connection.username,
            password=connection.password,
            connect_timeout=10
        )
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Get replication slot LSN info
        cursor.execute("""
            SELECT 
                slot_name,
                confirmed_flush_lsn AS cdc_lsn,
                pg_current_wal_lsn() AS current_lsn,
                pg_wal_lsn_diff(pg_current_wal_lsn(), confirmed_flush_lsn) AS lag_bytes,
                active
            FROM pg_replication_slots
            WHERE slot_name = %s
        """, (slot_name,))
        
        result = cursor.fetchone()
        
        if result:
            slot_info = {
                'slot_name': result['slot_name'],
                'cdc_lsn': str(result['cdc_lsn']) if result['cdc_lsn'] else None,
                'current_lsn': str(result['current_lsn']) if result['current_lsn'] else None,
                'lag_bytes': result['lag_bytes'] if result['lag_bytes'] else 0,
                'active': result['active']
            }
        else:
            slot_info = None
        
        cursor.close()
        conn.close()
        
        return slot_info
    except Exception as e:
        logger.error(f"Failed to get PostgreSQL replication slot LSN: {str(e)}")
        return None


def get_mysql_binlog_position(connection: ConnectionModel) -> Optional[str]:
    """Get current binlog position from MySQL database."""
    try:
        import pymysql
        
        conn = pymysql.connect(
            host=connection.host,
            port=connection.port,
            database=connection.database,
            user=connection.username,
            password=connection.password,
            connect_timeout=10
        )
        cursor = conn.cursor()
        
        # Get current binlog position
        cursor.execute("SHOW MASTER STATUS")
        result = cursor.fetchone()
        
        if result:
            # Format: file:position
            binlog_file = result[0]
            binlog_position = result[1]
            binlog_position_str = f"{binlog_file}:{binlog_position}"
        else:
            binlog_position_str = None
        
        cursor.close()
        conn.close()
        
        return binlog_position_str
    except Exception as e:
        logger.error(f"Failed to get MySQL binlog position: {str(e)}")
        return None


def get_sqlserver_lsn(connection: ConnectionModel) -> Optional[str]:
    """Get current LSN from SQL Server database."""
    try:
        import pyodbc
        
        # Build connection string
        conn_str = (
            f"DRIVER={{ODBC Driver 17 for SQL Server}};"
            f"SERVER={connection.host},{connection.port};"
            f"DATABASE={connection.database};"
            f"UID={connection.username};"
            f"PWD={connection.password}"
        )
        
        conn = pyodbc.connect(conn_str, timeout=10)
        cursor = conn.cursor()
        
        # Get current LSN from sys.fn_dblog or sys.dm_repl_traninfo
        # SQL Server LSN format: 00000000:00000000:0000
        cursor.execute("""
            SELECT 
                sys.fn_cdc_get_max_lsn() AS current_lsn
        """)
        
        result = cursor.fetchone()
        current_lsn = str(result[0]) if result and result[0] else None
        
        cursor.close()
        conn.close()
        
        return current_lsn
    except Exception as e:
        logger.error(f"Failed to get SQL Server LSN: {str(e)}")
        return None


def get_oracle_scn(connection: ConnectionModel) -> Optional[str]:
    """Get current SCN from Oracle database."""
    try:
        import cx_Oracle
        
        dsn = cx_Oracle.makedsn(connection.host, connection.port, service_name=connection.database)
        conn = cx_Oracle.connect(
            user=connection.username,
            password=connection.password,
            dsn=dsn
        )
        cursor = conn.cursor()
        
        # Get current SCN
        cursor.execute("SELECT CURRENT_SCN FROM V$DATABASE")
        result = cursor.fetchone()
        current_scn = str(result[0]) if result else None
        
        cursor.close()
        conn.close()
        
        return current_scn
    except Exception as e:
        logger.error(f"Failed to get Oracle SCN: {str(e)}")
        return None


def get_database_offset(connection: ConnectionModel, pipeline: Optional[PipelineModel] = None) -> Dict[str, Any]:
    """Get current offset/LSN/SCN based on database type.
    
    Returns:
        Dict with keys: 'current_lsn', 'current_offset', 'current_scn', 'offset_type', 'timestamp'
    """
    result = {
        'current_lsn': None,
        'current_offset': None,
        'current_scn': None,
        'offset_type': None,
        'timestamp': datetime.utcnow().isoformat()
    }
    
    db_type = connection.database_type.lower() if connection.database_type else None
    
    try:
        if db_type == 'postgresql':
            # Try to get from replication slot first if pipeline has connector name
            if pipeline and pipeline.debezium_connector_name:
                slot_name = f"{pipeline.name}_slot"
                slot_info = get_postgresql_replication_slot_lsn(connection, slot_name)
                if slot_info and slot_info.get('cdc_lsn'):
                    result['current_lsn'] = slot_info['cdc_lsn']
                    result['offset_type'] = 'replication_slot_lsn'
                elif slot_info and slot_info.get('current_lsn'):
                    result['current_lsn'] = slot_info['current_lsn']
                    result['offset_type'] = 'wal_lsn'
            else:
                # Fallback to current WAL LSN
                current_lsn = get_postgresql_lsn(connection)
                if current_lsn:
                    result['current_lsn'] = current_lsn
                    result['offset_type'] = 'wal_lsn'
                    
        elif db_type == 'mysql':
            binlog_position = get_mysql_binlog_position(connection)
            if binlog_position:
                result['current_offset'] = binlog_position
                result['offset_type'] = 'binlog_position'
                
        elif db_type == 'sqlserver' or db_type == 'mssql':
            current_lsn = get_sqlserver_lsn(connection)
            if current_lsn:
                result['current_lsn'] = current_lsn
                result['offset_type'] = 'transaction_lsn'
                
        elif db_type == 'oracle':
            current_scn = get_oracle_scn(connection)
            if current_scn:
                result['current_scn'] = current_scn
                result['offset_type'] = 'scn'
                
    except Exception as e:
        logger.error(f"Error getting database offset for {db_type}: {str(e)}")
    
    return result


def update_pipeline_offset(
    db: Session,
    pipeline: PipelineModel,
    connection: ConnectionModel,
    offset_data: Optional[Dict[str, Any]] = None
) -> bool:
    """Update pipeline with current offset/LSN/SCN from source database.
    
    Args:
        db: Database session
        pipeline: Pipeline model to update
        connection: Source connection
        offset_data: Optional pre-fetched offset data (if None, will fetch)
    
    Returns:
        True if update was successful
    """
    try:
        # Get offset data if not provided
        if offset_data is None:
            offset_data = get_database_offset(connection, pipeline)
        
        # Update pipeline fields based on database type
        if offset_data.get('current_lsn'):
            pipeline.current_lsn = offset_data['current_lsn']
        if offset_data.get('current_offset'):
            pipeline.current_offset = offset_data['current_offset']
        if offset_data.get('current_scn'):
            pipeline.current_scn = offset_data['current_scn']
        
        # Update timestamp
        from datetime import datetime
        pipeline.last_offset_updated = datetime.utcnow()
        
        db.commit()
        return True
    except Exception as e:
        logger.error(f"Failed to update pipeline offset: {str(e)}")
        db.rollback()
        return False

