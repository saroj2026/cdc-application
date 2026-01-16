"""CDC Manager service for managing CDC pipelines."""

from __future__ import annotations

import json
import logging
import time
from datetime import datetime
from typing import Any, Dict, List, Optional

import requests

from ingestion.models import Connection, Pipeline, PipelineStatus, FullLoadStatus, CDCStatus, PipelineMode
from ingestion.kafka_connect_client import KafkaConnectClient
from ingestion.debezium_config import DebeziumConfigGenerator
from ingestion.sink_config import SinkConfigGenerator
from ingestion.transfer import DataTransfer
from ingestion.connectors import SQLServerConnector, PostgreSQLConnector
from ingestion.connectors.base_connector import BaseConnector
from ingestion.schema_service import SchemaService
from ingestion.exceptions import FullLoadError, ValidationError
from ingestion.validation import validate_source_data, validate_target_row_count

logger = logging.getLogger(__name__)

# Global reference to database session factory (set from api.py)
_db_session_factory = None

def set_db_session_factory(session_factory):
    """Set the database session factory for status persistence."""
    global _db_session_factory
    _db_session_factory = session_factory


class CDCManager:
    """Manages CDC pipeline lifecycle and operations."""
    
    def __init__(
        self,
        kafka_connect_url: str = "http://localhost:8083",
        connection_store: Optional[Dict[str, Connection]] = None
    ):
        """Initialize CDC Manager.
        
        Args:
            kafka_connect_url: Kafka Connect REST API URL
            connection_store: Dictionary to store connections (in-memory for now)
        """
        self.kafka_client = KafkaConnectClient(base_url=kafka_connect_url)
        self.connection_store = connection_store or {}
        self.pipeline_store: Dict[str, Pipeline] = {}
        self.schema_service = SchemaService()
        self.schema_service = SchemaService()
    
    def add_connection(self, connection: Connection) -> None:
        """Add a connection to the store.
        
        Args:
            connection: Connection object to add
        """
        self.connection_store[connection.id] = connection
        logger.info(f"Added connection: {connection.name} ({connection.id})")
    
    def get_connection(self, connection_id: str) -> Optional[Connection]:
        """Get connection by ID.
        
        Args:
            connection_id: Connection ID
            
        Returns:
            Connection object or None if not found
        """
        return self.connection_store.get(connection_id)
    
    def create_pipeline(
        self,
        pipeline: Pipeline,
        source_connection: Connection,
        target_connection: Connection
    ) -> Pipeline:
        """Create a new CDC pipeline.
        
        Args:
            pipeline: Pipeline object
            source_connection: Source database connection
            target_connection: Target database connection
            
        Returns:
            Created pipeline
        """
        # Store connections
        self.add_connection(source_connection)
        self.add_connection(target_connection)
        
        # Store pipeline
        self.pipeline_store[pipeline.id] = pipeline
        
        logger.info(f"Created pipeline: {pipeline.name} ({pipeline.id})")
        return pipeline
    
    def _persist_pipeline_status(self, pipeline: Pipeline) -> None:
        """Persist pipeline status to database.
        
        Args:
            pipeline: Pipeline object with updated status
        """
        if not _db_session_factory:
            logger.debug("Database session factory not set, skipping status persistence")
            return
        
        try:
            from ingestion.database.models_db import PipelineStatus as DBPipelineStatus, FullLoadStatus as DBFullLoadStatus, CDCStatus as DBCDCStatus, PipelineModel
            from datetime import datetime
            
            db = next(_db_session_factory())
            try:
                pipeline_model = db.query(PipelineModel).filter(PipelineModel.id == pipeline.id).first()
                if not pipeline_model:
                    logger.warning(f"Pipeline {pipeline.id} not found in database for status update")
                    return
                
                # Update status fields - handle both enum objects and strings
                try:
                    # Convert status - handle both enum objects and string values
                    if isinstance(pipeline.status, str):
                        pipeline_model.status = DBPipelineStatus(pipeline.status)
                    elif hasattr(pipeline.status, 'value'):
                        pipeline_model.status = DBPipelineStatus(pipeline.status.value)
                    else:
                        pipeline_model.status = DBPipelineStatus.RUNNING
                except (ValueError, AttributeError) as e:
                    logger.warning(f"Failed to set status: {e}, using RUNNING")
                    pipeline_model.status = DBPipelineStatus.RUNNING
                
                try:
                    # Convert full_load_status - handle both enum objects and string values
                    if isinstance(pipeline.full_load_status, str):
                        pipeline_model.full_load_status = DBFullLoadStatus(pipeline.full_load_status)
                    elif hasattr(pipeline.full_load_status, 'value'):
                        pipeline_model.full_load_status = DBFullLoadStatus(pipeline.full_load_status.value)
                    else:
                        pipeline_model.full_load_status = DBFullLoadStatus.NOT_STARTED
                except (ValueError, AttributeError) as e:
                    logger.warning(f"Failed to set full_load_status: {e}, using NOT_STARTED")
                    pipeline_model.full_load_status = DBFullLoadStatus.NOT_STARTED
                
                try:
                    # Convert cdc_status - handle both enum objects and string values
                    if isinstance(pipeline.cdc_status, str):
                        pipeline_model.cdc_status = DBCDCStatus(pipeline.cdc_status)
                    elif hasattr(pipeline.cdc_status, 'value'):
                        pipeline_model.cdc_status = DBCDCStatus(pipeline.cdc_status.value)
                    else:
                        pipeline_model.cdc_status = DBCDCStatus.NOT_STARTED
                except (ValueError, AttributeError) as e:
                    logger.warning(f"Failed to set cdc_status: {e}, using NOT_STARTED")
                    pipeline_model.cdc_status = DBCDCStatus.NOT_STARTED
                
                # Update other fields
                pipeline_model.full_load_lsn = pipeline.full_load_lsn
                pipeline_model.debezium_connector_name = pipeline.debezium_connector_name
                pipeline_model.sink_connector_name = pipeline.sink_connector_name
                pipeline_model.kafka_topics = pipeline.kafka_topics or []
                pipeline_model.debezium_config = pipeline.debezium_config or {}
                pipeline_model.sink_config = pipeline.sink_config or {}
                pipeline_model.updated_at = datetime.utcnow()
                
                # Set full_load_completed_at if full load is completed
                # Check both enum object and string value
                full_load_completed = (
                    pipeline.full_load_status == FullLoadStatus.COMPLETED or
                    (isinstance(pipeline.full_load_status, str) and pipeline.full_load_status == "COMPLETED") or
                    (hasattr(pipeline.full_load_status, 'value') and pipeline.full_load_status.value == "COMPLETED")
                )
                if full_load_completed:
                    pipeline_model.full_load_completed_at = datetime.utcnow()
                
                db.commit()
                logger.info(
                    f"Persisted pipeline {pipeline.id} status to database: "
                    f"status={pipeline_model.status.value}, "
                    f"full_load_status={pipeline_model.full_load_status.value}, "
                    f"cdc_status={pipeline_model.cdc_status.value}"
                )
            except Exception as e:
                db.rollback()
                logger.error(f"Failed to persist pipeline status to database: {e}", exc_info=True)
                raise
            finally:
                db.close()
        except Exception as e:
            logger.error(f"Error in _persist_pipeline_status: {e}", exc_info=True)
            # Don't raise - allow pipeline to continue even if status persistence fails
    
    def start_pipeline(self, pipeline_id: str) -> Dict[str, Any]:
        """Start a CDC pipeline.
        
        This orchestrates:
        1. Full load (if enabled)
        2. LSN capture
        3. Debezium connector creation
        4. Sink connector creation
        
        Args:
            pipeline_id: Pipeline ID
            
        Returns:
            Dictionary with startup results
        """
        pipeline = self.pipeline_store.get(pipeline_id)
        if not pipeline:
            raise ValueError(f"Pipeline not found: {pipeline_id}")
        
        source_connection = self.get_connection(pipeline.source_connection_id)
        target_connection = self.get_connection(pipeline.target_connection_id)
        
        if not source_connection or not target_connection:
            raise ValueError("Source or target connection not found")
        
        result = {
            "pipeline_id": pipeline_id,
            "full_load": {},
            "debezium_connector": {},
            "sink_connector": {},
            "kafka_topics": [],
            "status": "STARTING"
        }
        
        try:
            # Update pipeline status
            pipeline.status = PipelineStatus.STARTING
            # IMPORTANT: Don't reset full_load_status if it's already COMPLETED
            # Only reset if we're actually going to run a new full load
            # This preserves the completed status and LSN for CDC
            if pipeline.full_load_status != FullLoadStatus.COMPLETED:
                pipeline.full_load_status = FullLoadStatus.NOT_STARTED
            else:
                logger.info(f"Preserving full_load_status=COMPLETED (LSN: {pipeline.full_load_lsn})")
            pipeline.cdc_status = CDCStatus.STARTING
            # Persist initial status
            self._persist_pipeline_status(pipeline)
            
            # Determine pipeline mode
            mode = pipeline.mode
            if isinstance(mode, str):
                mode = PipelineMode(mode)
            
            # Step 0: Auto-create target schema/tables if enabled
            # Skip if full load is already completed (schema/tables already exist)
            if pipeline.auto_create_target and pipeline.full_load_status != FullLoadStatus.COMPLETED:
                logger.info(f"Step 0: Auto-creating target schema/tables for pipeline: {pipeline.name}")
                try:
                    # For S3 targets, skip schema creation (S3 doesn't support schemas)
                    if target_connection.database_type == "s3":
                        logger.info("Step 0: Skipping schema creation for S3 target (S3 doesn't support schemas)")
                    else:
                        schema_created = self._auto_create_target_schema(
                            pipeline=pipeline,
                            source_connection=source_connection,
                            target_connection=target_connection
                        )
                        if schema_created:
                            logger.info("Step 0: Target schema/tables created successfully")
                        else:
                            logger.warning("Step 0: Target schema/tables creation returned False, but continuing")
                except Exception as e:
                    logger.error(f"Step 0: Auto-create target schema failed: {e}", exc_info=True)
                    # Don't continue if schema creation fails - it's critical for full load
                    raise FullLoadError(
                        f"Failed to create target schema/tables: {str(e)}. Full load cannot proceed without target schema.",
                        rows_transferred=0,
                        error=str(e)
                    )
            elif pipeline.full_load_status == FullLoadStatus.COMPLETED:
                logger.info("Step 0: Full load already completed, skipping schema creation")
            
            # Step 1: Run full load if mode requires it AND it hasn't been completed yet
            if mode in [PipelineMode.FULL_LOAD_ONLY, PipelineMode.FULL_LOAD_AND_CDC]:
                # Skip full load if already completed
                if pipeline.full_load_status == FullLoadStatus.COMPLETED:
                    logger.info(f"Step 1: Full load already completed, skipping (status: {pipeline.full_load_status})")
                    result["full_load"] = {
                        "success": True,
                        "message": "Full load already completed",
                        "tables_transferred": [],
                        "total_rows": 0,
                        "lsn": pipeline.full_load_lsn
                    }
                    # Use existing LSN if available
                    if pipeline.full_load_lsn:
                        logger.info(f"Step 1: Using existing LSN/offset: {pipeline.full_load_lsn}")
                else:
                    logger.info(f"Step 1: Starting full load for pipeline: {pipeline.name} (mode: {mode.value})")
                    logger.info(f"Step 1: Source: {pipeline.source_database}.{pipeline.source_schema}, Tables: {pipeline.source_tables}")
                    logger.info(f"Step 1: Target: {pipeline.target_database or target_connection.database}.{pipeline.target_schema or target_connection.schema or 'public'}")
                    
                    pipeline.full_load_status = FullLoadStatus.IN_PROGRESS
                    # Persist IN_PROGRESS status to database
                    self._persist_pipeline_status(pipeline)
                    logger.info("Step 1: Full load status set to IN_PROGRESS and persisted to database")
                    
                    full_load_result = self._run_full_load(
                        pipeline=pipeline,
                        source_connection=source_connection,
                        target_connection=target_connection
                    )
                    
                    result["full_load"] = full_load_result
                    
                    # Fix: Use 'is True' instead of truthy check to properly handle False values
                    if full_load_result.get("success") is True:
                        pipeline.full_load_status = FullLoadStatus.COMPLETED
                        # Extract LSN from result - handle both "lsn" key and nested "lsn_offset" dict
                        lsn_value = full_load_result.get("lsn")
                        if not lsn_value:
                            # Try to extract from lsn_offset dict (AS400 returns it this way)
                            lsn_offset = full_load_result.get("lsn_offset", {})
                            if isinstance(lsn_offset, dict):
                                lsn_value = lsn_offset.get("lsn")
                        
                        # CRITICAL: Store LSN for CDC to start from this offset
                        pipeline.full_load_lsn = lsn_value
                        tables_transferred = full_load_result.get("tables_transferred", 0)
                        total_rows = full_load_result.get("total_rows", 0)
                        
                        logger.info(f"Step 1: Full load completed successfully!")
                        logger.info(f"Step 1: Tables transferred: {tables_transferred}, Total rows: {total_rows}")
                        
                        if lsn_value:
                            logger.info(f"Step 1: ✅ LSN/offset captured: {lsn_value}")
                            logger.info(f"Step 1: CDC will start from this offset (no duplicate data)")
                        else:
                            logger.warning(f"Step 1: ⚠️  LSN/offset NOT captured - CDC will use initial snapshot (may have duplicates)")
                        # Persist COMPLETED status to database
                        self._persist_pipeline_status(pipeline)
                        logger.info("Step 1: Full load status set to COMPLETED and persisted to database")
                    else:
                        pipeline.full_load_status = FullLoadStatus.FAILED
                        error_msg = full_load_result.get('error', 'Unknown error')
                        logger.error(f"Step 1: Full load failed: {error_msg}")
                        # Persist FAILED status to database
                        self._persist_pipeline_status(pipeline)
                        raise FullLoadError(
                            f"Full load failed: {error_msg}",
                            rows_transferred=full_load_result.get('total_rows', 0)
                        )
            
            # If mode is FULL_LOAD_ONLY, skip CDC setup
            if mode == PipelineMode.FULL_LOAD_ONLY:
                logger.info(f"Step 2: Pipeline mode is FULL_LOAD_ONLY, skipping CDC setup")
                pipeline.cdc_status = CDCStatus.NOT_STARTED
                pipeline.status = PipelineStatus.RUNNING
                result["status"] = "RUNNING"
                result["message"] = "Full load completed. CDC is disabled for this pipeline."
                # Persist final status
                self._persist_pipeline_status(pipeline)
                logger.info("Step 2: Pipeline running in FULL_LOAD_ONLY mode (CDC disabled)")
                return result
            
            # Step 2: Generate and create Debezium connector (for CDC modes)
            logger.info(f"Step 2: Starting CDC setup for pipeline: {pipeline.name} (mode: {mode.value})")
            logger.info(f"Step 2: Full load completed, now setting up CDC connectors")
            
            # Check if configs already exist in pipeline (loaded from database)
            # If they exist and connectors are running, reuse them
            debezium_exists = False
            if pipeline.debezium_config and pipeline.debezium_connector_name:
                logger.info(f"Pipeline has existing Debezium config and connector name: {pipeline.debezium_connector_name}")
                try:
                    connector_status = self.kafka_client.get_connector_status(pipeline.debezium_connector_name)
                    if connector_status is None:
                        # Connector doesn't exist, will create new one
                        logger.info(f"Debezium connector {pipeline.debezium_connector_name} not found, will create new one")
                        debezium_exists = False
                    else:
                        connector_state = connector_status.get('connector', {}).get('state', 'UNKNOWN')
                        if connector_state == 'RUNNING':
                            logger.info(f"Existing Debezium connector {pipeline.debezium_connector_name} is RUNNING, reusing it")
                            # Skip connector creation, but still need to discover topics and create sink
                            debezium_exists = True
                        else:
                            logger.info(f"Existing Debezium connector {pipeline.debezium_connector_name} state is {connector_state}, will recreate")
                            debezium_exists = False
                except Exception as e:
                    logger.warning(f"Could not check existing Debezium connector status: {e}, will create new one")
                    debezium_exists = False
            else:
                logger.info("No existing Debezium config found, will generate new one")
                debezium_exists = False
            
            # Determine snapshot mode based on mode and full load status
            # Handle both enum and string values for mode
            mode_value = mode.value if hasattr(mode, 'value') else str(mode)
            has_full_load_lsn = bool(pipeline.full_load_lsn)
            full_load_completed = pipeline.full_load_status == FullLoadStatus.COMPLETED
            
            # Decision logic:
            # 1. CDC_ONLY: Never snapshot, start streaming immediately
            # 2. FULL_LOAD_AND_CDC with completed full load: Never snapshot (data already loaded)
            # 3. FULL_LOAD_AND_CDC without full load: Initial snapshot (capture existing data)
            # 4. FULL_LOAD_ONLY: Should not reach here, but if it does, use initial_only
            # 5. Default: Initial snapshot
            
            # Check if source is Oracle (Oracle doesn't support "never" snapshot mode)
            is_oracle = source_connection.database_type.lower() == "oracle"
            
            if mode_value == PipelineMode.CDC_ONLY.value or mode_value == "cdc_only":
                # For Oracle, use "initial_only" instead of "never" (Oracle doesn't support "never")
                snapshot_mode = "initial_only" if is_oracle else "never"
                reason = f"CDC_ONLY mode - {'schema only (Oracle)' if is_oracle else 'streaming changes only'}"
            elif (mode_value == PipelineMode.FULL_LOAD_AND_CDC.value or mode_value == "full_load_and_cdc"):
                if full_load_completed and has_full_load_lsn:
                    # For Oracle, use "initial_only" instead of "never" (Oracle doesn't support "never")
                    snapshot_mode = "initial_only" if is_oracle else "never"
                    reason = f"Full load completed - {'schema only (Oracle)' if is_oracle else 'streaming changes only'}"
                else:
                    snapshot_mode = "initial"
                    reason = "Full load not completed - capturing initial snapshot"
            elif has_full_load_lsn:
                snapshot_mode = "initial_only"
                reason = "Full load LSN present - schema only"
            else:
                snapshot_mode = "initial"
                reason = "No full load - capturing initial snapshot"
            
            logger.info(
                f"Snapshot mode determined: {snapshot_mode} "
                f"(mode={mode_value}, full_load_status={pipeline.full_load_status}, "
                f"full_load_lsn={has_full_load_lsn}, reason={reason})"
            )
            
            debezium_config = DebeziumConfigGenerator.generate_source_config(
                pipeline_name=pipeline.name,
                source_connection=source_connection,
                source_database=pipeline.source_database,
                source_schema=pipeline.source_schema,
                source_tables=pipeline.source_tables,
                full_load_lsn=pipeline.full_load_lsn,
                snapshot_mode=snapshot_mode
            )
            
            debezium_connector_name = DebeziumConfigGenerator.generate_connector_name(
                pipeline_name=pipeline.name,
                database_type=source_connection.database_type,
                schema=pipeline.source_schema
            )
            
            # Check if Debezium connector already exists and is running
            debezium_exists = False
            try:
                connector_info = self.kafka_client.get_connector_info(debezium_connector_name)
                connector_status = self.kafka_client.get_connector_status(debezium_connector_name)
                if connector_status is None:
                    # Connector doesn't exist, will create new one
                    debezium_exists = False
                else:
                    connector_state = connector_status.get('connector', {}).get('state', 'UNKNOWN')
                
                if connector_state == 'RUNNING':
                    logger.info(f"Debezium connector {debezium_connector_name} already exists and is RUNNING, reusing it")
                    debezium_exists = True
                    pipeline.debezium_connector_name = debezium_connector_name
                    pipeline.debezium_config = self.kafka_client.get_connector_config(debezium_connector_name)
                elif connector_state in ['FAILED', 'STOPPED']:
                    logger.warning(f"Debezium connector {debezium_connector_name} exists but is {connector_state}, attempting restart...")
                    try:
                        self.kafka_client.restart_connector(debezium_connector_name)
                        if self.kafka_client.wait_for_connector(debezium_connector_name, "RUNNING", max_wait_seconds=30):
                            logger.info(f"Successfully restarted connector {debezium_connector_name}")
                            debezium_exists = True
                            pipeline.debezium_connector_name = debezium_connector_name
                            pipeline.debezium_config = self.kafka_client.get_connector_config(debezium_connector_name)
                        else:
                            logger.warning(f"Restart failed, will delete and recreate")
                            self.kafka_client.delete_connector(debezium_connector_name)
                    except Exception as restart_error:
                        logger.warning(f"Could not restart connector: {restart_error}, will delete and recreate")
                        self.kafka_client.delete_connector(debezium_connector_name)
                else:
                    logger.info(f"Debezium connector {debezium_connector_name} exists but state is {connector_state}, will recreate")
                    # Delete and recreate
                    self.kafka_client.delete_connector(debezium_connector_name)
                    logger.info(f"Deleted existing Debezium connector: {debezium_connector_name}")
            except requests.exceptions.HTTPError as e:
                # If 404, connector doesn't exist (fine, will create)
                if e.response and e.response.status_code == 404:
                    logger.debug(f"Debezium connector {debezium_connector_name} doesn't exist, will create")
                else:
                    logger.warning(f"Could not check Debezium connector existence (continuing): {e}")
            except Exception as e:
                logger.warning(f"Could not check Debezium connector existence (continuing): {e}")
            
            # Create Debezium connector only if it doesn't exist
            if not debezium_exists:
                logger.info(f"Creating Debezium connector: {debezium_connector_name}")
                self.kafka_client.create_connector(
                    connector_name=debezium_connector_name,
                    config=debezium_config
                )
                
                # Wait for connector to start
                if not self.kafka_client.wait_for_connector(
                    connector_name=debezium_connector_name,
                    target_state="RUNNING",
                    max_wait_seconds=60
                ):
                    raise Exception(f"Debezium connector failed to start: {debezium_connector_name}")
                
                pipeline.debezium_connector_name = debezium_connector_name
                pipeline.debezium_config = debezium_config
            
            pipeline.debezium_connector_name = debezium_connector_name
            pipeline.debezium_config = debezium_config
            
            result["debezium_connector"] = {
                "name": debezium_connector_name,
                "status": "RUNNING"
            }
            
            # Step 3: Wait for topics to be created and discover them
            logger.info("Waiting for Kafka topics to be created by Debezium...")
            time.sleep(5)  # Wait for Debezium to create topics
            
            # Discover actual topics from the connector API
            # IMPORTANT: For Oracle, Debezium creates topics with UPPERCASE schema/table names
            # We must use the actual topic names from the connector, not generated ones
            kafka_topics = []
            try:
                # Try to get actual topics from the connector using session
                connector_topics_response = self.kafka_client.session.get(
                    f"{self.kafka_client.base_url}/connectors/{debezium_connector_name}/topics"
                )
                if connector_topics_response.status_code == 200:
                    topics_data = connector_topics_response.json()
                    connector_topics = topics_data.get(debezium_connector_name, {}).get('topics', [])
                    # Filter out schema change topic (it's just the pipeline name)
                    # We only want table-specific topics (format: {pipeline}.{schema}.{table})
                    table_topics = [t for t in connector_topics if '.' in t and t != pipeline.name]
                    if table_topics:
                        kafka_topics = table_topics
                        logger.info(f"Discovered actual topics from connector: {kafka_topics}")
                    else:
                        logger.warning(f"Connector topics found but no table topics: {connector_topics}")
            except Exception as e:
                logger.warning(f"Could not discover topics from connector API: {e}")
            
            # Fallback: Generate topic names if discovery failed
            if not kafka_topics:
                logger.info("Falling back to generating topic names...")
                for table in pipeline.source_tables:
                    # For Oracle, use UPPERCASE schema/table names (Debezium Oracle creates uppercase topics)
                    if source_connection.database_type == "oracle":
                        schema_upper = (pipeline.source_schema or "public").upper()
                        table_upper = table.upper()
                        topic_name = f"{pipeline.name}.{schema_upper}.{table_upper}"
                    else:
                        # Use get_topic_name which sanitizes invalid characters
                        topic_name = DebeziumConfigGenerator.get_topic_name(
                            pipeline_name=pipeline.name,
                            schema=pipeline.source_schema or "public",
                            table=table
                        )
                    kafka_topics.append(topic_name)
                logger.info(f"Generated topic names: {kafka_topics}")
            
            pipeline.kafka_topics = kafka_topics
            result["kafka_topics"] = kafka_topics
            
            if not kafka_topics:
                error_msg = "No Kafka topics discovered - cannot create sink connector. Debezium may not have created topics yet or table names are incorrect."
                logger.error(error_msg)
                raise Exception(error_msg)
            else:
                logger.info(f"Discovered {len(kafka_topics)} Kafka topics: {kafka_topics}")
            
            # Step 4: Generate and create Sink connector
            logger.info(f"Creating Sink connector for pipeline: {pipeline.name}")
            
            sink_connector_name = SinkConfigGenerator.generate_connector_name(
                pipeline_name=pipeline.name,
                database_type=target_connection.database_type,
                schema=pipeline.target_schema or target_connection.schema or "public"
            )
            
            # Check if sink config already exists in pipeline (loaded from database)
            sink_exists = False
            if pipeline.sink_config and pipeline.sink_connector_name:
                logger.info(f"Pipeline has existing Sink config and connector name: {pipeline.sink_connector_name}")
                try:
                    connector_status = self.kafka_client.get_connector_status(pipeline.sink_connector_name)
                    if connector_status is None:
                        # Connector doesn't exist, will create new one
                        logger.info(f"Sink connector {pipeline.sink_connector_name} not found, will create new one")
                        sink_exists = False
                    else:
                        connector_state = connector_status.get('connector', {}).get('state', 'UNKNOWN')
                    if connector_state == 'RUNNING':
                        # Check if the existing config has the correct topics
                        existing_topics = pipeline.sink_config.get('topics', '').split(',')
                        existing_topics = [t.strip() for t in existing_topics if t.strip()]
                        # Compare with discovered topics (case-insensitive for comparison, but must match exactly)
                        topics_match = set(existing_topics) == set(kafka_topics)
                        if topics_match:
                            logger.info(f"Existing Sink connector {pipeline.sink_connector_name} is RUNNING with correct topics, reusing it")
                            sink_exists = True
                            sink_connector_name = pipeline.sink_connector_name
                            sink_config = pipeline.sink_config
                        else:
                            logger.warning(f"Existing Sink connector topics don't match discovered topics. Existing: {existing_topics}, Discovered: {kafka_topics}. Will recreate.")
                            # Delete the connector to force recreation
                            try:
                                self.kafka_client.delete_connector(pipeline.sink_connector_name)
                                logger.info(f"Deleted Sink connector {pipeline.sink_connector_name} due to topic mismatch")
                            except Exception as e:
                                logger.warning(f"Could not delete connector: {e}")
                    else:
                        logger.info(f"Existing Sink connector {pipeline.sink_connector_name} state is {connector_state}, will recreate")
                except Exception as e:
                    logger.warning(f"Could not check existing Sink connector status: {e}, will create new one")
            
            if not sink_exists:
                sink_config = SinkConfigGenerator.generate_sink_config(
                    connector_name=sink_connector_name,
                    target_connection=target_connection,
                    target_database=pipeline.target_database or target_connection.database,
                    target_schema=pipeline.target_schema or target_connection.schema or "public",
                    kafka_topics=kafka_topics
                )
                
                # Try to delete existing connector if it exists
                # Skip the check and just try to delete - if it doesn't exist, that's fine
                try:
                    self.kafka_client.delete_connector(sink_connector_name)
                    logger.info(f"Deleted existing Sink connector: {sink_connector_name}")
                except Exception as e:
                    # Connector doesn't exist or Kafka Connect has issues - continue anyway
                    error_msg = str(e)
                    if "404" in error_msg or "not found" in error_msg.lower():
                        logger.debug(f"Connector {sink_connector_name} doesn't exist (will create fresh)")
                    else:
                        logger.warning(f"Could not delete connector (will try to create fresh): {e}")
                    # Continue - we'll try to create it
                
                # Create Sink connector
                logger.info(f"Creating Sink connector: {sink_connector_name}")
                self.kafka_client.create_connector(
                    connector_name=sink_connector_name,
                    config=sink_config
                )
            else:
                logger.info(f"Reusing existing Sink connector: {sink_connector_name}")
            
            # Wait for connector to start
            if not self.kafka_client.wait_for_connector(
                connector_name=sink_connector_name,
                target_state="RUNNING",
                max_wait_seconds=60
            ):
                raise Exception(f"Sink connector failed to start: {sink_connector_name}")
            
            pipeline.sink_connector_name = sink_connector_name
            pipeline.sink_config = sink_config
            pipeline.cdc_status = CDCStatus.RUNNING
            pipeline.status = PipelineStatus.RUNNING
            
            result["sink_connector"] = {
                "name": sink_connector_name,
                "status": "RUNNING"
            }
            result["status"] = "RUNNING"
            
            # Persist final status after CDC setup completes
            self._persist_pipeline_status(pipeline)
            
            logger.info(f"Pipeline started successfully: {pipeline.name}")
            
        except FullLoadError as e:
            logger.error(f"Full load failed for pipeline {pipeline_id}: {e}", exc_info=True)
            pipeline.status = PipelineStatus.ERROR
            pipeline.full_load_status = FullLoadStatus.FAILED
            pipeline.cdc_status = CDCStatus.ERROR
            result["status"] = "ERROR"
            result["error"] = str(e)
            result["full_load_error"] = True
            # Persist error status
            self._persist_pipeline_status(pipeline)
            raise
        except Exception as e:
            logger.error(f"Failed to start pipeline {pipeline_id}: {e}", exc_info=True)
            pipeline.status = PipelineStatus.ERROR
            pipeline.cdc_status = CDCStatus.ERROR
            result["status"] = "ERROR"
            result["error"] = str(e)
            # Persist error status
            self._persist_pipeline_status(pipeline)
            raise
        
        return result
    
    def _run_full_load(
        self,
        pipeline: Pipeline,
        source_connection: Connection,
        target_connection: Connection
    ) -> Dict[str, Any]:
        """Run full load for pipeline.
        
        Args:
            pipeline: Pipeline object
            source_connection: Source connection
            target_connection: Target connection
            
        Returns:
            Full load result dictionary
        """
        try:
            # Initialize connectors
            source_config = source_connection.get_connection_config()
            target_config = target_connection.get_connection_config()
            
            if source_connection.database_type == "postgresql":
                source_connector = PostgreSQLConnector(source_config)
            elif source_connection.database_type in ["sqlserver", "mssql"]:
                source_connector = SQLServerConnector(source_config)
            elif source_connection.database_type in ["as400", "ibm_i"]:
                from ingestion.connectors.as400 import AS400Connector
                source_connector = AS400Connector(source_config)
            elif source_connection.database_type == "oracle":
                from ingestion.connectors.oracle import OracleConnector
                source_connector = OracleConnector(source_config)
            else:
                raise ValueError(f"Unsupported source database type: {source_connection.database_type}")
            
            # Handle S3 target specially
            if target_connection.database_type == "s3":
                from ingestion.connectors.s3 import S3Connector
                target_connector = S3Connector(target_config)
                
                # For S3, we need to extract data from source and write to S3
                return self._run_full_load_to_s3(
                    pipeline=pipeline,
                    source_connector=source_connector,
                    target_connector=target_connector,
                    target_connection=target_connection
                )
            
            # Handle Snowflake target - need to transfer data directly
            if target_connection.database_type == "snowflake":
                from ingestion.connectors.snowflake import SnowflakeConnector
                target_connector = SnowflakeConnector(target_config)
                # Test connection
                target_connector.test_connection()
                # Run full load to Snowflake
                return self._run_full_load_to_snowflake(
                    pipeline=pipeline,
                    source_connector=source_connector,
                    target_connector=target_connector,
                    target_connection=target_connection
                )
            
            if target_connection.database_type == "postgresql":
                target_connector = PostgreSQLConnector(target_config)
            elif target_connection.database_type in ["sqlserver", "mssql"]:
                target_connector = SQLServerConnector(target_config)
            else:
                raise ValueError(f"Unsupported target database type: {target_connection.database_type}")
            
            # Verify source has data before transfer
            for table_name in pipeline.source_tables:
                logger.info(f"Validating source data for table: {table_name}")
                try:
                    validation_result = validate_source_data(
                        connector=source_connector,
                        database=pipeline.source_database,
                        schema=pipeline.source_schema,
                        table_name=table_name
                    )
                    if not validation_result.get('has_data'):
                        logger.warning(f"Source table {table_name} has no data, but continuing with transfer")
                except ValidationError as e:
                    logger.warning(f"Source validation warning for {table_name}: {e}")
                    # Continue anyway - let transfer handle it
            
            # Initialize data transfer
            logger.info("Initializing data transfer...")
            transfer = DataTransfer(source_connector, target_connector)
            
            # Transfer all tables
            logger.info(f"Transferring {len(pipeline.source_tables)} table(s): {pipeline.source_tables}")
            logger.info(f"Transfer settings: schema=True, data=True, batch_size=10000")
            
            transfer_result = transfer.transfer_tables(
                tables=pipeline.source_tables,
                source_database=pipeline.source_database,
                source_schema=pipeline.source_schema,
                target_database=pipeline.target_database or target_connection.database,
                target_schema=pipeline.target_schema or target_connection.schema or "public",
                transfer_schema=True,  # Transfer schema (create tables if needed)
                transfer_data=True,    # Transfer data
                batch_size=10000
            )
            
            logger.info(f"Transfer completed: {transfer_result.get('tables_successful', 0)} successful, {transfer_result.get('tables_failed', 0)} failed")
            
            # Post-transfer validation: Verify target row counts
            for table_name in pipeline.source_tables:
                target_table_name = pipeline.target_table_mapping.get(table_name, table_name) if pipeline.target_table_mapping else table_name
                
                # Parse target_table_name to extract schema and table if it contains a dot
                # This prevents double schema prefix (e.g., "dbo.dbo.department")
                target_schema_final = pipeline.target_schema or target_connection.schema or "public"
                target_table_final = target_table_name
                
                # If target_table_name contains schema prefix (e.g., "dbo.department"), extract just the table name
                if '.' in target_table_name:
                    parts = target_table_name.split('.')
                    if len(parts) == 2:
                        # If schema matches, use just the table name; otherwise keep as is
                        if parts[0].lower() == target_schema_final.lower():
                            target_table_final = parts[1]
                        # If schema doesn't match, use the provided schema and table
                        else:
                            target_schema_final = parts[0]
                            target_table_final = parts[1]
                    elif len(parts) > 2:
                        # Handle database.schema.table format - extract schema and table
                        target_schema_final = parts[-2]
                        target_table_final = parts[-1]
                
                logger.info(f"Validating target row count for table: {target_schema_final}.{target_table_final}")
                try:
                    validation_result = validate_target_row_count(
                        source_connector=source_connector,
                        target_connector=target_connector,
                        source_database=pipeline.source_database,
                        source_schema=pipeline.source_schema,
                        source_table=table_name,
                        target_database=pipeline.target_database or target_connection.database,
                        target_schema=target_schema_final,
                        target_table=target_table_final
                    )
                    logger.info(f"Row count validation passed for {target_table_name}: {validation_result.get('source_rows', 0)} rows match")
                except ValidationError as e:
                    # Check if this is a row count mismatch
                    if "row count mismatch" in str(e).lower() or (hasattr(e, 'validation_type') and e.validation_type == "row_count"):
                        # Extract row counts from error details
                        source_rows = None
                        target_rows = None
                        if hasattr(e, 'details') and isinstance(e.details, dict):
                            source_rows = e.details.get('source_rows')
                            target_rows = e.details.get('target_rows')
                        # Fallback: try to parse from error message
                        if source_rows is None or target_rows is None:
                            import re
                            match = re.search(r'source has (\d+) rows.*target has (\d+) rows', str(e))
                            if match:
                                source_rows = int(match.group(1))
                                target_rows = int(match.group(2))
                        
                        # Log warning but don't fail - allow pipeline to continue
                        # This could happen if:
                        # 1. Target table already had some data
                        # 2. Some rows failed to insert (duplicates, constraints, etc.)
                        # 3. Data was filtered during transfer
                        # 4. Partial transfer due to errors
                        logger.warning(
                            f"⚠️  Row count mismatch for {target_table_name}: "
                            f"source has {source_rows or 'unknown'} rows, target has {target_rows or 'unknown'} rows. "
                            f"This may be expected if the target table had existing data, some rows were filtered, "
                            f"or there were insertion errors. Pipeline will continue, but please verify data integrity manually."
                        )
                        # Don't raise error - just log warning and continue
                    else:
                        # For other validation errors, still raise
                        logger.error(f"Validation failed for {target_table_name}: {e}")
                        raise FullLoadError(
                            f"Post-transfer validation failed for {target_table_name}: {str(e)}",
                            table_name=target_table_name,
                            rows_transferred=transfer_result.get('total_rows_transferred', 0)
                        )
            
            # Debug logging
            logger.info(f"Transfer result: tables_successful={transfer_result.get('tables_successful')}, "
                       f"tables_failed={transfer_result.get('tables_failed')}, "
                       f"total_rows_transferred={transfer_result.get('total_rows_transferred')}")
            logger.info(f"Transfer result details: {json.dumps(transfer_result, default=str)}")
            
            # Check if transfer actually succeeded
            if transfer_result["tables_successful"] == 0:
                error_msg = "No tables were successfully transferred"
                if transfer_result.get("tables"):
                    # Get error from first failed table
                    first_table = transfer_result["tables"][0]
                    if first_table.get("errors"):
                        error_msg = f"Transfer failed: {first_table['errors'][0]}"
                    elif first_table.get("error"):
                        error_msg = f"Transfer failed: {first_table['error']}"
                logger.error(f"Full load validation failed: {error_msg}")
                raise FullLoadError(
                    error_msg,
                    rows_transferred=0,
                    error=error_msg
                )
            
            # Check if rows were actually transferred (0 rows when tables were "successful" indicates failure)
            # But first check if source actually has data
            source_has_data = False
            for table_name in pipeline.source_tables:
                try:
                    validation_result = validate_source_data(
                        connector=source_connector,
                        database=pipeline.source_database,
                        schema=pipeline.source_schema,
                        table_name=table_name
                    )
                    if validation_result.get('has_data'):
                        source_has_data = True
                        break
                except Exception:
                    pass  # Ignore validation errors here
            
            if transfer_result["total_rows_transferred"] == 0 and source_has_data:
                error_msg = "Full load reported success but transferred 0 rows (source has data)"
                if transfer_result.get("tables"):
                    # Check each table result for details
                    for table_result in transfer_result["tables"]:
                        if table_result.get("data_transferred") and table_result.get("rows_transferred", 0) == 0:
                            # Table was marked as transferred but has 0 rows - this is suspicious
                            if table_result.get("errors"):
                                error_msg = f"Transfer failed: {table_result['errors'][0]}"
                            elif table_result.get("error"):
                                error_msg = f"Transfer failed: {table_result['error']}"
                            else:
                                error_msg = f"Table {table_result.get('table_name', 'unknown')} reported success but transferred 0 rows. Check for schema mismatches or data insertion failures."
                logger.error(f"Full load validation failed: {error_msg}")
                raise FullLoadError(
                    error_msg,
                    rows_transferred=0,
                    error=error_msg
                )
            elif transfer_result["total_rows_transferred"] == 0:
                logger.warning("Full load transferred 0 rows, but source tables appear to be empty (this may be OK)")
            
            # Capture LSN after full load
            logger.info("Capturing LSN after full load...")
            lsn_info = source_connector.extract_lsn_offset(database=pipeline.source_database)
            
            result = {
                "success": True,
                "tables_transferred": transfer_result["tables_successful"],
                "total_rows": transfer_result["total_rows_transferred"],
                "lsn": lsn_info.get("lsn"),
                "offset": lsn_info.get("offset"),
                "timestamp": lsn_info.get("timestamp")
            }
            
            logger.info(f"Full load result: success=True, tables={result['tables_transferred']}, rows={result['total_rows']}, LSN={result['lsn']}")
            return result
            
        except FullLoadError:
            # Re-raise FullLoadError as-is
            raise
        except ValidationError as e:
            # Convert ValidationError to FullLoadError
            logger.error(f"Full load validation failed: {e}", exc_info=True)
            raise FullLoadError(
                f"Full load validation failed: {str(e)}",
                rows_transferred=0
            )
        except Exception as e:
            logger.error(f"Full load failed: {e}", exc_info=True)
            raise FullLoadError(
                f"Full load failed: {str(e)}",
                rows_transferred=0,
                error=str(e)
            )
    
    def _run_full_load_to_s3(
        self,
        pipeline: Pipeline,
        source_connector: BaseConnector,
        target_connector: BaseConnector,
        target_connection: Connection
    ) -> Dict[str, Any]:
        """Run full load from database to S3.
        
        Args:
            pipeline: Pipeline object
            source_connector: Source database connector
            target_connector: S3 connector
            target_connection: Target S3 connection
            
        Returns:
            Full load result dictionary
        """
        import json
        from datetime import datetime
        
        try:
            bucket = target_connection.database
            prefix = target_connection.schema or ""
            if prefix and not prefix.endswith('/'):
                prefix += '/'
            
            tables_transferred = []
            total_rows = 0
            
            # Process each table
            for table_name in pipeline.source_tables:
                logger.info(f"Transferring table {table_name} to S3")
                
                # Extract schema
                schema_result = source_connector.extract_schema(
                    database=pipeline.source_database,
                    schema=pipeline.source_schema,
                    table=table_name
                )
                
                # PostgreSQL connector returns tables list, not success/error
                # Check if we got schema data
                tables = schema_result.get('tables', [])
                if not tables:
                    logger.warning(f"Could not extract schema for {table_name}: No tables found in schema result")
                    continue
                
                # Get columns from the first table (should be the requested table)
                columns = tables[0].get('columns', []) if tables else []
                if not columns:
                    logger.warning(f"Could not extract columns for {table_name}: No columns found")
                    continue
                
                # Extract data in batches
                batch_size = 10000
                offset = 0
                all_rows = []
                column_names = None
                
                while True:
                    try:
                        data_result = source_connector.extract_data(
                            database=pipeline.source_database,
                            schema=pipeline.source_schema,
                            table_name=table_name,
                            limit=batch_size,
                            offset=offset
                        )
                    except Exception as e:
                        logger.error(f"Error extracting data from {table_name}: {e}")
                        break
                    
                    # PostgreSQL connector returns rows as list of lists, not dicts
                    rows = data_result.get('rows', [])
                    if not rows:
                        break
                    
                    # Get column names on first batch
                    if column_names is None:
                        column_names = data_result.get('column_names', [])
                    
                    # Convert list of lists to list of dicts
                    row_dicts = []
                    for row in rows:
                        row_dict = dict(zip(column_names, row)) if column_names else {}
                        row_dicts.append(row_dict)
                    
                    all_rows.extend(row_dicts)
                    offset += len(rows)
                    
                    # Check if there are more rows
                    has_more = data_result.get('has_more', False)
                    if not has_more:
                        break
                
                if not all_rows:
                    logger.warning(f"No data found for table {table_name}")
                    continue
                
                # Format data as JSON
                json_data = json.dumps(all_rows, indent=2, default=str)
                
                # Upload to S3
                s3_key = f"{prefix}{table_name}/full_load_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
                
                try:
                    s3_client = target_connector._get_s3_client()
                    s3_client.put_object(
                        Bucket=bucket,
                        Key=s3_key,
                        Body=json_data.encode('utf-8'),
                        ContentType='application/json'
                    )
                    
                    logger.info(f"Uploaded {len(all_rows)} rows from {table_name} to s3://{bucket}/{s3_key}")
                    tables_transferred.append(table_name)
                    total_rows += len(all_rows)
                    
                except Exception as e:
                    logger.error(f"Error uploading {table_name} to S3: {e}")
                    continue
            
            # Capture LSN after full load - CRITICAL for CDC to start from correct offset
            logger.info(f"Capturing LSN/offset after full load for database {pipeline.source_database}...")
            try:
                lsn_info = source_connector.extract_lsn_offset(database=pipeline.source_database)
                lsn_value = lsn_info.get("lsn") if lsn_info else None
                
                if lsn_value:
                    logger.info(f"✅ Successfully captured LSN/offset: {lsn_value}")
                else:
                    logger.warning(f"⚠️  LSN extraction returned None. Full result: {lsn_info}")
                    # For AS400, create a fallback LSN using timestamp
                    if source_connection.database_type in ["as400", "ibm_i"]:
                        from datetime import datetime
                        journal_library = source_connection.additional_config.get("journal_library", "JRNRCV") if source_connection.additional_config else "JRNRCV"
                        lsn_value = f"JOURNAL:{journal_library}:{datetime.utcnow().isoformat()}"
                        logger.info(f"✅ Created fallback AS400 journal offset: {lsn_value}")
            except Exception as e:
                logger.error(f"❌ Error extracting LSN/offset after full load: {e}", exc_info=True)
                # For AS400, create a fallback LSN using timestamp
                if source_connection.database_type in ["as400", "ibm_i"]:
                    from datetime import datetime
                    journal_library = source_connection.additional_config.get("journal_library", "JRNRCV") if source_connection.additional_config else "JRNRCV"
                    lsn_value = f"JOURNAL:{journal_library}:{datetime.utcnow().isoformat()}"
                    logger.warning(f"⚠️  Using fallback AS400 journal offset due to extraction error: {lsn_value}")
                else:
                    lsn_value = None
            
            return {
                "success": True,
                "tables_transferred": tables_transferred,
                "total_rows": total_rows,
                "lsn": lsn_value,
                "offset": lsn_info.get("offset") if lsn_info else None,
                "timestamp": lsn_info.get("timestamp") if lsn_info else datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Full load to S3 failed: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }
    
    def _run_full_load_to_snowflake(
        self,
        pipeline: Pipeline,
        source_connector: BaseConnector,
        target_connector: BaseConnector,
        target_connection: Connection
    ) -> Dict[str, Any]:
        """Run full load from database to Snowflake.
        
        Args:
            pipeline: Pipeline object
            source_connector: Source database connector
            target_connector: Snowflake connector
            target_connection: Target Snowflake connection
            
        Returns:
            Full load result dictionary
        """
        from datetime import datetime
        
        try:
            target_db = pipeline.target_database or target_connection.database
            target_schema = pipeline.target_schema or target_connection.schema or "PUBLIC"
            
            if not target_db:
                raise ValueError("Target database is required for Snowflake full load")
            
            tables_transferred = []
            total_rows = 0
            
            # Connect to Snowflake
            conn = target_connector.connect()
            cursor = conn.cursor()
            
            try:
                # Set database and schema context
                target_db_upper = target_db.upper().strip('"\'')
                target_schema_upper = target_schema.upper().strip('"\'')
                
                cursor.execute(f"USE DATABASE {target_db_upper}")
                cursor.execute(f"USE SCHEMA {target_schema_upper}")
                
                # Process each table
                for source_table in pipeline.source_tables:
                    # Get target table name from mapping
                    target_table = pipeline.target_table_mapping.get(source_table, source_table) if pipeline.target_table_mapping else source_table
                    target_table_upper = target_table.upper().strip('"\'')
                    
                    logger.info(f"Transferring table {source_table} to Snowflake table {target_table_upper}")
                    
                    # Extract data from source in batches
                    batch_size = 10000
                    offset = 0
                    column_names = None
                    rows_inserted = 0
                    
                    while True:
                        try:
                            data_result = source_connector.extract_data(
                                database=pipeline.source_database,
                                schema=pipeline.source_schema,
                                table_name=source_table,
                                limit=batch_size,
                                offset=offset
                            )
                        except Exception as e:
                            logger.error(f"Error extracting data from {source_table}: {e}")
                            break
                        
                        rows = data_result.get('rows', [])
                        if not rows:
                            break
                        
                        # Get column names on first batch
                        if column_names is None:
                            column_names = data_result.get('column_names', [])
                            if not column_names:
                                logger.warning(f"No column names found for {source_table}")
                                break
                        
                        # For Snowflake targets, insert data in RECORD_CONTENT/RECORD_METADATA format
                        # This matches the format that Snowflake Kafka connector uses for CDC
                        # RECORD_CONTENT: VARIANT column storing the record data as JSON
                        # RECORD_METADATA: OBJECT column storing metadata
                        
                        # Build INSERT statement for Snowflake Kafka connector format
                        # Use individual INSERT statements since Snowflake doesn't support PARSE_JSON in VALUES with executemany
                        # Insert rows one by one with PARSE_JSON in the SQL
                        rows_inserted_batch = 0
                        for row_idx, row in enumerate(rows):
                            try:
                                # Create RECORD_CONTENT as JSON object with column names as keys
                                record_content = {}
                                for i, col_name in enumerate(column_names):
                                    value = row[i] if i < len(row) else None
                                    # Convert value to JSON-serializable format
                                    if isinstance(value, (datetime,)):
                                        value = value.isoformat()
                                    elif hasattr(value, 'isoformat'):  # Handle other datetime-like objects
                                        value = value.isoformat()
                                    # Handle Oracle-specific types (LOB, etc.)
                                    elif hasattr(value, 'read'):  # LOB types
                                        try:
                                            value = value.read()
                                        except:
                                            value = str(value)
                                    record_content[col_name] = value
                                
                                # Create RECORD_METADATA as JSON object
                                # Format similar to what Snowflake Kafka connector uses
                                record_metadata = {
                                    "source": {
                                        "schema": pipeline.source_schema or "",
                                        "table": source_table,
                                        "database": pipeline.source_database or ""
                                    },
                                    "created_time": datetime.utcnow().isoformat(),
                                    "operation": "r",  # 'r' for full load (read/reload)
                                    "partition": 0,  # Default partition for full load
                                    "offset": offset + row_idx  # Sequential offset for full load
                                }
                                
                                # Convert to JSON strings for PARSE_JSON
                                # Use ensure_ascii=False to preserve Unicode and default=str for any non-serializable types
                                record_content_json = json.dumps(record_content, ensure_ascii=False, default=str)
                                record_metadata_json = json.dumps(record_metadata, ensure_ascii=False, default=str)
                                
                                # Escape single quotes in JSON strings for SQL
                                record_content_json_escaped = record_content_json.replace("'", "''")
                                record_metadata_json_escaped = record_metadata_json.replace("'", "''")
                                
                                # Insert with PARSE_JSON - use string formatting since we're inserting one at a time
                                insert_query = f'INSERT INTO "{target_table_upper}" ("RECORD_CONTENT", "RECORD_METADATA") SELECT PARSE_JSON(\'{record_content_json_escaped}\'), PARSE_JSON(\'{record_metadata_json_escaped}\')'
                                cursor.execute(insert_query)
                                rows_inserted_batch += 1
                                
                            except Exception as e:
                                logger.error(f"Error inserting row {row_idx} into {target_table_upper}: {e}")
                                # Log the problematic row for debugging
                                logger.error(f"Problematic record_content: {record_content_json[:200] if 'record_content_json' in locals() else 'N/A'}")
                                raise
                        
                        rows_inserted += rows_inserted_batch
                        logger.info(f"Inserted {rows_inserted_batch} rows into {target_table_upper} in RECORD_CONTENT/RECORD_METADATA format (total: {rows_inserted})")
                        
                        offset += len(rows)
                        
                        # Check if there are more rows
                        has_more = data_result.get('has_more', False)
                        if not has_more:
                            break
                    
                    if rows_inserted > 0:
                        logger.info(f"✓ Transferred {rows_inserted} rows from {source_table} to {target_table_upper}")
                        tables_transferred.append(target_table_upper)
                        total_rows += rows_inserted
                    else:
                        logger.warning(f"No data transferred for table {source_table}")
                
                # Commit all inserts
                conn.commit()
                
            finally:
                cursor.close()
                conn.close()
            
            # Capture LSN after full load
            logger.info(f"Capturing LSN/offset after full load for database {pipeline.source_database}...")
            try:
                lsn_info = source_connector.extract_lsn_offset(database=pipeline.source_database)
                lsn_value = lsn_info.get("lsn") if lsn_info else None
                
                if lsn_value:
                    logger.info(f"✅ Successfully captured LSN/offset: {lsn_value}")
                else:
                    logger.warning(f"⚠️  LSN extraction returned None. Full result: {lsn_info}")
            except Exception as e:
                logger.error(f"❌ Error extracting LSN/offset after full load: {e}", exc_info=True)
                lsn_value = None
                lsn_info = {}
            
            return {
                "success": True,
                "tables_transferred": tables_transferred,
                "total_rows": total_rows,
                "lsn": lsn_value,
                "offset": lsn_info.get("offset") if lsn_info else None,
                "timestamp": lsn_info.get("timestamp") if lsn_info else datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Full load to Snowflake failed: {e}", exc_info=True)
            raise FullLoadError(
                f"Full load to Snowflake failed: {str(e)}",
                rows_transferred=0,
                error=str(e)
            )
    
    def _discover_kafka_topics(
        self,
        pipeline_name: str,
        tables: List[str],
        schema: str = "public"
    ) -> List[str]:
        """Discover Kafka topics created by Debezium.
        
        Args:
            pipeline_name: Pipeline name (database.server.name)
            tables: List of source tables
            schema: Schema name (default: public)
            
        Returns:
            List of Kafka topic names
        """
        # Try to discover topics from Kafka first
        discovered_topics = []
        
        try:
            # Query Kafka REST API for topics (if available)
            # For now, we'll use the expected topic naming pattern
            # In production, you might want to use Kafka AdminClient to list topics
            logger.info(f"Discovering Kafka topics for pipeline {pipeline_name}")
            
            # Generate expected topic names based on Debezium naming convention
            # Format: {server_name}.{schema}.{table}
            for table in tables:
                # Use the same logic as DebeziumConfigGenerator
                topic = DebeziumConfigGenerator.get_topic_name(
                    pipeline_name=pipeline_name,
                    schema=schema,
                    table=table
                )
                discovered_topics.append(topic)
                logger.debug(f"Expected topic: {topic}")
            
            # TODO: In production, query actual Kafka topics using:
            # - Kafka AdminClient: admin_client.list_topics()
            # - Or Kafka REST API: GET /kafka/v3/clusters/{cluster_id}/topics
            # For now, we return expected topics
            
        except Exception as e:
            logger.warning(f"Failed to discover Kafka topics, using expected names: {e}")
            # Fallback to expected topic names
            for table in tables:
                topic = f"{pipeline_name}.{schema}.{table}"
                discovered_topics.append(topic)
        
        logger.info(f"Discovered {len(discovered_topics)} Kafka topics: {discovered_topics}")
        return discovered_topics
    
    def _auto_create_target_schema(
        self,
        pipeline: Pipeline,
        source_connection: Connection,
        target_connection: Connection
    ) -> bool:
        """Auto-create target schema and tables if enabled.
        
        Args:
            pipeline: Pipeline object
            source_connection: Source connection
            target_connection: Target connection
            
        Returns:
            True if schema/tables were created successfully, False otherwise
            
        Raises:
            FullLoadError: If critical schema creation failures occur
        """
        # Normalize database_type for comparison
        target_db_type = str(target_connection.database_type).lower()
        if target_db_type in ['aws_s3', 's3']:
            target_db_type = 's3'
        
        # Skip schema creation for S3 (S3 doesn't have schemas)
        if target_db_type == "s3":
            logger.info(f"Skipping schema creation for S3 target (S3 doesn't support schemas). Target DB type: {target_connection.database_type}")
            # S3 uses prefixes/folders instead of schemas, which are handled differently
            # Just proceed to table creation (which for S3 means creating the data files)
            target_schema = pipeline.target_schema or target_connection.schema or ""  # S3 uses empty or prefix
            target_database = pipeline.target_database or target_connection.database
        else:
            target_schema = pipeline.target_schema or target_connection.schema or ("public" if target_connection.database_type == "postgresql" else "dbo")
            target_database = pipeline.target_database or target_connection.database
            
            logger.info(f"Creating target schema: {target_schema} in database: {target_database}")
            
            # Create target schema if it doesn't exist
            try:
                schema_result = self.schema_service.create_target_schema(
                    connection_id=target_connection.id,
                    schema_name=target_schema,
                    database=target_database
                )
                
                if schema_result.get("success"):
                    if schema_result.get("created"):
                        logger.info(f"✓ Created target schema: {target_schema}")
                        # Wait a moment to ensure schema is visible across connections
                        import time
                        time.sleep(1)
                    else:
                        logger.info(f"✓ Target schema already exists: {target_schema}")
                else:
                    error_msg = schema_result.get('error', 'Unknown error')
                    logger.error(f"✗ Failed to create target schema: {error_msg}")
                    raise FullLoadError(
                        f"Failed to create target schema '{target_schema}': {error_msg}",
                        rows_transferred=0,
                        error=error_msg
                    )
            except FullLoadError:
                raise  # Re-raise FullLoadError
            except Exception as e:
                logger.error(f"✗ Error creating target schema: {e}", exc_info=True)
                raise FullLoadError(
                    f"Failed to create target schema '{target_schema}': {str(e)}",
                    rows_transferred=0,
                    error=str(e)
                )
        
        # Skip table creation for S3 (S3 doesn't have tables - data is stored as files)
        if target_db_type == "s3":
            logger.info(f"Skipping table creation for S3 target (S3 stores data as files, not database tables)")
            logger.info(f"✓ Schema/tables setup completed for S3 target")
            return True
        
        # Create target tables
        tables_created = 0
        tables_failed = 0
        
        for source_table in pipeline.source_tables:
            # Get target table name from mapping
            target_table = pipeline.target_table_mapping.get(source_table, source_table) if pipeline.target_table_mapping else source_table
            
            logger.info(f"Creating target table: {target_table} (from source: {source_table})")
            
            # Check if table exists
            try:
                table_schema = self.schema_service.connection_service.get_table_schema(
                    target_connection.id,
                    target_table,
                    database=target_database,
                    schema=target_schema
                )
                
                if table_schema.get("success"):
                    logger.info(f"✓ Target table {target_table} already exists, skipping creation")
                    tables_created += 1
                    continue
            except Exception:
                # Table doesn't exist, create it
                pass
            
            # Create table
            try:
                # For Oracle, use connection.database if pipeline.source_database is None
                source_db = pipeline.source_database or source_connection.database
                source_schema = pipeline.source_schema or source_connection.schema or source_connection.username
                
                table_result = self.schema_service.create_target_table(
                    source_connection_id=source_connection.id,
                    target_connection_id=target_connection.id,
                    table_name=source_table,
                    source_database=source_db,
                    source_schema=source_schema,
                    target_database=target_database,
                    target_schema=target_schema,
                    target_table_name=target_table
                )
                
                if table_result.get("success"):
                    logger.info(f"✓ Created target table: {target_table}")
                    tables_created += 1
                else:
                    error_msg = table_result.get('error', 'Unknown error')
                    logger.error(f"✗ Failed to create target table {target_table}: {error_msg}")
                    tables_failed += 1
                    # Raise error for critical table creation failures
                    raise FullLoadError(
                        f"Failed to create target table '{target_table}': {error_msg}",
                        rows_transferred=0,
                        error=error_msg
                    )
            except FullLoadError:
                raise  # Re-raise FullLoadError
            except Exception as e:
                logger.error(f"✗ Error creating target table {target_table}: {e}", exc_info=True)
                raise FullLoadError(
                    f"Failed to create target table '{target_table}': {str(e)}",
                    rows_transferred=0,
                    error=str(e)
                )
        
        if tables_created > 0:
            logger.info(f"✓ Schema creation completed: {tables_created} tables ready, {tables_failed} failed")
            return True
        else:
            logger.warning(f"⚠ No tables were created (all may already exist or all failed)")
            return False
    
    def _load_pipeline_from_db(self, pipeline_id: str) -> Optional[Pipeline]:
        """Load pipeline from database if not in memory store.
        
        Args:
            pipeline_id: Pipeline ID
            
        Returns:
            Pipeline object if found, None otherwise
        """
        try:
            from ingestion.database.session import get_db
            from ingestion.database.models_db import PipelineModel, ConnectionModel
            db = next(get_db())
            pipeline_model = db.query(PipelineModel).filter(
                PipelineModel.id == pipeline_id,
                PipelineModel.deleted_at.is_(None)
            ).first()
            if pipeline_model:
                # Load connections
                source_conn_model = db.query(ConnectionModel).filter_by(id=pipeline_model.source_connection_id).first()
                target_conn_model = db.query(ConnectionModel).filter_by(id=pipeline_model.target_connection_id).first()
                
                if source_conn_model and target_conn_model:
                    # Convert to Connection objects
                    source_connection = Connection(
                        id=source_conn_model.id,
                        name=source_conn_model.name,
                        connection_type=source_conn_model.connection_type.value if hasattr(source_conn_model.connection_type, 'value') else str(source_conn_model.connection_type),
                        database_type=str(source_conn_model.database_type).lower(),
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
                        database_type=str(target_conn_model.database_type).lower(),
                        host=target_conn_model.host,
                        port=target_conn_model.port,
                        database=target_conn_model.database,
                        username=target_conn_model.username,
                        password=target_conn_model.password,
                        schema=target_conn_model.schema,
                        additional_config=target_conn_model.additional_config or {}
                    )
                    
                    # Convert PipelineModel to Pipeline
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
                        mode=pipeline_model.mode.value if hasattr(pipeline_model.mode, 'value') else str(pipeline_model.mode),
                        auto_create_target=pipeline_model.auto_create_target,
                        target_table_mapping=pipeline_model.target_table_mapping or {},
                        table_filter=pipeline_model.table_filter,
                        full_load_status=pipeline_model.full_load_status.value if hasattr(pipeline_model.full_load_status, 'value') else str(pipeline_model.full_load_status),
                        full_load_lsn=pipeline_model.full_load_lsn,
                        cdc_status=pipeline_model.cdc_status.value if hasattr(pipeline_model.cdc_status, 'value') else str(pipeline_model.cdc_status),
                        debezium_connector_name=pipeline_model.debezium_connector_name,
                        sink_connector_name=pipeline_model.sink_connector_name,
                        kafka_topics=pipeline_model.kafka_topics or [],
                        debezium_config=pipeline_model.debezium_config or {},
                        sink_config=pipeline_model.sink_config or {},
                        status=pipeline_model.status.value if hasattr(pipeline_model.status, 'value') else str(pipeline_model.status),
                        created_at=pipeline_model.created_at,
                        updated_at=pipeline_model.updated_at
                    )
                    
                    # Add connections and pipeline to store
                    self.add_connection(source_connection)
                    self.add_connection(target_connection)
                    self.pipeline_store[pipeline_id] = pipeline
                    logger.info(f"Loaded pipeline {pipeline_id} from database into memory store")
                    return pipeline
        except Exception as e:
            logger.warning(f"Could not load pipeline from database: {e}", exc_info=True)
        return None
    
    def stop_pipeline(self, pipeline_id: str) -> Dict[str, Any]:
        """Stop a CDC pipeline.
        
        Args:
            pipeline_id: Pipeline ID
            
        Returns:
            Stop result dictionary
        """
        pipeline = self.pipeline_store.get(pipeline_id)
        if not pipeline:
            # Try to load from database
            pipeline = self._load_pipeline_from_db(pipeline_id)
        if not pipeline:
            raise ValueError(f"Pipeline not found: {pipeline_id}")
        
        result = {
            "pipeline_id": pipeline_id,
            "debezium_stopped": False,
            "sink_stopped": False,
            "status": "STOPPING"
        }
        
        try:
            pipeline.status = PipelineStatus.STOPPING
            
            # Stop Debezium connector
            if pipeline.debezium_connector_name:
                try:
                    self.kafka_client.pause_connector(pipeline.debezium_connector_name)
                    result["debezium_stopped"] = True
                except Exception as e:
                    logger.warning(f"Failed to pause Debezium connector: {e}")
            
            # Stop Sink connector
            if pipeline.sink_connector_name:
                try:
                    self.kafka_client.pause_connector(pipeline.sink_connector_name)
                    result["sink_stopped"] = True
                except Exception as e:
                    logger.warning(f"Failed to pause Sink connector: {e}")
            
            pipeline.status = PipelineStatus.STOPPED
            pipeline.cdc_status = CDCStatus.STOPPED
            result["status"] = "STOPPED"
            
            logger.info(f"Pipeline stopped: {pipeline.name}")
            
        except Exception as e:
            logger.error(f"Failed to stop pipeline {pipeline_id}: {e}", exc_info=True)
            pipeline.status = PipelineStatus.ERROR
            result["status"] = "ERROR"
            result["error"] = str(e)
            raise
        
        return result
    
    def pause_pipeline(self, pipeline_id: str) -> Dict[str, Any]:
        """Pause a CDC pipeline (temporarily stop without deleting connectors).
        
        Args:
            pipeline_id: Pipeline ID
            
        Returns:
            Pause result dictionary
        """
        pipeline = self.pipeline_store.get(pipeline_id)
        if not pipeline:
            # Try to load from database
            pipeline = self._load_pipeline_from_db(pipeline_id)
        if not pipeline:
            raise ValueError(f"Pipeline not found: {pipeline_id}")
        
        result = {
            "pipeline_id": pipeline_id,
            "debezium_paused": False,
            "sink_paused": False,
            "status": "PAUSING"
        }
        
        try:
            # Pause Debezium connector
            if pipeline.debezium_connector_name:
                try:
                    self.kafka_client.pause_connector(pipeline.debezium_connector_name)
                    result["debezium_paused"] = True
                except Exception as e:
                    logger.warning(f"Failed to pause Debezium connector: {e}")
            
            # Pause Sink connector
            if pipeline.sink_connector_name:
                try:
                    self.kafka_client.pause_connector(pipeline.sink_connector_name)
                    result["sink_paused"] = True
                except Exception as e:
                    logger.warning(f"Failed to pause Sink connector: {e}")
            
            pipeline.status = PipelineStatus.PAUSED
            pipeline.cdc_status = CDCStatus.PAUSED
            result["status"] = "PAUSED"
            
            logger.info(f"Pipeline paused: {pipeline.name}")
            
        except Exception as e:
            logger.error(f"Failed to pause pipeline {pipeline_id}: {e}", exc_info=True)
            pipeline.status = PipelineStatus.ERROR
            result["status"] = "ERROR"
            result["error"] = str(e)
            raise
        
        return result
    
    def get_pipeline_status(self, pipeline_id: str) -> Dict[str, Any]:
        """Get pipeline status.
        
        Args:
            pipeline_id: Pipeline ID
            
        Returns:
            Pipeline status dictionary
        """
        pipeline = self.pipeline_store.get(pipeline_id)
        if not pipeline:
            # Try to load from database if not in memory store
            pipeline = self._load_pipeline_from_db(pipeline_id)
        
        if not pipeline:
            raise ValueError(f"Pipeline not found: {pipeline_id}")
        
        # Reload from database to get latest sink_connector_name if in-memory is stale
        try:
            from ingestion.database.session import get_db
            from ingestion.database.models_db import PipelineModel
            db = next(get_db())
            pipeline_model = db.query(PipelineModel).filter(
                PipelineModel.id == pipeline_id,
                PipelineModel.deleted_at.is_(None)
            ).first()
            if pipeline_model and pipeline_model.sink_connector_name and not pipeline.sink_connector_name:
                # Update in-memory pipeline with sink connector name from database
                pipeline.sink_connector_name = pipeline_model.sink_connector_name
                logger.info(f"Reloaded sink_connector_name from database: {pipeline.sink_connector_name}")
        except Exception as e:
            logger.debug(f"Could not reload pipeline from database: {e}")
        
        # Get mode value - handle both enum and string
        mode_value = pipeline.mode.value if hasattr(pipeline.mode, 'value') else str(pipeline.mode) if pipeline.mode else None
        
        status = {
            "pipeline_id": pipeline_id,
            "id": pipeline_id,
            "name": pipeline.name,
            "status": pipeline.status.value if hasattr(pipeline.status, 'value') else str(pipeline.status),
            "full_load_status": pipeline.full_load_status.value if hasattr(pipeline.full_load_status, 'value') else str(pipeline.full_load_status),
            "cdc_status": pipeline.cdc_status.value if hasattr(pipeline.cdc_status, 'value') else str(pipeline.cdc_status),
            "mode": mode_value,
            "debezium_connector_name": pipeline.debezium_connector_name,
            "sink_connector_name": pipeline.sink_connector_name,
            "kafka_topics": pipeline.kafka_topics or [],
            "debezium_connector": None,
            "sink_connector": None
        }
        
        # Get Debezium connector status
        if pipeline.debezium_connector_name:
            try:
                debezium_status = self.kafka_client.get_connector_status(
                    pipeline.debezium_connector_name
                )
                # None means connector doesn't exist - that's okay
                status["debezium_connector"] = debezium_status
            except Exception as e:
                logger.warning(f"Failed to get Debezium connector status: {e}")
        
        # Get Sink connector status
        if pipeline.sink_connector_name:
            try:
                sink_status = self.kafka_client.get_connector_status(
                    pipeline.sink_connector_name
                )
                # None means connector doesn't exist - that's okay
                status["sink_connector"] = sink_status
            except Exception as e:
                logger.warning(f"Failed to get Sink connector status: {e}")
        
        # Update status based on actual connector states
        if status.get("debezium_connector") and status.get("sink_connector"):
            dbz_state = status["debezium_connector"].get("connector", {}).get("state", "").upper()
            sink_state = status["sink_connector"].get("connector", {}).get("state", "").upper()
            
            if dbz_state == "RUNNING" and sink_state == "RUNNING":
                # Both connectors are running, update status to RUNNING
                if pipeline.status != PipelineStatus.RUNNING:
                    logger.info(f"Updating pipeline status to RUNNING (connectors are running)")
                    pipeline.status = PipelineStatus.RUNNING
                    pipeline.cdc_status = CDCStatus.RUNNING
                    status["status"] = "RUNNING"
                    status["cdc_status"] = "RUNNING"
                    # Persist the updated status
                    self._persist_pipeline_status(pipeline)
        
        return status
    
    def list_pipelines(self) -> List[Dict[str, Any]]:
        """List all pipelines.
        
        Returns:
            List of pipeline dictionaries
        """
        return [pipeline.to_dict() for pipeline in self.pipeline_store.values()]

