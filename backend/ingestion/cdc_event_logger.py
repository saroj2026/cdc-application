"""CDC Event Logger - Consumes Kafka messages and logs CDC events to database.

This service listens to Kafka topics and logs individual CDC events (insert/update/delete)
to the pipeline_runs table for monitoring purposes.
"""

import json
import logging
import threading
import time
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional, Set
from contextlib import contextmanager

logger = logging.getLogger(__name__)

# Import Kafka consumer
try:
    from kafka import KafkaConsumer
    from kafka.errors import KafkaError, NoBrokersAvailable
    KAFKA_AVAILABLE = True
except ImportError:
    logger.warning("kafka-python not installed. CDC event logging will be disabled.")
    KAFKA_AVAILABLE = False
    KafkaConsumer = None
    KafkaError = Exception
    NoBrokersAvailable = Exception


class CDCEventLogger:
    """Logs CDC events from Kafka topics to the database.
    
    This class creates a Kafka consumer that listens to CDC topics and logs
    individual insert/update/delete events to the pipeline_runs table.
    """
    
    def __init__(
        self,
        kafka_bootstrap_servers: str = "72.61.233.209:9092",
        consumer_group_id: str = "cdc-event-logger",
        db_session_factory = None,
        max_batch_size: int = 100,
        batch_timeout_seconds: float = 5.0
    ):
        """Initialize the CDC Event Logger.
        
        Args:
            kafka_bootstrap_servers: Kafka bootstrap servers
            consumer_group_id: Kafka consumer group ID
            db_session_factory: SQLAlchemy session factory function
            max_batch_size: Maximum events to batch before committing
            batch_timeout_seconds: Max time to wait before committing a batch
        """
        self.kafka_bootstrap_servers = kafka_bootstrap_servers
        self.consumer_group_id = consumer_group_id
        self.db_session_factory = db_session_factory
        self.max_batch_size = max_batch_size
        self.batch_timeout_seconds = batch_timeout_seconds
        
        self._consumer: Optional[KafkaConsumer] = None
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._subscribed_topics: Set[str] = set()
        self._pipeline_topic_mapping: Dict[str, str] = {}  # topic -> pipeline_id
        self._lock = threading.Lock()
        
    def start(self, topics: Optional[List[str]] = None, pipeline_mapping: Optional[Dict[str, str]] = None):
        """Start the event logger in a background thread.
        
        Args:
            topics: List of Kafka topics to subscribe to
            pipeline_mapping: Mapping of topic names to pipeline IDs
        """
        if not KAFKA_AVAILABLE:
            logger.warning("Kafka library not available. CDC event logging disabled.")
            return False
            
        if self._running:
            logger.warning("CDC Event Logger is already running")
            return True
            
        if topics:
            self._subscribed_topics = set(topics)
        if pipeline_mapping:
            self._pipeline_topic_mapping = pipeline_mapping
            
        self._running = True
        self._thread = threading.Thread(target=self._run_consumer, daemon=True)
        self._thread.start()
        logger.info(f"CDC Event Logger started for topics: {self._subscribed_topics}")
        return True
        
    def stop(self):
        """Stop the event logger."""
        self._running = False
        if self._thread:
            self._thread.join(timeout=10)
        if self._consumer:
            try:
                self._consumer.close()
            except Exception as e:
                logger.warning(f"Error closing Kafka consumer: {e}")
        logger.info("CDC Event Logger stopped")
        
    def add_topic(self, topic: str, pipeline_id: str):
        """Add a topic to the subscription list.
        
        Args:
            topic: Kafka topic name
            pipeline_id: Associated pipeline ID
        """
        with self._lock:
            self._subscribed_topics.add(topic)
            self._pipeline_topic_mapping[topic] = pipeline_id
            
        # If consumer is running, update subscription
        if self._consumer and self._running:
            try:
                self._consumer.subscribe(list(self._subscribed_topics))
                logger.info(f"Added topic {topic} to CDC event logger")
            except Exception as e:
                logger.warning(f"Failed to update subscription with new topic {topic}: {e}")
                
    def remove_topic(self, topic: str):
        """Remove a topic from the subscription list.
        
        Args:
            topic: Kafka topic name to remove
        """
        with self._lock:
            self._subscribed_topics.discard(topic)
            self._pipeline_topic_mapping.pop(topic, None)
            
        # If consumer is running, update subscription
        if self._consumer and self._running and self._subscribed_topics:
            try:
                self._consumer.subscribe(list(self._subscribed_topics))
                logger.info(f"Removed topic {topic} from CDC event logger")
            except Exception as e:
                logger.warning(f"Failed to update subscription after removing topic {topic}: {e}")
    
    def _run_consumer(self):
        """Main consumer loop (runs in background thread)."""
        retry_count = 0
        max_retries = 5
        
        while self._running and retry_count < max_retries:
            try:
                # Create consumer
                self._consumer = KafkaConsumer(
                    bootstrap_servers=self.kafka_bootstrap_servers.split(','),
                    group_id=self.consumer_group_id,
                    auto_offset_reset='latest',  # Only process new messages
                    enable_auto_commit=False,
                    value_deserializer=lambda m: json.loads(m.decode('utf-8')) if m else None,
                    key_deserializer=lambda m: json.loads(m.decode('utf-8')) if m else None,
                    consumer_timeout_ms=1000,  # 1 second timeout for poll
                    max_poll_records=100,
                    session_timeout_ms=30000,
                    heartbeat_interval_ms=10000
                )
                
                # Subscribe to topics
                with self._lock:
                    topics = list(self._subscribed_topics)
                    
                if topics:
                    self._consumer.subscribe(topics)
                    logger.info(f"CDC Event Logger subscribed to topics: {topics}")
                else:
                    logger.info("CDC Event Logger waiting for topics to be added...")
                    
                retry_count = 0  # Reset retry count on successful connection
                
                # Main processing loop
                self._process_messages()
                
            except NoBrokersAvailable as e:
                retry_count += 1
                wait_time = min(30, 2 ** retry_count)  # Exponential backoff, max 30 seconds
                logger.warning(f"Kafka brokers not available (attempt {retry_count}/{max_retries}). Retrying in {wait_time}s...")
                time.sleep(wait_time)
                
            except Exception as e:
                retry_count += 1
                wait_time = min(30, 2 ** retry_count)
                logger.error(f"CDC Event Logger error (attempt {retry_count}/{max_retries}): {e}", exc_info=True)
                time.sleep(wait_time)
                
        if retry_count >= max_retries:
            logger.error("CDC Event Logger stopped after max retries")
            
    def _process_messages(self):
        """Process messages from Kafka."""
        batch = []
        batch_start_time = time.time()
        
        while self._running:
            try:
                # Check if topics need to be updated
                with self._lock:
                    current_topics = list(self._subscribed_topics)
                    
                if current_topics and self._consumer.subscription() != set(current_topics):
                    self._consumer.subscribe(current_topics)
                    logger.info(f"Updated subscription to: {current_topics}")
                    
                # Poll for messages
                message_batch = self._consumer.poll(timeout_ms=1000)
                
                for topic_partition, messages in message_batch.items():
                    for message in messages:
                        event = self._parse_debezium_message(message)
                        if event:
                            batch.append(event)
                            
                # Commit batch if size or time threshold reached
                current_time = time.time()
                if batch and (len(batch) >= self.max_batch_size or 
                              current_time - batch_start_time >= self.batch_timeout_seconds):
                    self._commit_batch(batch)
                    self._consumer.commit()
                    batch = []
                    batch_start_time = current_time
                    
            except Exception as e:
                logger.error(f"Error processing Kafka messages: {e}", exc_info=True)
                # Commit any pending events before continuing
                if batch:
                    try:
                        self._commit_batch(batch)
                        self._consumer.commit()
                    except Exception as commit_error:
                        logger.error(f"Failed to commit batch after error: {commit_error}")
                    batch = []
                    batch_start_time = time.time()
                time.sleep(1)  # Brief pause before retrying
                
        # Final commit
        if batch:
            self._commit_batch(batch)
            try:
                self._consumer.commit()
            except Exception:
                pass
                
    def _parse_debezium_message(self, message) -> Optional[Dict[str, Any]]:
        """Parse a Debezium message and extract CDC event information.
        
        Args:
            message: Kafka message
            
        Returns:
            Parsed event dict or None if not a valid CDC event
        """
        try:
            topic = message.topic
            value = message.value
            
            if not value:
                return None
                
            # Get pipeline ID from topic mapping
            pipeline_id = self._pipeline_topic_mapping.get(topic)
            if not pipeline_id:
                # Try to find pipeline by topic prefix
                for mapped_topic, pid in self._pipeline_topic_mapping.items():
                    if topic.startswith(mapped_topic.split('.')[0]):
                        pipeline_id = pid
                        break
                        
            if not pipeline_id:
                logger.debug(f"No pipeline mapping found for topic {topic}")
                return None
                
            # Parse Debezium message format
            # Debezium messages have structure: {"schema": ..., "payload": {"before": ..., "after": ..., "source": ..., "op": ...}}
            payload = value.get('payload', value)
            
            # Get operation type
            op = payload.get('op')
            if not op:
                return None
                
            # Map Debezium operation codes to event types
            op_mapping = {
                'c': 'insert',   # Create
                'r': 'insert',   # Read (snapshot)
                'u': 'update',   # Update
                'd': 'delete',   # Delete
                't': 'truncate'  # Truncate (some connectors)
            }
            
            event_type = op_mapping.get(op)
            if not event_type:
                logger.debug(f"Unknown Debezium operation: {op}")
                return None
                
            # Extract metadata
            source = payload.get('source', {})
            table_name = source.get('table', 'unknown')
            schema_name = source.get('schema', 'unknown')
            database_name = source.get('db', 'unknown')
            
            # Get timestamp
            ts_ms = source.get('ts_ms') or payload.get('ts_ms')
            event_time = datetime.utcfromtimestamp(ts_ms / 1000) if ts_ms else datetime.utcnow()
            
            # Create event record
            event = {
                'id': str(uuid.uuid4()),
                'pipeline_id': pipeline_id,
                'run_type': 'CDC',
                'event_type': event_type,
                'status': 'completed',
                'started_at': event_time,
                'completed_at': event_time,
                'rows_processed': 1,
                'errors_count': 0,
                'run_metadata': {
                    'event_type': event_type,
                    'operation': op,
                    'table_name': table_name,
                    'schema_name': schema_name,
                    'database_name': database_name,
                    'topic': topic,
                    'partition': message.partition,
                    'offset': message.offset,
                    'source_ts_ms': ts_ms
                }
            }
            
            return event
            
        except Exception as e:
            logger.debug(f"Failed to parse Debezium message: {e}")
            return None
            
    def _commit_batch(self, events: List[Dict[str, Any]]):
        """Commit a batch of events to the database.
        
        Args:
            events: List of event dictionaries
        """
        if not events:
            return
            
        if not self.db_session_factory:
            logger.warning("No database session factory configured, cannot commit events")
            return
            
        try:
            from ingestion.database.models_db import PipelineRunModel
            
            session = self.db_session_factory()
            try:
                for event in events:
                    run = PipelineRunModel(
                        id=event['id'],
                        pipeline_id=event['pipeline_id'],
                        run_type=event['run_type'],
                        status=event['status'],
                        started_at=event['started_at'],
                        completed_at=event['completed_at'],
                        rows_processed=event['rows_processed'],
                        errors_count=event['errors_count'],
                        run_metadata=event['run_metadata']
                    )
                    session.add(run)
                    
                session.commit()
                logger.info(f"Committed {len(events)} CDC events to database")
                
                # Log event type breakdown
                event_counts = {}
                for event in events:
                    et = event['run_metadata'].get('event_type', 'unknown')
                    event_counts[et] = event_counts.get(et, 0) + 1
                logger.info(f"Event breakdown: {event_counts}")
                
            except Exception as e:
                session.rollback()
                logger.error(f"Failed to commit events to database: {e}", exc_info=True)
            finally:
                session.close()
                
        except Exception as e:
            logger.error(f"Database error in CDC event logger: {e}", exc_info=True)


# Global event logger instance
_event_logger: Optional[CDCEventLogger] = None


def get_event_logger() -> Optional[CDCEventLogger]:
    """Get the global CDC event logger instance."""
    return _event_logger


def initialize_event_logger(
    kafka_bootstrap_servers: str = "72.61.233.209:9092",
    db_session_factory = None
) -> Optional[CDCEventLogger]:
    """Initialize and start the global CDC event logger.
    
    Args:
        kafka_bootstrap_servers: Kafka bootstrap servers
        db_session_factory: SQLAlchemy session factory
        
    Returns:
        CDCEventLogger instance or None if Kafka not available
    """
    global _event_logger
    
    if not KAFKA_AVAILABLE:
        logger.warning("Kafka library not available. CDC event logging disabled.")
        return None
        
    if _event_logger is not None:
        logger.info("CDC Event Logger already initialized")
        return _event_logger
        
    _event_logger = CDCEventLogger(
        kafka_bootstrap_servers=kafka_bootstrap_servers,
        db_session_factory=db_session_factory
    )
    
    return _event_logger


def shutdown_event_logger():
    """Shutdown the global CDC event logger."""
    global _event_logger
    
    if _event_logger:
        _event_logger.stop()
        _event_logger = None
        logger.info("CDC Event Logger shutdown complete")


