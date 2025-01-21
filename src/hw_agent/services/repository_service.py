# src/hw_agent/services/repository_service.py

from hw_agent.core.singleton_meta import SingletonMeta
from hw_agent.exceptions.custom_exceptions import ConfigurationNotFoundError
from hw_agent.repositories.repository_factory import RepositoryFactory
from hw_agent.dependencies import get_setting_service
from hw_agent.utils.helpers import generate_unique_id
from hw_agent.models.connection_config_models import ConnectionConfigCreate, ConnectionConfigRead
from hw_agent.core.plugin_manager import PluginManager

class RepositoryService:
    def __init__(self):

        settings = get_setting_service()
        
        # Get the repository type from the settings, by default use YAML
        repository_type = settings.get('repository_type', 'yaml')            
        self.repository = RepositoryFactory.create_repository(repository_type)

    def save_configuration(self, connection_info: ConnectionConfigCreate):
        
        # Check if Connection Info is provided
        if connection_info is None:
            raise ValueError("Connection info is required.")
        
        # Validate the Connection Info against connection schema if is it provided
        if connection_info.connection_info is not None:
            plugin_manager = PluginManager()
            plugin_manager.validate_connection_info(connection_info.connection_info, connection_info.orchestrator_type)
        
        config_id = generate_unique_id()
        self.repository.save_configuration(config_id, connection_info)
        return config_id

    def get_configuration(self, config_id) -> ConnectionConfigRead:
        config = self.repository.get_configuration(config_id)
        if not config:
            raise ConfigurationNotFoundError(f"Configuration with ID {config_id} not found.")
        return config
    
    def get_configurations(self):
        return self.repository.get_configurations()

    def clear_all_configurations(self):
        return self.repository.clear_all_configurations()
    
    
    def delete_configuration(self, config_id):
        
        # try to find the configuration in the repository first
        config = self.repository.get_configuration(config_id)
        if not config:
            raise ConfigurationNotFoundError(f"Configuration with ID {config_id} not found.")
        
        return self.repository.delete_configuration(config_id)