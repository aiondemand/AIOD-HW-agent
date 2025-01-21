# src/hw_agent/repositories/yaml_repository.py

from typing import Optional
import yaml
import os
from threading import Lock
from hw_agent.repositories.base_repository import BaseRepository
from hw_agent.repositories.repository_factory import RepositoryFactory
from hw_agent.services.settings_service import SettingsService
from hw_agent.models.connection_config_models import ConnectionConfigRead, ConnectionConfigCreate

@RepositoryFactory.register('yaml')
class YAMLRepository(BaseRepository):
    _lock = Lock()

    def __init__(self):
        settings = SettingsService()
        config_file = settings.get('yaml_config_file', 'data/configurations.yaml')
        self.config_file = os.path.abspath(config_file)
        # Ensure the configs directory exists
        os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
        # Initialize the YAML file if it doesn't exist
        if not os.path.exists(self.config_file):
            with open(self.config_file, 'w') as f:
                yaml.dump({}, f)

    def save_configuration(self, config_id, connection_info: ConnectionConfigCreate) -> None:
        with self._lock:
            data = self._read_all()
            data[config_id] = connection_info.model_dump(mode="json")
            with open(self.config_file, 'w') as f:
                yaml.dump(data, f)

    def get_configuration(self, config_id) -> Optional[ConnectionConfigRead]:
        with self._lock:
            configurations = self._read_all()
            config_data = configurations.get(config_id)
            if config_data:
                # Add the config_id to the data
                config_data['config_id'] = config_id
                # Instantiate ConnectionConfigRead using automatic mapping
                return ConnectionConfigRead(**config_data)
            else:
                return None        
        

    def _read_all(self):
        with open(self.config_file, 'r') as f:
            data = yaml.safe_load(f) or {}
        return data

    def get_configurations(self):
        with self._lock:
            data = self._read_all()
            return data
        
    def clear_all_configurations(self):
        with self._lock:
            data = {}
            with open(self.config_file, 'w') as f:
                yaml.dump(data, f)
        return True
    
    def delete_configuration(self, config_id):
        with self._lock:
            data = self._read_all()
            if config_id in data:
                del data[config_id]
                with open(self.config_file, 'w') as f:
                    yaml.dump(data, f)
                return True
            else:
                return False