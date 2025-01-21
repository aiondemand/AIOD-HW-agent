# src/hw_agent/services/plugin_manager_configuration_service.py

import os
import yaml
from typing import Any, Dict, Optional
from pydantic import BaseModel, ValidationError, field_validator
from hw_agent.core.singleton_meta import SingletonMeta
from hw_agent.models.plugin_models import PluginManagerConfig



class PluginManagerConfigurationService:
    def __init__(self, config_path: str = 'configs/plugin_manager_config.yaml'):
        self.config_path = config_path
        self.config: PluginManagerConfig
        self.load_configuration()

    def load_configuration(self):
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f"PluginManager config file not found at '{self.config_path}'")
        try:
            with open(self.config_path, 'r') as file:
                config_data = yaml.safe_load(file)
                self.config = PluginManagerConfig(**config_data)
        except ValidationError as ve:
            raise ValueError(f"Configuration validation error: {ve}") from ve
        except yaml.YAMLError as ye:
            raise ValueError(f"Error parsing YAML configuration: {ye}") from ye
        except Exception as e:
            raise RuntimeError(f"Unexpected error loading configuration: {e}") from e

    def get_config(self) -> PluginManagerConfig:
        if not self.config:
            raise ValueError("Configuration not loaded")
        return self.config

    def get_config_value(self, key: str, default: Any = None) -> Any:
        if not self.config:
            raise ValueError("Configuration not loaded")
        return getattr(self.config, key, default)

