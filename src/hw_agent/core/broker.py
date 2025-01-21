# src/hw_agent/core/broker.py

from hw_agent.core.orchestrator_type import OrchestratorType
from hw_agent.core.plugin_context import PluginContext
from hw_agent.core.singleton_meta import SingletonMeta
from hw_agent.core.plugin_manager import PluginManager
from hw_agent.models.computational_asset import ComputationalAsset
from hw_agent.services.aiod_metadata_client import AIODMetadataClient
from hw_agent.services.repository_service import RepositoryService
from hw_agent.utils.logger import get_logger
from hw_agent.models.connection_config_models import  ConnectionConfigRead
from hw_agent.models.computational_models import ComputationalData
from hw_agent.core.base_plugin import BasePlugin

plugin_manager = PluginManager()

class Broker(metaclass=SingletonMeta):
    
    
    def __init__(self):
        """
        Initialize the Broker class.

        This class is responsible for managing the communication with the orchestrator configuration service,
        AIOD metadata client, and handling data normalization and storage.

        Attributes:
        - config_service: An instance of OrchestratorConfigurationService for retrieving configuration details.
        - aiod_client: An instance of AIODMetadataClient for interacting with the AIOD metadata catalogue.
        - logger: A logger instance for logging messages.
        """
        self.config_service = RepositoryService() 
        self.aiod_client = AIODMetadataClient()
        self.logger = get_logger(self.__class__.__name__)

    def fetch_computational_data(self, config_id: str) -> ComputationalData:
        # Retrieve configuration
        connection_config = self.config_service.get_configuration(config_id)
        
        # Get plugin
        self.logger.info(f"Trying to load plugin for orchestrator type: '{connection_config.orchestrator_type}'.")        
        plugin = plugin_manager.get_plugin(connection_config.orchestrator_type)

        # Build the execution context
        plugin_context = self._build_context(connection_config, plugin)
        
        # Execute plugin command. For now it returns a ComputaqualAsset with specific information of each orchestrator
        computational_data = plugin.fetch(plugin_context)
        
        return computational_data
    
    def fetch_and_transform(self, config_id: str) -> ComputationalData:
        # Retrieve configuration
        connection_config = self.config_service.get_configuration(config_id)
                
        # Get plugin
        self.logger.info(f"Trying to load plugin for orchestrator type: '{connection_config.orchestrator_type}'.")        
        plugin = plugin_manager.get_plugin(connection_config.orchestrator_type)
        
        # Build the execution context
        plugin_context = self._build_context(connection_config, plugin)
        
        # Execute plugin command. For now it returns a ComputaqualAsset with specific information of each orchestrator
        computational_asset = plugin.fetch_and_transform(plugin_context)
        
        return computational_asset
    
    
    def _build_context(self, connection_config: ConnectionConfigRead, plugin: BasePlugin) -> PluginContext:
        return PluginContext(
            config_id=connection_config.config_id,
            connection_config=connection_config,
            plugin_definition=plugin.plugin_definition.to_dict(), #Exclude connection schema
        )