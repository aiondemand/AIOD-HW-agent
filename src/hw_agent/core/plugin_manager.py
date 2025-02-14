# src/hw_agent/core/plugin_manager.py

import os
import sys
import importlib
import jsonschema
from typing import Dict, List, Optional

from fastapi import Depends
import yaml
from hw_agent.core.base_plugin import BasePlugin
from hw_agent.core.plugin_context import PluginContext
from hw_agent.core.singleton_meta import SingletonMeta
from hw_agent.dependencies import get_plugin_cache_service, get_plugin_manager_configuration_service
from hw_agent.exceptions.custom_exceptions import ConnectionConfigurationError, PluginLoadError, PluginNotFoundError
from hw_agent.models.computational_models import ComputationalData
from hw_agent.models.plugin_models import PluginDefinition
from hw_agent.services.cache_service import CacheService
from hw_agent.services.plugin_manager_configuration_service import PluginManagerConfigurationService
from hw_agent.utils.logger import get_logger
from hw_agent.core.orchestrator_type import OrchestratorType


class PluginManager(metaclass=SingletonMeta):
    def __init__(self):
        
        self.logger = get_logger("PluginManager") 
        self.plugins: Dict[str, BasePlugin] = {}
        
        # Initalize the CacheService and the PluginManagerConfigurationService
        self.cache_service = get_plugin_cache_service()     
        self.config_service = get_plugin_manager_configuration_service()
        
        # Load the plugin configuration
        self.allowed_orchestrator_types = self.config_service.get_config_value('AllowedOrchestratorTypes', [])
        self.plugins_dir = self._get_plugins_directory()
        self.exclude_directories = self.config_service.get_config_value('ExcludeDirectories', [])
        
        # Finally load the plugins
        self._load_plugin_definitions()


    def execute_plugin(self, orchestrator_type: str, plugin_context: PluginContext) -> ComputationalData:
        """
        Executes the plugin for the specified orchestrator type.

        Args:
            orchestrator_type (str): The orchestrator type.
            plugin_context (PluginContext): The context for the plugin execution.

        Returns:
            ComputationalData: The result of the plugin execution.
        """
        plugin = self.get_plugin(orchestrator_type)
        return plugin.fecth_and_transform(plugin_context)
    
    def _get_plugins_directory(self) -> str:
        plugins_directory = self.config_service.get_config_value('PluginsDirectory')
        if not os.path.isabs(plugins_directory):
            # Assume relative to application root           
            plugins_directory = os.path.join(os.path.dirname(__file__), '..', plugins_directory)
            plugins_directory = os.path.abspath(plugins_directory)
            
        if not os.path.exists(plugins_directory):
            self.logger.error(f"Plugins directory '{plugins_directory}' does not exist")
            raise FileNotFoundError(f"Plugins directory '{plugins_directory}' does not exist")
        self.logger.info(f"Using plugins directory: '{plugins_directory}'")
        return plugins_directory

    def _load_plugin_definitions(self):
        self.logger.info("Loading plugin definitions...")
        self.plugins.clear()
        self.cache_service.clear_plugins() 

        plugin_folder_names = self._get_plugin_folder_names()
        for plugin_folder in plugin_folder_names:
            self.logger.debug(f"Attempting to load plugin from: '{plugin_folder}'")
            plugin_instance = self._load_plugin(plugin_folder)
            if plugin_instance:
                self._register_plugin(plugin_instance.plugin_definition.orchestrator_type, plugin_instance)

        self.logger.info(f"Total plugins loaded: {len(self.plugins)}")

    def _get_plugin_folder_names(self) -> List[str]:
        try:
            plugin_names = [
                name for name in os.listdir(self.plugins_dir)
                if os.path.isdir(os.path.join(self.plugins_dir, name)) and name not in self.exclude_directories
            ]
            self.logger.debug(f"Found plugin directories: {plugin_names}")
            return plugin_names
        except Exception as e:
            self.logger.error(f"Error accessing plugins directory '{self.plugins_dir}': {e}")
            raise PluginLoadError(plugin_names, e)

    def _load_plugin(self, plugin_folder: str) -> Optional[BasePlugin]:
        plugin_definition = self._read_plugin_definition(plugin_folder)
        
        if not plugin_definition:
            self.logger.warning(f"Error parsing config.yaml '{plugin_folder}'. Skipping plugin.")    
            return None

        # Check if the orchestrator type is allowed and it is not duplicated
        if not self._is_orchestrator_type_allowed(plugin_definition.orchestrator_type, plugin_definition.name):
            self.logger.warning(f"Orchestrator type '{plugin_definition.orchestrator_type}' is not allowed. Skipping plugin.")
            return None

        if not plugin_definition.module:
            self.logger.warning(f"Module not specified in config.yaml for plugin '{plugin_definition.name}'. Skipping plugin.")
            return None

        # Instantiate the plugin and set the configuration
        plugin_instance = self._import_plugin_instance(plugin_folder, plugin_definition)

        return plugin_instance


    def _read_plugin_definition(self, plugin_name: str) -> PluginDefinition:
        config_path = os.path.join(self.plugins_dir, plugin_name, 'config.yaml')
        if not os.path.isfile(config_path):
            self.logger.warning(f"No config.yaml found in plugin directory '{plugin_name}'. Skipping plugin.")
            return None 
        try:
            with open(config_path, 'r') as config_file:
                config_data = yaml.safe_load(config_file)
                self.logger.debug(f"Loaded config for plugin '{plugin_name}': {config_data}")
                return PluginDefinition(**config_data)
        except Exception as e:
            self.logger.error(f"Error reading plugin definition for plugin '{plugin_name}': {e}")
            return None

    def _is_orchestrator_type_allowed(self, orchestrator_type: str, plugin_name: str) -> bool:
        if orchestrator_type not in self.allowed_orchestrator_types:
            self.logger.warning(f"Invalid OrchestratorType '{orchestrator_type}' in plugin '{plugin_name}'. Skipping plugin.")
            return False
        if orchestrator_type in self.plugins:
            self.logger.warning(f"Duplicate OrchestratorType '{orchestrator_type}' found in plugin '{plugin_name}'. Skipping plugin.")
            return False
        return True

    def _import_plugin_instance(self, plugin_folder: str, plugin_definition: PluginDefinition) -> Optional[BasePlugin]:
        module_full_name = f"hw_agent.plugins.{plugin_folder}.{plugin_definition.module}"
        try:
            # Remove module from sys.modules if already loaded to allow reloading
            if module_full_name in sys.modules:
                del sys.modules[module_full_name]
            module = importlib.import_module(module_full_name)
            importlib.reload(module)

            plugin_class = self._find_plugin_class_in_module(module)
            if not plugin_class:
                self.logger.error(f"No valid plugin class found in module '{module_full_name}'.")
                return None

            # Instantiate the plugin and set the plugin configuration
            plugin_instance = plugin_class()
            plugin_instance.plugin_definition = plugin_definition
            
            self.logger.info(f"Loaded plugin '{plugin_definition.name}' for orchestrator '{plugin_definition.orchestrator_type}'.")
            
            return plugin_instance

        except Exception as e:
            self.logger.error(f"Error importing and initializing plugin '{module_full_name}': {e}")
            return None
                
    def _find_plugin_class_in_module(self, module) -> Optional[type]:
        for attribute_name in dir(module):
            attribute = getattr(module, attribute_name)
            if (
                isinstance(attribute, type)
                and issubclass(attribute, BasePlugin)
                and attribute is not BasePlugin
            ):
                self.logger.debug(f"Found plugin class '{attribute.__name__}' in module '{module.__name__}'.")
                return attribute
        return None

    def _register_plugin(self, orchestrator_type: str, plugin_instance: BasePlugin):
        self.plugins[orchestrator_type] = plugin_instance
        self.cache_service.store_plugin(orchestrator_type, plugin_instance)
        self.logger.info(f"Registered plugin for orchestrator '{orchestrator_type}'.")

    def get_plugin(self, orchestrator_type: str) -> BasePlugin:
        plugin = self.cache_service.retrieve_plugin(orchestrator_type)
        if not plugin:
            plugin = self.plugins.get(orchestrator_type)
            if not plugin:
                self.logger.error(f"No plugin found for orchestrator type: '{orchestrator_type}'.")
                raise PluginNotFoundError(f"No plugin found for orchestrator type: {orchestrator_type}")
            self.cache_service.store_plugin(orchestrator_type, plugin)
        return plugin

    def get_all_plugins(self) -> List[BasePlugin]:
        return [
            {
                "plugin": plugin.plugin_definition,
            }
            for _, plugin in self.plugins.items()
        ]

    def reload_plugins(self) -> List[BasePlugin]:
        self.logger.info("Reloading all plugins...")
        self._load_plugin_definitions()
        self.logger.info("Reloaded all plugins...")
        return self.get_all_plugins()

    def validate_connection_info(self, connection_definition: dict, orchestratory_type: OrchestratorType) -> bool:
        if plugin := self.get_plugin(orchestratory_type):
            try:
                self._validate_connection_info(plugin.plugin_definition.connection_schema, connection_definition)
            except jsonschema.ValidationError as e:
                self.logger.error(f"Connection data validation error: {e.message}")
                raise ConnectionConfigurationError(e)
        else:
            self.logger.error(f"No plugin found for orchestrator type: '{orchestratory_type}'.")
            raise PluginNotFoundError(f"No plugin found for orchestrator type: {orchestratory_type}")
    
    

    def _validate_connection_info(self, schema: dict, connection_data: dict) -> dict:
        """
        Validates 'connection_data' against a JSON Schema given by 'schema'.
        
        :param schema: A dict containing the JSON Schema structure.
        :param connection_data: The user-supplied connection info dict.
        :return: The same 'connection_data' if validation passes.
        :raises ValidationError: If the data does not match the schema.
        """
        try:
            jsonschema.validate(instance=connection_data, schema=schema)
            return connection_data
        except Exception as e:
            raise jsonschema.ValidationError(f"JSON Schema validation error: {e.message}") from e
