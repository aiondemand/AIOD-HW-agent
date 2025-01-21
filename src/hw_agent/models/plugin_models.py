from dataclasses import field
from pydantic import BaseModel, field_validator, Field
from hw_agent.core.orchestrator_type import OrchestratorType
from typing import Any, List, Dict, Optional


class PluginManagerConfig(BaseModel):

    AllowedOrchestratorTypes: list[str] = ["kubernetes", "openstack"]
    PluginsDirectory: str = "plugins"
    ExcludeDirectories: list[str] = ["__pycache__", ".git"]

    @field_validator('AllowedOrchestratorTypes')
    def orchestrator_type_not_empty(cls, v):
        for orchestrator_type in v:
            if not orchestrator_type.strip():
                raise ValueError("OrchestratorType cannot be empty")
        return v

    @field_validator('PluginsDirectory')
    def plugins_directory_not_empty(cls, v):
        if not v.strip():
            raise ValueError("PluginsDirectory cannot be empty")
        return v 
    

class PluginDocumentation(BaseModel):
    description: Optional[str]
    author: Optional[str]
    version: Optional[str]

class PluginDefinition(BaseModel):
    name: str
    orchestrator_type: OrchestratorType
    module: str = Field(description="The module name for the plugin")
    documentation: Optional[PluginDocumentation] = Field(default=None, description="The documentation for the plugin")
    dependencies: Optional[List[str]] = Field(default=None, description="The dependencies for the plugin")
    configuration: Optional[Dict[str, Any]] = Field(default_factory=dict, description="The configuration for the plugin")
    connection_schema: Optional[Dict[str, Any]] = Field(default=None, description="The connection schema for the plugin")        

    @field_validator('orchestrator_type')
    def orchestrator_type_must_not_be_empty(cls, v):
        if not v:
            raise ValueError("orchestrator_type cannot be empty")
        return v

    def get_config_value(self, key: str, default: Any = None) -> Any:
        """
        Getter method to extract values from the configuration dictionary.
        
        Args:
            key (str): The key to look for in the configuration dictionary.
            default (Any): The default value to return if the key is not found.
        
        Returns:
            Any: The value associated with the key, or the default value.
        """
        return self.configuration.get(key, default)
    
    def to_dict(self):
        return self.model_dump(exclude={'connection_schema'})
    
    
    def to_dict_with_connection_schema(self):
        return self.model_dump(include={'connection_schema'})