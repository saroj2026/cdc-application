"""Pipeline service for orchestrating full load and CDC."""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from ingestion.cdc_manager import CDCManager
from ingestion.models import Pipeline, Connection

logger = logging.getLogger(__name__)


class PipelineService:
    """Service for managing pipeline lifecycle."""
    
    def __init__(self, cdc_manager: CDCManager):
        """Initialize pipeline service.
        
        Args:
            cdc_manager: CDC Manager instance
        """
        self.cdc_manager = cdc_manager
    
    def create_pipeline(
        self,
        pipeline: Pipeline,
        source_connection: Connection,
        target_connection: Connection
    ) -> Pipeline:
        """Create a new pipeline.
        
        Args:
            pipeline: Pipeline object
            source_connection: Source connection
            target_connection: Target connection
            
        Returns:
            Created pipeline
        """
        return self.cdc_manager.create_pipeline(
            pipeline=pipeline,
            source_connection=source_connection,
            target_connection=target_connection
        )
    
    def start_pipeline(self, pipeline_id: str) -> Dict[str, Any]:
        """Start a pipeline (full load → CDC).
        
        Args:
            pipeline_id: Pipeline ID
            
        Returns:
            Startup result
        """
        return self.cdc_manager.start_pipeline(pipeline_id)
    
    def stop_pipeline(self, pipeline_id: str) -> Dict[str, Any]:
        """Stop a pipeline.
        
        Args:
            pipeline_id: Pipeline ID
            
        Returns:
            Stop result
        """
        return self.cdc_manager.stop_pipeline(pipeline_id)
    
    def pause_pipeline(self, pipeline_id: str) -> Dict[str, Any]:
        """Pause a pipeline.
        
        Args:
            pipeline_id: Pipeline ID
            
        Returns:
            Pause result
        """
        return self.cdc_manager.pause_pipeline(pipeline_id)
    
    def get_pipeline_status(self, pipeline_id: str) -> Dict[str, Any]:
        """Get pipeline status.
        
        Args:
            pipeline_id: Pipeline ID
            
        Returns:
            Pipeline status
        """
        return self.cdc_manager.get_pipeline_status(pipeline_id)
    
    def list_pipelines(self) -> List[Dict[str, Any]]:
        """List all pipelines.
        
        Returns:
            List of pipelines
        """
        return self.cdc_manager.list_pipelines()

