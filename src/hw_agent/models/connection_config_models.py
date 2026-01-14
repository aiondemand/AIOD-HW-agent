from typing import Any, Optional
from pydantic import BaseModel
from hw_agent.core.orchestrator_type import OrchestratorType


class ConnectionConfigResponse(BaseModel):
    config_id: str
    orchestrator_type: OrchestratorType

class ConnectionConfigMetadata(BaseModel):
    name: str
    description: str
    contact: str
    location: Optional[str] = None

class ConnectionConfigCreate(BaseModel):
    metadata: ConnectionConfigMetadata
    orchestrator_type: OrchestratorType
    connection_info: dict
    
    
class ConnectionConfigRead(BaseModel):
    config_id: str
    metadata: ConnectionConfigMetadata
    orchestrator_type: OrchestratorType
    connection_info: dict[str, Any]    