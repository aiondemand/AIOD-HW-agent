# src/hw_agent/core/plugin_context.py

from typing import Dict, Any
from hw_agent.core.orchestrator_type import OrchestratorType
from hw_agent.utils.logger import get_logger
from hw_agent.models.connection_config_models import ConnectionConfigCreate, ConnectionConfigMetadata
from hw_agent.models.plugin_models import PluginDefinition

class PluginContext:
    
    '''
    Represents the execution context in which a plugin is executed. It contains the connection configuration and the plugin definition.
    Attributes:
    - config_id (str): The ID of the configuration.
    - connection_config (ConnectionConfigCreate): The connection configuration.
    - plugin_definition (PluginDefinition): The plugin definition of the associated plugin.
    '''
    
    def __init__(
        self,
        config_id: str,
        connection_config: ConnectionConfigCreate,
        plugin_definition: PluginDefinition
    ):
        self.config_id = config_id
        self.connection_config = connection_config
        self.plugin_definition = plugin_definition        
        self.logger = get_logger(f"PluginContext-{config_id}")

    def get_connection_info(self, key: str, default=None):
        return self.connection_config.connection_info.get(key, default)
    
    def get_resource_metadata(self) -> ConnectionConfigMetadata:
        return self.connection_config.metadata
    
    def get_logger(self):
        return self.logger
    
    def get_plugin_definition(self) -> PluginDefinition:
        return self.plugin_definition
    
