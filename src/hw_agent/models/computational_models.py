from dataclasses import Field
from pydantic import BaseModel
from typing import Any, Dict, Optional
from datetime import datetime
from hw_agent.models.connection_config_models import ConnectionConfigMetadata
from hw_agent.models.plugin_models import PluginDefinition


class ComputationalMetadata(BaseModel):    
    plugin_definition: PluginDefinition
    start_time_in_utc: datetime
    duration_time_in_seconds: float  # Duration in seconds

class ComputationalInfo(BaseModel):
    data: Dict[str, Any]  # Orchestrator-specific data

class ComputationalData(BaseModel):        
    metadata: ComputationalMetadata
    computational_info: Dict[str, Any]
