"""Monitoring and metrics for CDC pipelines."""

from __future__ import annotations

import logging
import time
from datetime import datetime
from typing import Any, Dict, List, Optional

from ingestion.kafka_connect_client import KafkaConnectClient
from ingestion.models import Pipeline

logger = logging.getLogger(__name__)


class CDCMonitor:
    """Monitor CDC pipeline health and metrics."""
    
    def __init__(self, kafka_connect_client: KafkaConnectClient):
        """Initialize CDC monitor.
        
        Args:
            kafka_connect_client: Kafka Connect client instance
        """
        self.kafka_client = kafka_connect_client
    
    def check_connector_health(
        self,
        connector_name: str
    ) -> Dict[str, Any]:
        """Check connector health.
        
        Args:
            connector_name: Connector name
            
        Returns:
            Health status dictionary
        """
        try:
            status = self.kafka_client.get_connector_status(connector_name)
            connector_state = status.get("connector", {}).get("state", "UNKNOWN")
            tasks = status.get("tasks", [])
            
            failed_tasks = [
                task for task in tasks
                if task.get("state") == "FAILED"
            ]
            
            health = {
                "connector_name": connector_name,
                "status": "healthy" if connector_state == "RUNNING" and not failed_tasks else "unhealthy",
                "connector_state": connector_state,
                "total_tasks": len(tasks),
                "failed_tasks": len(failed_tasks),
                "task_details": tasks,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            if failed_tasks:
                health["errors"] = [
                    task.get("trace", "Unknown error")
                    for task in failed_tasks
                ]
            
            return health
            
        except Exception as e:
            logger.error(f"Failed to check connector health: {e}")
            return {
                "connector_name": connector_name,
                "status": "error",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    def check_pipeline_health(
        self,
        pipeline: Pipeline
    ) -> Dict[str, Any]:
        """Check overall pipeline health.
        
        Args:
            pipeline: Pipeline object
            
        Returns:
            Pipeline health status
        """
        health = {
            "pipeline_id": pipeline.id,
            "pipeline_name": pipeline.name,
            "overall_status": "unknown",
            "components": {},
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Check Debezium connector
        if pipeline.debezium_connector_name:
            debezium_health = self.check_connector_health(
                pipeline.debezium_connector_name
            )
            health["components"]["debezium"] = debezium_health
        
        # Check Sink connector
        if pipeline.sink_connector_name:
            sink_health = self.check_connector_health(
                pipeline.sink_connector_name
            )
            health["components"]["sink"] = sink_health
        
        # Determine overall status
        component_statuses = [
            comp.get("status", "unknown")
            for comp in health["components"].values()
        ]
        
        if all(status == "healthy" for status in component_statuses):
            health["overall_status"] = "healthy"
        elif any(status == "unhealthy" for status in component_statuses):
            health["overall_status"] = "unhealthy"
        elif any(status == "error" for status in component_statuses):
            health["overall_status"] = "error"
        
        return health
    
    def get_pipeline_metrics(
        self,
        pipeline: Pipeline
    ) -> Dict[str, Any]:
        """Get pipeline metrics.
        
        Args:
            pipeline: Pipeline object
            
        Returns:
            Metrics dictionary
        """
        metrics = {
            "pipeline_id": pipeline.id,
            "pipeline_name": pipeline.name,
            "status": pipeline.status,
            "full_load_status": pipeline.full_load_status,
            "cdc_status": pipeline.cdc_status,
            "kafka_topics_count": len(pipeline.kafka_topics),
            "tables_count": len(pipeline.source_tables),
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Add connector metrics
        if pipeline.debezium_connector_name:
            try:
                dbz_status = self.kafka_client.get_connector_status(
                    pipeline.debezium_connector_name
                )
                metrics["debezium_connector_state"] = dbz_status.get("connector", {}).get("state")
            except Exception:
                pass
        
        if pipeline.sink_connector_name:
            try:
                sink_status = self.kafka_client.get_connector_status(
                    pipeline.sink_connector_name
                )
                metrics["sink_connector_state"] = sink_status.get("connector", {}).get("state")
            except Exception:
                pass
        
        return metrics




